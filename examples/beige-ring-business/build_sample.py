#!/usr/bin/env python3
"""Render a draft style specimen with production layout/media/editor components.

This local development harness does not register, promote or install the style.
Formal projects must use build_deck.py after the style direction is approved.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SHARED = REPO / 'skills/white-blue-slides'
PACK = REPO / 'skills/beige-ring-business-slides'
sys.path.insert(0, str(SHARED / 'scripts'))
from build_deck import Builder
from common import slide_images
from style_packs import _load, discover_styles


class SpecimenBuilder(Builder):
    def __init__(self, deck):
        self.deck, self.root = deck, PACK / 'assets'
        self.draft = self.dry_run = self.allow_restyle = False
        self.mode = deck['presentation_mode']
        path = PACK / 'assets/style.json'
        self.style_pack = _load(path, json.loads(path.read_text()), allow_draft=True)
        self.embed_format, self.embed_quality = 'keep', 88
        self.brand = json.loads((SHARED / 'assets/brand.json').read_text())
        self.icons = json.loads((SHARED / 'assets/icons.json').read_text())
        self.cache, self.missing, self.current_slide = {}, [], {}
        self.embed = {'format': 'keep', 'converted': 0, 'kept': 0, 'notes': []}
        self.design = {'pages': [{key: s[key] for key in ('layout_intent', 'layout_selection')} for s in deck['slides']]}
        self.logo = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['speech', 'reading'], default='speech')
    args = parser.parse_args()
    inventory = discover_styles(include_drafts=True)
    if inventory['errors']:
        raise ValueError(inventory['errors'])
    source = 'deck.example.json' if args.mode == 'speech' else 'deck.reading.example.json'
    deck = json.loads((PACK / 'assets' / source).read_text())
    html = SpecimenBuilder(deck).render()
    html = html.replace('<body ', '<body data-style-status="draft" data-style-sample="true" ', 1)
    filename = '米白环线商务-中文风格样稿.html' if args.mode == 'speech' else '米白环线商务-阅读型样稿.html'
    output = ROOT / filename
    output.write_text(html)
    images = [im for s in deck['slides'] for im in slide_images(s)]
    print(json.dumps({'output': str(output), 'pages': len(deck['slides']), 'style_status': 'draft',
                      'image_placements': len(images), 'unique_images': len({im['src'] for im in images}),
                      'bytes': output.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
