// Local UI fixtures only: no live accounts or private production data.
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
test('exclusive disclosures, private title memory, sign-out clearing and responsive alignment',async()=>{
 const {chromium}=require('playwright'),bundle=await import(require.resolve('@sparticuz/chromium'));
 const root=path.resolve(process.env.BIOE_TEST_SITE||'../output-radar');
 const server=http.createServer((req,res)=>{try{let p=path.join(root,new URL(req.url,'http://local').pathname);if(fs.statSync(p).isDirectory())p=path.join(p,'index.html');res.setHeader('Content-Type',p.endsWith('.js')?'application/javascript':p.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(p));}catch{res.statusCode=404;res.end();}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true,executablePath:process.env.BIOE_TEST_CHROMIUM||'/tmp/radar-chromium',args:bundle.default.args});
 try{
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/static/literature-account.js*',route=>route.fulfill({contentType:'application/javascript',body:`(()=>{let state={status:'signed-out',user:null,feedback:{},events:[],reactions:[],communityStatus:'ready',message:'Signed out'},listeners=[],n=0;const emit=()=>listeners.forEach(fn=>fn(state));window.BioERadarAccount={subscribe(fn){listeners.push(fn);fn(state)},getState(){return state},async signInEmail(){this.signIn();return {ok:true}},signIn(){state={...state,status:'signed-in',user:{uid:'alice',displayName:'Alice'}};emit()},async signOut(){state={...state,status:'signed-out',user:null,feedback:{}};emit()},async saveInterest(title,note='add'){const key='interest:'+ ++n;state.feedback={...state.feedback,[key]:{key,title,note,updatedAt:Date.now()}};emit();return true;},save(){}}})();`}));
  const base='http://127.0.0.1:'+server.address().port;
  await page.goto(base+'/BioE_Radar/');
  assert.equal(await page.locator('#lit-interests').isVisible(),false);
  assert.equal(await page.locator('#lit-version-note').isVisible(),false);
  assert.equal(await page.locator('#lit-feedback-status').innerText(),'Private preferences across devices');
  await page.locator('#lit-sources-toggle').click();assert.equal(await page.locator('#lit-sources-body').isVisible(),true);
  await page.locator('#lit-recommendations-toggle').click();assert.equal(await page.locator('#lit-sources-body').isVisible(),false);assert.equal(await page.locator('#lit-recommendations-body').isVisible(),true);
  await page.locator('#lit-sources-toggle').click();assert.equal(await page.locator('#lit-recommendations-body').isVisible(),false);
  await page.getByRole('button',{name:'Log in',exact:true}).click();await page.getByLabel('Email address',{exact:true}).fill('local-ui@example.test');await page.getByLabel('Password',{exact:true}).fill('Local-ui-only9');await page.locator('#lit-email-submit').click();
  assert.equal(await page.locator('#lit-interests').isVisible(),true);
  const order=await page.locator('.lit-paper').evaluateAll(es=>es.map(e=>e.dataset.id));
  // Content retrieval and confirmed persistence are covered by content-ui.cjs.
  for(const width of [1366,390,320]){
   await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   const centered=await page.locator('#lit-feedback-status').evaluate(e=>{const a=e.getBoundingClientRect(),b=e.closest('.lit-account-panel').getBoundingClientRect();return Math.abs((a.left+a.right)/2-(b.left+b.right)/2)<1&&getComputedStyle(e).textAlign==='center';});assert.equal(centered,true);
   assert.equal(await page.locator('.lit-update-note').evaluate(e=>getComputedStyle(e).textAlign),'left');
  }
  await page.locator('#lit-account-signout').click();assert.equal(await page.locator('#lit-interests').isVisible(),false);assert.equal(await page.locator('#lit-interest-title').inputValue(),'');
  await page.goto(base+'/current/');const current=page.locator('details.member-publications');assert.ok(await current.count()>1);
  await current.nth(0).locator('summary').click();await current.nth(1).locator('summary').click();assert.equal(await current.nth(0).getAttribute('open'),null);assert.notEqual(await current.nth(1).getAttribute('open'),null);
  await page.goto(base+'/alumni/');const alumni=page.locator('.alumni-publications-toggle');assert.ok(await alumni.count()>1);
  await alumni.nth(0).click();await alumni.nth(1).click();assert.equal(await alumni.nth(0).getAttribute('aria-expanded'),'false');assert.equal(await alumni.nth(1).getAttribute('aria-expanded'),'true');
  assert.deepEqual(errors,[]);
 }finally{await browser.close();await new Promise(r=>server.close(r));}
});
