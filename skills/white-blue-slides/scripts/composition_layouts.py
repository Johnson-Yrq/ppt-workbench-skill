"""Shared compositions extracted from the approved and exploratory slide samples.

These layouts own content geometry, never a colour palette, header, font family,
photographic requirement or presentation mode. All text stays editable and all
images and charts use the common builder's resource and data handling.
"""
from html import escape
from math import isfinite
from functools import lru_cache
import json


SHARED_LAYOUTS = {
    'photo_pair': {'name': '双图夹文', 'role': 'explanation', 'image_count': (2, 2), 'fields': {'images', 'copy', 'eyebrow'}},
    'offset_pair': {'name': '阶梯错位双图', 'role': 'explanation', 'image_count': (2, 2), 'fields': {'images', 'paragraphs'}},
    'statement_tags': {'name': '大字与标签群', 'role': 'explanation', 'image_count': (0, 1), 'fields': {'image', 'copy', 'tags'}},
    'checklist_photo': {'name': '半幅图片与分组清单', 'role': 'capabilities', 'image_count': (1, 1), 'fields': {'image', 'groups'}},
    'snake_timeline': {'name': '双行折返时间线', 'role': 'process', 'image_count': (0, 1), 'fields': {'image', 'steps', 'note'}},
    'metric_cards': {'name': '图片横幅与指标卡', 'role': 'comparison', 'image_count': (0, 1), 'fields': {'image', 'metrics', 'copy', 'source'}},
    'photo_strip': {'name': '多图条带与底部标题', 'role': 'explanation', 'image_count': (2, 5), 'fields': {'images', 'copy'}},
    'problem_columns': {'name': '问题分栏与底部标题', 'role': 'comparison', 'image_count': (0, 1), 'fields': {'image', 'items'}},
    'service_cards': {'name': '不等尺寸服务块', 'role': 'capabilities', 'image_count': (0, 3), 'fields': {'items', 'highlight', 'aside'}},
    'metric_circles': {'name': '大小圆指标', 'role': 'comparison', 'image_count': (0, 1), 'fields': {'image', 'metrics', 'copy', 'source'}},
    'chart_focus': {'name': '结论与独立图表', 'role': 'briefing', 'image_count': (0, 0), 'fields': {'chart', 'copy', 'stat', 'conclusion'}},
    'photo_banner': {'name': '大标题与横幅图片', 'role': 'cover', 'image_count': (1, 1), 'fields': {'image', 'copy', 'eyebrow', 'tags'}},
    'photo_divider': {'name': '满幅图片与章节短句', 'role': 'explanation', 'image_count': (1, 1), 'fields': {'image', 'copy', 'eyebrow'}},
    'side_index': {'name': '侧向标题与目录', 'role': 'briefing', 'image_count': (0, 1), 'fields': {'image', 'items', 'eyebrow'}},
    'editorial_story': {'name': '双段正文与竖幅图片', 'role': 'explanation', 'image_count': (1, 1), 'fields': {'image', 'items', 'eyebrow'}},
    'step_sidebar': {'name': '侧栏说明与竖排步骤', 'role': 'process', 'image_count': (0, 1), 'fields': {'image', 'copy', 'steps', 'note'}},
    'type_poster': {'name': '纯文字海报与章节号', 'role': 'cover', 'image_count': (0, 0), 'fields': {'variant', 'number', 'show_title', 'placement', 'eyebrow', 'copy', 'bullets'}},
    'editorial_columns': {'name': '自由宽度编辑分栏', 'role': 'explanation', 'image_count': (0, 48), 'fields': {'columns', 'title_column', 'show_title'}},
    'hub_spoke': {'name': '中心关系与分支', 'role': 'explanation', 'image_count': (0, 0), 'fields': {'center', 'items', 'copy'}},
    'step_row': {'name': '横向步骤与说明', 'role': 'process', 'image_count': (0, 0), 'fields': {'steps', 'copy', 'note'}},
}
COMMON_FIELDS = {'id', 'layout', 'title', 'chapter', 'subtitle', 'header', 'notes', 'visual',
                 'surface', 'title_size', 'body_size', '_number', 'layout_intent', 'layout_selection'}
IMAGE_FIELDS = {'src', 'alt', 'caption', 'ratio', 'brief', 'ui_text', 'zoom', 'offset_x',
                'offset_y', 'edge_fade', 'background_mode'}
COLUMN_FIELDS = {
    'text': {'heading', 'paragraphs'}, 'image': {'image'},
    'gallery': {'images', 'grid_columns', 'row_weights'}, 'people': {'items'},
    'groups': {'items', 'group_columns'}, 'chart': {'chart', 'copy'},
}


def _text(value, label, optional=False):
    if optional and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} 必须为非空字符串')


def _list(slide, key, low, high):
    result = slide.get(key)
    if not isinstance(result, list) or not low <= len(result) <= high:
        raise ValueError(f'{slide["layout"]}.{key} 需要 {low}–{high} 项')
    return result


def _object(value, allowed, required, label):
    if not isinstance(value, dict):
        raise ValueError(f'{label} 必须为对象')
    extra = set(value) - set(allowed)
    if extra:
        raise ValueError(f'{label} 不支持字段：' + ' / '.join(sorted(extra)))
    for field in required:
        _text(value.get(field), f'{label}.{field}')


def _column_list(column, key, low, high, label):
    value = column.get(key)
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise ValueError(f'{label}.{key} 需要 {low}–{high} 项')
    return value


def _weight(value, label):
    if (isinstance(value, bool) or not isinstance(value, (float, int))
            or not .5 <= value <= 4 or not isfinite(value)):
        raise ValueError(f'{label} 必须为 0.5–4 之间的有限数字')


@lru_cache(maxsize=1)
def _icon_names():
    from common import ASSETS
    return frozenset(json.loads((ASSETS / 'icons.json').read_text(encoding='utf-8')))


def _chart(value, label):
    from chart_contract import chart_errors
    _object(value, ('title', 'chart_type', 'categories', 'series', 'unit', 'source'), ('title',), label)
    if isinstance(value.get('series'), list):
        for series in value['series']:
            _object(series, ('name', 'values'), ('name',), label + '.series[]')
    errors = chart_errors(value)
    if errors:
        raise ValueError(label + '：' + '；'.join(errors))


def editorial_columns(slide):
    """Validate columns once for image traversal and rendering, in reading order."""
    columns = _list(slide, 'columns', 2, 6)
    index = slide.get('title_column', 0)
    if type(index) is not int or not 0 <= index < len(columns):
        raise ValueError('editorial_columns.title_column 必须为从 0 开始的有效栏索引')
    if type(slide.get('show_title', True)) is not bool:
        raise ValueError('editorial_columns.show_title 必须为 true / false')
    for i, column in enumerate(columns):
        label = f'editorial_columns.columns[{i}]'
        kind = column.get('type') if isinstance(column, dict) else None
        if not isinstance(kind, str) or kind not in COLUMN_FIELDS:
            raise ValueError(f'{label}.type 可选 text / image / gallery / people / groups / chart')
        _object(column, COLUMN_FIELDS[kind] | {'type', 'weight', 'align'}, ('type',), label)
        _weight(column.get('weight', 1), label + '.weight')
        if column.get('align', 'start') not in ('start', 'end'):
            raise ValueError(f'{label}.align 可选 start / end')
        if kind == 'text':
            if 'heading' in column:
                _text(column['heading'], label + '.heading')
            if 'paragraphs' in column:
                for paragraph in _column_list(column, 'paragraphs', 1, 6, label):
                    _text(paragraph, label + '.paragraphs[]')
            elif not column.get('heading'):
                if i != index or not slide.get('show_title', True):
                    raise ValueError(f'{label} 省略 paragraphs 时必须有 heading 或承载可见页标题')
                _text(slide.get('title'), 'editorial_columns.title')
        elif kind == 'image':
            if 'image' not in column:
                raise ValueError(f'{label}.image 需要图片对象')
        elif kind == 'gallery':
            images = _column_list(column, 'images', 2, 8, label)
            if type(column.get('grid_columns', 2)) is not int or column.get('grid_columns', 2) not in (1, 2):
                raise ValueError(f'{label}.grid_columns 可选 1 / 2')
            if 'row_weights' in column:
                weights = column['row_weights']
                if column.get('grid_columns', 2) != 1:
                    raise ValueError(f'{label}.row_weights 仅用于 grid_columns: 1')
                if not isinstance(weights, list) or len(weights) != len(images):
                    raise ValueError(f'{label}.row_weights 需要与 images 数量相同的权重数组')
                for weight in weights:
                    _weight(weight, label + '.row_weights[]')
        elif kind == 'people':
            for person in _column_list(column, 'items', 1, 4, label):
                _object(person, ('image', 'name', 'role'), ('name', 'role'), label + '.items[]')
                if 'image' not in person:
                    raise ValueError(f'{label}.items[].image 需要图片对象')
        elif kind == 'groups':
            for group in _column_list(column, 'items', 2, 6, label):
                _object(group, ('title', 'text', 'icon'), ('title',), label + '.items[]')
                if 'text' in group:
                    _text(group['text'], label + '.items[].text')
                if 'icon' in group:
                    _text(group['icon'], label + '.items[].icon')
                    if group['icon'] not in _icon_names():
                        raise ValueError(f'{label}.items[] 未知图标 {group["icon"]}；查看 assets/icons.json 中的键名')
            if type(column.get('group_columns', 1)) is not int or column.get('group_columns', 1) not in (1, 2):
                raise ValueError(f'{label}.group_columns 可选 1 / 2')
        elif kind == 'chart':
            _chart(column.get('chart'), label + '.chart')
            if 'copy' in column:
                _text(column['copy'], label + '.copy')
    return columns


def composition_images(slide):
    """Return every image, including nested cards and columns, in DOM order."""
    layout = slide.get('layout')
    if layout not in SHARED_LAYOUTS:
        raise ValueError(f'未知共享构图：{layout}')
    if 'image' in slide and 'images' in slide:
        raise ValueError('image 与 images 不能同时使用')
    if layout == 'editorial_columns':
        images = []
        for column in editorial_columns(slide):
            if column['type'] == 'image':
                images.append(column['image'])
            elif column['type'] == 'gallery':
                images.extend(column['images'])
            elif column['type'] == 'people':
                images.extend(person['image'] for person in column['items'])
    elif layout == 'service_cards':
        items = slide.get('items', [])
        images = [item['image'] for item in items if isinstance(item, dict) and 'image' in item] if isinstance(items, list) else []
    elif 'images' in slide:
        if not isinstance(slide['images'], list):
            raise ValueError('images 必须为图片对象数组')
        images = slide['images']
    elif 'image' in slide:
        images = [slide['image']]
    else:
        images = []
    low, high = SHARED_LAYOUTS[layout]['image_count']
    if not low <= len(images) <= high:
        raise ValueError(f'{layout} 需要 {low}–{high} 张图片')
    for index, image in enumerate(images, 1):
        allowed = IMAGE_FIELDS | {'frame'} if layout == 'editorial_columns' else IMAGE_FIELDS
        _object(image, allowed, ('src', 'alt'), f'{layout}.image[{index}]')
        if 'caption' in image:
            _text(image['caption'], 'image.caption')
        if 'frame' in image and image['frame'] not in ('none', 'monitor'):
            raise ValueError('editorial_columns.image.frame 可选 none / monitor')
    return images


def validate_composition(slide):
    layout = slide.get('layout')
    if layout not in SHARED_LAYOUTS:
        raise ValueError(f'未知共享构图：{layout}')
    extra = set(slide) - COMMON_FIELDS - SHARED_LAYOUTS[layout]['fields']
    if extra:
        raise ValueError(f'{layout} 不支持字段：' + ' / '.join(sorted(extra)))
    _text(slide.get('title'), f'{layout}.title')
    for key in ('copy', 'eyebrow', 'note', 'source', 'aside', 'conclusion'):
        if key in slide:
            _text(slide[key], f'{layout}.{key}')
    composition_images(slide)
    if layout == 'type_poster':
        variant = slide.get('variant', 'cover')
        if variant not in ('cover', 'chapter', 'statement'):
            raise ValueError('type_poster.variant 可选 cover / chapter / statement')
        if 'placement' in slide:
            if slide['placement'] not in ('bottom-left', 'center', 'bottom-right'):
                raise ValueError('type_poster.placement 可选 bottom-left / center / bottom-right')
            if variant == 'chapter':
                raise ValueError('type_poster.chapter 使用固定章节编号构图，不设置 placement')
        if 'number' in slide or variant == 'chapter':
            _text(slide.get('number'), 'type_poster.number')
        if variant == 'statement' and 'number' in slide:
            raise ValueError('type_poster.statement 不设置 number；编号页使用 chapter')
        if type(slide.get('show_title', True)) is not bool:
            raise ValueError('type_poster.show_title 必须为 true / false')
        if variant != 'chapter' and not slide.get('show_title', True):
            raise ValueError('type_poster 的 cover / statement 必须显示 title；show_title: false 仅用于 chapter')
        if variant != 'statement' and any(key in slide for key in ('copy', 'bullets')):
            raise ValueError('type_poster.copy / bullets 仅用于 statement')
        if 'bullets' in slide:
            for bullet in _list(slide, 'bullets', 1, 8):
                _text(bullet, 'type_poster.bullets[]')
    if layout in {'photo_pair', 'statement_tags', 'chart_focus', 'step_sidebar'}:
        _text(slide.get('copy'), f'{layout}.copy')
    if layout == 'offset_pair':
        for value in _list(slide, 'paragraphs', 2, 3):
            _text(value, 'paragraphs[]')
    if layout == 'statement_tags' or 'tags' in slide:
        for tag in _list(slide, 'tags', 2, 6):
            _text(tag, 'tags[]')
    if layout in {'problem_columns', 'service_cards', 'editorial_story'}:
        low, high = (3, 3) if layout == 'service_cards' else (2, 3) if layout == 'problem_columns' else (1, 3)
        for item in _list(slide, 'items', low, high):
            _object(item, ('title', 'text', 'image') if layout == 'service_cards' else ('title', 'text'), ('title', 'text'), 'items[]')
        if 'highlight' in slide and (type(slide['highlight']) is not int or not 0 <= slide['highlight'] < 3):
            raise ValueError('service_cards.highlight 使用从 0 开始的索引 0 / 1 / 2')
    if layout == 'side_index':
        for item in _list(slide, 'items', 2, 12):
            _object(item, ('title', 'label'), ('title',), 'items[]')
            if 'label' in item:
                _text(item['label'], 'items[].label')
    if layout == 'checklist_photo':
        for group in _list(slide, 'groups', 2, 3):
            _object(group, ('title', 'text', 'checks'), ('title', 'text'), 'groups[]')
            checks = group.get('checks')
            if not isinstance(checks, list) or not 2 <= len(checks) <= 6:
                raise ValueError('groups[].checks 需要 2–6 项')
            for check in checks:
                _object(check, ('label', 'checked'), ('label',), 'checks[]')
                if type(check.get('checked')) is not bool:
                    raise ValueError('checks[].checked 必须为 true / false，状态不能只靠颜色表示')
    if layout == 'hub_spoke':
        _object(slide.get('center'), ('title', 'text'), ('title',), 'hub_spoke.center')
        for item in [slide['center']] + _list(slide, 'items', 4, 8):
            _object(item, ('title', 'text'), ('title',), 'hub_spoke.node')
            if 'text' in item:
                _text(item['text'], 'hub_spoke.node.text')
    if layout in {'snake_timeline', 'step_sidebar', 'step_row'}:
        low, high = (4, 8) if layout == 'snake_timeline' else (2, 6) if layout == 'step_row' else (2, 4)
        for step in _list(slide, 'steps', low, high):
            _object(step, ('title', 'text', 'period'), ('title', 'text'), 'steps[]')
            if 'period' in step:
                _text(step['period'], 'steps[].period')
    if layout in {'metric_cards', 'metric_circles'}:
        low, high = (2, 2) if layout == 'metric_circles' else (2, 4)
        _text(slide.get('source'), f'{layout}.source')
        for metric in _list(slide, 'metrics', low, high):
            _object(metric, ('label', 'value', 'text', 'progress') if layout == 'metric_cards' else ('label', 'value', 'text'), ('label',), 'metrics[]')
            if 'progress' in metric:
                if 'value' in metric:
                    raise ValueError('metrics[].progress 与 value 不能同时设置；比例文字由进度数据计算')
                progress = metric['progress']
                _object(progress, ('value', 'max'), (), 'metrics[].progress')
                value, maximum = progress.get('value'), progress.get('max')
                try:
                    finite = all(not isinstance(v, bool) and isinstance(v, (int, float)) and isfinite(v) for v in (value, maximum))
                except OverflowError:
                    finite = False
                if not finite or not 0 <= value <= maximum or maximum <= 0:
                    raise ValueError('metrics[].progress 需要有限数值 0 ≤ value ≤ max，且 max > 0')
            if layout == 'metric_circles':
                _text(metric.get('value'), 'metrics[].value')
            elif not metric.get('value') and not metric.get('text') and 'progress' not in metric:
                raise ValueError('metric_cards 每项需要 value 或 text')
            for key in ('value', 'text'):
                if key in metric:
                    _text(metric[key], f'metrics[].{key}')
    if layout == 'chart_focus':
        _chart(slide.get('chart'), 'chart_focus.chart')
        if 'stat' in slide:
            _object(slide['stat'], ('value', 'label'), ('value', 'label'), 'stat')
    return layout


def render_composition(builder, slide):
    """Render all shared layouts through the common editable/image/chart APIs."""
    from build_deck import editable
    layout = validate_composition(slide)
    def e(tag, value, cls='', component=''):
        return editable(tag, value, cls, True, component)
    def optional(key, tag='p', cls=''):
        return e(tag, slide[key], cls or 'comp-' + key) if slide.get(key) else ''
    def image(value, cls=''):
        result = builder.image({'image': value, '_number': slide.get('_number', '?')}, 'comp-image' + (' ' + cls if cls else ''), caption=bool(value.get('caption')))
        if value.get('frame') == 'monitor':
            # Ratios are numeric constants, never free CSS from deck data.
            from common import IMAGE_RATIOS
            ratio = value.get('ratio', '16:9')
            if ratio not in IMAGE_RATIOS:
                raise ValueError('monitor 图片 ratio 必须为受支持的图片比例')
            result = '<div class="comp-monitor-frame" style="--monitor-screen-ratio:' + ratio.replace(':', '/') + '">' + result + '</div>'
        return result
    def photo(key='image', cls=''):
        return image(slide[key], cls) if slide.get(key) else ''
    def title():
        return e('h1', slide['title'], 'comp-title') + optional('subtitle', cls='comp-subtitle')
    def tags():
        return '<div class="comp-tags">' + ''.join(e('span', t, 'comp-tag', 'tag') for t in slide.get('tags', [])) + '</div>'
    def articles(values, cls='comp-article'):
        return ''.join('<article class="' + cls + '">' + e('h2', item['title']) + e('p', item['text']) + '</article>' for item in values)
    def steps():
        values = slide['steps']
        columns = (len(values) + 1) // 2 if layout == 'snake_timeline' else len(values) if layout == 'step_row' else 1
        out = '<div class="comp-steps" style="--step-columns:' + str(columns) + '">'
        for i, item in enumerate(values):
            row, column = (1, i + 1) if i < columns else (2, columns - (i - columns))
            placement = f' style="--step-row:{row};--step-column:{column}"' if layout == 'snake_timeline' else ''
            out += f'<article class="comp-step" data-step="{i+1}"{placement}>' + e('span', f'{i+1:02}', 'comp-index')
            out += '<div>' + e('h2', item['title'])
            if item.get('period'):
                out += e('p', item['period'], 'comp-period')
            out += e('p', item['text']) + '</div></article>'
        return out + '</div>'
    def metrics():
        out = '<div class="comp-metrics" style="--metric-count:' + str(len(slide['metrics'])) + '">'
        for i, item in enumerate(slide['metrics']):
            out += f'<article class="comp-metric comp-metric-{i+1}" data-component="metric">'
            if 'progress' in item:
                progress = item['progress']
                percent = f'{progress["value"] / progress["max"] * 100:.1f}'.rstrip('0').rstrip('.')
                out += f'<div class="comp-progress" data-component="progress"><div class="comp-progress-track" role="meter" aria-label="{escape(item["label"], quote=True)}" aria-valuemin="0" aria-valuemax="{progress["max"]}" aria-valuenow="{progress["value"]}"><span class="comp-progress-fill" style="width:{percent}%"></span></div><strong class="comp-progress-percent">{percent}%</strong>'
                out += '<details class="comp-progress-editor"><summary>编辑进度数据</summary><table class="comp-progress-data"><thead><tr><th>当前值</th><th>目标值</th></tr></thead><tbody><tr>' + e('td', str(progress['value'])) + e('td', str(progress['max'])) + '</tr></tbody></table></details></div>'
            elif item.get('value'):
                out += e('strong', item['value'], 'comp-metric-value')
            out += e('h2', item['label'])
            if item.get('text'):
                out += e('p', item['text'])
            out += '</article>'
        return out + '</div>'

    if layout == 'hub_spoke':
        values = slide['items']
        branches = (len(values) + 1) // 2
        center_column = branches // 2 + 1
        content = '<div class="comp-hub-heading">' + title() + optional('copy') + '</div>'
        content += f'<div class="comp-hub-board" style="--hub-columns:{branches + 1};--hub-center-column:{center_column}">'
        for index in range(branches):
            column = index + 1 + (index + 1 >= center_column)
            content += f'<span class="comp-hub-branch" aria-hidden="true" style="--hub-column:{column}"></span>'
        center = slide['center']
        content += '<article class="comp-hub-center">' + e('h2', center['title']) + (e('p', center['text']) if center.get('text') else '') + '</article>'
        for index, item in enumerate(values):
            branch = index % branches
            column = branch + 1 + (branch + 1 >= center_column)
            row = 1 + index // branches
            content += f'<article class="comp-hub-node" data-component="relation" data-hub-row="{row}" style="--hub-column:{column};--hub-row:{row}">' + e('h2', item['title']) + (e('p', item['text']) if item.get('text') else '') + '</article>'
        content += '</div>'
    elif layout == 'step_row':
        content = '<div class="comp-sequence-heading">' + title() + optional('copy') + '</div>' + steps() + optional('note')
    elif layout == 'type_poster':
        hidden = ' is-concealed' if not slide.get('show_title', True) else ''
        content = '<div class="comp-poster-heading' + hidden + '">' + optional('eyebrow') + e('h1', slide['title'], 'comp-title comp-poster-title') + optional('subtitle', cls='comp-subtitle') + optional('copy')
        if slide.get('bullets'):
            content += '<ul class="comp-poster-bullets">' + ''.join(e('li', bullet) for bullet in slide['bullets']) + '</ul>'
        content += '</div>'
        content += e('p', slide['number'], 'comp-poster-number') if slide.get('number') else ''
    elif layout == 'editorial_columns':
        content = ''
        for i, column in enumerate(slide['columns']):
            kind = column['type']
            content += f'<section class="comp-column" data-column-type="{kind}" data-align="{column.get("align", "start")}" data-column-index="{i}">'
            if i == slide.get('title_column', 0):
                hidden = ' is-concealed' if not slide.get('show_title', True) else ''
                content += '<div class="comp-column-title' + hidden + '">' + title() + '</div>'
            content += f'<div class="comp-column-content comp-column-{kind}">'
            if kind == 'text':
                if column.get('heading'):
                    content += e('h2', column['heading'], 'comp-column-heading')
                content += ''.join(e('p', paragraph) for paragraph in column.get('paragraphs', []))
            elif kind == 'image':
                content += image(column['image'])
            elif kind == 'gallery':
                row_style = ';grid-template-rows:' + ' '.join(f'minmax(0,{weight:g}fr)' for weight in column['row_weights']) if 'row_weights' in column else ''
                content += '<div class="comp-gallery-grid" style="--grid-columns:' + str(column.get('grid_columns', 2)) + ';--grid-rows:' + str((len(column['images']) + column.get('grid_columns', 2) - 1) // column.get('grid_columns', 2)) + row_style + '">' + ''.join(image(im) for im in column['images']) + '</div>'
            elif kind == 'people':
                for person in column['items']:
                    content += '<article class="comp-column-person">' + image(person['image']) + '<div>' + e('h2', person['name'], 'comp-person-name') + e('p', person['role'], 'comp-person-role') + '</div></article>'
            elif kind == 'chart':
                content += '<div class="comp-chart-caption">' + e('h2', column['chart']['title'], 'comp-chart-title')
                if column.get('copy'):
                    content += e('p', column['copy'], 'comp-chart-copy')
                content += '</div>' + builder.chart(column['chart'])
            elif kind == 'groups':
                content += '<div class="comp-groups-grid" style="--group-columns:' + str(column.get('group_columns', 1)) + '">'
                for group in column['items']:
                    copy = e('h2', group['title']) + (e('p', group['text']) if group.get('text') else '')
                    if group.get('icon'):
                        content += '<article class="comp-column-group has-icon">' + builder.icon(group['icon']) + '<div class="comp-group-copy">' + copy + '</div></article>'
                    else:
                        content += '<article class="comp-column-group">' + copy + '</article>'
                content += '</div>'
            content += '</div></section>'
    elif layout == 'photo_pair':
        content = title() + '<div class="comp-pair">' + image(slide['images'][0]) + '<div class="comp-copy-block">' + optional('eyebrow') + optional('copy') + '</div>' + image(slide['images'][1]) + '</div>'
    elif layout == 'offset_pair':
        content = '<div class="comp-offset-heading">' + title() + '</div>' + image(slide['images'][0], 'comp-portrait') + image(slide['images'][1], 'comp-detail')
        content += '<div class="comp-paragraphs">' + ''.join(e('p', p) for p in slide['paragraphs']) + '</div>'
    elif layout == 'statement_tags':
        content = '<div class="comp-statement">' + title() + optional('copy') + tags() + '</div>' + photo()
    elif layout == 'checklist_photo':
        content = '<div class="comp-photo-panel">' + photo() + title() + '</div><div class="comp-check-groups">'
        for group in slide['groups']:
            content += '<article>' + e('h2', group['title']) + e('p', group['text']) + '<ul class="comp-checks">'
            for check in group['checks']:
                symbol = '✓' if check['checked'] else '—'
                state = 'included' if check['checked'] else 'excluded'
                content += f'<li data-component="state" data-state="{state}"><span aria-hidden="true">{symbol}</span>' + e('span', check['label']) + '</li>'
            content += '</ul></article>'
        content += '</div>'
    elif layout == 'snake_timeline':
        content = steps() + '<div class="comp-timeline-bottom">' + title() + photo() + optional('note') + '</div>'
    elif layout == 'metric_cards':
        content = '<div class="comp-metric-banner">' + photo() + title() + optional('copy') + '</div>' + metrics() + optional('source')
    elif layout == 'photo_strip':
        content = '<div class="comp-strip" style="--image-count:' + str(len(slide['images'])) + '">' + ''.join(image(im) for im in slide['images']) + '</div>' + title() + optional('copy')
    elif layout == 'problem_columns':
        content = '<div class="comp-problems" style="--column-count:' + str(len(slide['items'])) + '">' + articles(slide['items']) + '</div><div class="comp-problem-bottom">' + title() + photo() + '</div>'
    elif layout == 'service_cards':
        content = title() + '<div class="comp-services">'
        highlight = slide.get('highlight', 0)
        for i, item in enumerate(slide['items']):
            content += f'<article class="comp-service comp-service-{i+1}' + (' is-highlighted' if i == highlight else '') + '" data-component="panel">'
            content += e('span', f'{i+1:02}', 'comp-index')
            if item.get('image'):
                content += image(item['image'])
            content += e('h2', item['title']) + e('p', item['text']) + '</article>'
        content += '</div>' + optional('aside')
    elif layout == 'metric_circles':
        content = '<div class="comp-metric-copy">' + title() + optional('copy') + '</div>' + metrics() + photo(cls='comp-circle-image')
        content += '<div class="comp-metric-notes">' + optional('source') + e('p', '圆形面积仅表示视觉主次，不代表数值比例。', 'comp-scale-note') + '</div>'
    elif layout == 'chart_focus':
        content = '<div class="comp-chart-copy">' + title() + optional('copy')
        if slide.get('stat'):
            content += '<div class="comp-stat">' + e('strong', slide['stat']['value']) + e('p', slide['stat']['label']) + '</div>'
        content += '</div><div class="comp-chart">' + e('h2', slide['chart']['title']) + builder.chart(slide['chart']) + optional('conclusion') + '</div>'
    elif layout == 'photo_banner':
        content = '<div class="comp-banner-heading">' + optional('eyebrow') + title() + optional('copy') + '</div>' + photo() + (tags() if slide.get('tags') else '')
    elif layout == 'photo_divider':
        content = photo() + '<div class="comp-divider-copy">' + optional('eyebrow') + title() + optional('copy') + '</div>'
    elif layout == 'side_index':
        content = photo() + '<div class="comp-index-heading">' + title() + optional('eyebrow') + '</div><ol class="comp-index-list">'
        for i, item in enumerate(slide['items'], 1):
            content += '<li>' + e('span', item.get('label', f'{i:02}'), 'comp-index') + e('span', item['title']) + '</li>'
        content += '</ol>'
    elif layout == 'editorial_story':
        content = '<div class="comp-story-copy">' + optional('eyebrow') + title() + articles(slide['items']) + '</div>' + photo()
    else:  # step_sidebar
        content = '<div class="comp-step-aside">' + title() + optional('copy') + photo() + '</div>' + steps() + optional('note')
    image_class = ' has-image' if composition_images(slide) else ' no-image'
    variant_class = ' variant-' + slide.get('variant', 'cover') if layout == 'type_poster' else ''
    if layout == 'type_poster':
        variant = slide.get('variant', 'cover')
        if variant != 'chapter':
            variant_class += ' placement-' + slide.get('placement', 'center' if variant == 'statement' else 'bottom-left')
        if variant == 'statement' and not any(slide.get(key) for key in ('subtitle', 'copy', 'bullets')):
            variant_class += ' is-title-only'
    columns_style = (' style="grid-template-columns:' + ' '.join(f'minmax(0,{column.get("weight", 1):g}fr)' for column in slide['columns']) + '"') if layout == 'editorial_columns' else ''
    return f'<div class="shared-composition comp-{escape(layout, quote=True)}{image_class}{variant_class}"{columns_style}>{content}</div>'
