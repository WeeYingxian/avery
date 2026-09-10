const {chromium}=require(process.env.AVERY_PLAYWRIGHT||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({channel:process.env.AVERY_BROWSER==='chromium'?undefined:(process.env.AVERY_BROWSER||'msedge')});
 async function setup(blockStorage){
  const context=await browser.newContext();
  await context.route('http://avery.test/**',r=>r.fulfill(r.request().url().includes('/api/')||r.request().url().endsWith('.json')?{status:404,body:''}:{contentType:'text/html',body:fs.readFileSync(path.join(root,'index.html'),'utf8')}));
  if(blockStorage)await context.addInitScript(()=>Storage.prototype.setItem=function(){throw new DOMException('Storage blocked','QuotaExceededError')});
  const page=await context.newPage();await page.goto('http://avery.test/');await page.waitForFunction(()=>appReady);return {context,page};
 }
 let {context,page}=await setup(false);
 assert.deepEqual(await page.evaluate(()=>HOSP.filter(h=>h.t.includes('unsubsidised')).map(newbornFor)),[800,800]);
 await page.locator('[data-tab="discuss"]').click();await page.locator('.task [data-toggle]').first().click();
 await page.locator('.task textarea[data-k="notes"]').first().fill('Quick note must survive refresh');await page.reload();
 assert.ok(await page.evaluate(()=>localStorage.getItem('avery:tasks').includes('Quick note must survive refresh')));
 const before=await page.evaluate(()=>cfg('help'));await page.evaluate(()=>save('tasks',{q20:{agreed:'No nanny, family help',status:'agreed'}}));assert.equal(await page.evaluate(()=>cfg('help')),before);
 await page.locator('[data-tab="money"]').click();await page.locator('#shareBtn').click();
 await page.locator('input[data-restorefile]').setInputFiles({name:'replacement.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({settings:{cdaDeposit:1000},tasks:{},buys:{},checks:{}}))});
 await page.locator('dialog').getByRole('button',{name:'Replace this device’s plan'}).click();assert.equal(await page.evaluate(()=>Object.keys(S.tasks).length),0);
 await page.locator('#undoPlan').click();assert.ok(await page.evaluate(()=>Object.keys(S.tasks).length>0));
 await context.close();
 ({context,page}=await setup(true));await page.locator('#due').fill('2028-01-01');await page.locator('#due').dispatchEvent('change');
 await page.waitForFunction(()=>document.querySelector('.panel.on .savebar').textContent.includes('Not saved'));
 assert.equal(await page.evaluate(()=>localStorage.getItem('avery:settings')),null);assert.ok(await page.locator('#emergencyExport').isVisible());
 assert.ok(await page.evaluate(()=>isDirty()));await context.close();await browser.close();
 console.log('PASS hospital category, immediate note persistence, no free-text budget mutation, replace import + undo, and visible storage failure without false saved status');
})();
