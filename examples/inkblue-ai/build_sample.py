from pathlib import Path
import base64
import re

root = Path(__file__).resolve().parent
def image_data(name):
    return 'data:image/webp;base64,' + base64.b64encode((root/'images'/f'{name}.webp').read_bytes()).decode()

photo = image_data('compute')
html = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>墨蓝雾灰 · AI协作工作台 · 风格样例</title>
<style>
:root{--paper:#F5F4F0;--ink:#20384B;--line:rgba(32,56,75,.35)}
*{box-sizing:border-box}body{margin:0;background:#E0E4E5;font-family:"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink)}
.toolbar{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;font-size:13px;gap:20px}.toolbar strong{font-weight:500}.controls{display:flex;gap:8px;align-items:center;white-space:nowrap}.toolbar strong{white-space:nowrap}@media(max-width:800px){.toolbar strong{display:none}.toolbar{justify-content:center;padding:0 8px}}button{font:inherit;color:inherit;background:transparent;border:1px solid var(--line);border-radius:30px;padding:8px 15px;cursor:pointer}button:hover{background:var(--ink);color:var(--paper)}
main{position:relative;margin:auto;width:1600px;height:900px;transform-origin:top left}.frame{position:relative;margin:0 auto}.slide{position:absolute;inset:0;background:var(--paper);overflow:hidden;display:none}.slide.active{display:block}
.meta{position:absolute;top:49px;left:62px;right:62px;display:flex;justify-content:space-between;align-items:start;font-size:20px;line-height:1.15;letter-spacing:-.3px}.meta .mid{position:absolute;left:50%;transform:translateX(-50%)}.meta .right{text-align:right}
h1,h2,h3,p{margin:0;font-weight:400}h1{font-size:172px;letter-spacing:-9px;line-height:1.04}h2{font-size:99px;letter-spacing:-5px;line-height:1.08}p{font-size:25px;line-height:1.7}
.cover h1{position:absolute;top:178px;left:60px;z-index:2;white-space:nowrap;font-weight:350}.cover .hero{position:absolute;left:0;top:371px;height:529px;width:1840px;object-fit:cover;object-position:0 58%}.cover .caption{position:absolute;right:65px;bottom:55px;width:335px;color:var(--paper);font-size:24px;line-height:1.55}.cover .caption small{display:block;margin-bottom:20px;font-size:16px;letter-spacing:1px}
.idea{background:var(--ink);color:var(--paper)}.idea .photo{position:absolute;right:0;top:145px;width:640px;height:755px;object-fit:cover;object-position:20% 50%}.idea h2{position:absolute;left:65px;top:205px;font-size:123px;line-height:1.18;letter-spacing:-5px}.idea .statement{position:absolute;top:568px;left:70px;width:760px;font-size:28px;line-height:1.75}.idea .tags{position:absolute;bottom:93px;left:70px;display:flex;gap:16px}.tags span{border:1px solid rgba(245,244,240,.7);padding:11px 29px;border-radius:40px;font-size:21px}.folio{position:absolute;left:66px;bottom:33px;font-size:17px;letter-spacing:.5px}
.plan h2{position:absolute;left:65px;top:173px;font-size:113px}.plan .intro{position:absolute;left:69px;top:435px;width:488px;font-size:25px;line-height:1.7}.plan .detail-photo{position:absolute;left:68px;bottom:75px;width:480px;height:260px;object-fit:cover;object-position:left center}.steps{position:absolute;top:191px;left:680px;right:66px}.step{border-top:1px solid var(--ink);padding:27px 0 31px;display:grid;grid-template-columns:70px 1fr;gap:15px;min-height:184px}.step .num{font-size:22px;padding-top:8px}.step h3{font-size:41px;letter-spacing:-1px;margin-bottom:14px}.step p{font-size:23px;line-height:1.6}.step .period{font-size:17px;float:right;padding-top:12px}.plan .bottom-note{position:absolute;left:680px;bottom:75px;font-size:16px}
[contenteditable=true]{outline:1px dashed currentColor;outline-offset:6px}body.overview .frame{width:min(1280px,95vw)!important;height:auto!important}body.overview main{transform:none!important;width:100%;height:auto;display:grid;gap:24px}body.overview .slide{display:block;position:relative;width:1600px;height:900px;transform-origin:top left}body.overview .slide-wrap{position:relative;overflow:hidden}
@media print{body{background:white}.toolbar{display:none}.frame,main{width:1600px!important;height:auto!important;transform:none!important}.slide{display:block;position:relative;width:1600px;height:900px;break-after:page} @page{size:1600px 900px;margin:0}}
</style></head><body>
<header class="toolbar"><strong>墨蓝雾灰 / 风格样例 01 <span style="opacity:.6;margin-left:16px">AI 概念提案 · 配色样例</span></strong><div class="controls"><button id="prev" aria-label="上一页">←</button><span id="count">1 / 3</span><button id="next" aria-label="下一页">→</button><button id="edit">编辑文字</button><button id="save">另存 HTML</button><button id="fullscreen">全屏</button></div></header>
<div class="frame"><main>
<section class="slide cover active" aria-label="封面">
<div class="meta"><span data-edit>知序<br>KNOWFLOW</span><span class="mid" data-edit>AI / WORK / KNOWLEDGE</span><span class="right" data-edit>企业 AI 协作工作台<br>Product Concept</span></div>
<h1 data-edit>让知识，进入工作。</h1><img class="hero" src="PHOTO" alt="墨蓝底上的银灰计算模块特写">
<div class="caption" data-edit><small>KNOWLEDGE INTO ACTION.</small>连接企业知识，<br>让每一次协作都有依据。</div>
</section>
<section class="slide idea" aria-label="产品理念">
<div class="meta"><span data-edit>知序 / KNOWFLOW</span><span class="mid" data-edit>The Working Principle</span><span class="right" data-edit>产品理念 / 02</span></div>
<img class="photo" src="{{BLOOM}}" alt="磨砂玻璃知识节点的连接装置"><h2 data-edit>知识不再分散，<br>协作有据可循。</h2>
<p class="statement" data-edit>让 AI 在授权资料中检索，帮助团队整理信息与草稿。<br>回答保留来源，重要结论经过人工复核，<br>把知识沉淀成可以持续改进的工作过程。</p>
<div class="tags"><span data-edit>来源可查</span><span data-edit>权限可控</span><span data-edit>人工复核</span></div><div class="folio" data-edit>PRODUCT DIRECTION — CONCEPT SAMPLE</div>
</section>
<section class="slide plan" aria-label="协作流程">
<div class="meta"><span data-edit>知序 / KNOWFLOW</span><span class="mid" data-edit>From Question to Action</span><span class="right" data-edit>协作流程 / 03</span></div>
<h2 data-edit>从提问，<br>走向协作。</h2><p class="intro" data-edit>连接资料、整理草稿、支持复核，<br>把常用动作放进同一个入口。</p><img class="detail-photo" src="PHOTO" alt="计算模块的金属与线路细节">
<div class="steps"><div class="step"><span class="num">01</span><div><span class="period" data-edit>检索 · RETRIEVE</span><h3 data-edit>先找到可靠依据</h3><p data-edit>围绕问题查找已授权的知识资料，<br>列出相关段落、来源与适用范围。</p></div></div><div class="step"><span class="num">02</span><div><span class="period" data-edit>整理 · DRAFT</span><h3 data-edit>再形成可用草稿</h3><p data-edit>将检索结果组织成摘要、对比或初稿，<br>显式标记资料缺口和需要确认的事项。</p></div></div><div class="step"><span class="num">03</span><div><span class="period" data-edit>复核 · REVIEW</span><h3 data-edit>由人完成判断</h3><p data-edit>业务人员核对事实与结论后再使用，<br>将反馈沉淀为后续优化的依据。</p></div></div></div>
<div class="bottom-note" data-edit>概念方案示例；功能、部署与效果需在实际项目中验证。</div><div class="folio">KNOWFLOW — 03</div>
</section>
</main></div>
<script>
const slides=[...document.querySelectorAll('.slide')];let index=0,editing=false;
function fit(){const scale=Math.min((innerWidth-40)/1600,(innerHeight-88)/900);document.querySelector('main').style.transform=`scale(${scale})`;const frame=document.querySelector('.frame');frame.style.width=1600*scale+'px';frame.style.height=900*scale+'px'}
function show(n){index=(n+slides.length)%slides.length;slides.forEach((s,i)=>s.classList.toggle('active',i===index));document.getElementById('count').textContent=`${index+1} / ${slides.length}`;location.hash=String(index+1)}
document.getElementById('prev').onclick=()=>show(index-1);document.getElementById('next').onclick=()=>show(index+1);
document.getElementById('edit').onclick=()=>{editing=!editing;document.querySelectorAll('[data-edit]').forEach(e=>e.contentEditable=editing);document.getElementById('edit').textContent=editing?'完成编辑':'编辑文字'};
document.getElementById('save').onclick=()=>{const copy=document.documentElement.cloneNode(true);copy.querySelectorAll('[contenteditable]').forEach(e=>e.removeAttribute('contenteditable'));copy.querySelector('#edit').textContent='编辑文字';const blob=new Blob(['<!doctype html>\n'+copy.outerHTML],{type:'text/html;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='墨蓝雾灰-AI协作工作台.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
document.addEventListener('keydown',e=>{if(editing)return;if(e.key==='ArrowRight'||e.key==='PageDown')show(index+1);if(e.key==='ArrowLeft'||e.key==='PageUp')show(index-1)});addEventListener('resize',fit);show(Math.max(0,Math.min(2,(parseInt(location.hash.slice(1))||1)-1)));fit();
</script></body></html>'''
html = html.replace('</style>', (root/'layouts.css').read_text() + '\n</style>', 1)
html = html.replace('</main>', (root/'layouts.html').read_text() + '\n</main>', 1)
html = html.replace('风格样例 01', '全版式样例')
html = html.replace('<span style="opacity:.6;margin-left:16px">', '<span class="description" style="opacity:.6;margin-left:16px">')
html = html.replace('<button id="edit">', '<select id="jump" aria-label="选择版式"></select><button id="overview">总览</button><button id="edit">', 1)
dialog = '<dialog id="overview-dialog" aria-label="全部版式"><div class="overview-head"><strong>墨蓝雾灰 · 14 种页面表达</strong><button id="close-overview">关闭总览</button></div><div class="overview-grid"></div></dialog>'
html = re.sub(r'<script>.*?</script>', lambda _: dialog + '<script>\n' + (root/'player.js').read_text() + '\n</script>', html, flags=re.S)
html = html.replace('PHOTO', photo).replace('{{BLOOM}}', image_data('knowledge')).replace('{{ORCHID}}', image_data('servers'))
(root/'墨蓝雾灰-AI协作工作台.html').write_text(html,encoding='utf-8')
print(root/'墨蓝雾灰-AI协作工作台.html')
