"""Behavioral coverage for the shared sample-derived composition library."""
import contextlib
import copy
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import tempfile
import unittest

from build_deck import Builder, check_plan
from common import load_deck, placeholder_png, slide_images
from composition_layouts import SHARED_LAYOUTS
from chart_contract import slide_charts
from design_contract import planned_features
from prepare_images import prepare
from style_packs import discover_styles, resolve_style
from test_editorial import ContentDocument
from test_refinements import EditableText
from test_styles import Document


def fixtures():
    """Independent content fixtures, deliberately exercising optional content."""
    slides = []
    for layout in SHARED_LAYOUTS:
        def image(index=0):
            return {'src': f'images/{layout}-{index}.png', 'alt': f'{layout} 配图 {index}',
                    'caption': f'{layout} 图注 {index} < & >'}
        def items(count):
            return [{'title': f'{layout} 项目 {i}', 'text': f'{layout} 说明 {i} < & >'} for i in range(count)]
        def steps(count):
            return [dict(item, period=f'{layout} 阶段 {i + 1}') for i, item in enumerate(items(count))]
        s = {'id': layout, 'layout': layout, 'title': f'{layout} 标题 < & >',
             'subtitle': f'{layout} 副标题', 'chapter': f'{layout} 章节',
             'notes': f'{layout} 讲者备注',
             'visual': {'rationale': '内容关系决定布局，风格与用途独立选择。', 'requirements': []}}
        if layout in {'photo_pair', 'offset_pair', 'photo_strip'}:
            s['images'] = [image(0), image(1)]
        elif layout not in {'chart_focus', 'service_cards', 'type_poster', 'editorial_columns', 'hub_spoke', 'step_row'}:
            s['image'] = image()
        if layout in {'photo_pair', 'statement_tags', 'metric_cards', 'metric_circles', 'photo_strip',
                      'chart_focus', 'photo_banner', 'photo_divider', 'step_sidebar'}:
            s['copy'] = f'{layout} 完整正文 < & >'
        if layout in {'photo_pair', 'photo_banner', 'photo_divider', 'side_index', 'editorial_story'}:
            s['eyebrow'] = f'{layout} 引题'
        if layout == 'offset_pair':
            s['paragraphs'] = [f'{layout} 第一段正文', f'{layout} 第二段正文']
        if layout in {'statement_tags', 'photo_banner'}:
            s['tags'] = [f'{layout} 标签 {i}' for i in range(3)]
        if layout == 'checklist_photo':
            s['groups'] = [dict(item, checks=[{'label': f'分组 {i} 已具备', 'checked': True},
                                              {'label': f'分组 {i} 未纳入', 'checked': False}])
                           for i, item in enumerate(items(2))]
        if layout in {'snake_timeline', 'step_sidebar', 'step_row'}:
            s.update(steps=steps(6 if layout == 'snake_timeline' else 3), note=f'{layout} 步骤附注')
        if layout in {'metric_cards', 'metric_circles'}:
            s.update(metrics=[{'label': f'{layout} 指标 {i}', 'value': f'{70+i}%',
                               'text': f'{layout} 口径 {i}'} for i in range(2)], source=f'{layout} 示例数据来源')
        if layout in {'problem_columns', 'editorial_story'}:
            s['items'] = items(2)
        if layout == 'service_cards':
            s.update(items=[dict(item, image=image(i)) for i, item in enumerate(items(3))],
                     highlight=1, aside='service_cards 旁注')
        if layout == 'side_index':
            s['items'] = [{'title': '目录条目甲', 'label': 'A'}, {'title': '目录条目乙', 'label': 'B'}]
        if layout == 'chart_focus':
            s.update(chart={'title': '分阶段业务量', 'chart_type': 'bar', 'categories': ['准备', '运行', '复盘'],
                            'series': [{'name': '示例业务', 'values': [12, 20, 18]}], 'unit': '项', 'source': '图表：示例数据'},
                     stat={'value': '50', 'label': '示例业务总量'}, conclusion='图表结论需结合示例口径阅读。')
        if layout == 'type_poster':
            s.update(variant='cover', number='01')
        if layout == 'hub_spoke':
            s.update(center={'title': '关系中心', 'text': '中心说明'}, items=items(8), copy='分支解释')
        if layout == 'editorial_columns':
            s.update(title_column=1, columns=[
                {'type': 'text', 'heading': '分栏引题', 'paragraphs': ['第一栏第一段', '第一栏第二段'], 'align': 'end'},
                {'type': 'groups', 'weight': 2, 'group_columns': 2, 'items': items(4)},
                {'type': 'people', 'items': [{'image': image(i), 'name': f'同事 {i}', 'role': f'职责 {i}'} for i in range(3)]},
                {'type': 'gallery', 'images': [image(3), dict(image(4), frame='monitor')], 'grid_columns': 1}])
        slides.append(s)
    return slides


TEXT_FIELDS = {'title', 'subtitle', 'chapter', 'copy', 'eyebrow', 'note', 'source', 'aside',
               'conclusion', 'paragraphs', 'tags', 'label', 'value', 'text', 'period', 'caption',
               'categories', 'name', 'values', 'heading', 'role', 'number', 'bullets'}


def content_values(value, key=''):
    """Content promised by these fixtures, excluding structural metadata."""
    if isinstance(value, dict):
        return [text for field, child in value.items() if field not in {'visual', 'notes'}
                for text in content_values(child, field)]
    if isinstance(value, list):
        return [text for child in value for text in content_values(child, key)]
    if key in TEXT_FIELDS and isinstance(value, (str, int, float)):
        return [str(value)]
    return []


class StepDocument(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.steps, self.states, self.services = [], [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'data-step' in attrs:
            self.steps.append(attrs)
        if 'data-state' in attrs:
            self.states.append(attrs['data-state'])
        if 'comp-service' in attrs.get('class', '').split():
            self.services.append(attrs)


class CompositionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='slide-compositions-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.slides = fixtures()
        self.styles = [s['id'] for s in discover_styles()['styles']]
        for slide in self.slides:
            for image in slide_images(slide):
                path = self.root / image['src']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(placeholder_png(24, 16))

    def sample(self, layout):
        return copy.deepcopy(next(s for s in self.slides if s['layout'] == layout))

    def deck(self, slides=None, style='scene-white', mode='speech'):
        return {'version': 1, 'title': '共享版式回归', 'style': style, 'company': 'TEST STUDIO',
                'year': 2026, 'presentation_mode': mode, 'slides': copy.deepcopy(slides or self.slides)}

    def load(self, deck):
        file = self.root / 'deck.json'
        file.write_text(json.dumps(deck, ensure_ascii=False))
        return load_deck(file)

    def render(self, deck, draft=False):
        data, root = self.load(deck)
        report = check_plan(data, root)
        self.assertTrue(report['ok'], report['errors'])
        return Builder(data, root, draft=draft, embed_format='keep').render(), report

    def handoff(self, deck):
        self.load(deck)
        with contextlib.redirect_stdout(io.StringIO()):
            return prepare(self.root / 'deck.json', self.root / 'handoff')

    def test_all_layouts_keep_editable_content_across_styles_and_modes(self):
        self.assertEqual(len(self.slides), len(SHARED_LAYOUTS))
        self.assertGreaterEqual(len(self.styles), 4)
        expected = [value for s in self.slides for value in content_values(s)]
        images = [im for s in self.slides for im in slide_images(s)]
        for style in self.styles:
            rendered_without_mode = None
            for mode in ('speech', 'reading'):
                with self.subTest(style=style, mode=mode):
                    html, report = self.render(self.deck(style=style, mode=mode))
                    doc, content, editable = Document(html), ContentDocument(html), EditableText(html).values
                    self.assertEqual(len(doc.pages), len(SHARED_LAYOUTS))
                    self.assertEqual(doc.body['data-style'], style)
                    self.assertEqual(doc.body['data-presentation-mode'], mode)
                    self.assertEqual([p['shared_layout'] for p in report['pages']], list(SHARED_LAYOUTS))
                    self.assertEqual([t['text'] for t in content.titles], [s['title'] for s in self.slides])
                    self.assertTrue(all(t['in_main'] and 'data-edit' in t['attrs'] for t in content.titles))
                    for value in expected:
                        self.assertIn(value, editable)
                    self.assertEqual([im['alt'] for im in doc.images], [im['alt'] for im in images])
                    self.assertTrue(all(im['src'].startswith('data:image/png;base64,') for im in doc.images))
                    self.assertEqual([c['text'] for c in content.captions], [im['caption'] for im in images])
                    self.assertEqual([p['data-speaker-notes'] for p in doc.pages.values()], [s['notes'] for s in self.slides])
                    self.assertIn(f'{len(self.slides):02} / {len(self.slides):02}', editable)
                    self.assertNotIn('src="http', html)
                    self.assertFalse(any('illustration_fill' in page for page in report['pages']))
                    config = json.loads(doc.scripts[0])
                    self.assertEqual(config, self.sample('chart_focus')['chart'])
                    self.assertEqual([i for i, s in enumerate(StepDocument(html).services)
                                      if 'is-highlighted' in s['class'].split()], [1])
                    signature = html.replace(f'data-presentation-mode="{mode}"', 'data-presentation-mode="checked"')
                    if rendered_without_mode is None:
                        rendered_without_mode = signature
                    else:
                        self.assertTrue(signature == rendered_without_mode,
                                        '改变用途不得改变相同内容的布局 DOM、CSS、页头或资源')

    def test_zero_image_compositions_work_in_every_style_and_mode(self):
        slides = []
        for slide in self.slides:
            if SHARED_LAYOUTS[slide['layout']]['image_count'][0] == 0:
                slide = copy.deepcopy(slide)
                slide.pop('image', None)
                for item in slide.get('items', []):
                    item.pop('image', None)
                if slide['layout'] == 'editorial_columns':
                    slide['columns'] = [{'type': 'text', 'paragraphs': ['独立可编辑正文。']},
                                        {'type': 'groups', 'items': [{'title': '甲', 'text': '内容甲'}, {'title': '乙', 'text': '内容乙'}]}]
                slides.append(slide)
        self.assertEqual(len(slides), 13)
        for style in self.styles:
            for mode in ('speech', 'reading'):
                with self.subTest(style=style, mode=mode):
                    html, _ = self.render(self.deck(slides, style, mode))
                    doc = Document(html)
                    self.assertEqual(doc.images, [])
                    self.assertTrue(all('no-image' in p['class'].split() for p in doc.pages.values()))
        self.assertEqual(self.handoff(self.deck(slides))['images'], [])

    def test_nested_images_reach_handoff_and_missing_files_stop_formal_builds(self):
        slide = self.sample('service_cards')
        deck = self.deck([slide])
        images = slide_images(slide)
        manifest = self.handoff(deck)
        self.assertEqual([im['file'] for im in manifest['images']], [im['src'] for im in images])
        self.assertEqual([im['image_index'] for im in manifest['images']], [1, 2, 3])
        self.assertTrue(all(im['status'] == 'provided' for im in manifest['images']))
        self.assertEqual([im['caption'] for im in manifest['images']], [im['caption'] for im in images])
        (self.root / images[1]['src']).unlink()
        with self.assertRaisesRegex(ValueError, '缺少图片'):
            self.render(deck)
        draft, _ = self.render(deck, draft=True)
        self.assertEqual(len(Document(draft).images), 2)
        self.assertIn('待补配图', draft)
        deck['slides'][0]['items'][1]['image']['brief'] = self.brief()
        self.assertEqual([im['status'] for im in self.handoff(deck)['images']], ['provided', 'missing', 'provided'])
        bad = self.deck([self.sample('service_cards')])
        bad['slides'][0]['items'][1]['image']['src'] = 'images/./service_cards-0.png'
        with self.assertRaisesRegex(ValueError, '重复同一 src'):
            self.load(bad)

    def test_column_images_keep_nested_order_and_monitor_is_separate_from_media(self):
        slide = self.sample('editorial_columns')
        nested = slide_images(slide)
        self.assertEqual(len(nested), 5)
        html, _ = self.render(self.deck([slide]))
        self.assertEqual([im['alt'] for im in Document(html).images], [im['alt'] for im in nested])
        self.assertIn('class="comp-monitor-frame"', html)
        self.assertIn('data-column-index="1"><div class="comp-column-title"><h1 data-edit', html)
        self.assertIn('grid-template-columns:minmax(0,1fr) minmax(0,2fr) minmax(0,1fr) minmax(0,1fr)', html)
        nested[-1].update(brief=self.brief(), ratio='16:9')
        (self.root / nested[-1]['src']).unlink()
        manifest = self.handoff(self.deck([slide]))
        self.assertEqual([item['file'] for item in manifest['images']], [im['src'] for im in nested])
        self.assertEqual([item['image_index'] for item in manifest['images']], [1, 2, 3, 4, 5])
        monitor = manifest['images'][-1]
        self.assertEqual((monitor['frame'], monitor['status']), ('monitor', 'missing'))
        self.assertIn('editable CSS monitor frame', monitor['prompt'])
        self.assertIn('do not draw a monitor bezel', monitor['prompt'])
        with self.assertRaisesRegex(ValueError, '缺少图片'):
            self.render(self.deck([slide]))
        bad = self.sample('editorial_columns')
        bad['columns'][3]['images'][0]['src'] = bad['columns'][2]['items'][0]['image']['src']
        with self.assertRaisesRegex(ValueError, '重复同一 src'):
            self.load(self.deck([bad]))

    def test_nested_charts_preserve_data_editing_and_component_counts_across_styles(self):
        slide = self.sample('editorial_columns')
        slide.update(title_column=0, columns=[])
        for kind in ('bar', 'line', 'pie'):
            chart = self.sample('chart_focus')['chart']
            chart.update(chart_type=kind, title=f'{kind} 比较 < & >')
            slide['columns'].append({'type': 'chart', 'chart': chart, 'copy': f'{kind} 图表解释'})
        slide['columns'][0]['chart']['categories'][0] = '</script><script>window.injected=true</script>'
        charts = [column['chart'] for column in slide['columns']]
        titles = [chart['title'] for chart in charts]
        self.assertEqual(slide_charts(slide), charts)
        self.assertEqual(slide_images(slide), [])
        counts, texts = planned_features(slide)
        self.assertEqual((counts['charts'], texts['charts']), (3, titles))
        slide['visual']['requirements'] = [{'feature': 'charts', 'min': 3, 'texts': titles, 'source': '三项真实数据对比'}]
        for style in self.styles:
            for mode in ('speech', 'reading'):
                with self.subTest(style=style, mode=mode):
                    html, report = self.render(self.deck([slide], style, mode))
                    doc = Document(html)
                    self.assertEqual([json.loads(config) for config in doc.scripts[:3]], charts)
                    self.assertEqual(report['pages'][0]['planned']['charts'], 3)
                    self.assertIn('Apache ECharts adapter', doc.scripts[-1])
                    self.assertIn('Apache License', html)
                    self.assertEqual(html.count('class="chart-shell"'), 3)
                    self.assertEqual(html.count('class="chart-data"'), 3)
                    self.assertEqual(html.count('class="echart" data-component="chart"'), 3)
                    for value in content_values(slide):
                        self.assertIn(value, EditableText(html).values)
                    self.assertNotIn('src="http', html)

    def test_nested_chart_contract_rejects_incomplete_or_executable_fields(self):
        column = {'type': 'chart', 'chart': self.sample('chart_focus')['chart'], 'copy': '可编辑说明'}
        for mutate in (lambda c: c.pop('chart'), lambda c: c.update(chart=True),
                       lambda c: c['chart'].pop('title'), lambda c: c['chart'].pop('source'),
                       lambda c: c['chart'].update(unit=''), lambda c: c.update(copy=' '),
                       lambda c: c['chart'].update(chart_type='scatter'),
                       lambda c: c['chart'].update(categories=['一项']),
                       lambda c: c['chart']['series'][0].update(values=[1, 2]),
                       lambda c: c['chart']['series'][0].update(values=[1, True, 2]),
                       lambda c: c['chart']['series'][0].update(values=[1, float('inf'), 2]),
                       lambda c: c['chart'].update(option={'formatter': 'alert(1)'}),
                       lambda c: c['chart']['series'][0].update(extra='lost')):
            with self.subTest(mutate=mutate):
                bad = copy.deepcopy(column)
                mutate(bad)
                slide = self.sample('editorial_columns')
                slide.update(title_column=0, columns=[{'type': 'text'}, bad])
                with self.assertRaises(ValueError):
                    self.load(self.deck([slide]))

    def test_title_only_columns_and_unordered_icon_groups_keep_editable_content(self):
        slide = self.sample('editorial_columns')
        items = [{'title': f'联系项目 {i}', 'icon': 'CircleCheck'} for i in range(6)]
        items[0]['text'] = '可选联系说明'
        slide.update(title_column=0, columns=[{'type': 'text'}, {'type': 'groups', 'items': items}])
        slide['visual']['requirements'] = [{'feature': 'icons', 'min': 6,
            'texts': [item['title'] for item in items], 'source': '各联系项独立图标'}]
        for style in self.styles:
            with self.subTest(style=style):
                html, report = self.render(self.deck([slide], style))
                self.assertEqual(report['pages'][0]['planned']['icons'], 6)
                self.assertEqual(html.count('<svg class="semantic-icon"'), 6)
                self.assertEqual(StepDocument(html).steps, [])
                self.assertEqual(html.count('<article class="comp-column-group has-icon">'), 6)
                for value in [slide['title'], items[0]['text']] + [item['title'] for item in items]:
                    self.assertIn(value, EditableText(html).values)
                self.assertNotIn('Apache ECharts adapter', html)
        # A heading supports a text-only column even when the page title is elsewhere or concealed.
        slide['columns'][0]['heading'] = '独立栏标题'
        slide.update(title_column=1, show_title=False)
        html, _ = self.render(self.deck([slide]))
        self.assertIn('独立栏标题', EditableText(html).values)

    def test_empty_text_columns_and_invalid_optional_group_content_are_rejected(self):
        slide = self.sample('editorial_columns')
        slide.update(title_column=0, columns=[{'type': 'text'}, {'type': 'groups', 'items': [{'title': '甲'}, {'title': '乙'}]}])
        for mutate in (lambda s: s.update(title_column=1), lambda s: s.update(show_title=False),
                       lambda s: s.update(title=' '), lambda s: s['columns'][0].update(heading=' '),
                       lambda s: s['columns'][0].update(paragraphs=[]),
                       lambda s: s['columns'][1].update(items=[{'title': '不足一项'}]),
                       lambda s: s['columns'][1].update(items=[{'title': str(i)} for i in range(7)]),
                       lambda s: s['columns'][1]['items'][0].update(text=''),
                       lambda s: s['columns'][1]['items'][0].update(text=None),
                       lambda s: s['columns'][1]['items'][0].update(icon=''),
                       lambda s: s['columns'][1]['items'][0].update(icon='NonexistentIcon'),
                       lambda s: s['columns'][1]['items'][0].update(icon=['CircleCheck']),
                       lambda s: s['columns'][1]['items'][0].pop('title')):
            with self.subTest(mutate=mutate):
                bad = copy.deepcopy(slide)
                mutate(bad)
                with self.assertRaises(ValueError):
                    self.load(self.deck([bad]))

    def test_hierarchy_fields_render_editable_numbers_lists_and_one_emphasis(self):
        slide = self.sample('editorial_columns')
        slide.update(title_column=0, columns=[
            {'type': 'text', 'eyebrow': 'SCENARIO 01', 'paragraphs': ['一句引导']},
            {'type': 'groups', 'numbered': True, 'items': [
                {'title': '要点甲', 'text': '说明甲'}, {'title': '要点乙', 'emphasis': True}]},
            {'type': 'text', 'heading': '清单栏', 'list': True, 'paragraphs': ['单行条目', '条目名\n条目说明']}])
        for style in self.styles:
            with self.subTest(style=style):
                html, _ = self.render(self.deck([slide], style))
                values = EditableText(html).values
                for value in ('SCENARIO 01', '01', '02', '单行条目', '条目名', '条目说明', '清单栏'):
                    self.assertIn(value, values)
                self.assertIn('class="comp-groups-grid is-numbered"', html)
                self.assertEqual(html.count('class="comp-column-group has-number is-emphasis"'), 1)
                self.assertIn('comp-column-text is-list"', html)
                self.assertEqual(html.count('class="comp-list-entry"'), 1)
        for mutate in (lambda s: s['columns'][0].update(eyebrow=' '),
                       lambda s: s['columns'][2].update(list='yes'),
                       lambda s: s['columns'][2].pop('paragraphs'),
                       lambda s: s['columns'][1].update(numbered=1),
                       lambda s: s['columns'][1]['items'][0].update(icon='CircleCheck'),
                       lambda s: s['columns'][1]['items'][0].update(emphasis=True),
                       lambda s: s['columns'][1]['items'][0].update(emphasis='true')):
            with self.subTest(mutate=mutate):
                bad = copy.deepcopy(slide)
                mutate(bad)
                with self.assertRaises(ValueError):
                    self.load(self.deck([bad]))

    def test_side_index_accepts_twelve_entries_and_rejects_thirteen(self):
        slide = self.sample('side_index')
        slide['items'] = [{'title': f'目录条目 {i + 1}'} for i in range(12)]
        html, _ = self.render(self.deck([slide]))
        editable = EditableText(html).values
        for item in slide['items']:
            self.assertIn(item['title'], editable)
        self.assertIn('12', editable)
        slide['items'].append({'title': '超出容量'})
        with self.assertRaisesRegex(ValueError, '2–12'):
            self.load(self.deck([slide]))

    def test_poster_keeps_heading_editable_when_chapter_title_is_visually_hidden(self):
        slide = self.sample('type_poster')
        slide.update(variant='chapter', show_title=False, number='4')
        for style in self.styles:
            with self.subTest(style=style):
                html, _ = self.render(self.deck([slide], style=style))
                titles = ContentDocument(html).titles
                self.assertEqual([t['text'] for t in titles], [slide['title']])
                self.assertTrue(titles[0]['in_main'])
                self.assertIn('data-edit', titles[0]['attrs'])
                self.assertNotIn('aria-hidden', titles[0]['attrs'])
                self.assertIn('comp-poster-heading is-concealed', html)
                self.assertIn('.editing .comp-type_poster .comp-poster-heading.is-concealed', html)
                self.assertEqual(Document(html).images, [])

    def test_centered_cover_and_statement_keep_all_text_editable_in_both_modes(self):
        cover = self.sample('type_poster')
        cover.update(placement='center', eyebrow='摄影工作室 < & >')
        statement = self.sample('type_poster')
        statement.pop('number')
        statement.update(id='statement', variant='statement', placement='bottom-right', eyebrow='我们的创作方式',
                         copy='从日常观察开始，理解每一个独特的瞬间。', bullets=['保留真实', '关注关系', '持续观察'])
        for style in self.styles:
            for mode in ('speech', 'reading'):
                with self.subTest(style=style, mode=mode):
                    html, report = self.render(self.deck([cover, statement], style, mode))
                    self.assertIn('variant-cover placement-center', html)
                    self.assertIn('variant-statement placement-bottom-right', html)
                    self.assertEqual([page['role'] for page in report['pages']], ['cover', 'explanation'])
                    self.assertIn('<ul class="comp-poster-bullets"><li data-edit>保留真实</li>', html)
                    for value in content_values(cover) + content_values(statement):
                        self.assertIn(value, EditableText(html).values)
                    self.assertTrue(all(title['in_main'] for title in ContentDocument(html).titles))
        # Unadorned statements and old covers have useful, different defaults.
        plain = {'id': 'plain', 'layout': 'type_poster', 'title': '用影像记录\n平凡而独特的生活',
                 'variant': 'statement', 'visual': {'rationale': '短声明保留留白。', 'requirements': []}}
        html, _ = self.render(self.deck([plain]))
        self.assertIn('variant-statement placement-center is-title-only', html)
        self.assertIn('用影像记录<br>平凡而独特的生活', html)
        explicit = copy.deepcopy(plain)
        explicit['placement'] = 'center'
        self.assertEqual(html, self.render(self.deck([explicit]))[0])
        default_cover = self.sample('type_poster')
        self.assertEqual(self.render(self.deck([default_cover]))[0],
                         self.render(self.deck([dict(default_cover, placement='bottom-left')]))[0])

    def test_image_only_columns_preserve_hidden_heading_and_weighted_gallery(self):
        slide = self.sample('editorial_columns')
        images = slide_images(slide)[:3]
        slide.update(title_column=0, show_title=False, columns=[
            {'type': 'image', 'image': images[0]},
            {'type': 'gallery', 'grid_columns': 1, 'row_weights': [2, 1], 'images': images[1:]}])
        for style in self.styles:
            with self.subTest(style=style):
                html, _ = self.render(self.deck([slide], style))
                self.assertEqual([im['alt'] for im in Document(html).images], [im['alt'] for im in images])
                self.assertIn('comp-column-title is-concealed', html)
                self.assertIn('grid-template-rows:minmax(0,2fr) minmax(0,1fr)', html)
                self.assertIn('.editing .comp-editorial_columns .comp-column-title.is-concealed', html)
                titles = ContentDocument(html).titles
                self.assertEqual([title['text'] for title in titles], [slide['title']])
                self.assertTrue(titles[0]['in_main'])
                self.assertIn('data-edit', titles[0]['attrs'])
                self.assertNotIn('aria-hidden', titles[0]['attrs'])
                self.assertIn(slide['subtitle'], EditableText(html).values)
        manifest = self.handoff(self.deck([slide]))
        self.assertEqual([item['file'] for item in manifest['images']], [im['src'] for im in images])

    def test_new_poster_and_gallery_fields_reject_invalid_or_ignored_values(self):
        def as_statement(s, **fields):
            s.pop('number', None)
            s.update(variant='statement', **fields)
        cases = [('type_poster', lambda s: s.update(placement='top-center')),
                 ('type_poster', lambda s: s.update(variant='chapter', placement='center')),
                 ('type_poster', lambda s: s.update(eyebrow='')),
                 ('type_poster', lambda s: s.update(copy='忽略的封面正文')),
                 ('type_poster', lambda s: s.update(bullets=['忽略的封面列表'])),
                 ('type_poster', lambda s: as_statement(s, number='1')),
                 ('type_poster', lambda s: as_statement(s, show_title=False)),
                 ('type_poster', lambda s: as_statement(s, bullets='文字不是列表')),
                 ('type_poster', lambda s: as_statement(s, bullets=[])),
                 ('type_poster', lambda s: as_statement(s, bullets=[''])),
                 ('type_poster', lambda s: as_statement(s, bullets=['重复'] * 9)),
                 ('editorial_columns', lambda s: s.update(show_title='false')),
                 ('editorial_columns', lambda s: s['columns'][0].update(row_weights=[2, 1])),
                 ('editorial_columns', lambda s: s['columns'][3].update(grid_columns=2, row_weights=[2, 1])),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights=[])),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights=[1])),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights='2fr 1fr')),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights=[0, 1])),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights=[5, 1])),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights=[True, 1])),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights=[float('inf'), 1])),
                 ('editorial_columns', lambda s: s['columns'][3].update(row_weights=[10 ** 1000, 1]))]
        for layout, mutate in cases:
            with self.subTest(layout=layout, mutate=mutate):
                slide = self.sample(layout)
                mutate(slide)
                with self.assertRaises(ValueError):
                    self.load(self.deck([slide]))

    def test_poster_and_columns_reject_ignored_fields_and_unsafe_geometry(self):
        cases = [('type_poster', lambda s: s.update(variant='other')),
                 ('type_poster', lambda s: s.update(variant='chapter', number=None)),
                 ('type_poster', lambda s: s.update(show_title=False)),
                 ('type_poster', lambda s: s.update(show_title='false')),
                 ('editorial_columns', lambda s: s.update(title_column=True)),
                 ('editorial_columns', lambda s: s.update(title_column=4)),
                 ('editorial_columns', lambda s: s.update(columns=s['columns'][:1])),
                 ('editorial_columns', lambda s: s['columns'][0].update(type='unknown')),
                 ('editorial_columns', lambda s: s['columns'][0].update(weight=float('nan'))),
                 ('editorial_columns', lambda s: s['columns'][0].update(weight=10 ** 1000)),
                 ('editorial_columns', lambda s: s['columns'][0].update(weight=0)),
                 ('editorial_columns', lambda s: s['columns'][0].update(weight=True)),
                 ('editorial_columns', lambda s: s['columns'][0].update(weight='1fr;display:none')),
                 ('editorial_columns', lambda s: s['columns'][0].update(align='center')),
                 ('editorial_columns', lambda s: s['columns'][0].update(paragraphs=[])),
                 ('editorial_columns', lambda s: s['columns'][0].update(extra='lost')),
                 ('editorial_columns', lambda s: s['columns'][1].update(group_columns=3)),
                 ('editorial_columns', lambda s: s['columns'][1]['items'][0].update(extra='lost')),
                 ('editorial_columns', lambda s: s['columns'][2]['items'][0].pop('role')),
                 ('editorial_columns', lambda s: s['columns'][2]['items'][0].pop('image')),
                 ('editorial_columns', lambda s: s['columns'][3].update(grid_columns=True)),
                 ('editorial_columns', lambda s: s['columns'][3].update(images=[])),
                 ('editorial_columns', lambda s: s['columns'][3]['images'][0].update(frame='phone')),
                 ('photo_banner', lambda s: s['image'].update(frame='monitor'))]
        for layout, mutate in cases:
            with self.subTest(layout=layout, mutate=mutate):
                slide = self.sample(layout)
                mutate(slide)
                with self.assertRaises(ValueError):
                    self.load(self.deck([slide]))

    def test_unknown_fields_are_not_silently_discarded(self):
        for slide in self.slides:
            with self.subTest(layout=slide['layout']):
                bad = dict(copy.deepcopy(slide), unrendered='这段内容不能消失')
                with self.assertRaisesRegex(ValueError, '不支持字段'):
                    self.load(self.deck([bad]))
        cases = [('service_cards', lambda s: s['items'][0].update(icon='Sparkles')),
                 ('service_cards', lambda s: s['items'][0]['image'].update(crop='cover')),
                 ('checklist_photo', lambda s: s['groups'][0].update(extra='hidden')),
                 ('checklist_photo', lambda s: s['groups'][0]['checks'][0].update(extra='hidden')),
                 ('metric_cards', lambda s: s['metrics'][0].update(extra='hidden')),
                 ('snake_timeline', lambda s: s['steps'][0].update(extra='hidden')),
                 ('chart_focus', lambda s: s['chart'].update(extra='hidden')),
                 ('chart_focus', lambda s: s['chart']['series'][0].update(extra='hidden')),
                 ('chart_focus', lambda s: s['stat'].update(extra='hidden'))]
        for layout, mutate in cases:
            with self.subTest(layout=layout, mutate=mutate):
                slide = self.sample(layout)
                mutate(slide)
                with self.assertRaisesRegex(ValueError, '不支持字段'):
                    self.load(self.deck([slide]))

    def test_progress_is_one_numeric_source_and_adds_only_its_small_runtime(self):
        slide = self.sample('metric_cards')
        slide.pop('image', None)
        slide['metrics'] = [{'label': '完成率', 'text': '示例口径', 'progress': {'value': 77, 'max': 100}},
                            {'label': '目标比例', 'progress': {'value': 20, 'max': 50}}]
        html, _ = self.render(self.deck([slide]))
        self.assertIn('>77%</strong>', html)
        self.assertIn('>40%</strong>', html)
        self.assertIn('slideCompositions', html)
        self.assertNotIn('Apache ECharts adapter', html)
        self.assertIn('77', EditableText(html).values)
        self.assertIn('100', EditableText(html).values)
        self.assertNotIn('77%', EditableText(html).values)
        for progress in ({'value': -1, 'max': 100}, {'value': 101, 'max': 100}, {'value': 0, 'max': 0},
                         {'value': True, 'max': 100}, {'value': 10, 'max': float('nan')},
                         {'value': 10, 'max': 10 ** 1000},
                         {'value': 10, 'max': 100, 'color': 'red'}):
            bad = copy.deepcopy(slide); bad['metrics'][0]['progress'] = progress
            with self.subTest(progress=progress), self.assertRaises(ValueError):
                self.load(self.deck([bad]))
        slide['metrics'][0]['value'] = '不同步值'
        with self.assertRaisesRegex(ValueError, '不能同时设置'):
            self.load(self.deck([slide]))

    def test_five_people_columns_and_six_column_boundary(self):
        slide = self.sample('editorial_columns')
        person = slide['columns'][2]['items'][0]
        for count in (5, 6):
            slide['columns'] = [{'type': 'people', 'items': [dict(person, image=dict(person['image'], src=f'images/portrait-{i}.png'))]} for i in range(count)]
            for image in slide_images(slide):
                (self.root / image['src']).write_bytes(placeholder_png(24, 24))
            html, _ = self.render(self.deck([slide]))
            self.assertEqual(html.count('class="comp-column-person"'), count)
        slide['columns'].append(copy.deepcopy(slide['columns'][-1]))
        with self.assertRaises(ValueError):
            self.load(self.deck([slide]))

    def test_pie_shares_source_contract_and_rejects_empty_total(self):
        slide = self.sample('chart_focus'); slide['chart']['chart_type'] = 'pie'
        html, _ = self.render(self.deck([slide]))
        self.assertEqual(json.loads(Document(html).scripts[0]), slide['chart'])
        for values in ([0, 0, 0], [-1, 2, 3]):
            bad = copy.deepcopy(slide); bad['chart']['series'][0]['values'] = values
            with self.assertRaises(ValueError):
                self.load(self.deck([bad]))
        slide['chart']['series'].append(copy.deepcopy(slide['chart']['series'][0]))
        with self.assertRaises(ValueError):
            self.load(self.deck([slide]))

    def test_hub_and_row_reject_missing_semantics(self):
        for layout, field, value in [('hub_spoke', 'center', {'text': '无中心标题'}),
                                     ('hub_spoke', 'items', [{'title': '太少'}]),
                                     ('step_row', 'steps', [{'title': '缺说明'}] * 3)]:
            slide = self.sample(layout); slide[field] = value
            with self.subTest(layout=layout), self.assertRaises(ValueError):
                self.load(self.deck([slide]))

    def test_invalid_image_counts_states_metrics_and_charts_are_rejected(self):
        cases = [('photo_pair', lambda s: s.update(images=s['images'][:1])),
                 ('offset_pair', lambda s: s.update(images=s['images'] + [dict(s['images'][0], src='third.png')])),
                 ('photo_strip', lambda s: s.update(images=[dict(s['images'][0], src=f'{i}.png') for i in range(6)])),
                 ('checklist_photo', lambda s: s.pop('image')),
                 ('service_cards', lambda s: s['items'][1]['image'].pop('src')),
                 ('service_cards', lambda s: s.update(highlight=True)),
                 ('service_cards', lambda s: s.update(highlight=3)),
                 ('checklist_photo', lambda s: s['groups'][0]['checks'][0].update(checked='true')),
                 ('checklist_photo', lambda s: s['groups'][0]['checks'][0].pop('checked')),
                 ('metric_cards', lambda s: s.pop('source')),
                 ('metric_cards', lambda s: s['metrics'][0].update(value='', text='')),
                 ('metric_circles', lambda s: s['metrics'][0].update(value=70)),
                 ('metric_circles', lambda s: s.update(source=' ')),
                 ('chart_focus', lambda s: s['chart'].pop('title')),
                 ('chart_focus', lambda s: s['chart'].update(chart_type='pie3d')),
                 ('chart_focus', lambda s: s['chart'].update(source='')),
                 ('chart_focus', lambda s: s['chart'].update(unit='')),
                 ('chart_focus', lambda s: s['chart'].update(categories=['one'])),
                 ('chart_focus', lambda s: s['chart']['series'][0].update(values=[1, 2])),
                 ('chart_focus', lambda s: s['chart']['series'][0].update(values=[1, True, 2])),
                 ('chart_focus', lambda s: s['chart']['series'][0].update(values=[1, float('nan'), 2]))]
        for layout, mutate in cases:
            with self.subTest(layout=layout, mutate=mutate):
                slide = self.sample(layout)
                mutate(slide)
                with self.assertRaises(ValueError):
                    self.load(self.deck([slide]))

    def test_steps_remain_in_chronological_dom_order_and_states_are_explicit(self):
        for layout in ('snake_timeline', 'step_sidebar', 'step_row'):
            slide = self.sample(layout)
            html, _ = self.render(self.deck([slide]))
            doc = StepDocument(html)
            self.assertEqual([int(s['data-step']) for s in doc.steps], list(range(1, len(slide['steps']) + 1)))
            text = EditableText(html).values
            positions = [text.index(step['title']) for step in slide['steps']]
            self.assertEqual(positions, sorted(positions))
            if layout == 'snake_timeline':
                self.assertEqual([s['style'] for s in doc.steps[3:]],
                                 ['--step-row:2;--step-column:3', '--step-row:2;--step-column:2', '--step-row:2;--step-column:1'])
        html, _ = self.render(self.deck([self.sample('checklist_photo')]))
        self.assertEqual(StepDocument(html).states, ['included', 'excluded', 'included', 'excluded'])

    def test_explicit_requirements_match_planned_components(self):
        cases = [('statement_tags', 'tags', 'tags'), ('photo_banner', 'tags', 'tags'),
                 ('service_cards', 'panels', 'items'), ('metric_cards', 'visual_blocks', 'metrics'),
                 ('metric_circles', 'visual_blocks', 'metrics'), ('snake_timeline', 'steps', 'steps'),
                 ('step_sidebar', 'steps', 'steps'), ('checklist_photo', 'states', 'groups'),
                 ('chart_focus', 'charts', 'chart')]
        for layout, feature, field in cases:
            with self.subTest(layout=layout):
                slide = self.sample(layout)
                if field == 'groups':
                    texts = [c['label'] for group in slide[field] for c in group['checks']]
                elif field == 'chart':
                    texts = [slide[field]['title']]
                elif field == 'tags':
                    texts = slide[field]
                else:
                    texts = [item['label' if field == 'metrics' else 'title'] for item in slide[field]]
                counts, planned_texts = planned_features(slide)
                self.assertEqual(counts[feature], len(texts))
                self.assertEqual(planned_texts[feature], texts)
                req = {'feature': feature, 'min': len(texts), 'texts': texts, 'source': '显式设计要求'}
                slide['visual']['requirements'] = [req]
                _, report = self.render(self.deck([slide]))
                self.assertEqual(report['pages'][0]['planned'][feature], len(texts))
                req['min'] += 1
                data, root = self.load(self.deck([slide]))
                self.assertTrue(any('计划只有' in e for e in check_plan(data, root)['errors']))
                req.update(min=len(texts), texts=['没有实现的内容'])
                data, root = self.load(self.deck([slide]))
                self.assertTrue(any('文案' in e for e in check_plan(data, root)['errors']))

    @staticmethod
    def brief():
        return {'subject': 'Three distinct staff members arrange labelled-free physical materials around a shared worktable.',
                'action': 'The centre person compares two samples while the others prepare the next stage.',
                'structure': 'One continuous table links the incoming tray at left to the completed material at right.',
                'details': 'Tools, trays, paper sheets and material samples have clear realistic proportions and coherent shadows.'}

    def test_prompt_medium_comes_from_style_and_not_layout_or_mode(self):
        slide = self.sample('photo_banner')
        slide['image'].update(src='images/not-yet-generated.png', brief=self.brief())
        for style in self.styles:
            with self.subTest(style=style):
                deck = self.deck([slide], style)
                pack = resolve_style(deck)
                if style in {'monochrome-editorial', 'warm-minimal-editorial'}:
                    self.assertEqual(pack['image_background'], 'scene', '摄影风格须保留场景背景')
                speech = self.handoff(deck)['images'][0]
                reading = self.handoff(dict(deck, presentation_mode='reading'))['images'][0]
                self.assertEqual(speech['prompt'], reading['prompt'])
                self.assertTrue(speech['prompt'].startswith(pack['image_prompt'].read_text().strip()))
                self.assertIn("selected style's medium", speech['prompt'])
                self.assertEqual(speech['image_background'], pack['image_background'])
                if pack['image_background'] == 'paper':
                    self.assertIn('Required background for BOTH', speech['prompt'])
                    self.assertNotIn('Photographic background policy:', speech['prompt'])
                else:
                    self.assertIn('preserve the real setting', speech['prompt'])


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompositionTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(run())
