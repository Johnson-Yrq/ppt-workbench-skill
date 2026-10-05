from pathlib import Path
import base64
import re

root = Path(__file__).resolve().parent
def image_data(name):
    return 'data:image/webp;base64,' + base64.b64encode((root/'images'/f'{name}.webp').read_bytes()).decode()

photo = image_data('gerbera')
html = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>朱红柔焦 · 花间品牌提案 · 风格样例</title>
<style>
:root{--paper:#F6F3EE;--red:#8C1718;--line:rgba(140,23,24,.35)}
*{box-sizing:border-box}body{margin:0;background:#e5e0da;font-family:"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;color:var(--red)}
.toolbar{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;font-size:13px;gap:20px}.toolbar strong{font-weight:500}.controls{display:flex;gap:8px;align-items:center;white-space:nowrap}.toolbar strong{white-space:nowrap}@media(max-width:800px){.toolbar strong{display:none}.toolbar{justify-content:center;padding:0 8px}}button{font:inherit;color:inherit;background:transparent;border:1px solid var(--line);border-radius:30px;padding:8px 15px;cursor:pointer}button:hover{background:var(--red);color:var(--paper)}
main{position:relative;margin:auto;width:1600px;height:900px;transform-origin:top left}.frame{position:relative;margin:0 auto}.slide{position:absolute;inset:0;background:var(--paper);overflow:hidden;display:none}.slide.active{display:block}
.meta{position:absolute;top:49px;left:62px;right:62px;display:flex;justify-content:space-between;align-items:start;font-size:20px;line-height:1.15;letter-spacing:-.3px}.meta .mid{position:absolute;left:50%;transform:translateX(-50%)}.meta .right{text-align:right}
h1,h2,h3,p{margin:0;font-weight:400}h1{font-size:172px;letter-spacing:-9px;line-height:1.04}h2{font-size:99px;letter-spacing:-5px;line-height:1.08}p{font-size:25px;line-height:1.7}
.cover h1{position:absolute;top:178px;left:60px;z-index:2;white-space:nowrap;font-weight:350}.cover .hero{position:absolute;left:0;top:371px;height:529px;width:1840px;object-fit:cover;object-position:0 58%}.cover .caption{position:absolute;right:65px;bottom:55px;width:335px;color:var(--paper);font-size:24px;line-height:1.55}.cover .caption small{display:block;margin-bottom:20px;font-size:16px;letter-spacing:1px}
.idea{background:var(--red);color:var(--paper)}.idea .photo{position:absolute;right:0;top:145px;width:640px;height:755px;object-fit:cover;object-position:20% 50%}.idea h2{position:absolute;left:65px;top:205px;font-size:123px;line-height:1.18;letter-spacing:-5px}.idea .statement{position:absolute;top:568px;left:70px;width:760px;font-size:28px;line-height:1.75}.idea .tags{position:absolute;bottom:93px;left:70px;display:flex;gap:16px}.tags span{border:1px solid rgba(246,243,238,.7);padding:11px 29px;border-radius:40px;font-size:21px}.folio{position:absolute;left:66px;bottom:33px;font-size:17px;letter-spacing:.5px}
.plan h2{position:absolute;left:65px;top:173px;font-size:113px}.plan .intro{position:absolute;left:69px;top:435px;width:488px;font-size:25px;line-height:1.7}.plan .detail-photo{position:absolute;left:68px;bottom:75px;width:480px;height:260px;object-fit:cover;object-position:left center}.steps{position:absolute;top:191px;left:680px;right:66px}.step{border-top:1px solid var(--red);padding:27px 0 31px;display:grid;grid-template-columns:70px 1fr;gap:15px;min-height:184px}.step .num{font-size:22px;padding-top:8px}.step h3{font-size:41px;letter-spacing:-1px;margin-bottom:14px}.step p{font-size:23px;line-height:1.6}.step .period{font-size:17px;float:right;padding-top:12px}.plan .bottom-note{position:absolute;left:680px;bottom:75px;font-size:16px}
[contenteditable=true]{outline:1px dashed currentColor;outline-offset:6px}body.overview .frame{width:min(1280px,95vw)!important;height:auto!important}body.overview main{transform:none!important;width:100%;height:auto;display:grid;gap:24px}body.overview .slide{display:block;position:relative;width:1600px;height:900px;transform-origin:top left}body.overview .slide-wrap{position:relative;overflow:hidden}
@media print{body{background:white}.toolbar{display:none}.frame,main{width:1600px!important;height:auto!important;transform:none!important}.slide{display:block;position:relative;width:1600px;height:900px;break-after:page} @page{size:1600px 900px;margin:0}}
</style></head><body>
<header class="toolbar"><strong>朱红柔焦 / 风格样例 01 <span style="opacity:.6;margin-left:16px">虚构品牌 · 待确认方向</span></strong><div class="controls"><button id="prev" aria-label="上一页">←</button><span id="count">1 / 3</span><button id="next" aria-label="下一页">→</button><button id="edit">编辑文字</button><button id="save">另存 HTML</button><button id="fullscreen">全屏</button></div></header>
<div class="frame"><main>
<section class="slide cover active" aria-label="封面">
<div class="meta"><span data-edit>花间<br>HUĀ JIĀN</span><span class="mid" data-edit>Spring / 2027</span><span class="right" data-edit>品牌焕新<br>Creative Proposal</span></div>
<h1 data-edit>让日常，自然盛放。</h1><img class="hero" src="PHOTO" alt="暗红背景上的柔焦白色非洲菊">
<div class="caption" data-edit><small>A LITTLE BLOOM, EVERY DAY.</small>把一束花的仪式感，<br>放回每一个平凡的日子。</div>
</section>
<section class="slide idea" aria-label="品牌理念">
<div class="meta"><span data-edit>花间 / HUĀ JIĀN</span><span class="mid" data-edit>The Idea</span><span class="right" data-edit>品牌理念 / 02</span></div>
<img class="photo" src="PHOTO" alt="花瓣的近距离柔焦摄影"><h2 data-edit>花不只属于<br>特别的日子。</h2>
<p class="statement" data-edit>我们想让鲜花从节日里的礼物，变成生活中的陪伴。<br>用轻盈的选择、自然的搭配与持续的灵感，<br>让人们愿意为自己，留下一点盛放的空间。</p>
<div class="tags"><span data-edit>自然表达</span><span data-edit>日常陪伴</span><span data-edit>轻盈仪式</span></div><div class="folio" data-edit>BRAND DIRECTION — CONCEPT SAMPLE</div>
</section>
<section class="slide plan" aria-label="传播计划">
<div class="meta"><span data-edit>花间 / HUĀ JIĀN</span><span class="mid" data-edit>From Idea to Everyday</span><span class="right" data-edit>传播计划 / 03</span></div>
<h2 data-edit>把心意，<br>带进日常。</h2><p class="intro" data-edit>从一次看见，到一次亲手挑选，<br>再到值得被分享的生活片段。</p><img class="detail-photo" src="PHOTO" alt="白色花朵的颗粒质感局部">
<div class="steps"><div class="step"><span class="num">01</span><div><span class="period" data-edit>看见 · DISCOVER</span><h3 data-edit>先让人停留</h3><p data-edit>以花瓣、光线和真实生活片段建立视觉记忆，<br>让每一张画面都讲述一个简单的心意。</p></div></div><div class="step"><span class="num">02</span><div><span class="period" data-edit>体验 · EXPERIENCE</span><h3 data-edit>再给出一个理由</h3><p data-edit>围绕餐桌、窗边与下班后的片刻，<br>提供容易开始的鲜花搭配与养护灵感。</p></div></div><div class="step"><span class="num">03</span><div><span class="period" data-edit>分享 · SHARE</span><h3 data-edit>让故事继续生长</h3><p data-edit>邀请人们记录自己的日常花事，<br>把一次购买延伸为持续的生活表达。</p></div></div></div>
<div class="bottom-note" data-edit>示例内容用于验证排版与风格，不代表真实品牌计划。</div><div class="folio">HUĀ JIĀN — 03</div>
</section>
</main></div>
<script>
const slides=[...document.querySelectorAll('.slide')];let index=0,editing=false;
function fit(){const scale=Math.min((innerWidth-40)/1600,(innerHeight-88)/900);document.querySelector('main').style.transform=`scale(${scale})`;const frame=document.querySelector('.frame');frame.style.width=1600*scale+'px';frame.style.height=900*scale+'px'}
function show(n){index=(n+slides.length)%slides.length;slides.forEach((s,i)=>s.classList.toggle('active',i===index));document.getElementById('count').textContent=`${index+1} / ${slides.length}`;location.hash=String(index+1)}
document.getElementById('prev').onclick=()=>show(index-1);document.getElementById('next').onclick=()=>show(index+1);
document.getElementById('edit').onclick=()=>{editing=!editing;document.querySelectorAll('[data-edit]').forEach(e=>e.contentEditable=editing);document.getElementById('edit').textContent=editing?'完成编辑':'编辑文字'};
document.getElementById('save').onclick=()=>{const copy=document.documentElement.cloneNode(true);copy.querySelectorAll('[contenteditable]').forEach(e=>e.removeAttribute('contenteditable'));copy.querySelector('#edit').textContent='编辑文字';const blob=new Blob(['<!doctype html>\n'+copy.outerHTML],{type:'text/html;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='朱红柔焦-花间品牌提案.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
document.addEventListener('keydown',e=>{if(editing)return;if(e.key==='ArrowRight'||e.key==='PageDown')show(index+1);if(e.key==='ArrowLeft'||e.key==='PageUp')show(index-1)});addEventListener('resize',fit);show(Math.max(0,Math.min(2,(parseInt(location.hash.slice(1))||1)-1)));fit();
</script></body></html>'''
html = html.replace('</style>', (root/'layouts.css').read_text() + '\n</style>', 1)
html = html.replace('</main>', (root/'layouts.html').read_text() + '\n</main>', 1)
html = html.replace('风格样例 01', '全版式样例')
html = html.replace('<span style="opacity:.6;margin-left:16px">', '<span class="description" style="opacity:.6;margin-left:16px">')
html = html.replace('<button id="edit">', '<select id="jump" aria-label="选择版式"></select><button id="overview">总览</button><button id="edit">', 1)
dialog = '<dialog id="overview-dialog" aria-label="全部版式"><div class="overview-head"><strong>朱红柔焦 · 14 种页面表达</strong><button id="close-overview">关闭总览</button></div><div class="overview-grid"></div></dialog>'
html = re.sub(r'<script>.*?</script>', lambda _: dialog + '<script>\n' + (root/'player.js').read_text() + '\n</script>', html, flags=re.S)
html = html.replace('PHOTO', photo).replace('{{BLOOM}}', image_data('bloom')).replace('{{ORCHID}}', image_data('orchid'))
(root/'朱红柔焦-花间品牌提案.html').write_text(html,encoding='utf-8')
print(root/'朱红柔焦-花间品牌提案.html')
