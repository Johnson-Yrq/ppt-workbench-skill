"""Regression checks for style-owned headers and shared layout selection."""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from build_deck import Builder, check_plan
from common import HEADER_STYLES, load_deck, placeholder_png
from style_packs import discover_styles, resolve_style, validate_header_template
from test_editorial import ContentDocument
from test_styles import Document, all_layouts_deck


class HeaderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='slide-headers-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.image = {'src': 'image.png', 'alt': '页头回归配图'}
        (self.root / 'image.png').write_bytes(placeholder_png(24, 16))

    def deck(self, style):
        regular = copy.deepcopy(next(s for s in all_layouts_deck(style)['slides'] if s['layout'] == 'split'))
        regular.update(title='普通标题 < & >', chapter='章节 < & >', subtitle='副标题 < & >', image=self.image)
        editorial = {'id': 'editorial', 'layout': 'editorial', 'editorial_variant': 'intro', 'title': '编辑标题 < & >',
                     'copy': '主内容中的完整说明。', 'chapter': '编辑章', 'image': self.image,
                     'visual': {'rationale': '用图片与文字验证页头和主内容的分工。', 'requirements': []}}
        return {'version': 1, 'style': style, 'title': 'Header fixture', 'year': 2026,
                'company': 'STUDIO < & >', 'slides': [regular, editorial]}

    def render(self, deck):
        file = self.root / 'deck.json'
        file.write_text(json.dumps(deck, ensure_ascii=False))
        data, root = load_deck(file)
        report = check_plan(data, root)
        self.assertTrue(report['ok'], report['errors'])
        return Builder(data, root, embed_format='keep').render()

    def fixture_style(self, template=None):
        skills = self.root / 'skills'
        assets = skills / 'fixture-slides' / 'assets'
        assets.mkdir(parents=True)
        manifest = {'schema': 'html-slide-style/v1', 'id': 'fixture', 'name': 'Fixture',
                    'description': 'A style with its own declarative header.', 'status': 'ready',
                    'image_prompt': 'image-style.txt', 'ui_text_modes': ['none'],
                    'default_ui_text': 'none', 'ui_text_prompts': {'none': 'No text.'}}
        (assets / 'image-style.txt').write_text('Photographic image.')
        if template is not None:
            manifest['header_template'] = 'header.html'
            (assets / 'header.html').write_text(template)
        (assets / 'style.json').write_text(json.dumps(manifest))
        registry = patch('style_packs.SKILLS', skills)
        registry.start()
        self.addCleanup(registry.stop)
        return assets, manifest

    def test_six_presets_are_explicitly_scoped_to_the_original_styles(self):
        inventory = discover_styles()
        self.assertEqual(inventory['errors'], [])
        original = {'scene-white', 'saas-3d', 'real-miniature'}
        self.assertEqual({s['id'] for s in inventory['styles'] if s['header_system'] == 'preset-six'}, original)
        for style in original:
            for preset in HEADER_STYLES:
                with self.subTest(style=style, preset=preset):
                    deck = self.deck(style)
                    deck['header'] = preset
                    html = self.render(deck)
                    doc = Document(html)
                    self.assertEqual(doc.body['data-header-system'], 'preset-six')
                    expected = [] if preset == 'standard' else ['head-' + preset]
                    for page in doc.pages.values():
                        self.assertEqual([c for c in page['class'].split() if c.startswith('head-')], expected)
                    self.assertTrue(any('.head-band' in css for css in doc.styles))
                    self.assertEqual([t['text'] for t in ContentDocument(html).titles], [s['title'] for s in deck['slides']])
            cover = copy.deepcopy(next(s for s in all_layouts_deck(style)['slides'] if s['layout'] == 'cover'))
            cover['image'] = self.image
            with self.assertRaisesRegex(ValueError, 'header'):
                self.render(dict(self.deck(style), header='unknown', slides=[cover]))

    def test_header_source_depends_on_style_in_both_presentation_modes(self):
        styles = {s['id']: s for s in discover_styles()['styles']}
        for style, info in styles.items():
            for mode in ('speech', 'reading'):
                with self.subTest(style=style, mode=mode):
                    deck = self.deck(style)
                    deck['presentation_mode'] = mode
                    html = self.render(deck)
                    doc, content = Document(html), ContentDocument(html)
                    self.assertEqual(doc.body['data-header-system'], info['header_system'])
                    self.assertEqual([t['text'] for t in content.titles], [s['title'] for s in deck['slides']])
                    self.assertEqual([t['in_main'] for t in content.titles], [False, True])
                    self.assertEqual(len(re.findall(r'<header(?:\s|>)', html)), 2)
                    if info['header_system'] == 'style':
                        self.assertFalse(any('.head-band' in css for css in doc.styles))
                        self.assertTrue(all('head-band' not in p['class'] for p in doc.pages.values()))
                        header_open = re.search(r'<header\b[^>]*>', resolve_style(deck)['header_markup'])[0]
                        self.assertEqual(html.count(header_open), 2)
                        self.assertIn('STUDIO &lt; &amp; &gt;', html)
                        deck['header'] = 'band'
                        with self.assertRaisesRegex(ValueError, 'header_template'):
                            self.render(deck)
                        deck.pop('header')
                        deck['slides'][0]['header'] = 'band'
                        with self.assertRaisesRegex(ValueError, 'header_template'):
                            self.render(deck)

    def test_custom_template_keeps_metadata_and_escaped_editable_content(self):
        self.fixture_style('<header class="fixture-head"><div>{{company}}{{year}}{{page}}</div>'
                           '<div>{{chapter}}{{title}}{{subtitle}}</div></header>')
        html = self.render(self.deck('fixture'))
        self.assertEqual(html.count('<header class="fixture-head">'), 2)
        self.assertIn('data-edit class="header-company">STUDIO &lt; &amp; &gt;', html)
        self.assertIn('data-edit class="chapter">章节 &lt; &amp; &gt;', html)
        self.assertIn('data-edit class="subtitle">副标题 &lt; &amp; &gt;', html)
        self.assertNotIn('{{', html)
        self.assertFalse(any('.head-band' in css for css in Document(html).styles))
        self.assertTrue(all('data-edit' in title['attrs'] for title in ContentDocument(html).titles))

    def test_omitted_header_template_uses_neutral_fallback(self):
        self.fixture_style()
        html = self.render(self.deck('fixture'))
        self.assertEqual(Document(html).body['data-header-system'], 'style')
        self.assertEqual(html.count('<header class="style-header">'), 2)
        self.assertFalse(any('.head-band' in css for css in Document(html).styles))

    def test_templates_reject_unsafe_invalid_and_unrenderable_fragments(self):
        for source in ('', '<div>{{title}}</div>', '<header>{{unknown}}</header>',
                       '<header>{{title}}{{title}}</header>', '<header><script>alert(1)</script>{{title}}</header>',
                       '<header onclick="run()">{{title}}</header>', '<header><img src="https://example.com">{{title}}</header>',
                       '<header class="{{company}}">{{title}}</header>', '<header><div>{{title}}</header>',
                       '<header><!-- {{company}} -->{{title}}</header>', '<header>{{TITLE}}</header>',
                       '<header>&#123;&#123;title&#125;&#125;</header>'):
            with self.subTest(source=source), self.assertRaisesRegex(ValueError, 'header_template'):
                validate_header_template(source)
        assets, manifest = self.fixture_style('<header>{{title}}</header>')
        report = check_plan(self.deck('fixture'), self.root)
        self.assertFalse(report['ok'])
        self.assertTrue(any('chapter' in error for error in report['errors']))
        outside = self.root / 'outside.html'
        outside.write_text('<header>{{title}}</header>')
        for field, value in [('header_template', '../../../../outside.html'),
                             ('header_template', str(outside)), ('header_template', 'https://example.com/header.html'),
                             ('header_template', str(assets / 'header.html')),
                             ('header_system', 'all'), ('header_system', None),
                             ('heading_icons', True), ('cover_copy_policy', False)]:
            bad = dict(manifest, **{field: value})
            (assets / 'style.json').write_text(json.dumps(bad))
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                resolve_style(self.deck('fixture'))
        (assets / 'style.json').write_text(json.dumps(dict(manifest, header_system='preset-six')))
        with self.assertRaisesRegex(ValueError, 'preset-six'):
            resolve_style(self.deck('fixture'))

    def test_aligned_flow_rows_are_not_gated_by_presentation_mode(self):
        from test_refinements import example
        deck = example()
        deck['slides'] = deck['slides'][:1]
        for mode in ('speech', 'reading'):
            deck['presentation_mode'] = mode
            html = self.render(deck)
            self.assertIn('data-align-rows="true"', html)
            self.assertTrue(any('.control-groups[data-align-rows="true"]' in css for css in Document(html).styles))


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HeaderTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(run())
