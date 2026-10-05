#!/usr/bin/env python3
"""Build a development specimen using the shared compositions, without promoting
or installing a draft style. This is not a production build_deck entry point.
"""
import base64
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SHARED = REPO / 'skills/white-blue-slides'
PACK = REPO / 'skills/primary-architecture-slides'
sys.path.insert(0, str(SHARED / 'scripts'))
from build_deck import Builder
from common import read_raster
from composition_layouts import render_composition, validate_composition, composition_images
from style_packs import discover_styles


class SpecimenMedia:
    """Use the production image component; only package orchestration is local."""
    image = Builder.image

    def __init__(self):
        self.root = PACK / 'assets'
        self.dry_run = self.draft = False
        self.cache = {}

    def data_uri(self, path, **_):
        if path not in self.cache:
            mime, raw = read_raster(path)
            self.cache[path] = f'data:{mime};base64,' + base64.b64encode(raw).decode()
        return self.cache[path]


def main():
    deck = json.loads((PACK / 'assets/deck.example.json').read_text())
    manifest = json.loads((PACK / 'assets/style.json').read_text())
    inventory = discover_styles(include_drafts=True)
    if inventory['errors'] or not any(p['id'] == deck['style'] for p in inventory['styles']):
        raise ValueError(inventory)
    media = SpecimenMedia()
    slides, images = [], []
    for i, source in enumerate(deck['slides'], 1):
        slide = dict(source, _number=i)
        validate_composition(slide)
        images.extend(composition_images(slide))
        surface = slide.get('surface', 'light')
        if surface not in manifest['surfaces']:
            raise ValueError('Unknown surface: ' + surface)
        title_chars = max(sum(1 if ord(c) > 0x2E7F else .55 for c in ln) for ln in slide['title'].split('\n'))
        attrs = f' data-surface="{surface}" style="--title-chars:{title_chars}"'
        attrs += f' data-speaker-notes="{escape(slide["notes"], quote=True)}"'
        slides.append(f'<section id="{slide["id"]}" class="slide layout-{slide["layout"]}'
                      + (' active' if i == 1 else '') + f'"{attrs} aria-label="第 {i} 页"'
                      + f' aria-hidden="{"false" if i == 1 else "true"}"><main>'
                      + render_composition(media, slide) + '</main></section>')
    assets = SHARED / 'assets'
    css = '\n'.join(p.read_text() for p in [assets/'theme.css', assets/'compositions.css', PACK/'assets/theme.css'])
    js = '\n'.join((assets/p).read_text() for p in ['vendor/echarts.min.js', 'charts.js', 'pptx-export.js', 'player.js'])
    license_text = '\n'.join((assets/'vendor'/p).read_text() for p in ['ECHARTS-LICENSE.txt', 'ECHARTS-NOTICE.txt'])
    values = {'TITLE': escape(deck['title']), 'CSS': css, 'JS': js,
              'SLIDES': '\n'.join(slides), 'COUNT': str(len(slides)), 'LOGO_DEFS': '',
              'BODY_ATTR': ' data-style="primary-architecture" data-style-status="draft" data-style-sample="true" data-presentation-mode="speech"',
              'LICENSE': '<!--\n' + license_text.replace('--', '- -') + '\n-->'}
    html = (assets/'template.html').read_text()
    for key, value in values.items():
        html = html.replace('{{' + key + '}}', value)
    out = ROOT / '原色建筑编辑式-中文风格样稿.html'
    out.write_text(html)
    print(json.dumps({'output': str(out), 'pages': len(slides), 'image_placements': len(images),
                      'unique_images': len({im['src'] for im in images}), 'style_status': manifest['status'],
                      'bytes': out.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
