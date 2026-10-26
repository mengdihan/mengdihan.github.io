const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
test('email dialog modes, errors, reset, registration and password clearing',async()=>{
 const {chromium}=require('playwright'),bundle=await import(require.resolve('@sparticuz/chromium'));
 const root=path.resolve(process.env.BIOE_TEST_SITE||'../output-email');
 const server=http.createServer((req,res)=>{try{let p=path.join(root,new URL(req.url,'http://local').pathname);if(fs.statSync(p).isDirectory())p=path.join(p,'index.html');res.setHeader('Content-Type',p.endsWith('.js')?'application/javascript':p.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(p));}catch{res.statusCode=404;res.end();}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,executablePath:process.env.BIOE_TEST_CHROMIUM||'/tmp/bioe-email-chromium',args:bundle.default.args});
 try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/static/literature-account.js*',route=>route.fulfill({contentType:'application/javascript',body:`(()=>{let state={status:'signed-out',user:null,feedback:{},events:[],reactions:[],communityStatus:'ready',message:'Signed out'},listeners=[];const emit=()=>listeners.forEach(fn=>fn(state));window.BioERadarAccount={subscribe(fn){listeners.push(fn);fn(state)},getState(){return state},signIn(){},async signInEmail(){return {ok:false,message:'Email or password is incorrect.'}},async resetEmailPassword(){return {ok:true,message:'If this address has a password account, a reset email has been sent.'}},async registerEmail(email,password,name){state={...state,status:'signed-in',user:{uid:'test-reader',displayName:name},message:'Synced'};emit();return {ok:true}},async signOut(){state={...state,status:'signed-out',user:null,feedback:{},message:'Signed out'};emit()},save(){}}})();`}));
 await page.goto('http://127.0.0.1:'+server.address().port+'/BioE_Radar/');
 await page.getByRole('button',{name:'Log in',exact:true}).click();const dialog=page.locator('#lit-email-dialog');assert.equal(await dialog.getByRole('button',{name:'Continue with Google',exact:true}).count(),0);assert.equal(await page.locator('.lit-account-actions button:visible').count(),1);
 await page.getByLabel('Email address',{exact:true}).fill('local-ui@example.test');await page.getByLabel('Password',{exact:true}).fill('Local-ui-only9');
 await dialog.getByRole('button',{name:'Sign in',exact:true}).last().click();await page.getByText('Email or password is incorrect.',{exact:true}).waitFor();
 assert.equal(await page.getByLabel('Password',{exact:true}).inputValue(),'');assert.equal(new URL(page.url()).search,'');
 await page.getByRole('button',{name:'Forgot password?',exact:true}).click();assert.equal(await page.locator('#lit-email-password-row').isVisible(),false);
 await page.getByRole('button',{name:'Send reset email',exact:true}).click();await page.getByText('If this address has a password account, a reset email has been sent.',{exact:true}).waitFor();
 await page.getByRole('button',{name:'Back to sign in',exact:true}).click();await dialog.getByRole('button',{name:'Create account',exact:true}).first().click();
 assert.equal(await page.getByLabel('Public display name',{exact:true}).isVisible(),true);assert.equal(await page.getByLabel('Password',{exact:true}).getAttribute('autocomplete'),'new-password');
 await page.getByLabel('Public display name',{exact:true}).fill('Lab Reader');await page.getByLabel('Password',{exact:true}).fill('Local-ui-only9');await dialog.getByRole('button',{name:'Create account',exact:true}).last().click();
 await dialog.waitFor({state:'hidden'});assert.equal(await page.locator('#lit-email-password').inputValue(),'');assert.equal(await page.locator('#lit-account-name').innerText(),'Lab Reader');
 await page.getByRole('button',{name:'Sign out',exact:true}).click();
 for(const width of [1366,390,320]){await page.setViewportSize({width,height:850});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.getByRole('button',{name:'Log in',exact:true}).click();assert.equal(await page.evaluate(()=>document.querySelector('#lit-email-dialog').getBoundingClientRect().right<=innerWidth),true);if(process.env.BIOE_EMAIL_PREVIEW)await page.screenshot({path:process.env.BIOE_EMAIL_PREVIEW+'-'+width+'.png'});await page.getByRole('button',{name:'Close email sign-in',exact:true}).click();}
 assert.deepEqual(errors,[]);
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
});
