#!/usr/bin/env python3
"""Render the draft style specimen with shared offline player/export controls.

This finite warm-editorial-sample/v1 renderer is separate from production deck.json.
It does not change the style's draft status or install the package.
"""
import base64
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SHARED = REPO / 'skills' / 'white-blue-slides'
PACK = REPO / 'skills' / 'warm-minimal-editorial-slides'
sys.path.insert(0, str(SHARED / 'scripts'))
from common import read_raster
from style_packs import discover_styles


def text(tag, value, cls=''):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'Nonempty {tag} content required')
    return f'<{tag} data-edit class="{cls}">' + escape(value).replace('\n', '<br>') + f'</{tag}>'


def photo(key, caption=None):
    if key not in {'courtyard', 'living', 'materials', 'detail', 'studio'}:
        raise ValueError(f'Unknown photo: {key}')
    mime, raw = read_raster(ROOT / 'images' / f'{key}.webp')
    alt = {'courtyard':'斜阳下的建筑天井','living':'自然光中的暖色客厅','materials':'石材、亚麻与陶器的材质静物','detail':'木椅与窗帘的空间细节','studio':'设计师手中的材质选择'}[key]
    return '<figure>' + (text('figcaption', caption) if caption else '') + f'<img alt="{alt}，原创生成意象" src="data:{mime};base64,' + base64.b64encode(raw).decode() + '"></figure>'


def content(s):
    layout = s['layout']
    title = text('h1', s['title'], 'wm-serif' if layout in ('cover', 'closing') else '')
    if layout == 'cover':
        return photo(s['image']) + title + text('p',s['kicker'],'wm-kicker') + text('p',s['subtitle'],'wm-subtitle')
    if layout == 'intro':
        return title + text('p',s['copy'],'wm-copy') + photo(s['image'])
    if layout == 'contents':
        rows = ''.join('<div class="wm-index-row">'+text('span',name)+text('span',num)+'</div>' for name,num in s['items'])
        return title + photo(s['image']) + '<aside>'+rows+'</aside>' + text('p',s['copy'],'wm-copy')
    if layout == 'about':
        return title + photo(s['image']) + text('p',s['lead'],'wm-lead wm-serif') + '<div class="wm-columns">' + ''.join(text('p',t) for t in s['columns']) + '</div>'
    if layout == 'services':
        items = ''.join('<article>'+text('h2',name)+text('p',copy)+'</article>' for name,copy in s['items'])
        return title + '<div class="wm-services-list">'+items+'</div><div class="wm-strip">'+''.join(photo(p) for p in s['images'])+'</div>'
    if layout == 'process':
        items = ''.join('<article>'+text('span',f'{i:02}','wm-step-index')+text('h2',name)+text('p',copy)+'</article>' for i,(name,copy) in enumerate(s['items'],1))
        return photo(s['image']) + title + '<div class="wm-steps">'+items+'</div>'
    if layout == 'reading':
        items = ''.join('<article>'+text('h2',name)+text('p',copy)+'</article>' for name,copy in s['items'])
        return title + text('p',s['subtitle'],'wm-subtitle') + photo(s['image']) + '<div class="wm-reading-grid">'+items+'</div>'
    if layout == 'portfolio':
        if len(s['images']) != len(s['captions']):
            raise ValueError('Gallery captions must match images')
        return title + text('p',s['copy'],'wm-copy') + '<div class="wm-gallery">'+''.join(photo(p,c) for p,c in zip(s['images'],s['captions']))+'</div>'
    if layout == 'closing':
        return photo(s['image']) + title + text('p',s['subtitle'],'wm-subtitle') + text('p',s['copy'],'wm-copy')
    raise ValueError(f'Unknown sample layout: {layout}')


def main():
    deck = json.loads((ROOT/'deck.sample.json').read_text())
    if deck.get('schema') != 'warm-editorial-sample/v1' or deck.get('style') != 'warm-minimal-editorial':
        raise ValueError('Only the warm editorial specimen schema is supported')
    result = discover_styles(include_drafts=True)
    pack = [s for s in result['styles'] if s['id'] == deck['style']]
    if len(pack) != 1 or result['errors']:
        raise ValueError(result)
    slides=[]
    for i,s in enumerate(deck['slides'],1):
        if s['surface'] not in ('light','dark') or s['mode'] not in ('speech','reading'):
            raise ValueError('Invalid surface or specimen density')
        header='<header>'+text('span',deck['wordmark'])+text('span',deck['date'])+'</header>'
        footer='<footer>'+text('span',s['note'])+text('span',f'{i:02} / {len(deck["slides"]):02}')+'</footer>'
        notes='风格开发样张；示例品牌与文案不代表真实项目。配图均为原创生成意象。版式：'+s['label']+'；用途密度：'+s['mode']+'。'
        slides.append(f'<section id="{s["id"]}" class="slide wm-page wm-{s["layout"]}'+(' active' if i==1 else '')+f'" data-surface="{s["surface"]}" data-sample-mode="{s["mode"]}" data-speaker-notes="{escape(notes,quote=True)}" aria-label="{s["label"]}">'+header+'<main>'+content(s)+'</main>'+footer+'</section>')
    assets=SHARED/'assets'
    css='\n'.join(p.read_text() for p in [assets/'theme.css',assets/'reading.css',PACK/'assets/theme.css',ROOT/'layouts.css'])
    js='\n'.join((assets/p).read_text() for p in ['vendor/echarts.min.js','charts.js','pptx-export.js','player.js'])
    license_text='\n'.join((assets/'vendor'/p).read_text() for p in ['ECHARTS-LICENSE.txt','ECHARTS-NOTICE.txt'])
    context={'TITLE':escape(deck['title']),'CSS':css,'JS':js,'SLIDES':'\n'.join(slides),'COUNT':str(len(slides)),'BODY_ATTR':' data-style="warm-minimal-editorial" data-style-status="draft" data-presentation-mode="speech" data-style-sample="true"','LOGO_DEFS':'','LICENSE':'<!--\n'+license_text.replace('--','- -')+'\n-->'}
    html=(assets/'template.html').read_text()
    for key,value in context.items():
        html=html.replace('{{'+key+'}}',value)
    out=ROOT/'暖褐极简编辑式-中文风格样稿.html'
    out.write_text(html)
    print(json.dumps({'output':str(out),'pages':len(slides),'style_status':pack[0]['status'],'bytes':out.stat().st_size},ensure_ascii=False))


if __name__=='__main__':
    main()
