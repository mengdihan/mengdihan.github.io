const {test,before,after}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {initializeTestEnvironment,assertSucceeds,assertFails}=require('@firebase/rules-unit-testing');
const F=require('firebase/firestore');
let env,alice,bob,anon;const hash='a'.repeat(64),key='10.1234/test',event='A'.repeat(20);
const feedback=()=>({key,id:'paper',doi:key,title:'Test paper',journal:'Science',signals:['more'],note:'private note',updatedAt:F.serverTimestamp()});
const shared=()=>({key,article:hash,uid:'alice',name:'Alice',signals:['more']});
function batch(db,change={}){const b=F.writeBatch(db);b.set(F.doc(db,'readers','alice','feedback',hash),{...feedback(),...(change.feedback||{})});b.set(F.doc(db,'communityReactions','alice_'+hash),{...shared(),event,updatedAt:F.serverTimestamp(),...(change.reaction||{})});b.set(F.doc(db,'reactionEvents',event),{...shared(),createdAt:F.serverTimestamp(),...(change.event||{})});const signals=change.reaction?.signals||['more'];b.set(F.doc(db,'publicReactionCounts',hash),{key,like:signals.includes('more')?1:0,useful:signals.includes('useful')?1:0,updatedAt:F.serverTimestamp()});return b.commit();}
before(async()=>{env=await initializeTestEnvironment({projectId:'demo-bioe-radar',firestore:{host:'127.0.0.1',port:8080,rules:fs.readFileSync(__dirname+'/../firestore.rules','utf8')}});alice=env.authenticatedContext('alice',{name:'Alice'}).firestore();bob=env.authenticatedContext('bob',{name:'Bob'}).firestore();anon=env.unauthenticatedContext().firestore();});
after(async()=>{await env?.cleanup();});
test('manual title events fit the deployed private schema and stay owner-only',async()=>{
 await env.clearFirestore();
 const record={key:'interest:local-event',id:'interest:local-event',doi:'',title:'A private research interest',journal:'Personal reading interests',signals:[],note:'add',updatedAt:F.serverTimestamp()};
 const ref=F.doc(alice,'readers','alice','feedback','c'.repeat(64));
 await assertSucceeds(F.setDoc(ref,record));
 await assertSucceeds(F.getDoc(ref));
 await assertFails(F.getDoc(F.doc(bob,'readers','alice','feedback','c'.repeat(64))));
 await assertFails(F.getDoc(F.doc(anon,'readers','alice','feedback','c'.repeat(64))));
 assert.equal((await F.getDocs(F.collection(alice,'communityReactions'))).size,0);
 await assertFails(F.setDoc(F.doc(alice,'readers','bob','feedback','d'.repeat(64)),record));
});
test('atomic own reaction, public signed-in reads and private isolation',async()=>{await env.clearFirestore();await assertSucceeds(batch(alice));const reaction=await assertSucceeds(F.getDoc(F.doc(bob,'communityReactions','alice_'+hash)));assert.equal(reaction.data().name,'Alice');assert.equal('note' in reaction.data(),false);await assertFails(F.getDoc(F.doc(bob,'readers','alice','feedback',hash)));await assertSucceeds(F.getDocs(F.collection(bob,'communityReactions')));await assertSucceeds(F.getDocs(F.query(F.collection(bob,'reactionEvents'),F.where('createdAt','<=',F.Timestamp.now()))));});
test('anonymous access and other-account writes fail',async()=>{await assertFails(F.getDocs(F.collection(anon,'communityReactions')));await assertFails(F.getDocs(F.collection(anon,'reactionEvents')));await assertFails(batch(bob));await assertFails(batch(anon));});
test('standalone reactions/events and timestamps cannot be forged',async()=>{await env.clearFirestore();await assertFails(F.setDoc(F.doc(alice,'communityReactions','alice_'+hash),{...shared(),event,updatedAt:F.serverTimestamp()}));await assertFails(F.setDoc(F.doc(alice,'reactionEvents',event),{...shared(),createdAt:F.serverTimestamp()}));await assertFails(batch(alice,{event:{createdAt:F.Timestamp.fromMillis(1)}}));});
test('names, uid and public notes/email injection are rejected',async()=>{for(const patch of [{name:'Bob'},{uid:'bob'},{note:'leak'},{email:'alice@example.test'}]){await env.clearFirestore();await assertFails(batch(alice,{reaction:patch,event:patch}));}});
test('conflicting, duplicate or invalid signals rejected',async()=>{for(const signals of [['more','irrelevant'],['more','more'],['invalid'],['useful','more','irrelevant']]){await env.clearFirestore();await assertFails(batch(alice,{reaction:{signals},event:{signals},feedback:{signals}}));}});
test('create and update enforce strict bounds, required fields and immutability',async()=>{await env.clearFirestore();await assertSucceeds(batch(alice));for(const patch of [{name:'a'.repeat(101)},{key:'a'.repeat(1001)},{uid:'bob'},{article:'b'.repeat(64)},{extra:true},{name:42},{signals:F.deleteField()}])await assertFails(F.updateDoc(F.doc(alice,'communityReactions','alice_'+hash),patch));await assertFails(F.updateDoc(F.doc(alice,'readers','alice','feedback',hash),{note:'a'.repeat(2001)}));await assertFails(F.updateDoc(F.doc(alice,'reactionEvents',event),{signals:[]}));await assertFails(F.deleteDoc(F.doc(alice,'reactionEvents',event)));await assertFails(F.deleteDoc(F.doc(alice,'communityReactions','alice_'+hash)));});
test('undo is atomic, retains history and does not reveal private notes',async()=>{await env.clearFirestore();await assertSucceeds(batch(alice));const b=F.writeBatch(alice),undo='B'.repeat(20);b.set(F.doc(alice,'readers','alice','feedback',hash),{...feedback(),signals:[]});b.set(F.doc(alice,'communityReactions','alice_'+hash),{...shared(),signals:[],event:undo,updatedAt:F.serverTimestamp()});b.set(F.doc(alice,'reactionEvents',undo),{...shared(),signals:[],createdAt:F.serverTimestamp()});b.set(F.doc(alice,'publicReactionCounts',hash),{key,like:0,useful:0,updatedAt:F.serverTimestamp()});await assertSucceeds(b.commit());assert.deepEqual((await F.getDoc(F.doc(bob,'communityReactions','alice_'+hash))).data().signals,[]);assert.equal((await F.getDocs(F.collection(bob,'reactionEvents'))).size,2);});


test('anonymous visitors read only aggregate counts; neither named collection nor private feedback is exposed',async()=>{
 await env.clearFirestore();await assertSucceeds(batch(alice));
 const counts=await assertSucceeds(F.getDocs(F.collection(anon,'publicReactionCounts')));
 assert.equal(counts.size,1);assert.deepEqual(Object.keys(counts.docs[0].data()).sort(),['key','like','updatedAt','useful']);assert.equal(counts.docs[0].data().like,1);
 await assertFails(F.getDocs(F.collection(anon,'communityReactions')));await assertFails(F.getDocs(F.collection(anon,'reactionEvents')));await assertFails(F.getDocs(F.collection(anon,'readers','alice','feedback')));
 await assertFails(F.updateDoc(F.doc(anon,'publicReactionCounts',hash),{like:99}));
});
test('public totals reject standalone writes, replay, wrong deltas, injected names and schema changes',async()=>{
 await env.clearFirestore();await assertSucceeds(batch(alice));const ref=F.doc(alice,'publicReactionCounts',hash);
 for(const patch of [{like:2,updatedAt:F.serverTimestamp()},{like:-1},{like:'1'},{name:'Alice'},{uid:'alice'},{key:'changed'},{useful:F.deleteField()},{extra:'x'.repeat(10000)}])await assertFails(F.updateDoc(ref,patch));
 await assertFails(F.deleteDoc(ref));
 await assertFails(F.setDoc(F.doc(bob,'publicReactionCounts','b'.repeat(64)),{key,like:1,useful:0,updatedAt:F.serverTimestamp()}));
});

test('two readers, double positives and undo produce exact totals; a valid vote cannot inflate its counter',async()=>{
 await env.clearFirestore();await assertSucceeds(batch(alice));
 const make=(signals,likeDelta,usefulDelta)=>{
  const b=F.writeBatch(bob),eventRef=F.doc(F.collection(bob,'reactionEvents'));
  const d={key,article:hash,uid:'bob',name:'Bob',signals};
  b.set(F.doc(bob,'readers','bob','feedback',hash),{...feedback(),signals});
  b.set(F.doc(bob,'communityReactions','bob_'+hash),{...d,event:eventRef.id,updatedAt:F.serverTimestamp()});
  b.set(eventRef,{...d,createdAt:F.serverTimestamp()});
  b.set(F.doc(bob,'publicReactionCounts',hash),{key,like:F.increment(likeDelta),useful:F.increment(usefulDelta),updatedAt:F.serverTimestamp()},{merge:true});
  return b.commit();
 };
 await assertFails(make(['more','useful'],2,1));
 await assertSucceeds(make(['more','useful'],1,1));
 let counts=(await F.getDoc(F.doc(anon,'publicReactionCounts',hash))).data();assert.equal(counts.like,2);assert.equal(counts.useful,1);
 await assertSucceeds(make([], -1,-1));counts=(await F.getDoc(F.doc(anon,'publicReactionCounts',hash))).data();assert.equal(counts.like,1);assert.equal(counts.useful,0);
 await assertFails(make([],1,0));
});


test('Not Relevant is private and may not be written into named current or historical records',async()=>{
 await env.clearFirestore();
 const b=F.writeBatch(alice);
 b.set(F.doc(alice,'readers','alice','feedback',hash),{...feedback(),signals:['irrelevant']});
 b.set(F.doc(alice,'communityReactions','alice_'+hash),{...shared(),signals:[],event,updatedAt:F.serverTimestamp()});
 b.set(F.doc(alice,'reactionEvents',event),{...shared(),signals:[],createdAt:F.serverTimestamp()});
 b.set(F.doc(alice,'publicReactionCounts',hash),{key,like:0,useful:0,updatedAt:F.serverTimestamp()});
 await assertSucceeds(b.commit());
 assert.deepEqual((await F.getDoc(F.doc(alice,'readers','alice','feedback',hash))).data().signals,['irrelevant']);
 assert.deepEqual((await F.getDoc(F.doc(bob,'communityReactions','alice_'+hash))).data().signals,[]);
 await env.clearFirestore();await assertFails(batch(alice,{reaction:{signals:['irrelevant']},event:{signals:['irrelevant']},feedback:{signals:['irrelevant']}}));
});
