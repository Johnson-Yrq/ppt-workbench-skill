"""Discover independent presentation styles beside the shared toolkit.

Only declarative manifests bearing our schema are considered; deck data cannot
supply a package path or executable loader. Adding a sibling style needs no code edit.
"""
import argparse
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from editorial_contract import EDITORIAL_VARIANTS

SKILLS = Path(__file__).resolve().parents[2]
SCHEMA = 'html-slide-style/v1'
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SURFACES = ('light', 'dark')  # Historical names; each manifest now owns its safe slug whitelist.
IMAGE_FREE_LAYOUTS = ('cover', 'closing', 'table')
IMAGE_BACKGROUNDS = ('paper', 'scene')
HEADER_SYSTEMS = ('preset-six', 'style')
HEADER_SLOTS = {'chapter', 'title', 'subtitle', 'page', 'company', 'year'}
DEFAULT_HEADER_TEMPLATE = ('<header class="style-header"><div class="head-copy">{{chapter}}{{title}}{{subtitle}}</div>'
                           '<div class="header-meta">{{company}}{{year}}{{page}}</div></header>')


def validate_header_template(source):
    """Validate a local declarative fragment; only Builder-owned text slots expand.

    Templates define the style's frame, never script execution, remote resources
    or per-project HTML. Restricting slots to text positions also prevents a
    generated editable node from being interpolated into an HTML attribute.
    """
    class HeaderParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack, self.slots, self.headers = [], [], 0

        def handle_starttag(self, tag, attrs):
            if tag not in {'header', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'small', 'strong', 'b', 'em', 'i', 'br'}:
                raise ValueError(f'header_template 不支持标签：{tag}')
            if not self.stack and tag != 'header':
                raise ValueError('header_template 需要单个外层 header')
            if tag == 'header':
                self.headers += 1
                if self.stack or self.headers > 1:
                    raise ValueError('header_template 需要单个外层 header')
            for key, value in attrs:
                if key not in {'class', 'role', 'aria-label', 'aria-hidden'} or value is None:
                    raise ValueError(f'header_template 不支持属性：{key}')
                if '{{' in value or '}}' in value:
                    raise ValueError('header_template 占位符只能位于文字位置，不能放入属性')
            if tag != 'br':
                self.stack.append(tag)

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if tag != 'br':
                self.handle_endtag(tag)

        def handle_endtag(self, tag):
            if not self.stack or self.stack.pop() != tag:
                raise ValueError('header_template 标签没有正确闭合')

        def handle_data(self, data):
            if not self.stack and data.strip():
                raise ValueError('header_template 不在 header 外放置内容')
            slots = re.findall(r'\{\{\s*([a-z_]+)\s*\}\}', data)
            if any(slot not in HEADER_SLOTS for slot in slots):
                raise ValueError('header_template 占位符可选：' + ' / '.join(sorted(HEADER_SLOTS)))
            remaining = re.sub(r'\{\{\s*([a-z_]+)\s*\}\}', '', data)
            if '{{' in remaining or '}}' in remaining:
                raise ValueError('header_template 含无效占位符')
            self.slots.extend(slots)

        def handle_comment(self, data):
            if '{{' in data or '}}' in data:
                raise ValueError('header_template 注释中不放占位符')

        def handle_decl(self, decl):
            raise ValueError('header_template 仅接受 header 片段')

    parser = HeaderParser()
    parser.feed(source)
    parser.close()
    if re.findall(r'\{\{\s*([a-z_]+)\s*\}\}', source) != parser.slots:
        raise ValueError('header_template 占位符使用字面的 {{name}}，不能用 HTML 实体编码')
    if parser.headers != 1 or parser.stack:
        raise ValueError('header_template 需要正确闭合的单个 header')
    if len(parser.slots) != len(set(parser.slots)):
        raise ValueError('header_template 每种占位符最多出现一次')
    if 'title' not in parser.slots:
        raise ValueError('header_template 必须包含 {{title}}，供普通内容页显示标题')
    return source


def _scan():
    found, errors = {}, []
    for path in sorted(SKILLS.glob('*/assets/style.json')):
        try:
            pack = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            errors.append(f'不能读取风格清单 {path}: {exc}')
            continue
        if not isinstance(pack, dict) or pack.get('schema') != SCHEMA:
            continue  # unrelated skills may also use a file called style.json
        name = pack.get('id')
        if not isinstance(name, str) or len(name) > 64 or not ID.fullmatch(name):
            errors.append(f'风格 id 需要短横线分隔的小写字母或数字：{path}')
            continue
        found.setdefault(name, []).append((path, pack))
    return found, errors


def _load(path, source, allow_draft=False):
    """Resolve a manifest's resource paths; only fields the builder and prompt export actually read are checked."""
    pack = dict(source)
    for key in ('name', 'description'):
        if not isinstance(pack.get(key), str) or not pack[key].strip():
            raise ValueError(f'风格清单 {key} 需要非空说明：{path}')
    if pack.get('status') != 'ready' and not allow_draft:
        raise ValueError(f'{pack["id"]} 仍为 draft；先完成风格样例确认和验证，再设为 ready')
    assets, root = path.parent.resolve(), path.parent.parent.resolve()
    for field in ('css', 'image_prompt', 'image_reference', 'header_template'):
        value = pack.get(field)
        if value is None and field != 'image_prompt':
            continue
        if field == 'header_template' and (not isinstance(value, str) or not value.strip()
                                           or Path(value).is_absolute() or '://' in value):
            raise ValueError(f'header_template 须为 assets 内的相对 HTML 文件路径：{path}')
        resource = (assets / str(value)).resolve()
        if not resource.is_relative_to(assets) or not resource.is_file():
            raise ValueError(f'风格资源缺失或路径无效：{field}={value}（{path}）')
        pack[field] = resource
    modes, prompts = pack.get('ui_text_modes') or [], pack.get('ui_text_prompts') or {}
    if pack.get('default_ui_text') not in modes or any(m not in prompts for m in modes):
        raise ValueError(f'ui_text_modes、default_ui_text 与 ui_text_prompts 需要一一对应：{path}')
    surfaces, image_free = pack.get('surfaces', ['light']), pack.get('image_free_layouts', [])
    if (not isinstance(surfaces, list) or 'light' not in surfaces
            or any(not isinstance(x, str) or len(x) > 32 or not ID.fullmatch(x) for x in surfaces)
            or len(set(surfaces)) != len(surfaces)):
        raise ValueError(f'surfaces 须包含 light、名称唯一，且仅用至多 32 位小写字母/数字/短横线 slug：{path}')
    if not isinstance(image_free, list) or not all(x in IMAGE_FREE_LAYOUTS for x in image_free):
        raise ValueError(f'image_free_layouts 可选 {" / ".join(IMAGE_FREE_LAYOUTS)}：{path}')
    editorial = pack.get('editorial_variants', [])
    if (not isinstance(editorial, list) or any(not isinstance(x, str) or x not in EDITORIAL_VARIANTS for x in editorial)
            or len(set(editorial)) != len(editorial)):
        raise ValueError(f'editorial_variants 须为不重复数组，可选 {" / ".join(EDITORIAL_VARIANTS)}：{path}')
    background = pack.get('image_background', 'paper')
    if not isinstance(background, str) or background not in IMAGE_BACKGROUNDS:
        raise ValueError(f'image_background 可选 {" / ".join(IMAGE_BACKGROUNDS)}：{path}')
    header_system = pack.get('header_system', 'style')
    if not isinstance(header_system, str) or header_system not in HEADER_SYSTEMS:
        raise ValueError(f'header_system 可选 {" / ".join(HEADER_SYSTEMS)}：{path}')
    if header_system == 'preset-six' and pack.get('header_template'):
        raise ValueError(f'preset-six 不使用 header_template；自定义页头使用 header_system: style：{path}')
    header_markup = None
    if header_system == 'style':
        header_markup = validate_header_template(pack['header_template'].read_text(encoding='utf-8')
                                                if pack.get('header_template') else DEFAULT_HEADER_TEMPLATE)
    heading_icons = pack.get('heading_icons', 'optional')
    if not isinstance(heading_icons, str) or heading_icons not in {'required', 'optional'}:
        raise ValueError(f'heading_icons 可选 required / optional：{path}')
    cover_copy_policy = pack.get('cover_copy_policy', 'style')
    if not isinstance(cover_copy_policy, str) or cover_copy_policy not in {'legacy', 'style'}:
        raise ValueError(f'cover_copy_policy 可选 legacy / style：{path}')
    pack.update(layout_hints=pack.get('layout_hints', {}), skill_file=root / 'SKILL.md', manifest=path.resolve(),
                surfaces=surfaces, image_free_layouts=image_free, editorial_variants=list(EDITORIAL_VARIANTS),
                image_background=background, header_system=header_system, header_markup=header_markup,
                heading_icons=heading_icons, cover_copy_policy=cover_copy_policy)
    return pack


def paper_color(deck, pack=None):
    """Resolve paper using the same base → style → deck override order as the builder."""
    from common import ASSETS
    pack = pack or resolve_style(deck)
    result = None
    for css in [ASSETS / 'theme.css', pack.get('css')]:
        if css:
            source = re.sub(r'/\*.*?\*/', '', css.read_text(encoding='utf-8'), flags=re.S)
            colors = re.findall(r'--paper\s*:\s*(#[0-9a-fA-F]{6})\b', source)
            if colors: result = colors[-1]
    theme = deck.get('theme', {})
    if not isinstance(theme, dict):
        raise ValueError('theme 须为对象')
    result = theme.get('paper', result)
    if not isinstance(result, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', result):
        raise ValueError('无法解析当前主题纸色；theme.paper 须为 #RRGGBB')
    return result.upper()


def discover_styles(include_drafts=False):
    found, errors = _scan()
    styles = []
    for name, candidates in sorted(found.items()):
        if len(candidates) != 1:
            errors.append(f'风格 id 重复，无法选择 {name}：' + '、'.join(str(p) for p, _ in candidates))
            continue
        path, source = candidates[0]
        if source.get('status') == 'draft' and not include_drafts:
            continue
        try:
            pack = _load(path, source, allow_draft=include_drafts)
            styles.append({'id': name, 'name': pack['name'], 'description': pack['description'], 'status': pack['status'],
                           'skill_file': str(pack['skill_file']), 'manifest': str(pack['manifest']),
                           'image_reference': str(pack['image_reference']) if pack.get('image_reference') else None,
                           'presentation_modes': ['speech', 'reading'],
                           'editorial_variants': pack['editorial_variants'], 'image_background': pack['image_background'],
                           'header_system': pack['header_system'], 'heading_icons': pack['heading_icons'],
                           'cover_copy_policy': pack['cover_copy_policy']})
        except ValueError as exc:
            errors.append(str(exc))
    return {'styles': styles, 'errors': errors}


def resolve_style(deck):
    name = deck.get('style', 'scene-white')
    if not isinstance(name, str) or len(name) > 64 or not ID.fullmatch(name):
        raise ValueError('style 需要已安装风格的 id；运行 style_packs.py --list 查看')
    found, scan_errors = _scan()
    candidates = found.get(name, [])
    if len(candidates) > 1:
        raise ValueError(f'风格 id 重复，无法选择 {name}：' + '、'.join(str(p) for p, _ in candidates))
    if not candidates:
        available = ', '.join(s['id'] for s in discover_styles()['styles']) or '无'
        raise ValueError(f'缺少或未知的 style：{name}；可用：{available}。将风格技能与 white-blue-slides 同级安装到 skills 目录；运行 style_packs.py --list 查看资源问题。' + ('\n' + '\n'.join(scan_errors) if scan_errors else ''))
    pack = _load(*candidates[0])
    from common import slide_images
    from composition_layouts import SHARED_LAYOUTS
    for i, slide in enumerate(deck.get('slides', []), 1):
        if not isinstance(slide, dict):
            continue
        images = slide_images(slide)
        if 'style' in slide or any('style' in image for image in images):
            raise ValueError(f'第 {i} 页不能单独设置 style；整稿在根对象选择一种风格')
        shared = SHARED_LAYOUTS.get(slide.get('layout'))
        allows_no_image = shared is not None and shared['image_count'][0] == 0
        if not images and not allows_no_image and slide.get('layout') not in pack['image_free_layouts']:
            allowed = ' / '.join(pack['image_free_layouts'])
            raise ValueError(f'第 {i} 页需要 image 对象（含 src、alt）' + (f'；{name} 风格只有 {allowed} 可以无图' if allowed else ''))
        if not images and shared is None and (slide.get('variant', 'standard') != 'standard' or slide.get('labels')):
            raise ValueError(f'第 {i} 页无图时只用 standard 排布，不加 labels')
        surface = slide.get('surface', 'light')
        if not isinstance(surface, str) or surface not in pack['surfaces']:
            raise ValueError(f'第 {i} 页 surface 可选 {" / ".join(pack["surfaces"])}（当前 {name} 风格）')
        for image in images:
            mode = image.get('ui_text', pack['default_ui_text'])
            if not isinstance(mode, str) or mode not in pack['ui_text_modes']:
                raise ValueError(f'第 {i} 页 image.ui_text 可选 {" / ".join(pack["ui_text_modes"])}（当前 {name} 风格）')
    return pack


def ui_text_prompt(pack, mode):
    return pack['ui_text_prompts'][mode]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true', help='列出已安装且资源有效的风格，输出 JSON')
    parser.add_argument('--include-drafts', action='store_true', help='开发新风格时检查草稿，不使其可用于正式构建')
    args = parser.parse_args()
    result = discover_styles(args.include_drafts)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
