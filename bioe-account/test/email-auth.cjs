// Production account adapter against the local Auth emulator; Firestore is stubbed.
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const A=require('firebase/auth'),App=require('firebase/app');
test('email registration, display-name claims, login errors, reset and account isolation',async()=>{
 const writes=[];
 const F={getFirestore:()=>({}),collection:(...p)=>p,query:(...p)=>p,where:(...p)=>p,Timestamp:{fromMillis:n=>n},serverTimestamp:()=>({serverTimestamp:true}),doc:(...p)=>({id:'T'.repeat(20),path:p}),writeBatch:()=>({set:(ref,data)=>writes.push({ref,data}),commit:async()=>{}}),onSnapshot:(...args)=>{const callback=args.find(x=>typeof x==='function');queueMicrotask(()=>callback({docs:[],forEach(){},metadata:{hasPendingWrites:false,fromCache:false}}));return()=>{};}};
 F.setDoc=async(ref,data)=>{writes.push({ref,data});};
 let source=fs.readFileSync(__dirname+'/../../static/literature-account.js','utf8');
 source=source.replace("import(base+'firebase-app.js')","Promise.resolve(require('firebase/app'))").replace("import(base+'firebase-auth.js')","Promise.resolve(require('firebase/auth'))").replace("import(base+'firebase-firestore.js')","Promise.resolve(fakeFirestore)").replace("projectId:'bioe-radar'","projectId:'demo-bioe-email'").replace('auth=A.getAuth(instance);','auth=A.getAuth(instance);A.connectAuthEmulator(auth,\'http://127.0.0.1:9099\',{disableWarnings:true});');
 const window={BioERadarPersonalization:{cutoff:()=>Date.now()}},context={window,require,fakeFirestore:F,queueMicrotask,TextEncoder,crypto:require('node:crypto').webcrypto,document:{getElementById:()=>({content:{textContent:'{"editions":[{}]}'}})}};
 vm.runInNewContext(source,context);const account=window.BioERadarAccount;
 const waitFor=async predicate=>{for(let n=0;n<100;n++){if(predicate(account.getState()))return;await new Promise(r=>setTimeout(r,20));}throw Error('Account state timeout');};
 try{
 await waitFor(s=>s.status==='signed-out');
 const address='reader-'+Date.now()+'@example.test',password='Emulator-only-Password9';
 assert.equal((await account.registerEmail(address,password,'Lab Reader')).ok,true);
 await waitFor(s=>s.status==='signed-in');const uid=account.getState().user.uid;
 assert.equal(account.getState().user.displayName,'Lab Reader');
 assert.equal((await A.getAuth(App.getApp()).currentUser.getIdTokenResult()).claims.name,'Lab Reader');
 assert.equal(await account.save({key:'10.1234/test',id:'paper',doi:'10.1234/test',title:'Paper',journal:'Science',signals:['more'],note:'private'}),true);
 assert.equal(writes.find(x=>x.data.name)?.data.name,'Lab Reader');
 assert.equal(writes.some(x=>'email' in x.data||'password' in x.data),false);
 const before=writes.length;
 assert.equal(await account.saveInterest('  Wireless magnetic implants  ','add',{v:2,action:'add',basis:'abstract',text:'Wireless magnetic implants physiological monitoring biosensors. '.repeat(5),terms:['wireless','magnetic','implants','physiological','monitoring','biosensors','readout','tissue']}),true);
 assert.equal(writes.length,before+1);
 assert.equal(writes.at(-1).ref.path[1],'readers');assert.equal(writes.at(-1).ref.path[2],uid);
 assert.equal(writes.at(-1).data.title,'Wireless magnetic implants');assert.equal(JSON.parse(writes.at(-1).data.note).action,'add');assert.equal(writes.at(-1).data.signals.length,0);
 assert.equal(await account.saveInterest('Wireless magnetic implants','remove'),true);
 assert.equal(writes.at(-1).data.note,'remove');
 await account.signOut();await waitFor(s=>s.status==='signed-out');assert.equal(Object.keys(account.getState().feedback).length,0);
 assert.equal(await account.saveInterest('Signed-out interest'),false);
 assert.equal((await account.signInEmail(address,'incorrect-password')).ok,false);
 assert.equal((await account.signInEmail(address,password)).ok,true);await waitFor(s=>s.status==='signed-in');assert.equal(account.getState().user.uid,uid);
 assert.equal((await account.resetEmailPassword(address)).ok,true);
 assert.equal((await account.registerEmail(address,password,'Duplicate')).ok,false);
 await account.signOut();await waitFor(s=>s.status==='signed-out');
 assert.equal((await account.registerEmail('other-'+Date.now()+'@example.test',password,'Other Reader')).ok,true);await waitFor(s=>s.status==='signed-in');assert.notEqual(account.getState().user.uid,uid);
 }finally{await account.signOut();await App.deleteApp(App.getApp());}
});
