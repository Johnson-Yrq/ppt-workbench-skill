/* Focused fixture test for editable pie charts and metric progress ratios. */
'use strict';
const assert=require('assert/strict');
const fs=require('fs');
const os=require('os');
const path=require('path');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');

(async()=>{
 if(!process.argv[2])throw new Error('Supply a fixture HTML containing a pie and progress metrics.');
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'composition-runtime-'));
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const context=await browser.newContext({acceptDownloads:true,viewport:{width:1944,height:1172}});
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve(process.argv[2])).href);
  await page.locator('#edit').click();
  const pieIndex=await page.evaluate(()=>[...document.querySelectorAll('.slide')].findIndex(s=>s.querySelector('.chart-config')&&JSON.parse(s.querySelector('.chart-config').textContent).chart_type==='pie'));
  assert.ok(pieIndex>=0);
  await page.evaluate(n=>window.deckAPI.show(n),pieIndex);
  await page.locator('.slide.active .chart-editor').evaluate(el=>el.open=true);
  const pieCell=page.locator('.slide.active .chart-data tbody tr').first().locator('td').first();
  await pieCell.fill('-1');assert.equal(await page.locator('.slide.active .chart-shell[data-invalid]').count(),1);
  await pieCell.fill('97');
  const pieState=()=>{
   const shell=document.querySelector('.slide.active .chart-shell'),config=JSON.parse(shell.querySelector('.chart-config').textContent);
   const option=echarts.getInstanceByDom(shell.querySelector('.echart')).getOption();
   return {value:config.series[0].values[0],rendered:option.series[0].data[0].value,radius:option.series[0].radius,title:option.title[0].show};
  };
  assert.deepEqual(await page.evaluate(pieState),{value:97,rendered:97,radius:'83%',title:false});
  const extraColors=await page.evaluate(()=>{
   const host=document.querySelector('.slide.active .echart'),css=getComputedStyle(host);
   const extra=['--chart-quaternary','--chart-quinary'].map(key=>css.getPropertyValue(key).trim()).filter(Boolean);
   const palette=echarts.getInstanceByDom(host).getOption().color;
   return {extra,palette};
  });
  assert.deepEqual(extraColors.palette.slice(3),extraColors.extra);
  const progressIndex=await page.evaluate(()=>[...document.querySelectorAll('.slide')].findIndex(s=>s.querySelector('.comp-progress')));
  await page.evaluate(n=>window.deckAPI.show(n),progressIndex);
  await page.locator('.slide.active .comp-progress-editor').first().evaluate(el=>el.open=true);
  const cells=page.locator('.slide.active .comp-progress-data tbody tr').first().locator('td');
  await cells.nth(0).fill('25');await cells.nth(1).fill('50');
  const progressState=()=>{const host=document.querySelector('.slide.active .comp-progress');return {text:host.querySelector('.comp-progress-percent').textContent,width:host.querySelector('.comp-progress-fill').style.width,value:host.querySelector('.comp-progress-track').getAttribute('aria-valuenow'),max:host.querySelector('.comp-progress-track').getAttribute('aria-valuemax')};};
  assert.deepEqual(await page.evaluate(progressState),{text:'50%',width:'50%',value:'25',max:'50'});
  await cells.nth(0).fill('51');assert.equal(await page.locator('.slide.active .comp-progress[data-invalid]').count(),1);
  assert.ok(await page.evaluate(async()=>{try{await window.deckPptx.build();return false;}catch{return true;}}));
  await cells.nth(0).fill('40');
  const download=page.waitForEvent('download');await page.locator('#save').click();
  const savedPath=path.join(tmp,'saved.html');await(await download).saveAs(savedPath);
  const saved=await context.newPage();await saved.goto(pathToFileURL(savedPath).href);
  await saved.evaluate(n=>window.deckAPI.show(n),pieIndex);
  assert.deepEqual(await saved.evaluate(pieState),{value:97,rendered:97,radius:'83%',title:false});
  await saved.evaluate(n=>window.deckAPI.show(n),progressIndex);
  assert.deepEqual(await saved.evaluate(progressState),{text:'80%',width:'80%',value:'40',max:'50'});
  // Disable ZIP compression in this isolated fixture so XML can be inspected directly.
  const exported=await saved.evaluate(async extra=>{
   window.CompressionStream=undefined;
   const result=await window.deckPptx.build(),xml=new TextDecoder().decode(result.bytes);
   return {pie:xml.includes('<c:pieChart>'),donut:xml.includes('<c:doughnutChart>'),percent:xml.includes('<a:t>80%</a:t>'),editor:xml.includes('<a:t>当前值</a:t>'),charts:result.stats.charts,palette:extra.every(color=>xml.includes('val="'+color.replace('#','').toUpperCase()+'"'))};
  },extraColors.extra);
  assert.equal(exported.pie,true);assert.equal(exported.donut,false);assert.equal(exported.percent,true);assert.equal(exported.editor,false);assert.equal(exported.charts,1);
  assert.equal(exported.palette,true);
  assert.deepEqual(errors,[]);
  console.log('PASS pie/progress: validation, live update, save/reopen, native pie and editable percentage export.');
 }finally{await browser.close();fs.rmSync(tmp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
