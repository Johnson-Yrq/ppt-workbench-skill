#!/usr/bin/env python3
"""Behavioral tests of content routing, truthful metadata and renderer integration."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from build_deck import Builder, check_plan
from common import NATIVE_LAYOUTS, load_deck, placeholder_png as solid_png, slide_images
from select_layout import load_library, media_info, observed_count, select_deck, selection_errors, text_units
from test_compositions import fixtures
from test_editorial import EditorialTests
from test_styles import all_layouts_deck

HERE = Path(__file__).resolve().parent
STYLES = ('scene-white', 'saas-3d', 'real-miniature', 'warm-minimal-editorial', 'monochrome-editorial')


def planning(relation='sequence', count=3, mode='speech', **intent):
    return {'title': '内容选版验证', 'style': 'scene-white', 'presentation_mode': mode, 'slides': [{
        'id': 'p01', 'title': '内容关系验证',
        'content': ['接收材料并记录。', '核对必需字段。', '完成交接并保留记录。'],
        'layout_intent': dict(relation=relation, item_count=count,
                              media={'count': 1, 'status': 'planned'}, **intent)}]}


def recommended(deck):
    page = select_deck(deck)['pages'][0]
    return page['candidates'][0] if page['candidates'] else None


def recorded(slide, relation=None):
    slide = copy.deepcopy(slide)
    pid = ('editorial.' + slide['editorial_variant'] if slide['layout'] == 'editorial'
           else 'shared.' + slide['layout'])
    profile = next(p for p in load_library()['profiles'] if p['id'] == pid)
    relation = relation or profile['relations'][0]
    intent = {'relation': relation, 'item_count': observed_count(slide, relation, profile)}
    intent['media'] = {'count': media_info(slide, intent)[0], 'status': 'provided'}
    if relation == 'comparison':
        intent['dimension_count'] = 1
    slide.update(layout_intent=intent, layout_selection={'version': 1, 'profile': pid, 'source_ids': []})
    return slide


class LayoutSelection(unittest.TestCase):
    def test_chart_columns_require_real_data_and_count_charts(self):
        chart = {'title': '样本', 'chart_type': 'line', 'categories': ['一', '二'],
                 'series': [{'name': '示例', 'values': [2, 3]}], 'unit': '项', 'source': '虚构示例'}
        slide = {'id': 'charts', 'layout': 'editorial_columns', 'title': '不同口径',
                 'columns': [{'type': 'chart', 'chart': copy.deepcopy(chart)} for _ in range(3)],
                 'layout_intent': {'relation': 'data', 'item_count': 3, 'media': {'count': 0, 'status': 'unavailable'}},
                 'layout_selection': {'version': 1, 'profile': 'shared.editorial_charts', 'source_ids': []}}
        for mode in ('speech', 'reading'):
            self.assertEqual(selection_errors(slide, mode, 'warm-minimal-editorial'), [])
        slide['layout_intent']['item_count'] = 2
        self.assertTrue(any('实际' in e for e in selection_errors(slide, 'speech', 'scene-white')))
        slide['layout_intent']['item_count'] = 3
        slide['columns'][1]['chart'].pop('source')
        self.assertTrue(selection_errors(slide, 'speech', 'scene-white'))
        planned = planning('data', count=3)
        self.assertNotIn('shared.editorial_charts', {x['profile'] for x in select_deck(planned)['pages'][0]['candidates']})

    def test_twelve_item_agenda_and_structured_contact(self):
        slide = {'layout': 'side_index', 'title': '目录', 'items': [{'title': str(i)} for i in range(12)]}
        self.assertEqual(selection_errors(recorded(slide), 'speech', 'scene-white'), [])
        slide['items'].append({'title': '十三'})
        self.assertTrue(selection_errors(recorded(slide), 'speech', 'scene-white'))
        contact = {'layout': 'editorial_columns', 'title': '联系', 'columns': [
            {'type': 'text'}, {'type': 'groups', 'items': [{'title': '邮箱', 'text': 'hello@example.com'}, {'title': '合作', 'text': '需求访谈'}]}]}
        self.assertEqual(selection_errors(recorded(contact, 'contact'), 'speech', 'scene-white'), [])

    def test_hub_and_step_row_count_real_items_and_keep_timeline_dates(self):
        for layout in ('hub_spoke', 'step_row'):
            slide = recorded(next(s for s in fixtures() if s['layout'] == layout))
            for mode in ('speech', 'reading'):
                for style in STYLES:
                    self.assertEqual(selection_errors(slide, mode, style), [])
            slide['layout_intent']['item_count'] += 1
            self.assertTrue(any('实际渲染主体' in e for e in selection_errors(slide, 'speech', 'scene-white')))
        steps = recorded(next(s for s in fixtures() if s['layout'] == 'step_row'), 'timeline')
        for item in steps['steps']: item.pop('period', None)
        self.assertTrue(any('periods' in e for e in selection_errors(steps, 'speech', 'scene-white')))

    def test_five_person_team_requires_five_portraits(self):
        deck = planning('team', count=5)
        deck['slides'][0]['layout_intent']['media'] = {'count': 5, 'status': 'planned'}
        ids = {x['profile'] for x in select_deck(deck)['pages'][0]['candidates']}
        self.assertIn('shared.editorial_people', ids)
        deck['slides'][0]['layout_intent']['media']['count'] = 4
        ids = {x['profile'] for x in select_deck(deck)['pages'][0]['candidates']}
        self.assertNotIn('shared.editorial_people', ids)

    def test_six_gallery_columns_allow_forty_eight_distinct_photos(self):
        slide = {'id': 'gallery48', 'layout': 'editorial_columns', 'title': '作品索引',
                 'columns': [{'type': 'gallery', 'images': [
                     {'src': f'{c}-{i}.png', 'alt': f'作品{c}-{i}'} for i in range(8)]} for c in range(6)],
                 'layout_intent': {'relation': 'gallery', 'item_count': 48, 'media': {'count': 48, 'status': 'provided'}},
                 'layout_selection': {'version': 1, 'profile': 'shared.editorial_gallery', 'source_ids': []}}
        self.assertEqual(selection_errors(slide, 'reading', 'warm-minimal-editorial'), [])

    def test_image_free_table_requires_explicit_style_declaration(self):
        slide = {'id': 'table', 'layout': 'table', 'title': '组合', 'columns': ['一', '二'], 'rows': [['甲', '乙']],
                 'layout_intent': {'relation': 'table', 'item_count': 1, 'column_count': 2, 'media': {'count': 0, 'status': 'unavailable'}},
                 'layout_selection': {'version': 1, 'profile': 'table.matrix', 'source_ids': []}}
        self.assertTrue(any('需要图片' in e for e in selection_errors(slide, 'speech', 'scene-white')))
        with patch('select_layout.resolve_style', return_value={'image_free_layouts': ['table']}):
            self.assertEqual(selection_errors(slide, 'speech', 'table-capable-style'), [])

    def test_gallery_counts_single_image_and_gallery_columns_without_team_portraits(self):
        image = lambda name: {'src': name + '.png', 'alt': name}
        for columns in ([{'type': 'image', 'image': image(x)} for x in ('one', 'two', 'three')],
                        [{'type': 'image', 'image': image('one')},
                         {'type': 'gallery', 'images': [image('two'), image('three')], 'grid_columns': 1}]):
            slide = {'id': 'group', 'layout': 'editorial_columns', 'title': '三幅组照', 'columns': columns,
                     'layout_intent': {'relation': 'gallery', 'item_count': 3, 'media': {'count': 3, 'status': 'provided'}},
                     'layout_selection': {'version': 1, 'profile': 'shared.editorial_gallery', 'source_ids': []}}
            self.assertEqual(selection_errors(slide, 'reading', 'warm-minimal-editorial'), [])
            slide['layout_intent']['item_count'] = 2
            self.assertTrue(any('实际渲染主体' in e for e in selection_errors(slide, 'reading', 'warm-minimal-editorial')))
        profile = next(p for p in load_library()['profiles'] if p['id'] == 'shared.editorial_gallery')
        self.assertEqual(observed_count({'layout': 'editorial_columns', 'columns': [
            {'type': 'people', 'items': [{'name': '甲', 'role': '摄影', 'image': image('person')}]}]}, 'gallery', profile), 0)

    def test_statement_bullets_contribute_to_actual_text_capacity(self):
        self.assertEqual(text_units({'title': '理念', 'bullets': ['观察', '等待']}), 6)

    def test_new_editorial_nested_media_and_real_person_counts(self):
        image = lambda name: {'src': name + '.png', 'alt': name}
        slide = {'id': 'team', 'layout': 'editorial_columns', 'title': '设计团队',
                 'columns': [{'type': 'text', 'paragraphs': ['共同工作。']},
                             {'type': 'people', 'items': [
                                 {'name': '甲', 'role': '建筑', 'image': image('one')},
                                 {'name': '乙', 'role': '材料', 'image': image('two')},
                                 {'name': '丙', 'role': '空间', 'image': image('three')}]},
                             {'type': 'image', 'image': image('building')}],
                 'layout_intent': {'relation': 'team', 'item_count': 3,
                                   'media': {'count': 4, 'status': 'provided'}},
                 'layout_selection': {'version': 1, 'profile': 'shared.editorial_people', 'source_ids': []}}
        self.assertEqual(media_info(slide, slide['layout_intent'])[0], 4)
        self.assertEqual(selection_errors(slide, 'speech', 'warm-minimal-editorial'), [])
        slide['layout_intent']['item_count'] = 2
        self.assertTrue(any('实际渲染主体' in e for e in selection_errors(slide, 'speech', 'warm-minimal-editorial')))

    def test_new_gallery_counts_photographs_and_poster_needs_no_image(self):
        slide = {'id': 'gallery', 'layout': 'editorial_columns', 'title': '空间作品',
                 'columns': [{'type': 'text', 'paragraphs': ['不同尺度的作品。']},
                             {'type': 'gallery', 'images': [{'src': f'{i}.png', 'alt': f'作品{i}'} for i in range(8)]}],
                 'layout_intent': {'relation': 'gallery', 'item_count': 8, 'media': {'count': 8, 'status': 'provided'}},
                 'layout_selection': {'version': 1, 'profile': 'shared.editorial_gallery', 'source_ids': []}}
        self.assertEqual(selection_errors(slide, 'reading', 'warm-minimal-editorial'), [])
        self.assertEqual(media_info(slide, slide['layout_intent'])[0], 8)
        poster = {'id': 'chapter', 'layout': 'type_poster', 'title': '设计理念', 'number': '1', 'variant': 'chapter', 'show_title': False,
                  'layout_intent': {'relation': 'explanation', 'item_count': 1, 'media': {'count': 0, 'status': 'unavailable'}},
                  'layout_selection': {'version': 1, 'profile': 'shared.type_poster', 'source_ids': []}}
        self.assertEqual(selection_errors(poster, 'speech', 'scene-white'), [])

    def test_three_items_do_not_imply_three_cards(self):
        process = recommended(planning())
        comparison = recommended(planning('comparison', dimension_count=4))
        points = recommended(planning('parallel'))
        people = select_deck(planning('team'))
        self.assertEqual(process['layout'], 'journey')
        self.assertEqual(process['settings']['connected'], True)
        self.assertEqual(comparison['layout'], 'table')
        self.assertEqual(points['layout'], 'split')
        self.assertFalse(people['ok'])
        self.assertEqual(people['pages'][0]['status'], 'needs_revision')
        self.assertNotEqual(process['profile'], comparison['profile'])

    def test_control_flow_needs_control_content(self):
        ordinary = select_deck(planning())['pages'][0]
        self.assertNotIn('flow.controls', [c['profile'] for c in ordinary['candidates']])
        controlled = recommended(planning(control_group_count=2))
        self.assertEqual(controlled['layout'], 'flow')

    def test_missing_images_and_data_do_not_get_fabricated(self):
        deck = planning(); deck['slides'][0]['layout_intent']['media']['status'] = 'unavailable'
        before = copy.deepcopy(deck)
        self.assertFalse(select_deck(deck)['ok'])
        self.assertEqual(deck, before)
        deck = planning('data', mode='reading')
        self.assertFalse(select_deck(deck)['ok'])
        deck['slides'][0]['chart'] = {'chart_type': 'bar', 'categories': ['一', '二', '三'],
            'series': [{'name': '测试', 'values': [2, 3, 4]}], 'unit': '件', 'source': '测试用示例数据'}
        self.assertIn(recommended(deck)['layout'], {'reading', 'chart_focus'})
        for mutate in (lambda c: c.update(chart_type='scatter'), lambda c: c.pop('source'),
                       lambda c: c['series'][0].update(values=[2, None, 4])):
            invalid = copy.deepcopy(deck); mutate(invalid['slides'][0]['chart'])
            self.assertFalse(select_deck(invalid)['ok'])

    def test_modes_share_layouts_and_styles_share_capabilities(self):
        speech = select_deck(planning('comparison', dimension_count=3))
        reading = select_deck(planning('comparison', mode='reading', dimension_count=3))
        self.assertEqual({c['profile'] for c in speech['pages'][0]['candidates']},
                         {c['profile'] for c in reading['pages'][0]['candidates']})
        self.assertIn('reading', {c['layout'] for c in speech['pages'][0]['candidates']})
        self.assertIn('table', {c['layout'] for c in reading['pages'][0]['candidates']})
        for style in STYLES:
            deck = planning(); deck['style'] = style
            self.assertEqual(recommended(deck)['layout'], 'journey')
        invalid = planning(); invalid.pop('presentation_mode')
        with self.assertRaisesRegex(ValueError, '显式记录'): select_deck(invalid)

    def test_long_chinese_changes_capacity_choice_without_deleting_content(self):
        deck = planning('parallel'); short = recommended(deck)
        deck['slides'][0]['content'] = ['内容说明' * 35] * 3
        before = copy.deepcopy(deck)
        long = recommended(deck)
        self.assertNotEqual(short['profile'], long['profile'])
        self.assertEqual(deck, before)
        deck['slides'][0]['content'] = ['保留必要事实' * 100] * 3
        self.assertFalse(select_deck(deck)['ok'])

    def test_timeline_requires_real_times(self):
        self.assertIsNone(recommended(planning('timeline')))
        self.assertEqual(recommended(planning('timeline', periods=['第一天', '第二天', '第三天']))['profile'], 'journey.timeline')

    def test_reading_compositions_respect_media_and_blocks(self):
        deck = planning(mode='reading', block_types=['process', 'facts'])
        deck['slides'][0]['layout_intent']['media']['count'] = 2
        self.assertTrue(select_deck(deck)['ok'])
        ids = {c['profile'] for c in select_deck(deck)['pages'][0]['candidates']}
        self.assertTrue({'reading.half_tb', 'reading.half_diagonal'} <= ids)
        self.assertNotIn('reading.half_lr', ids)
        self.assertNotIn('reading.quarter', ids)
        deck['slides'][0]['layout_intent']['block_types'].append('facts')
        ids = {c['profile'] for c in select_deck(deck)['pages'][0]['candidates']}
        self.assertNotIn('reading.half_tb', ids)
        self.assertNotIn('reading.half_diagonal', ids)
        deck['slides'][0]['layout_intent']['media']['count'] = 1
        self.assertIn('reading.quarter', {c['profile'] for c in select_deck(deck)['pages'][0]['candidates']})

    def test_source_catalog_is_complete_and_not_an_execution_whitelist(self):
        lib = load_library()
        self.assertEqual({r['id'] for r in lib['references']}, {f'L{i:03}' for i in range(1, 101)})
        process = recommended(planning())
        self.assertIn('L042', process['source_ids'])
        self.assertNotIn('L046', process['source_ids'])
        self.assertEqual(next(r for r in lib['references'] if r['id'] == 'L085')['status'], 'reference_only')

    def test_browser_feedback_reranks_only_affected_page(self):
        deck = planning('parallel')
        first = select_deck(deck)['pages'][0]['selection']
        deck['slides'][0]['layout_selection'] = first
        deck['slides'].append(dict(copy.deepcopy(deck['slides'][0]), id='p02'))
        feedback = {'pages': [{'id': 'p01', 'issues': [{'type': 'text-overflow'}], 'design': {'issues': []}}]}
        report = select_deck(deck, feedback)
        self.assertNotEqual(report['pages'][0]['selection']['profile'], first['profile'])
        self.assertEqual(report['pages'][1]['selection']['profile'], first['profile'])
        feedback['pages'][0]['issues'] = [{'type': 'broken-image'}]
        self.assertEqual(select_deck(deck, feedback)['pages'][0]['selection']['profile'], first['profile'])

    def test_metadata_rejects_stale_counts_layouts_and_wrong_sources(self):
        slide = all_layouts_deck('scene-white')['slides'][4]  # journey
        self.assertEqual(slide['layout'], 'journey')
        slide['layout_intent'] = {'relation': 'sequence', 'item_count': 2}
        slide['layout_selection'] = {'version': 1, 'profile': 'journey.sequence', 'source_ids': []}
        self.assertEqual(selection_errors(slide, 'reading', 'scene-white'), [])
        for mutate in (lambda s: s['layout_intent'].update(item_count=3),
                       lambda s: s['layout_selection'].update(profile='split.points'),
                       lambda s: s['layout_selection'].update(source_ids=['L046']),
                       lambda s: s.update(connected=False)):
            invalid = copy.deepcopy(slide); mutate(invalid)
            self.assertTrue(selection_errors(invalid, 'reading', 'scene-white'))

    def test_legacy_renderers_accept_truthful_records_in_all_styles(self):
        metadata = {
            'cover': ('cover.fixed', 'cover', 1), 'scene': ('scene.annotations', 'explanation', 2),
            'split': ('split.points', 'parallel', 2), 'triad': ('triad.controls', 'controls', 3),
            'journey': ('journey.sequence', 'sequence', 2), 'architecture': ('architecture.labels', 'hierarchy', 1),
            'flow': ('flow.controls', 'sequence', 3), 'domains': ('domains.list', 'parallel', 2),
            'formula': ('formula.factors', 'formula', 2), 'table': ('table.matrix', 'table', 1),
            'relations': ('relations.chain', 'network', 2), 'closing': ('closing.fixed', 'closing', 1)}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for style in STYLES:
                deck = all_layouts_deck(style)
                for slide in deck['slides']:
                    if slide['layout'] == 'reading': continue  # covered by actual reading fixture below
                    pid, relation, count = metadata[slide['layout']]
                    slide['layout_intent'] = {'relation': relation, 'item_count': count}
                    slide['layout_selection'] = {'version': 1, 'profile': pid, 'source_ids': []}
                    image = root / slide['image']['src']; image.parent.mkdir(parents=True, exist_ok=True)
                    image.write_bytes(solid_png(324, 215))
                report = check_plan(deck, root)
                self.assertTrue(report['ok'], '\n'.join(report['errors']))
                # A dry render exercises every actual renderer without requiring
                # unrelated reading fixture images, and embeds the selection contract.
                html = Builder(deck, root, draft=True, dry_run=True).render()
                self.assertIn('layout_selection', html)
                self.assertIn(f'data-style="{style}"', html)

    def test_selected_sequence_plan_becomes_a_formal_deck(self):
        plan = planning(); best = recommended(plan)
        slide = copy.deepcopy(plan['slides'][0]); texts = slide.pop('content')
        slide.update(layout=best['layout'], **best['settings'])
        slide['items'] = [{'title': title, 'text': text, 'icon': 'CircleCheck'} for title, text in zip(['接收', '核对', '完成'], texts)]
        slide['image'] = {'src': 'scene.png', 'alt': '流程验证图'}
        slide['layout_selection'] = select_deck(plan)['pages'][0]['selection']
        slide['visual'] = {'role': 'process', 'treatment': 'panels', 'rationale': best['rationale'], 'requirements': []}
        deck = dict(plan, slides=[slide])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'scene.png').write_bytes(solid_png(324, 215))
            self.assertTrue(check_plan(deck, root)['ok'])
            html = Builder(deck, root, embed_format='keep').render()
            for text in texts: self.assertIn(text, html)
            self.assertIn('data-step="true"', html)

    def test_malformed_intent_is_reported_and_other_pages_continue(self):
        for field, value in [('item_count', True), ('relation', []), ('media', 'one'), ('block_types', [3])]:
            deck = planning(); deck['slides'].append(dict(copy.deepcopy(deck['slides'][0]), id='p02'))
            deck['slides'][0]['layout_intent'][field] = value
            report = select_deck(deck)
            self.assertEqual(report['pages'][0]['status'], 'invalid')
            self.assertEqual(report['pages'][1]['status'], 'selected')
        empty = planning(); empty['slides'][0].pop('content')
        self.assertEqual(select_deck(empty)['pages'][0]['status'], 'invalid')

    def test_registry_covers_native_layouts_without_theme_whitelists(self):
        profiles = load_library()['profiles']
        self.assertEqual(len(profiles), 49)
        self.assertEqual({p['layout'] for p in profiles}, NATIVE_LAYOUTS)
        self.assertEqual(sum(p['renderer_family'] == 'shared' for p in profiles), 23)
        self.assertEqual(sum(p['renderer_family'] == 'editorial' for p in profiles), 8)
        self.assertTrue(all(p['styles'] == ['*'] and set(p['modes']) == {'speech', 'reading'} for p in profiles))

    def test_zero_images_and_unavailable_media_keep_text_layouts_available(self):
        deck = planning('parallel', count=3)
        deck['slides'][0]['layout_intent']['media'] = {'count': 0, 'status': 'unavailable'}
        before = copy.deepcopy(deck)
        for style in STYLES:
            deck['style'] = style
            for mode in ('speech', 'reading'):
                deck['presentation_mode'] = mode
                ids = {c['profile'] for c in select_deck(deck)['pages'][0]['candidates']}
                self.assertIn('shared.problem_columns', ids)
                self.assertIn('shared.service_cards', ids)
                self.assertNotIn('split.points', ids)
        self.assertEqual(deck['slides'], before['slides'])
        cover = planning('cover', count=1)
        cover['slides'][0]['layout_intent']['media'] = {'count': 0, 'status': 'unavailable'}
        cover['style'] = 'monochrome-editorial'
        self.assertEqual(recommended(cover)['profile'], 'cover.fixed')
        cover['style'] = 'scene-white'
        self.assertEqual(recommended(cover)['profile'], 'shared.type_poster')

    def test_nested_service_images_and_shared_metadata_are_truthful(self):
        slide = recorded(next(s for s in fixtures() if s['layout'] == 'service_cards'))
        self.assertEqual(media_info(slide, slide['layout_intent'])[0], 3)
        self.assertEqual(selection_errors(slide, 'speech', 'monochrome-editorial'), [])
        mutations = (
            lambda s: s['layout_intent'].update(item_count=2),
            lambda s: s['layout_intent']['media'].update(count=1),
            lambda s: s.update(highlight=3),
            lambda s: s.update(copy='这个字段不会被服务卡片渲染'),
            lambda s: s['items'][0].update(ignored_field='不得悄悄忽略'),
            lambda s: s['layout_selection'].update(version=True),
            lambda s: s['layout_selection'].pop('source_ids'),
        )
        for mutate in mutations:
            invalid = copy.deepcopy(slide); mutate(invalid)
            self.assertTrue(selection_errors(invalid, 'speech', 'monochrome-editorial'))

    def test_chart_focus_requires_real_chart_source_and_category_count(self):
        slide = recorded(next(s for s in fixtures() if s['layout'] == 'chart_focus'))
        deck = {'title': '图表选版', 'style': 'monochrome-editorial', 'presentation_mode': 'speech', 'slides': [slide]}
        self.assertEqual(recommended(deck)['profile'], 'shared.chart_focus')
        self.assertEqual(selection_errors(slide, 'speech', 'monochrome-editorial'), [])
        for mutate in (lambda s: s.pop('chart'), lambda s: s['chart'].pop('source'),
                       lambda s: s['chart']['series'][0].update(values=[12, None, 18]),
                       lambda s: s['layout_intent'].update(item_count=2)):
            invalid = copy.deepcopy(slide); mutate(invalid)
            self.assertTrue(selection_errors(invalid, 'speech', 'monochrome-editorial'))
            self.assertFalse(select_deck(dict(deck, slides=[invalid]))['ok'])

    def test_editorial_variants_counts_and_fields_are_checked(self):
        slide = recorded(EditorialTests().slide('services'))
        self.assertEqual(selection_errors(slide, 'reading', 'warm-minimal-editorial'), [])
        for mutate in (lambda s: s.update(editorial_variant='portfolio'),
                       lambda s: s['items'].pop(), lambda s: s.update(lead='服务页无此字段'),
                       lambda s: s['layout_selection'].update(profile='editorial.process')):
            invalid = copy.deepcopy(slide); mutate(invalid)
            self.assertTrue(selection_errors(invalid, 'reading', 'warm-minimal-editorial'))

    def test_all_new_profiles_render_in_all_styles_and_both_modes(self):
        shared = [recorded(s) for s in fixtures()]
        editorial = [recorded(EditorialTests().slide(p['settings']['editorial_variant']))
                     for p in load_library()['profiles'] if p['layout'] == 'editorial']
        for style in STYLES:
            for mode in ('speech', 'reading'):
                deck = {'title': '新共享结构选版', 'style': style, 'presentation_mode': mode,
                        'slides': copy.deepcopy(shared + editorial)}
                with self.subTest(style=style, mode=mode):
                    report = check_plan(deck, HERE)
                    self.assertTrue(report['ok'], report['errors'])
                    html = Builder(deck, HERE, draft=True, dry_run=True).render()
                    self.assertIn('layout_selection', html)

    def test_recorded_shared_and_editorial_decks_load_and_block_invalid_records(self):
        shared = next(s for s in fixtures() if s['layout'] == 'problem_columns')
        shared.pop('image')
        slides = [recorded(shared), recorded(EditorialTests().slide('intro'))]
        deck = {'title': '原生契约验证', 'style': 'monochrome-editorial', 'presentation_mode': 'speech', 'slides': slides}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for slide in slides:
                for image in slide_images(slide):
                    path = root / image['src']; path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(solid_png(24, 16))
            path = root / 'deck.json'; path.write_text(json.dumps(deck), encoding='utf-8')
            loaded, _ = load_deck(path)
            self.assertTrue(check_plan(loaded, root)['ok'])
            self.assertIn('layout_selection', Builder(loaded, root, embed_format='keep').render())
            loaded['slides'][0]['layout_intent']['item_count'] = 3
            self.assertFalse(check_plan(loaded, root)['ok'])
            with self.assertRaisesRegex(ValueError, '实际渲染主体项数'):
                Builder(loaded, root, embed_format='keep').render()

    def test_facts_only_reading_layout_is_available_for_both_modes(self):
        for mode in ('speech', 'reading'):
            deck = planning('mixed', count=2, mode=mode, block_types=['facts'])
            ids = {c['profile'] for c in select_deck(deck)['pages'][0]['candidates']}
            self.assertIn('reading.half_lr', ids)

    def test_library_rejects_unimplemented_settings_and_false_field_metadata(self):
        baseline = copy.deepcopy(load_library())
        for pid, changes in (
            ('shared.metric_cards', {'count_field': 'items'}),
            ('shared.metric_cards', {'settings': {'composition': 'quarter'}}),
            ('shared.metric_cards', {'renderer_family': 'editorial'}),
            ('shared.metric_cards', {'image_count': [0, 9]}),
            ('editorial.cover', {'settings': {'editorial_variant': 'made_up'}}),
        ):
            data = copy.deepcopy(baseline)
            next(p for p in data['profiles'] if p['id'] == pid).update(changes)
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / 'library.json'; path.write_text(json.dumps(data), encoding='utf-8')
                with patch('select_layout.LIBRARY', path):
                    load_library.cache_clear()
                    with self.assertRaises(ValueError):
                        load_library()
                load_library.cache_clear()

    def test_reference_only_sources_cannot_be_claimed_by_new_profiles(self):
        slide = recorded(next(s for s in fixtures() if s['layout'] == 'service_cards'))
        source = next(r['id'] for r in load_library()['references'] if r['status'] == 'reference_only')
        slide['layout_selection']['source_ids'] = [source]
        self.assertTrue(any('source_ids' in e for e in selection_errors(slide, 'speech', 'scene-white')))

    def test_cli_does_not_overwrite_the_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / 'plan.json'; out = Path(temp) / 'report.json'
            src.write_text(json.dumps(planning()), encoding='utf-8'); before = src.read_bytes()
            cmd = [sys.executable, str(HERE / 'select_layout.py'), str(src), '--out']
            result = subprocess.run(cmd + [str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(out.read_text())['ok'])
            self.assertNotEqual(subprocess.run(cmd + [str(src)], capture_output=True).returncode, 0)
            self.assertEqual(src.read_bytes(), before)


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LayoutSelection))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(run())
