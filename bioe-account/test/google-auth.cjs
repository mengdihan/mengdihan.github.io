const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
test('Google popup starts synchronously and returns actionable errors or success',async()=>{
 let calls=0,failure='auth/unauthorized-domain';
 const A={getAuth:()=>({}),onAuthStateChanged:(auth,callback)=>callback(null),GoogleAuthProvider:class{setCustomParameters(value){assert.equal(value.prompt,'select_account');}},signInWithPopup:async()=>{calls++;if(failure)throw {code:failure};}};
 const source=fs.readFileSync(__dirname+'/../../static/literature-account.js','utf8').replace("import(base+'firebase-app.js')","Promise.resolve(fakeApp)").replace("import(base+'firebase-auth.js')","Promise.resolve(fakeAuth)").replace("import(base+'firebase-firestore.js')","Promise.resolve(fakeFirestore)");
 const window={};vm.runInNewContext(source,{window,fakeApp:{initializeApp:()=>({})},fakeAuth:A,fakeFirestore:{getFirestore:()=>({})}});
 const account=window.BioERadarAccount;
 await new Promise(resolve=>setImmediate(resolve));
 const request=account.signIn();assert.equal(calls,1);
 let result=await request;assert.equal(result.ok,false);assert.equal(result.code,'auth/unauthorized-domain');assert.match(result.message,/not yet authorized/);
 failure='auth/popup-blocked';result=await account.signIn();assert.match(result.message,/popup/);
 failure=null;assert.equal((await account.signIn()).ok,true);
});
