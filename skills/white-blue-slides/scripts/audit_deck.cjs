#!/usr/bin/env node
/* Inspect a generated local deck in an isolated browser: per-page content checks and screenshots.
 * Player behaviour (navigation, edit, save, export, fullscreen, print) is the same in every deck and is
 * covered by test_player.cjs when the player or theme changes. */
'use strict';
const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');

async function run() {
  const args = process.argv.slice(2), filename = args.shift();
  let out, channel;
  while (args.length) {
    const flag = args.shift();
    if (flag === '--out') out = args.shift();
    else if (flag === '--browser') channel = args.shift();
    else throw new Error(`未知参数：${flag}`);
  }
  if (!filename || !out) throw new Error('用法：node audit_deck.cjs 演示稿.html --out qa [--browser chrome]');
  let chromium;
  try { ({chromium} = require('playwright')); }
  catch { throw new Error('找不到 Playwright。请使用当前环境已有的 Node.js + Playwright，或按用户授权准备依赖。'); }
  out = path.resolve(out); fs.mkdirSync(out, {recursive: true});
  const report = {file: path.resolve(filename), pages: [], errors: [], screenshots: [], externalRequests: []};
  const browser = await chromium.launch({headless: true, ...(channel ? {channel} : {})});
  try {
    const context = await browser.newContext({viewport: {width: 1944, height: 1172}, deviceScaleFactor: 1});
    await context.route(/^https?:\/\//i, route => {report.externalRequests.push(route.request().url()); return route.abort();});
    const page = await context.newPage();
    page.on('pageerror', e => report.errors.push(e.message));
    await page.goto(pathToFileURL(path.resolve(filename)).href, {waitUntil: 'load'});
    await page.evaluate(async () => {await document.fonts.ready; await Promise.all([...document.images].map(im => im.decode().catch(() => {})));});
    const count = await page.locator('.slide').count();
    if (!count) throw new Error('没有找到演示页面');
    report.count = count;
    report.style = await page.evaluate(() => document.body.dataset.style || 'scene-white');
    report.presentation_mode = await page.evaluate(() => document.body.dataset.presentationMode || 'speech');
    report.selfContained = await page.evaluate(() => ({
      externalElements: [...document.querySelectorAll('img[src],script[src],link[href],iframe[src],audio[src],video[src],source[src],image[href]')]
        .filter(el => !/^(data:|#)/.test(el.getAttribute('src') || el.getAttribute('href') || '')).map(el => el.tagName),
      cssImports: /@import\b/i.test([...document.querySelectorAll('style')].map(s => s.textContent).join('\n')),
      draft: document.body.classList.contains('draft') || !!document.querySelector('.missing-image')
    }));
    for (let i = 0; i < count; i++) {
      await page.evaluate(n => window.deckAPI.show(n), i);
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const checks = await page.evaluate(() => {
        const s = document.querySelector('.slide.active'), sr = s.getBoundingClientRect(), footer = s.querySelector('footer').getBoundingClientRect();
        const issues = [], warnings = [], rect = el => {const r = el.getBoundingClientRect(); return {x:r.x-sr.x,y:r.y-sr.y,w:r.width,h:r.height,right:r.right-sr.x,bottom:r.bottom-sr.y};};
        const readingMode = document.body.dataset.presentationMode === 'reading';
        const label = el => el.textContent.trim().slice(0,70);
        const visible = el => {
          const r = el.getBoundingClientRect();
          if (r.width<1||r.height<1) return false;
          for (let p=el;p&&p!==s.parentElement;p=p.parentElement){const cs=getComputedStyle(p);if(cs.display==='none'||cs.visibility==='hidden'||Number(cs.opacity)===0)return false;}
          return true;
        };
        // Visible clip of an image inside its overflow-clipping ancestors (stopping at `stop`).
        const clipped = (img, stop) => {
          const b = img.getBoundingClientRect(), r = {left:b.left,right:b.right,top:b.top,bottom:b.bottom};
          for (let p=img.parentElement;p&&p!==stop;p=p.parentElement){const cs=getComputedStyle(p),c=p.getBoundingClientRect();
            if(/hidden|clip|scroll|auto/.test(cs.overflowX)){r.left=Math.max(r.left,c.left);r.right=Math.min(r.right,c.right);}
            if(/hidden|clip|scroll|auto/.test(cs.overflowY)){r.top=Math.max(r.top,c.top);r.bottom=Math.min(r.bottom,c.bottom);}}
          return r;
        };

        // Text: bounds, footer collision, overflow, overlap, minimum reading size.
        const textEls = [...s.querySelectorAll('[data-edit],.page-number')].filter(el => el.textContent.trim() && el.getBoundingClientRect().width > 0);
        for (const el of textEls) {
          const r = rect(el);
          if (r.x < -1 || r.y < -1 || r.right > sr.width+1 || r.bottom > sr.height+1) issues.push({type:'out-of-bounds',text:label(el),rect:r});
          if (el.closest('main') && r.bottom > footer.top-sr.top-8) issues.push({type:'footer-collision',text:label(el),bottom:r.bottom});
          const cs=getComputedStyle(el), clippedY=['hidden','clip','auto','scroll'].includes(cs.overflowY);
          if(readingMode&&el.closest('main')&&parseFloat(cs.fontSize)<21)issues.push({type:'reading-text-too-small',text:label(el),size:parseFloat(cs.fontSize),minimum:21});
          // Font ascenders can exceed a line box without clipping; only flag vertical overflow when the element clips.
          if (el.clientWidth && (el.scrollWidth > el.clientWidth+2 || (clippedY && el.scrollHeight > el.clientHeight+2))) issues.push({type:'text-overflow',text:label(el)});
        }
        for (let a=0; a<textEls.length; a++) for (let b=a+1; b<textEls.length; b++) {
          const x=textEls[a],y=textEls[b]; if (x.contains(y)||y.contains(x)) continue;
          const xr=rect(x),yr=rect(y),w=Math.min(xr.right,yr.right)-Math.max(xr.x,yr.x),h=Math.min(xr.bottom,yr.bottom)-Math.max(xr.y,yr.y);
          if (w>2 && h>2) issues.push({type:'text-overlap',a:label(x),b:label(y),width:w,height:h});
        }
        const brokenImages=[...s.querySelectorAll('img')].filter(im => !im.complete || !im.naturalWidth).map(im => im.alt);
        for (const el of s.querySelectorAll('.architecture-label')) {
          const cs=getComputedStyle(el);
          if (cs.backgroundColor!=='rgba(0, 0, 0, 0)' || parseFloat(cs.borderTopWidth)>0) issues.push({type:'architecture-label-box',text:label(el)});
        }

        let contract = {};
        try { contract = JSON.parse(s.dataset.designContract || '{}'); } catch {}
        const main = s.querySelector('main'), isCover = s.classList.contains('layout-cover'), isClosing = s.classList.contains('layout-closing');

        // Image above, captions below: thresholds come from the page contract (design_contract.IMAGE_BALANCE).
        let imageBalance = null;
        if (contract.image_balance) {
          const target=contract.image_balance,frame=s.querySelector('main .scene-image'),captions=s.querySelector('.journey-labels,[data-captions]'),im=frame?.querySelector('img'),scale=sr.width/1920;
          if (!frame||!im) issues.push({type:'missing-upper-image'});
          else {
            const fr=frame.getBoundingClientRect(),ir=im.getBoundingClientRect();
            const widthRatio=Math.max(0,Math.min(ir.right,fr.right)-Math.max(ir.left,fr.left))/fr.width,heightRatio=Math.max(0,Math.min(ir.bottom,fr.bottom)-Math.max(ir.top,fr.top))/fr.height;
            imageBalance={height:fr.height/scale,mainRatio:fr.height/main.getBoundingClientRect().height,fillRatio:Math.max(widthRatio,heightRatio),captionHeight:captions?captions.getBoundingClientRect().height/scale:0};
            if(imageBalance.height+1<target.min_height||imageBalance.mainRatio+.005<target.min_main_ratio||imageBalance.fillRatio+.005<target.min_fill_ratio||imageBalance.captionHeight-1>target.max_caption_height)
              issues.push({type:'image-area-too-small',actual:imageBalance,expected:target,hint:'图框高度、图框占 main 比例、配图贴满图框宽或高、下方文字行高四项须同时达标；主体是否横向铺开仍需看图。'});
          }
        }

        if (readingMode && s.classList.contains('layout-reading')) {
          // Each illustration reaches its region's width or height (design_contract.READING_IMAGE).
          const minFill = contract.illustration_fill?.min_fill_ratio;
          for (const el of s.querySelectorAll('.reading-media-item')) {
            const cs=getComputedStyle(el),r=el.getBoundingClientRect(),w=r.width-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight),h=r.height-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom),im=el.querySelector('.scene-image img');
            const ir = im && visible(im) ? clipped(im, el) : null;
            const fill = ir && w>0 && h>0 ? Math.max(Math.max(0,ir.right-ir.left)/w,Math.max(0,ir.bottom-ir.top)/h) : 0;
            if (Number.isFinite(minFill) && fill+.005<minFill) issues.push({type:'reading-image-underfilled',fill,minimum:minFill,hint:'按可见本体放大配图，不用空图框或缩小的图片凑分区。'});
          }
          // Alignment (user preference): a block heading stays on the region's top edge so headings align across a row;
          // the body below it, or an image with its caption, is centred in the remaining space (12px tolerance).
          for (const cell of s.querySelectorAll('.reading-body .reading-block,.reading-body .reading-media-item')) {
            const cs=getComputedStyle(cell),cr=cell.getBoundingClientRect(),kids=[...cell.children].filter(el=>visible(el)&&el.getBoundingClientRect().height>0);if(!kids.length)continue;
            const contentTop=cr.top+parseFloat(cs.borderTopWidth)+parseFloat(cs.paddingTop),contentBottom=cr.bottom-parseFloat(cs.borderBottomWidth)-parseFloat(cs.paddingBottom),region=cell.classList.contains('reading-block')?cell.dataset.visualType:'image';
            const heading=kids[0].matches('h3')?kids[0]:null,body=heading?kids.slice(1):kids;
            if(heading&&heading.getBoundingClientRect().top-contentTop>4)issues.push({type:'reading-heading-not-top',region,text:label(heading).slice(0,40),hint:'模块标题贴分区上沿，同一行的标题对齐。'});
            if(!body.length)continue;
            const top=Math.min(...body.map(el=>el.getBoundingClientRect().top))-(heading?heading.getBoundingClientRect().bottom+parseFloat(getComputedStyle(heading).marginBottom):contentTop),bottom=contentBottom-Math.max(...body.map(el=>el.getBoundingClientRect().bottom));
            if(bottom<-1)issues.push({type:'reading-block-overflow',region,text:label(cell).slice(0,40),overflow:Math.round(-bottom),hint:'模块内容超出分区高度；减少条目、让整行模块用 span: 2，或拆页，不靠缩小字号。'});
            else if(Math.abs(top-bottom)>12)issues.push({type:'reading-region-not-centered',region,text:label(cell).slice(0,40),above:Math.round(top),below:Math.round(bottom),hint:'标题下方的内容（或配图与说明）在分区剩余空间内垂直居中。'});
          }
        }

        for (const host of s.querySelectorAll('.echart')) {
          const hr=host.getBoundingClientRect(),svg=host.querySelector('svg');
          if(!svg||host.dataset.chartReady!=='true')issues.push({type:'chart-not-rendered'});
          for(const t of host.querySelectorAll('svg text')){const lr=t.getBoundingClientRect();if(lr.width&&lr.height&&(lr.left<hr.left-3||lr.right>hr.right+3||lr.top<hr.top-3||lr.bottom>hr.bottom+3))issues.push({type:'chart-label-clipped',text:t.textContent});}
        }

        // Advisory: speech pages with a small scene, wrapped control labels, narrow reading captions.
        let imageArea=null;const heroImg=s.querySelector('main .scene-image img');
        if(heroImg&&!isCover&&!isClosing){const ir=heroImg.getBoundingClientRect(),mr=main.getBoundingClientRect();const w=Math.max(0,Math.min(ir.right,mr.right)-Math.max(ir.left,mr.left)),h=Math.max(0,Math.min(ir.bottom,mr.bottom)-Math.max(ir.top,mr.top));imageArea=Math.round((w*h)/(mr.width*mr.height)*1000)/1000;const floor=s.classList.contains('layout-table')?.08:.30;if(!readingMode&&imageArea<floor)warnings.push({type:'image-area-small',imageArea,floor,hint:'放大场景本体、收窄文字或换左右排布；不要用小图配大段文字'});}
        for(const row of s.querySelectorAll('.control-group dl>div')){
          const dt=row.querySelector('dt'),cs=dt&&getComputedStyle(dt);
          if(dt&&getComputedStyle(row).display==='grid'&&dt.getBoundingClientRect().height>parseFloat(cs.lineHeight)*(sr.width/1920)*1.6)warnings.push({type:'control-label-wrapped',text:dt.textContent,hint:'检查短标签断行；可用 rows_layout: stacked 或重新分配栏宽'});
        }
        if(readingMode&&[...s.querySelectorAll('.journey-item')].some(el=>el.getBoundingClientRect().width/(sr.width/1920)<240))warnings.push({type:'journey-caption-narrow',hint:'阶段栏宽较窄；优先调整场景构图及图文占幅，再选择短字段或其他版式'});

        return {page:Number(document.querySelector('#page-input').value),id:s.id,title:s.querySelector('h1').textContent,issues,brokenImages,imageBalance,imageArea,warnings,manualReview:contract.manual||[]};
      });
      report.pages.push(checks);
      const shot = path.join(out, `p${String(i+1).padStart(2,'0')}.png`);
      await page.locator('.slide.active').screenshot({path: shot}); report.screenshots.push(shot);
    }
    try {
      const sharp = require('sharp'), cols=3, thumbWidth=640, thumbHeight=360, gap=20, rows=Math.ceil(count/cols);
      const tiles = await Promise.all(report.screenshots.map(async (file,i) => ({input:await sharp(file).resize(thumbWidth,thumbHeight).toBuffer(),left:gap+(i%cols)*(thumbWidth+gap),top:gap+Math.floor(i/cols)*(thumbHeight+gap)})));
      await sharp({create:{width:cols*(thumbWidth+gap)+gap,height:rows*(thumbHeight+gap)+gap,channels:3,background:'#E3E6EA'}}).composite(tiles).png().toFile(path.join(out,'overview.png'));
      report.overview = path.join(out,'overview.png');
    } catch(e) {report.overviewNote = '联系表未生成；逐页截图可用。'+e.message;}
    report.warnings = report.pages.flatMap(p=>p.warnings.map(w=>({page:p.page,...w})));
    report.ok = report.pages.every(p => !p.issues.length && !p.brokenImages.length) && !report.errors.length && !report.externalRequests.length
      && !report.selfContained.externalElements.length && !report.selfContained.cssImports && !report.selfContained.draft;
    fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify({ok:report.ok,style:report.style,pages:count,issues:report.pages.reduce((sum,p)=>sum+p.issues.length+p.brokenImages.length,0),warnings:report.warnings.length,pageErrors:report.errors.length,externalRequests:report.externalRequests.length,draft:report.selfContained.draft,report:path.join(out,'report.json')},null,2));
    if (!report.ok) process.exitCode=1;
  } finally {await browser.close();}
}
run().catch(e => {console.error('检查失败：'+e.message);process.exitCode=1;});
