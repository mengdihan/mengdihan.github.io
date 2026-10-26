// Local UI contract test: account adapter is stubbed; no production data is used.
// NODE_PATH must expose playwright and @sparticuz/chromium for this optional check.
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
test('sign-in, feedback, undo and clearing private UI on sign-out',async()=>{
 const {chromium}=require('playwright'),bundle=await import(require.resolve('@sparticuz/chromium'));
 const root=path.resolve(process.env.BIOE_TEST_SITE||'../output-account');
 const server=http.createServer((req,res)=>{try{const p=path.join(root,new URL(req.url,'http://local').pathname);const file=fs.statSync(p).isDirectory()?path.join(p,'index.html'):p;res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));}catch{res.statusCode=404;res.end();}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,executablePath:process.env.BIOE_TEST_CHROMIUM||'/tmp/chromium',args:bundle.default.args});
 try{
  const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/static/literature-account.js*',route=>route.fulfill({contentType:'application/javascript',body:`(()=>{let state={status:'signed-out',user:null,feedback:{},message:'Signed out'},listeners=[];const emit=()=>listeners.forEach(fn=>fn(state));window.BioERadarAccount={subscribe(fn){listeners.push(fn);fn(state)},async signInEmail(){this.signIn();return {ok:true}},signIn(){state={status:'signed-in',user:{uid:'alice',displayName:'Alice'},feedback:{},message:'Synced'};emit()},signOut(){state={status:'signed-out',user:null,feedback:{},message:'Signed out'};emit()},async save(entry){state.feedback={...state.feedback,[entry.key]:entry};state.reactions=[{key:entry.key,uid:'alice',name:'Alice',signals:entry.signals}];state.events=[...(state.events||[]),{key:entry.key,uid:'alice',signals:entry.signals,createdAt:Date.now()}];emit();return true},getState(){return state}}})();`}));
  await page.goto('http://127.0.0.1:'+server.address().port+'/BioE_Radar/');
  await page.getByRole('button',{name:'Log in',exact:true}).waitFor();
  assert.equal(await page.locator('.lit-paper').count(),52);
  assert.equal(await page.getByRole('button',{name:'Useful',exact:true}).first().isEnabled(),false);
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.getByLabel('Email address',{exact:true}).fill('local-ui@example.test');await page.getByLabel('Password',{exact:true}).fill('Local-ui-only9');await page.locator('#lit-email-submit').click();
  assert.equal(await page.locator('#lit-sort').inputValue(),'personal');
  const summary=page.locator('#lit-recommendations-toggle');
  const position=()=>summary.evaluate(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y+scrollY}));
  const initialPosition=await position();await summary.click();assert.deepEqual(await position(),initialPosition);await summary.click();
  const order=await page.locator('.lit-paper').evaluateAll(es=>es.map(e=>e.dataset.id));
  const first=page.locator('.lit-paper').first(),id=await first.getAttribute('data-id');
  await first.getByRole('button',{name:'Useful',exact:true}).click();
  assert.deepEqual(await page.locator('.lit-paper').evaluateAll(es=>es.map(e=>e.dataset.id)),order);
  await page.locator('.lit-paper').first().getByRole('button',{name:'Useful',exact:true}).hover();
  assert.equal(await page.locator('.lit-paper').first().locator('.lit-reaction-tip:visible').innerText(),'Alice');
  await page.getByRole('button',{name:'Community average',exact:true}).click();assert.equal(await page.locator('.lit-paper').count(),52);
  await page.getByRole('button',{name:'Personal',exact:true}).click();
  let card=page.locator('.lit-paper').filter({has:page.locator('[data-signal="useful"][aria-pressed="true"]')});
  assert.equal(await card.count(),1);await card.getByRole('button',{name:'Like',exact:true}).click();
  await card.getByRole('button',{name:'Not relevant',exact:true}).click();
  assert.deepEqual(await page.locator('.lit-paper').evaluateAll(es=>es.map(e=>e.dataset.id)),order);
  card=page.locator('.lit-paper').filter({has:page.locator('[data-signal="irrelevant"][aria-pressed="true"]')});
  assert.equal(await card.getByRole('button',{name:'Useful',exact:true}).getAttribute('aria-pressed'),'false');
  await page.locator('#lit-feedback-filter').selectOption('marked');assert.equal(await page.locator('.lit-paper').count(),1);
  await card.getByRole('button',{name:'Not relevant',exact:true}).click();assert.equal(await page.locator('.lit-paper').count(),0);
  await page.locator('#lit-feedback-filter').selectOption('all');
  await page.getByRole('button',{name:'Sign out',exact:true}).click();
  assert.equal(await page.locator('.lit-paper').count(),52);assert.equal(await page.locator('#lit-sort').inputValue(),'personal');
  assert.equal(await page.locator('[aria-pressed="true"][data-signal]').count(),0);
  assert.equal(await page.getByRole('button',{name:'Useful',exact:true}).first().isEnabled(),false);
  assert.equal(await page.locator('#lit-feedback-export').count(),0);assert.deepEqual(errors,[]);
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
});
