#!/usr/bin/env python3
"""Build a finite, reviewable style specimen, without registering a draft as ready.

This renderer reads editorial-style-sample/v1, not the production deck schema.
The layout prototypes are evaluated visually before shared-schema integration.
Player, charts, editable chart markup and PPTX conversion come from the shared kit.
"""
from pathlib import Path
from html import escape
import base64
import json
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SHARED = REPO / 'skills' / 'white-blue-slides'
PACK = REPO / 'skills' / 'monochrome-editorial-slides'
sys.path.insert(0, str(SHARED / 'scripts'))
from build_deck import Builder
from common import local_path, read_raster
from style_packs import discover_styles


def e(tag, value, cls=''):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{tag} needs nonempty text')
    text = escape(value, quote=True).replace('\n', '<br>')
    return f'<{tag} data-edit' + (f' class="{cls}"' if cls else '') + f'>{text}</{tag}>'


def photo(image):
    path = local_path(ROOT, image['src'])
    mime, raw = read_raster(path)
    uri = f'data:{mime};base64,' + base64.b64encode(raw).decode('ascii')
    return '<img src="' + uri + '" alt="' + escape(image['alt'], quote=True) + '">'


def cover(s):
    band = '<div class="ed-cover-band">' + photo(s['image']) + '</div>' if s.get('image') else '<div class="ed-rule" aria-hidden="true"></div>'
    return e('p', s['eyebrow'], 'ed-eyebrow') + e('h1', s['title']) + '<div class="ed-cover-summary">' + e('small', s['summary_label']) + e('p', s['summary']) + '</div>' + band + e('p', s['byline'], 'ed-cover-byline') + e('p', s['context'], 'ed-cover-context')


def problems(s):
    assert len(s['items']) == 3
    content = '<div class="ed-problem-grid">'
    for item in s['items']:
        content += '<section class="ed-problem">' + e('h2', item['title']) + e('p', item['text']) + '<span class="ed-problem-link" aria-hidden="true"></span></section>'
    return content + '</div>' + e('h1', s['title'])


def introduction(s):
    text = '<div class="ed-photo-text">'
    for item in s['items']:
        text += '<section>' + e('h2', item['title']) + e('p', item['text']) + '</section>'
    return e('p', s['eyebrow'], 'ed-eyebrow') + e('h1', s['title']) + '<div class="ed-photo-frame">' + photo(s['image']) + '</div><div class="ed-photo-caption">' + e('span', s['caption']) + '<span aria-hidden="true">↗</span></div>' + text + '</div>'


def services(s):
    assert len(s['items']) == 3
    content = e('h1', s['title'])
    for index, (name, item) in enumerate(zip(('one', 'two', 'three'), s['items']), 1):
        content += f'<section class="ed-service ed-service-{name}" data-component="panel">' + e('span', f'{index:02}', 'ed-service-index')
        if item.get('image'):
            content += '<div class="ed-service-photo">' + photo(item['image']) + '</div>'
        elif index == 1:
            content += '<span class="ed-large-arrow" aria-hidden="true">↗</span>'
        content += e('h2', item['title']) + e('p', item['text']) + '</section>'
    return content + e('p', s['aside'], 'ed-service-aside')


def metrics(s):
    content = e('h1', s['title']) + e('p', s['description'], 'ed-metric-description') + e('p', s['note'], 'ed-metric-note')
    for size, key in [('large', 'primary'), ('small', 'secondary')]:
        metric = s[key]
        content += f'<div class="ed-orb ed-orb-{size}" data-component="metric">' + e('p', metric['value'], 'ed-orb-number') + e('p', metric['label'], 'ed-orb-label')
        if metric.get('detail'):
            content += e('p', metric['detail'], 'ed-orb-detail')
        content += '</div>'
    if s.get('image'):
        content += '<div class="ed-orb ed-orb-photo">' + photo(s['image']) + '</div>'
    return content


def divider(s):
    return '<div class="ed-divider-photo">' + photo(s['image']) + '</div>' + e('p', s['eyebrow'], 'ed-eyebrow') + e('h1', s['title']) + e('p', s['text'], 'ed-divider-text')


def closing(s):
    return e('h1', s['title']) + e('p', s['subtitle'], 'ed-closing-subtitle') + '<div class="ed-closing-photo">' + photo(s['image']) + '</div><div class="ed-rule" aria-hidden="true"></div>' + e('p', s['message'], 'ed-closing-message') + e('p', s['byline'], 'ed-closing-byline')


def growth(s):
    # The shared chart method only uses its input block; no Builder/style is instantiated.
    chart = Builder.chart(None, s['chart'])
    return e('h1', s['title']) + e('p', s['description'], 'ed-growth-copy') + '<div class="ed-growth-stat">' + e('strong', s['stat']) + e('span', s['stat_label']) + '</div><div class="ed-chart-region"><div class="ed-chart-top">' + e('h2', s['chart_label']) + e('span', s['chart_unit']) + '</div>' + chart + e('p', s['conclusion'], 'ed-chart-bottom') + '</div>'


def main():
    deck = json.loads((ROOT / 'deck.sample.json').read_text())
    if deck.get('schema') != 'editorial-style-sample/v1' or deck.get('style') != 'monochrome-editorial':
        raise ValueError('This script only builds the monochrome editorial review sample')
    discovery = discover_styles(include_drafts=True)
    matches = [x for x in discovery['styles'] if x['id'] == deck['style']]
    if len(matches) != 1 or discovery['errors']:
        raise ValueError(discovery)
    functions = {'cover': cover, 'problems': problems, 'photo': introduction, 'services': services, 'metrics': metrics, 'growth': growth, 'divider': divider, 'closing': closing}
    slides = []
    for index, s in enumerate(deck['slides'], 1):
        if s['surface'] not in ('light', 'dark') or s['layout'] not in functions:
            raise ValueError('Invalid sample surface/layout')
        header = '<header><div class="ed-header-left">' + e('span', deck['wordmark'], 'ed-wordmark') + e('span', s['section'], 'ed-pill') + '</div><div class="ed-header-right">' + e('span', deck['date'], 'ed-pill') + '<span class="ed-arrow" aria-hidden="true">↗</span></div></header>'
        footer = '<footer>' + e('span', s['footer']) + e('span', f'{index:02d} / {len(deck["slides"]):02d}') + '</footer>'
        slides.append(f'<section id="{escape(s["id"], quote=True)}" class="slide editorial-page ed-{s["layout"]}' + (' active' if index == 1 else '') + f'" data-surface="{s["surface"]}" data-speaker-notes="{escape(s["notes"], quote=True)}" aria-label="{escape(s["section"], quote=True)}">' + header + '<main>' + functions[s['layout']](s) + '</main>' + footer + '</section>')
    assets = SHARED / 'assets'
    css = '\n'.join((path.read_text() for path in [assets / 'theme.css', assets / 'reading.css', PACK / 'assets/theme.css']))
    js = '\n'.join((path.read_text() for path in [assets / 'vendor/echarts.min.js', assets / 'charts.js', assets / 'pptx-export.js', assets / 'player.js']))
    license_text = '\n'.join((assets / 'vendor' / p).read_text() for p in ('ECHARTS-LICENSE.txt', 'ECHARTS-NOTICE.txt'))
    context = {'TITLE': escape(deck['title']), 'CSS': css, 'JS': js, 'SLIDES': '\n'.join(slides), 'COUNT': str(len(slides)), 'BODY_ATTR': ' data-style="monochrome-editorial" data-style-status="draft" data-presentation-mode="speech" data-style-sample="true"', 'LOGO_DEFS': '', 'LICENSE': '<!--\n' + license_text.replace('--', '- -') + '\n-->'}
    html = (assets / 'template.html').read_text()
    for key, value in context.items():
        html = html.replace('{{' + key + '}}', value)
    out = ROOT / '黑白编辑式-中文风格样稿.html'
    out.write_text(html)
    print(json.dumps({'output': str(out), 'pages': len(slides), 'style_status': matches[0]['status'], 'bytes': out.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
