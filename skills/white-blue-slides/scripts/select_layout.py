#!/usr/bin/env python3
"""Offline layout eligibility and ranking; semantic intent is supplied by the agent.

The selector never rewrites content, generates facts, changes style, or emits a
finished deck. It works before rendering and rechecks a recorded choice at build.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path

from common import NATIVE_LAYOUTS, SKILL, VARIANTS, presentation_mode
from chart_contract import chart_errors, slide_charts
from composition_layouts import SHARED_LAYOUTS, composition_images
from editorial_contract import EDITORIAL_VARIANTS
from style_packs import resolve_style

LIBRARY = SKILL / 'references/layout-library.json'
RELATIONS = {'cover', 'closing', 'explanation', 'parallel', 'agenda', 'sequence',
             'timeline', 'comparison', 'hierarchy', 'network', 'causality',
             'formula', 'table', 'data', 'controls', 'mixed', 'team',
             'testimonials', 'statistics', 'gallery', 'contact', 'quote'}
BLOCK_TYPES = {'process', 'matrix', 'layers', 'chart', 'facts'}
CAPACITY_ISSUES = {'text-overflow', 'text-overlap', 'out-of-bounds', 'footer-collision',
                   'reading-block-overflow', 'reading-composition-mismatch', 'chart-label-clipped'}
TEXT_FIELDS = {'title', 'subtitle', 'summary', 'text', 'label', 'message', 'description',
               'period', 'state', 'states', 'deliverable', 'output', 'note', 'detail',
               'columns', 'rows', 'cells', 'categories', 'layers', 'items', 'steps',
               'groups', 'left', 'right', 'blocks', 'labels', 'credits', 'chains', 'nodes',
               'relation', 'formula', 'terms', 'result', 'fields', 'bottom', 'value',
               'copy', 'paragraphs', 'lead', 'kicker', 'eyebrow', 'tags', 'metrics',
               'aside', 'conclusion', 'source', 'stat', 'checks', 'caption',
               'chart', 'image', 'images', 'product', 'heading', 'name', 'role', 'number', 'bullets', 'center'}
COUNT_FIELDS = {'single', 'items', 'images', 'paragraphs', 'groups', 'steps',
                'metrics', 'tags', 'columns', 'chart.categories', 'columns.people', 'columns.gallery', 'columns.photos', 'columns.charts', 'nodes'}
SHARED_COUNT_FIELDS = {
    'photo_pair': 'images', 'offset_pair': 'paragraphs', 'statement_tags': 'tags',
    'checklist_photo': 'groups', 'snake_timeline': 'steps', 'metric_cards': 'metrics',
    'photo_strip': 'images', 'problem_columns': 'items', 'service_cards': 'items',
    'metric_circles': 'metrics', 'chart_focus': 'chart.categories',
    'photo_banner': 'single', 'photo_divider': 'single', 'side_index': 'items',
    'editorial_story': 'items', 'step_sidebar': 'steps', 'type_poster': 'single',
    'hub_spoke': 'items', 'step_row': 'steps'}
EDITORIAL_COUNT_FIELDS = {'cover': 'single', 'intro': 'single', 'contents': 'items',
                         'about': 'columns', 'services': 'items', 'process': 'items',
                         'portfolio': 'images', 'closing': 'single'}


def profile_settings_errors(profile):
    """Profile settings describe executable structure, never a theme or density."""
    layout, settings = profile['layout'], profile.get('settings')
    if not isinstance(settings, dict):
        return ['settings 需要对象']
    allowed = {'reading': {'composition'}, 'journey': {'connected'},
               'cover': {'variant'}, 'closing': {'variant'},
               'editorial': {'editorial_variant'}, 'service_cards': {'highlight'}}.get(layout, set())
    errors = []
    if set(settings) - allowed:
        errors.append('settings 含当前 renderer 不支持的字段')
    if layout == 'editorial' and settings.get('editorial_variant') not in EDITORIAL_VARIANTS:
        errors.append('editorial 需要已登记的 editorial_variant')
    if 'variant' in settings and settings['variant'] not in VARIANTS.get(layout, ()):
        errors.append('variant 与当前 layout 不匹配')
    if 'composition' in settings and settings['composition'] not in {'half_lr', 'half_tb', 'half_diagonal', 'quarter'}:
        errors.append('reading.composition 无效')
    if 'connected' in settings and type(settings['connected']) is not bool:
        errors.append('journey.connected 需要布尔值')
    if 'highlight' in settings and (type(settings['highlight']) is not int or not 0 <= settings['highlight'] < 3):
        errors.append('service_cards.highlight 需要 0 / 1 / 2')
    return errors


def range_valid(value, low=0):
    return (isinstance(value, list) and len(value) == 2
            and all(integer(x, low) for x in value) and value[0] <= value[1])


def integer(value, low=0):
    return isinstance(value, int) and not isinstance(value, bool) and value >= low


@lru_cache(maxsize=1)
def load_library():
    data = json.loads(LIBRARY.read_text(encoding='utf-8'))
    if data.get('version') != 1:
        raise ValueError('layout-library 版本无效')
    profiles = data.get('profiles', [])
    if not isinstance(profiles, list) or any(not isinstance(p, dict) or not isinstance(p.get('id'), str) for p in profiles):
        raise ValueError('布局 profiles 需要带 id 的对象数组')
    ids = [p['id'] for p in profiles]
    if not profiles or len(set(ids)) != len(ids):
        raise ValueError('布局 profile.id 必须唯一')
    for p in profiles:
        if p.get('layout') not in NATIVE_LAYOUTS or p.get('status') not in {'ready', 'reference_only'}:
            raise ValueError(f'布局未注册或状态无效：{p["id"]}')
        if (not isinstance(p.get('relations'), list) or not p['relations']
                or any(not isinstance(r, str) or r not in RELATIONS for r in p['relations'])
                or not isinstance(p.get('modes'), list) or not p['modes']
                or any(m not in {'speech', 'reading'} for m in p['modes'])):
            raise ValueError(f'布局适用条件无效：{p["id"]}')
        if (not isinstance(p.get('styles'), list) or not p['styles']
                or any(not isinstance(s, str) or not s for s in p['styles'])):
            raise ValueError(f'布局 styles 需要风格 id 或 *：{p["id"]}')
        for field, minimum in (('item_count', 1), ('reading_item_count', 1), ('image_count', 0), ('block_count', 1)):
            if (field in {'item_count', 'image_count'} or field in p) and not range_valid(p.get(field), minimum):
                raise ValueError(f'布局 {field} 需要有效上下限：{p["id"]}')
        budget = p.get('text_budget')
        if (not isinstance(budget, dict) or any(not integer(budget.get(mode), 1) for mode in ('speech', 'reading'))):
            raise ValueError(f'布局 text_budget 需要 speech/reading 的正整数容量：{p["id"]}')
        expected_family = 'shared' if p['layout'] in SHARED_LAYOUTS else 'editorial' if p['layout'] == 'editorial' else 'native'
        if p.get('renderer_family', expected_family) != expected_family:
            raise ValueError(f'布局 renderer_family 与 layout 不一致：{p["id"]}')
        if 'count_field' in p and (not isinstance(p['count_field'], str) or p['count_field'] not in COUNT_FIELDS):
            raise ValueError(f'布局 count_field 未实现：{p["id"]}')
        if profile_settings_errors(p):
            raise ValueError(f'布局 settings 无效：{p["id"]}：' + '；'.join(profile_settings_errors(p)))
        expected_count = (SHARED_COUNT_FIELDS.get(p['layout']) if p['layout'] != 'editorial'
                          else EDITORIAL_COUNT_FIELDS[p['settings']['editorial_variant']])
        if expected_count and p.get('count_field') != expected_count:
            raise ValueError(f'布局 count_field 应为 {expected_count}：{p["id"]}')
        if p['layout'] in SHARED_LAYOUTS:
            image_low, image_high = SHARED_LAYOUTS[p['layout']]['image_count']
            if not image_low <= p['image_count'][0] <= p['image_count'][1] <= image_high:
                raise ValueError(f'布局 image_count 超出 renderer 契约：{p["id"]}')
        if not isinstance(p.get('adaptation'), str) or not p['adaptation'].strip():
            raise ValueError(f'布局 adaptation 需要真实的适配说明：{p["id"]}')
    refs = data.get('references', [])
    if (not isinstance(refs, list) or not isinstance(data.get('source'), dict)
            or len(refs) != data['source'].get('count')
            or any(not isinstance(r, dict) or not isinstance(r.get('id'), str) for r in refs)
            or len({r['id'] for r in refs}) != len(refs)):
        raise ValueError('布局来源数量或编号不一致')
    for ref in refs:
        if not isinstance(ref.get('profiles'), list) or any(pid not in ids for pid in ref['profiles']):
            raise ValueError(f'来源引用了不存在的 profile：{ref["id"]}')
        if (ref.get('status') not in {'adapted', 'reference_only'}
                or (ref['status'] == 'reference_only' and ref['profiles'])
                or (ref['status'] == 'adapted' and not ref['profiles'])):
            raise ValueError(f'来源状态不一致：{ref["id"]}')
    return data


def text_units(slide):
    """Read real copy, excluding notes, file paths, metadata and source examples."""
    def gather(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                yield from gather(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                if key in TEXT_FIELDS:
                    yield from gather(item)
    # Planning content is only used before layout fields exist; final decks are
    # measured from what the renderer consumes, never from stale planning copy.
    value = slide if slide.get('layout') else slide.get('content', slide)
    texts = list(gather(value))
    units = sum(sum(.55 if ord(c) < 0x2E80 else 1 for c in s) for s in texts)
    return round(units, 1)


def media_info(slide, intent):
    if slide.get('layout') in SHARED_LAYOUTS:
        try:
            values = composition_images(slide)
            return len(values), 'planned' if values else 'unavailable'
        except (ValueError, TypeError, KeyError):
            return 0, 'unavailable'
    # Service cards own their photographs inside the item objects. Do not count
    # stale planning metadata or non-rendered top-level image fields instead.
    items = slide.get('items', [])
    items = items if isinstance(items, list) else []
    if slide.get('layout') == 'service_cards' or any(isinstance(item, dict) and 'image' in item for item in items):
        values = [item['image'] for item in items if isinstance(item, dict) and 'image' in item]
        return len(values), 'planned' if all(isinstance(im, dict) for im in values) else 'unavailable'
    if 'images' in slide:
        values = slide['images']
        return (len(values), 'planned') if isinstance(values, list) else (0, 'unavailable')
    if isinstance(slide.get('image'), dict):
        return 1, 'planned'
    if slide.get('layout'):
        return 0, 'unavailable'
    media = intent.get('media', {})
    return media.get('count', 0), media.get('status', 'unavailable')


def blocks_for(slide, intent):
    if isinstance(slide.get('blocks'), list):
        return [b.get('type') for b in slide['blocks'] if isinstance(b, dict)]
    return intent.get('block_types', {
        'sequence': ['process'], 'comparison': ['matrix'], 'hierarchy': ['layers'],
        'data': ['chart']}.get(intent.get('relation'), []))


def charts_for(slide):
    return slide_charts(slide)


def intent_errors(slide):
    value = slide.get('layout_intent')
    if not isinstance(value, dict):
        return ['需要 layout_intent；先由模型判断内容关系，脚本不按关键词猜测']
    errors = []
    if not isinstance(slide.get('title'), str) or not slide['title'].strip():
        errors.append('每页需要非空 title')
    if not slide.get('layout') and 'content' not in slide and not any(key in slide for key in (
            'blocks', 'items', 'steps', 'rows', 'labels', 'chains', 'formula',
            'copy', 'paragraphs', 'groups', 'metrics', 'tags', 'chart', 'lead')):
        errors.append('规划页需要实际 content 或结构化内容；不能只按标题和项数估算容量')
    if not isinstance(value.get('relation'), str) or value['relation'] not in RELATIONS:
        errors.append('layout_intent.relation 无效；见 layout-selection.md')
    if not integer(value.get('item_count'), 1):
        errors.append('layout_intent.item_count 需要正整数')
    for key in ('dimension_count', 'column_count', 'control_group_count', 'chain_count'):
        if key in value and not integer(value[key], 1):
            errors.append(f'layout_intent.{key} 需要正整数')
    if value.get('relation') == 'comparison' and not integer(value.get('dimension_count'), 1):
        errors.append('比较需要 dimension_count，区分单维度对照与多维矩阵')
    for key in ('spatial',):
        if key in value and not isinstance(value[key], bool):
            errors.append(f'layout_intent.{key} 需要布尔值')
    if 'media' in value:
        media = value['media']
        if not isinstance(media, dict) or not integer(media.get('count')) or media.get('status') not in {'provided', 'planned', 'unavailable'}:
            errors.append('layout_intent.media 需要 count 和 status: provided/planned/unavailable')
    if 'block_types' in value:
        kinds = value['block_types']
        if not isinstance(kinds, list) or not 1 <= len(kinds) <= 4 or any(not isinstance(k, str) or k not in BLOCK_TYPES for k in kinds):
            errors.append('block_types 需要 1–4 个 process/matrix/layers/chart/facts')
    excluded = value.get('exclude_profiles', [])
    known = {p['id'] for p in load_library()['profiles']}
    if not isinstance(excluded, list) or any(not isinstance(x, str) or x not in known for x in excluded):
        errors.append('exclude_profiles 只能包含已登记 profile.id')
    if 'content' in slide and (not isinstance(slide['content'], list) or not slide['content'] or any(not isinstance(t, str) or not t.strip() for t in slide['content'])):
        errors.append('规划页 content 需要非空字符串数组，保留真实待排文字')
    if text_units(slide) == 0:
        errors.append('需要实际待排文字用于容量估算')
    return errors


def eligibility(profile, slide, mode, style, excluded=()):
    intent = slide['layout_intent']
    relation, count = intent['relation'], intent['item_count']
    pid, layout = profile['id'], profile['layout']
    errors = []
    if profile['status'] != 'ready': errors.append('渲染尚未实现')
    if pid in set(excluded) | set(intent.get('exclude_profiles', [])): errors.append('本轮反馈已排除此布局')
    if relation not in profile['relations']: errors.append('内容关系不匹配')
    # modes is descriptive catalog metadata. Presentation density may change a
    # copy budget, but never makes a renderer or its geometry unavailable.
    if '*' not in profile['styles'] and style not in profile['styles']:
        errors.append('尚未登记此风格的兼容性')
    low, high = profile.get('reading_item_count', profile['item_count']) if mode == 'reading' else profile['item_count']
    if not low <= count <= high: errors.append(f'主体项数需为 {low}–{high}')
    images, status = media_info(slide, intent)
    if (status == 'unavailable' and images > 0) or not profile['image_count'][0] <= images <= profile['image_count'][1]:
        errors.append(f'需要 {profile["image_count"][0]}–{profile["image_count"][1]} 张已提供或已规划的配图')
    if pid == 'shared.editorial_people' and images < count:
        errors.append('每位成员需要一张已提供或已规划的独立头像')
    if images == 0 and layout in {'cover', 'closing', 'table'}:
        pack = resolve_style({'style': style, 'slides': []})
        if layout not in pack['image_free_layouts']:
            errors.append('当前风格的此布局需要图片')
    dimensions = intent.get('dimension_count', 0)
    if pid == 'journey.compare' and dimensions != 1: errors.append('多维比较需要矩阵')
    if layout in {'metric_cards', 'metric_circles'} and relation == 'comparison' and dimensions != 1:
        errors.append('指标比较只承载一个比较维度；多维比较需要矩阵')
    if relation == 'timeline':
        periods = intent.get('periods')
        for key in ('items', 'steps'):
            if isinstance(slide.get(key), list):
                periods = [x.get('period') for x in slide[key] if isinstance(x, dict)]
                break
        if not isinstance(periods, list) or len(periods) != count or any(not isinstance(x, str) or not x.strip() for x in periods):
            errors.append('时间线需要与事件逐一对应的真实 periods')
    if pid == 'flow.controls':
        groups = len(slide['groups']) if isinstance(slide.get('groups'), list) else intent.get('control_group_count', 0)
        if not 2 <= groups <= (4 if mode == 'reading' else 3): errors.append('流程控制版式需要真实的控制分组')
    if pid == 'relations.chain':
        chains = len(slide['chains']) if isinstance(slide.get('chains'), list) else intent.get('chain_count', 1)
        if not 1 <= chains <= 5: errors.append('关系链需为 1–5 条')
    if layout == 'table':
        cols = len(slide['columns']) if isinstance(slide.get('columns'), list) else (dimensions + 1 if relation == 'comparison' else intent.get('column_count', 0))
        if not 2 <= cols <= 5: errors.append('表格需要 2–5 列（含对象名称列）')
    if layout == 'reading':
        kinds = blocks_for(slide, intent)
        low, high = profile['block_count']
        if not low <= len(kinds) <= high: errors.append(f'此阅读构图需要 {low}–{high} 个内容模块')
        required = {'sequence': 'process', 'comparison': 'matrix', 'hierarchy': 'layers', 'data': 'chart'}.get(relation)
        if required and required not in kinds: errors.append(f'本页关系需要 {required} 模块')
        if 'process' in kinds and relation == 'sequence' and not 3 <= count <= 6: errors.append('阅读流程需要 3–6 个步骤')
        if 'matrix' in kinds and relation == 'comparison' and not (2 <= count <= 6 and 1 <= dimensions <= 4): errors.append('阅读矩阵需要 2–6 个对象、1–4 个维度')
        if 'layers' in kinds and relation == 'hierarchy' and not 2 <= count <= 4: errors.append('阅读分层需要 2–4 层')
        if 'chart' in kinds:
            charts = charts_for(slide)
            if len(charts) != kinds.count('chart'): errors.append('每个图表模块都需要实际 chart 数据、单位与来源')
            for chart in charts: errors.extend(chart_errors(chart))
    if layout == 'chart_focus':
        chart = slide.get('chart')
        if not isinstance(chart, dict):
            errors.append('chart_focus 需要实际 chart 数据、单位与来源')
        else:
            errors.extend(chart_errors(chart))
            if not isinstance(chart.get('title'), str) or not chart['title'].strip():
                errors.append('chart_focus.chart.title 必填')
            if isinstance(chart.get('categories'), list) and len(chart['categories']) != count:
                errors.append('chart_focus 主体项数需对应实际 chart.categories')
    if pid == 'shared.editorial_charts':
        columns = slide.get('columns', [])
        charts = [c.get('chart') for c in columns if isinstance(c, dict) and c.get('type') == 'chart'] if isinstance(columns, list) else []
        if len(charts) != count:
            errors.append('图表分栏主体项数需对应实际 chart 栏数量')
        for chart in charts:
            if not isinstance(chart, dict):
                errors.append('每个图表栏都需要实际 chart 数据、单位与来源')
            else:
                errors.extend(chart_errors(chart))
                if not isinstance(chart.get('title'), str) or not chart['title'].strip():
                    errors.append('图表栏 chart.title 必填')
    budget = profile['text_budget'].get(mode, 1)
    if text_units(slide) > budget * 1.6:
        errors.append(f'文字明显超过初筛预算 {budget} 单位；换容量更大的布局或拆页，不能缩字塞入')
    return errors


def matching_sources(profile, intent, slide):
    chart_types = {c.get('chart_type') for c in charts_for(slide)}
    return [r['id'] for r in load_library()['references'] if r['status'] == 'adapted' and profile['id'] in r['profiles']
            and r['relation'] == intent['relation'] and r['item_count'] in (None, intent['item_count'])
            and (not r.get('chart_types') or bool(chart_types & set(r['chart_types'])))]


def choose_slide(slide, mode, style, previous=None, excluded=()):
    errors = intent_errors(slide)
    result = {'slide_id': slide.get('id'), 'title': slide.get('title', ''), 'candidates': [], 'rejected': [], 'errors': errors}
    if errors:
        return dict(result, status='invalid', selection=None)
    intent, units = slide['layout_intent'], text_units(slide)
    for profile in load_library()['profiles']:
        why = eligibility(profile, slide, mode, style, excluded)
        if why:
            result['rejected'].append({'profile': profile['id'], 'reasons': why})
            continue
        layout, pid = profile['layout'], profile['id']
        priority = {'split': 40, 'scene': 25, 'triad': 45, 'journey': 40, 'flow': 55,
                    'domains': 28, 'table': 45, 'architecture': 42, 'reading': 35,
                    'type_poster': 30}.get(layout, 38)
        if intent.get('spatial') and layout in {'scene', 'architecture'}: priority += 15
        if intent['relation'] == 'hierarchy' and layout == 'reading' and intent.get('spatial'): priority -= 20
        ratio = units / profile['text_budget'][mode]
        # Rhythm is only a small tie-break: it cannot rescue a semantic mismatch.
        score = round(priority - 15 * ratio - (2 if previous == pid else 0), 2)
        settings = dict(profile['settings'])
        reason = f'{intent["relation"]} 关系，{intent["item_count"]} 个主体项；文字约 {units:g} 单位，符合内容容量与配图条件。{profile["adaptation"]}'
        result['candidates'].append({'profile': pid, 'layout': layout, 'settings': settings, 'score': score,
            'source_ids': matching_sources(profile, intent, slide), 'rationale': reason,
            'warnings': ['接近容量边界，可增加分区或在页数允许时拆页'] if ratio > 1 else []})
    result['candidates'].sort(key=lambda c: (-c['score'], c['profile']))
    best = result['candidates'][0] if result['candidates'] else None
    result.update(status='selected' if best else 'needs_revision', text_units=units,
                  selection={'version': 1, 'profile': best['profile'], 'source_ids': best['source_ids']} if best else None)
    if not best:
        result['next_actions'] = ['检查排除原因；保留关键事实，调整分区或在页数允许时拆页。',
                                  '素材/数据缺失只暂停依赖步骤；不补造数据，不更改已确认风格或用途。',
                                  '仅供参考的结构需先实现并验证渲染器；不能将来源编号直接作为 layout。']
    return result


def feedback_exclusions(feedback, slide):
    # The page's current profiles follow from its rendered layout and settings; no record is kept in the deck.
    current = [p['id'] for p in load_library()['profiles'] if p['layout'] == slide.get('layout')
               and all(slide.get(key) == value for key, value in p['settings'].items())]
    for page in feedback.get('pages', []):
        if page.get('id') != slide.get('id'): continue
        issues = page.get('issues', []) + page.get('design', {}).get('issues', [])
        if any(isinstance(i, dict) and i.get('type') in CAPACITY_ISSUES for i in issues): return current
    return []


def select_deck(deck, feedback=None):
    if not isinstance(deck, dict) or not isinstance(deck.get('slides'), list) or not deck['slides']:
        raise ValueError('需要含非空 slides 的规划或 deck 对象')
    if 'style' not in deck or 'presentation_mode' not in deck:
        raise ValueError('选版前显式记录已确认的 style 与 presentation_mode；不使用旧稿兼容默认替用户决定')
    # Resolve the installed theme without requiring a rendered deck's images;
    # planning deliberately happens before image paths and layouts are assigned.
    mode, style = presentation_mode(deck), resolve_style({'style': deck['style'], 'slides': []})['id']
    pages, seen, previous = [], set(), None
    for slide in deck['slides']:
        if not isinstance(slide, dict) or not isinstance(slide.get('id'), str) or not slide['id'].strip() or slide['id'] in seen:
            raise ValueError('每页需要唯一的非空 id')
        seen.add(slide['id'])
        result = choose_slide(slide, mode, style, previous, feedback_exclusions(feedback or {}, slide))
        pages.append(result)
        if result['selection']: previous = result['selection']['profile']
    return {'version': 1, 'style': style, 'presentation_mode': mode,
            'ok': all(p['status'] == 'selected' for p in pages), 'pages': pages,
            'limitations': '容量是初筛估算；按候选字段保留完整事实并完成排版。选版脚本只生成推荐报告，检查与导出按用户授权单独执行。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', nargs='?', help='布局规划 JSON 或带 layout_intent 的 deck.json')
    parser.add_argument('--out', help='推荐报告；不会改写输入')
    parser.add_argument('--feedback', help='audit_deck 的 report.json；排除有容量问题的当前 profile')
    parser.add_argument('--list', action='store_true', help='列出可执行 profile 和来源统计')
    parser.add_argument('--catalog', action='store_true', help='查看来源布局，不加载示例文案')
    parser.add_argument('--relation', choices=sorted(RELATIONS), help='筛选 --catalog 的语义家族')
    args = parser.parse_args()
    try:
        library = load_library()
        if args.list:
            result = {'profiles': library['profiles'], 'references': len(library['references']),
                      'adapted': sum(r['status'] == 'adapted' for r in library['references'])}
        elif args.catalog:
            result = [r for r in library['references'] if not args.relation or r['relation'] == args.relation]
        elif args.plan:
            deck = json.loads(Path(args.plan).read_text(encoding='utf-8'))
            feedback = json.loads(Path(args.feedback).read_text(encoding='utf-8')) if args.feedback else None
            result = select_deck(deck, feedback)
        else:
            parser.error('提供规划文件，或使用 --list / --catalog')
        content = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.out:
            out = Path(args.out).resolve()
            if args.plan and out == Path(args.plan).resolve(): raise ValueError('--out 不能覆盖规划或 deck 输入')
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding='utf-8')
            print(json.dumps({'ok': result.get('ok', True) if isinstance(result, dict) else True, 'report': str(out)}, ensure_ascii=False))
        else:
            print(content, end='')
        if isinstance(result, dict) and result.get('ok') is False: parser.exit(1)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(1, f'选版失败：{exc}\n')


if __name__ == '__main__':
    main()
