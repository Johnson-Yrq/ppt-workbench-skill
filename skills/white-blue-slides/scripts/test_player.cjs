#!/usr/bin/env node
/* Player regression test: run on any built deck after changing player.js, pptx-export.js, charts.js,
 * template.html or the theme CSS. Not part of the per-deck audit; every deck embeds the same player. */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const {pathToFileURL} = require('url');

// Page structure in slide coordinates, independent of viewport/print zoom.
function slideFrames() {
  return [...document.querySelectorAll('.slide')].filter(s => s.getBoundingClientRect().width).map(s => {
    const r = s.getBoundingClientRect(), scale = 1920 / r.width;
    return {id: s.id, regions: ['header', 'main', 'footer'].map(selector => {
      const b = s.querySelector(selector).getBoundingClientRect();
      return [(b.x-r.x)*scale, (b.y-r.y)*scale, b.width*scale, b.height*scale];
    })};
  });
}
function matchingFrames(expected, actual) {
  return expected.length === actual.length && expected.every((s, i) => s.id === actual[i].id &&
    s.regions.every((r, j) => r.every((v, k) => Math.abs(v-actual[i].regions[j][k]) < 2.5)));
}

async function run() {
  const args = process.argv.slice(2), filename = args.shift();
  let channel, pdf = false;
  while (args.length) {
    const flag = args.shift();
    if (flag === '--browser') channel = args.shift();
    else if (flag === '--pdf') pdf = true;
    else throw new Error(`未知参数：${flag}`);
  }
  if (!filename) throw new Error('用法：node test_player.cjs 演示稿.html [--browser chrome] [--pdf]');
  const {chromium} = require('playwright');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'deck-player-'));
  const browser = await chromium.launch({headless: true, ...(channel ? {channel} : {})});
  const f = {};
  try {
    const context = await browser.newContext({viewport: {width: 1944, height: 1172}, deviceScaleFactor: 1, acceptDownloads: true});
    const page = await context.newPage();
    const url = pathToFileURL(path.resolve(filename)).href;
    await page.goto(url, {waitUntil: 'load'});
    await page.evaluate(async () => {await document.fonts.ready; await Promise.all([...document.images].map(im => im.decode().catch(() => {})));});
    const count = await page.locator('.slide').count();
    const screenFrames = [];
    for (let i = 0; i < count; i++) {
      await page.evaluate(n => window.deckAPI.show(n), i);
      screenFrames.push((await page.evaluate(slideFrames))[0]);
    }
    await page.keyboard.press('Home');
    f.home = await page.evaluate(() => window.deckAPI.current === 1);
    f.firstPrevDisabled = await page.locator('#prev').isDisabled();
    if (count>1) {await page.keyboard.press('ArrowRight'); f.arrow = await page.evaluate(() => window.deckAPI.current === 2);}
    await page.keyboard.press('End');
    f.end = await page.evaluate(n => window.deckAPI.current === n, count);
    f.lastNextDisabled = await page.locator('#next').isDisabled();
    f.pageCount = Number(await page.locator('#page-input').getAttribute('max'))===count;
    await page.locator('#overview').click();
    f.overview = await page.locator('.slide:visible').count()===count;
    f.overviewLayout = matchingFrames(screenFrames, await page.evaluate(slideFrames));
    await page.locator('.slide').nth(Math.min(1,count-1)).click();
    f.overviewJump = await page.evaluate(n => window.deckAPI.current === n && !document.body.classList.contains('overview-mode'), Math.min(2,count));
    await page.locator('#notes').click();
    f.notes = await page.locator('#notes-panel').isVisible() && await page.evaluate(() => document.querySelector('#notes-content').textContent === document.querySelector('.slide.active').dataset.speakerNotes);
    await page.locator('#close-notes').click();
    await page.locator('#edit').click();
    const editTarget = page.locator('.slide.active h1 [data-edit],.slide.active h1[data-edit]').first();
    const marker = '保存验证 · 可编辑文字';
    await editTarget.fill(marker);
    f.edit = await editTarget.textContent()===marker;
    const chartSlide = await page.evaluate(()=>[...document.querySelectorAll('.slide')].findIndex(s=>s.querySelector('.chart-data')));
    if(chartSlide>=0){
      await page.evaluate(index=>window.deckAPI.show(index),chartSlide);
      await page.locator('.slide.active .chart-editor').first().evaluate(el=>el.open=true);
      const cell=page.locator('.slide.active .chart-data tbody tr').first().locator('td').first();
      await cell.fill('invalid');
      const rejected=await page.locator('.slide.active .chart-shell[data-invalid]').count()===1;
      await cell.fill('97');
      f.chartDataEdit=rejected&&await page.evaluate(()=>{const shell=document.querySelector('.slide.active .chart-shell'),config=JSON.parse(shell.querySelector('.chart-config').textContent),series=echarts.getInstanceByDom(shell.querySelector('.echart')).getOption().series[0];return config.series[0].values[0]===97&&(series.data[0]?.value??series.data[0])===97&&!shell.hasAttribute('data-invalid');});
      await page.locator('.slide.active .chart-editor').first().evaluate(el=>el.open=false);
    }
    const downloadPromise = page.waitForEvent('download'); await page.locator('#save').click();
    const savedPath = path.join(tmp,'save-test.html'); await (await downloadPromise).saveAs(savedPath);
    const saved = await context.newPage(); await saved.goto(pathToFileURL(savedPath).href);
    await saved.evaluate(async () => {await Promise.all([...document.images].map(im => im.decode().catch(() => {})));});
    f.saveReopen = await saved.evaluate(({marker,count}) => [...document.querySelectorAll('h1')].some(h => h.textContent.includes(marker)) && document.querySelectorAll('.slide').length===count && [...document.images].every(im => im.naturalWidth>0) && !document.body.classList.contains('editing'), {marker,count});
    if(chartSlide>=0){
      await saved.evaluate(index=>window.deckAPI.show(index),chartSlide);
      f.chartSaveReopen=await saved.evaluate(()=>{const shell=document.querySelector('.slide.active .chart-shell'),config=JSON.parse(shell.querySelector('.chart-config').textContent),host=shell.querySelector('.echart'),series=echarts.getInstanceByDom(host).getOption().series[0];return config.series[0].values[0]===97&&(series.data[0]?.value??series.data[0])===97&&!!host.querySelector('svg path');});
    }
    await saved.close();
    if (await page.locator('#pptx').count()) {
      const pptxPromise = page.waitForEvent('download'); await page.locator('#pptx').click();
      const pptxPath = path.join(tmp, 'export-test.pptx'); await (await pptxPromise).saveAs(pptxPath);
      const head = fs.readFileSync(pptxPath);
      f.pptxExport = head.length > 1000 && head[0] === 0x50 && head[1] === 0x4B && head.includes('ppt/presentation.xml') && !await page.evaluate(() => document.body.classList.contains('editing'));
    }
    await page.goto(url);
    await page.setViewportSize({width:390,height:844});
    await page.evaluate(() => new Promise(resolve => {window.deckAPI.fit(); requestAnimationFrame(() => requestAnimationFrame(resolve));}));
    f.mobileFit = await page.evaluate(() => {const r=document.querySelector('.slide.active').getBoundingClientRect();return r.width<=innerWidth && r.left>=-1 && r.right<=innerWidth+1 && r.bottom<=innerHeight-60;});
    await page.setViewportSize({width:1920,height:1080});
    await page.locator('#fullscreen').click();
    f.fullscreen = await page.evaluate(() => !!document.fullscreenElement);
    const sizes = [];
    for (const size of [{width:1920,height:1080},{width:1440,height:900},{width:2560,height:1080},{width:1024,height:768}]) {
      await page.setViewportSize(size);
      sizes.push(await page.evaluate(() => {
        window.deckAPI.fit();
        const r=document.querySelector('.slide.active').getBoundingClientRect(),scale=Math.min(innerWidth/1920,innerHeight/1080);
        return Math.abs(r.width-1920*scale)<1 && Math.abs(r.height-1080*scale)<1 && Math.abs(r.x-(innerWidth-r.width)/2)<1 && Math.abs(r.y-(innerHeight-r.height)/2)<1;
      }));
    }
    f.fullscreenFit = sizes.every(Boolean);
    await page.setViewportSize({width:1920,height:1080});
    if (f.fullscreen) {
      await page.locator('.toolbar').hover();
      const revealed = await page.locator('.toolbar').evaluate(el=>getComputedStyle(el).opacity==='1');
      await page.mouse.move(0,0);
      f.fullscreenToolbar = revealed && await page.locator('.toolbar').evaluate(el=>getComputedStyle(el).opacity==='0');
      await page.locator('#edit').evaluate(el=>el.click());
      f.fullscreenEditFit = await page.evaluate(() => {
        const r=document.querySelector('.slide.active').getBoundingClientRect(),bar=document.querySelector('.toolbar').getBoundingClientRect();
        return r.bottom<=bar.top && getComputedStyle(document.querySelector('.toolbar')).opacity==='1';
      });
      await page.locator('#edit').click();
      await page.evaluate(() => document.exitFullscreen());
    }
    await page.setViewportSize({width:1944,height:1172});
    if (pdf) {
      // Print from overview with another slide selected: inactive pages keep single-slide geometry.
      await page.evaluate(()=>window.deckAPI.show(window.deckAPI.count-1));
      await page.locator('#overview').click();
      await page.emulateMedia({media:'print'});
      await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
      f.printLayout = matchingFrames(screenFrames, await page.evaluate(slideFrames));
      const {writePresentationPdf} = require('./export_pdf.cjs');
      const printed = await writePresentationPdf(page, path.join(tmp,'print-check.pdf'), count);
      f.printCount = printed.pages===count;
      f.printSize = printed.sizes.every(s=>Math.abs(s.width-960)<.5 && Math.abs(s.height-540)<.5);
      f.printReturnLayout = matchingFrames(screenFrames, await page.evaluate(slideFrames));
    }
  } finally {
    await browser.close();
    fs.rmSync(tmp, {recursive: true, force: true});
  }
  const failed = Object.entries(f).filter(([, ok]) => !ok).map(([name]) => name);
  console.log(JSON.stringify({ok: !failed.length, failed, functions: f}, null, 2));
  if (failed.length) process.exitCode = 1;
}
run().catch(e => {console.error('播放器测试失败：'+e.message);process.exitCode=1;});
