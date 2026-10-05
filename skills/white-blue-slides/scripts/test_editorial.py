#!/usr/bin/env python3
"""Behavioral checks for shared editorial layouts and photographic prompts."""
import contextlib
import copy
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build_deck import Builder, check_plan
from common import ASSETS, LAYOUTS, NATIVE_LAYOUTS, load_deck, placeholder_png, slide_images
from editorial_contract import EDITORIAL_VARIANTS
from prepare_images import prepare
from style_packs import discover_styles


class ContentDocument(HTMLParser):
    """Read user-facing content and embedding, independent of CSS source text."""
    def __init__(self, html):
        super().__init__()
        self.pages, self.images, self.titles, self.captions = [], [], [], []
        self.in_main, self.capture = False, None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and 'slide' in attrs.get('class', '').split():
            self.pages.append(attrs)
        if tag == 'main':
            self.in_main = True
        if tag == 'img':
            self.images.append(attrs)
        if tag in {'h1', 'figcaption'}:
            self.capture = {'tag': tag, 'attrs': attrs, 'in_main': self.in_main, 'text': ''}
        if tag == 'br' and self.capture:
            self.capture['text'] += '\n'

    def handle_endtag(self, tag):
        if self.capture and tag == self.capture['tag']:
            (self.titles if tag == 'h1' else self.captions).append(self.capture)
            self.capture = None
        if tag == 'main':
            self.in_main = False

    def handle_data(self, text):
        if self.capture:
            self.capture['text'] += text


class EditorialTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='slide-editorial-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.skills = self.root / 'skills'
        self.pack_path = self.skills / 'editorial-test-slides' / 'assets'
        self.pack_path.mkdir(parents=True)
        self.pack = {'schema': 'html-slide-style/v1', 'id': 'editorial-test', 'name': 'Editorial fixture',
                     'description': 'An independent supported editorial style.', 'status': 'ready',
                     'css': 'theme.css', 'image_prompt': 'image-style.txt',
                     'ui_text_modes': ['none'], 'default_ui_text': 'none', 'ui_text_prompts': {'none': 'No text.'},
                     'surfaces': ['light', 'dark'], 'image_free_layouts': ['cover', 'closing'],
                     'cover_labels_expected': False, 'editorial_variants': list(EDITORIAL_VARIANTS),
                     'image_background': 'scene'}
        (self.pack_path / 'theme.css').write_text('body[data-style="editorial-test"]{--paper:#EFEEEA}')
        (self.pack_path / 'image-style.txt').write_text('Real life-size editorial photography with natural light.')
        self.save_pack()
        # Copy the real legacy manifest/prompt, so its omitted background field
        # exercises backward-compatible paper policy rather than a new fixture default.
        legacy = self.skills / 'white-blue-slides' / 'assets'
        legacy.mkdir(parents=True)
        for file in ('style.json', 'image-style.txt'):
            (legacy / file).write_text((ASSETS / file).read_text())
        self.registry = patch('style_packs.SKILLS', self.skills)
        self.registry.start()
        self.addCleanup(self.registry.stop)
        (self.root / 'images').mkdir()
        for index in range(6):
            (self.root / 'images' / f'{index}.png').write_bytes(placeholder_png(24, 16))

    def save_pack(self):
        (self.pack_path / 'style.json').write_text(json.dumps(self.pack))

    def image(self, index=0, caption=True):
        image = {'src': f'images/{index}.png', 'alt': f'摄影内容 {index}'}
        if caption:
            image['caption'] = f'可编辑图注 {index} < & >'
        return image

    def slide(self, variant):
        s = {'id': variant, 'layout': 'editorial', 'editorial_variant': variant,
             'title': f'{variant} 标题 < & >\n保留第二行', 'notes': '讲者备注 <原样保留>',
             'visual': {'rationale': '以摄影与可编辑文字构成已确认的编辑式层级。', 'requirements': []}}
        if variant in {'services', 'portfolio'}:
            s['images'] = [self.image(i) for i in range(3 if variant == 'services' else 6)]
        else:
            s['image'] = self.image()
        if variant == 'cover':
            s.update(kicker='简洁的引题', subtitle='Cover subtitle')
        elif variant == 'intro':
            s['copy'] = '完整保留介绍正文。'
        elif variant == 'contents':
            s.update(copy='目录旁的短说明。', items=[{'title': '第一章', 'label': '01'}, {'title': '第二章', 'label': '02'}])
        elif variant == 'about':
            s.update(lead='关于设计的主张。', columns=['第一栏完整正文。', '第二栏完整正文。'])
        elif variant in {'services', 'process'}:
            s['items'] = [{'title': f'条目 {i}', 'text': f'条目 {i} 的完整解释。'} for i in range(3)]
        elif variant == 'portfolio':
            s['copy'] = '摄影档案的背景说明。'
        elif variant == 'closing':
            s.update(subtitle='Closing subtitle', copy='从下一步开始。')
        return s

    def deck(self, variants=EDITORIAL_VARIANTS, mode='speech'):
        return {'version': 1, 'style': 'editorial-test', 'title': '原生编辑式测试', 'company': 'TEST STUDIO',
                'year': 2026, 'footer_label': 'SHARED FOOTER', 'presentation_mode': mode,
                'slides': [self.slide(v) for v in variants]}

    def load(self, deck):
        path = self.root / 'deck.json'
        path.write_text(json.dumps(deck, ensure_ascii=False))
        return load_deck(path)

    def prepare(self, deck):
        self.load(deck)
        with contextlib.redirect_stdout(io.StringIO()):
            return prepare(self.root / 'deck.json', self.root / 'handoff')

    def test_all_variants_embed_editable_content_in_both_modes(self):
        for mode in ('speech', 'reading'):
            with self.subTest(mode=mode):
                deck = self.deck(mode=mode)
                data, root = self.load(deck)
                report = check_plan(data, root)
                self.assertTrue(report['ok'], report['errors'])
                self.assertFalse(report['warnings'])
                self.assertEqual([p['editorial_variant'] for p in report['pages']], list(EDITORIAL_VARIANTS))
                self.assertEqual(report['pages'][5]['planned']['steps'], 3)
                html = Builder(data, root, embed_format='keep').render()
                doc = ContentDocument(html)
                self.assertEqual(len(doc.pages), 8)
                self.assertEqual([t['text'] for t in doc.titles], [s['title'] for s in deck['slides']])
                self.assertTrue(all(t['in_main'] and 'data-edit' in t['attrs'] for t in doc.titles))
                expected_images = [im for s in deck['slides'] for im in slide_images(s)]
                self.assertEqual(len(doc.images), len(expected_images))
                self.assertEqual([im['alt'] for im in doc.images], [im['alt'] for im in expected_images])
                self.assertTrue(all(im['src'].startswith('data:image/png;base64,') for im in doc.images))
                self.assertEqual([c['text'] for c in doc.captions], [im['caption'] for im in expected_images])
                self.assertTrue(all('data-edit' in c['attrs'] for c in doc.captions))
                self.assertTrue(all(p['data-speaker-notes'] == '讲者备注 <原样保留>' for p in doc.pages))
                self.assertIn('class="header-company">TEST STUDIO', html)
                self.assertIn('class="header-year">2026', html)
                self.assertIn('class="footer-label">SHARED FOOTER', html)
                self.assertIn('class="editorial-folio">08 / 08', html)
                self.assertNotIn('src="http', html)
                self.assertEqual(len(LAYOUTS), 13)
                self.assertIn('editorial', NATIVE_LAYOUTS)
                self.assertIn('editorial', Builder.LAYOUTS)

    def test_photo_counts_and_captions_reach_handoff(self):
        for variant, count in [('services', 1), ('services', 3), ('portfolio', 2), ('portfolio', 6)]:
            with self.subTest(variant=variant, count=count):
                deck = self.deck([variant])
                deck['slides'][0]['images'] = [self.image(i) for i in range(count)]
                manifest = self.prepare(deck)
                self.assertEqual([im['image_index'] for im in manifest['images']], list(range(1, count + 1)))
                self.assertTrue(all(im['status'] == 'provided' for im in manifest['images']))
                self.assertTrue(all(im['caption'].startswith('可编辑图注') for im in manifest['images']))
                self.assertTrue(all(im['image_background'] == 'scene' and im['editorial_variant'] == variant for im in manifest['images']))
                data, root = self.load(deck)
                doc = ContentDocument(Builder(data, root, embed_format='keep').render())
                self.assertEqual(len(doc.images), count)

    def test_rejects_unrendered_fields_missing_content_and_unsupported_counts(self):
        cases = [
            ('cover', lambda s: s.update(editorial_variant='gallery'), 'editorial_variant'),
            ('cover', lambda s: s.pop('image'), '需要一个 image'),
            ('intro', lambda s: s.pop('copy'), 'copy'),
            ('about', lambda s: s.update(columns=['only one']), 'columns'),
            ('contents', lambda s: s['items'][0].pop('label'), 'label'),
            ('services', lambda s: s['items'][0].pop('text'), 'text'),
            ('services', lambda s: s.update(copy='Would otherwise disappear'), '不支持字段'),
            ('services', lambda s: s['items'][0].update(icon='Sparkles'), '不支持字段'),
            ('cover', lambda s: s.update(images=[self.image()]), '不支持字段'),
            ('services', lambda s: s.update(image=self.image()), '不支持字段'),
            ('portfolio', lambda s: s.update(captions=['Wrong parallel array']), '不支持字段'),
            ('portfolio', lambda s: s.update(images=[self.image()]), '2–6'),
            ('portfolio', lambda s: s.update(images=[self.image(i) for i in range(7)]), '2–6'),
            ('services', lambda s: s.update(images=[self.image(i) for i in range(4)]), '1–3'),
            ('services', lambda s: s.update(items=s['items'] * 2), '1–3'),
            ('process', lambda s: s.update(items=s['items'][:1]), '2–5'),
            ('process', lambda s: s.update(items=s['items'] * 2), '2–5'),
            ('intro', lambda s: s.update(copy='  '), '非空字符串'),
            ('cover', lambda s: s['image'].update(caption=4), 'caption'),
            ('cover', lambda s: s['image'].update(crop='ignored'), '不支持字段'),
            ('cover', lambda s: s.update(header='band'), 'header_template'),
            ('cover', lambda s: s.update(variant='mirror'), '不支持字段'),
            ('cover', lambda s: s.update(layout='cover'), 'editorial_variant 仅用于'),
        ]
        for variant, mutate, message in cases:
            with self.subTest(variant=variant, message=message):
                deck = self.deck([variant])
                mutate(deck['slides'][0])
                with self.assertRaisesRegex(ValueError, message):
                    self.load(deck)

    def test_duplicate_paths_are_rejected_after_normalization(self):
        for duplicate in ('images/0.png', 'images/./0.png', 'images/../images/0.png'):
            with self.subTest(duplicate=duplicate):
                deck = self.deck(['portfolio'])
                deck['slides'][0]['images'] = [self.image(), dict(self.image(), src=duplicate)]
                with self.assertRaisesRegex(ValueError, '重复同一 src'):
                    self.load(deck)
        # A real photo may still be reused intentionally on a different page.
        self.load(self.deck(['cover', 'closing']))

    def test_editorial_is_shared_and_ready_status_is_required(self):
        deck = self.deck(['cover'])
        legacy = dict(deck, style='scene-white')
        self.load(legacy)
        self.pack['editorial_variants'] = ['intro']
        self.save_pack()
        self.load(deck)
        inventory = discover_styles()['styles']
        self.assertTrue(all(style['editorial_variants'] == list(EDITORIAL_VARIANTS) for style in inventory))
        self.pack.update(editorial_variants=list(EDITORIAL_VARIANTS), status='draft')
        self.save_pack()
        self.assertTrue(any(p['id'] == 'editorial-test' for p in discover_styles(include_drafts=True)['styles']))
        with self.assertRaisesRegex(ValueError, 'draft'):
            self.load(deck)
        with self.assertRaisesRegex(ValueError, 'draft'):
            Builder(deck, self.root, draft=True)

    def test_invalid_manifest_capabilities_are_reported(self):
        for field, value in [('editorial_variants', ['cover', 'cover']), ('editorial_variants', ['unknown']),
                             ('editorial_variants', 'cover'), ('image_background', 'transparent'), ('image_background', None)]:
            with self.subTest(field=field, value=value):
                original = copy.deepcopy(self.pack)
                self.pack[field] = value
                self.save_pack()
                inventory = discover_styles(include_drafts=True)
                self.assertTrue(any(field in error for error in inventory['errors']), inventory)
                self.pack = original
                self.save_pack()

    def test_photography_prompts_keep_scene_background_and_legacy_keeps_paper(self):
        brief = {'subject': 'A real architect seated at a long timber table with pale stone samples and natural linen swatches.',
                 'action': 'The architect compares two material samples in soft window light.',
                 'structure': 'The table leads from the near foreground to a quiet plaster wall; a tall window lights one side.',
                 'details': 'Visible wood grain, stone pores, folded linen and anatomically correct hands form one calm photographic scene.'}
        deck = self.deck(['intro'])
        image = deck['slides'][0]['image']
        image.update(src='images/missing.png', brief=brief)
        manifest = self.prepare(deck)
        entry = manifest['images'][0]
        self.assertEqual(entry['ratio'], '21:9')
        self.assertEqual(entry['status'], 'missing')
        self.assertEqual(entry['image_background'], 'scene')
        self.assertIn('preserve the real setting', entry['prompt'])
        self.assertNotIn('Required background for BOTH', entry['prompt'])
        self.assertNotIn('exact flat page colour', entry['prompt'])
        self.assertNotIn('Inspect the actual output', entry['prompt'])
        data, root = self.load(deck)
        with self.assertRaisesRegex(ValueError, '缺少图片'):
            Builder(data, root, embed_format='keep').render()
        draft = Builder(data, root, draft=True, embed_format='keep').render()
        self.assertIn('待补配图', draft)
        self.assertEqual(ContentDocument(draft).images, [])
        legacy = {'version': 1, 'style': 'scene-white', 'title': 'Paper contract', 'slides': [
            {'layout': 'cover', 'title': '封面', 'image': copy.deepcopy(image)}]}
        legacy['slides'][0]['image'].pop('caption')
        legacy_entry = self.prepare(legacy)['images'][0]
        self.assertEqual(legacy_entry['image_background'], 'paper')
        self.assertIn('Required background for BOTH', legacy_entry['prompt'])
        self.assertIn('exact flat page colour', legacy_entry['prompt'])


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EditorialTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(run())
