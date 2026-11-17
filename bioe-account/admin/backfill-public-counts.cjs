// Trusted, one-time migration. Use ADC; never pass credential JSON on the command line.
const {initializeApp,applicationDefault}=require('firebase-admin/app');
const {getFirestore,FieldValue}=require('firebase-admin/firestore');
const {createHash}=require('node:crypto');
const apply=process.argv.includes('--apply'),emulator=!!process.env.FIRESTORE_EMULATOR_HOST;
const projectId=process.env.GOOGLE_CLOUD_PROJECT;
if(!projectId)throw Error('Set GOOGLE_CLOUD_PROJECT to the intended Firebase project.');
initializeApp({projectId,...(emulator?{}:{credential:applicationDefault()})});
const db=getFirestore();
const digest=key=>createHash('sha256').update(key).digest('hex');
(async()=>{
 const shared=await db.collection('communityReactions').get(),existing=await db.collection('publicReactionCounts').get();
 const articles=new Map();
 for(const doc of [...shared.docs,...existing.docs]){
  const d=doc.data(),article=d.article||doc.id;
  if(typeof d.key!=='string'||digest(d.key)!==article)throw Error('Invalid article identity; migration stopped.');
  if(articles.has(article)&&articles.get(article)!==d.key)throw Error('Conflicting article identity.');
  articles.set(article,d.key);
 }
 if(!apply){console.log(JSON.stringify({mode:'dry-run',articles:articles.size,message:'No writes. Run with --apply after deploying the new rules.'}));return;}
 for(const [article,key] of articles){
  await db.runTransaction(async transaction=>{
   const query=db.collection('communityReactions').where('article','==',article);
   const votes=await transaction.get(query),ref=db.collection('publicReactionCounts').doc(article);
   await transaction.get(ref); // Conflict with concurrent public-counter updates.
   const seen=new Set();let like=0,useful=0;
   for(const doc of votes.docs){const d=doc.data();
    if(d.key!==key||typeof d.uid!=='string'||doc.id!==d.uid+'_'+article||seen.has(d.uid)||!Array.isArray(d.signals))throw Error('Invalid reaction record; migration stopped.');
    seen.add(d.uid);like+=Number(d.signals.includes('more'));useful+=Number(d.signals.includes('useful'));
   }
   // Replacement deliberately publishes only this strict four-field projection.
   transaction.set(ref,{key,like,useful,updatedAt:FieldValue.serverTimestamp()});
  });
 }
 console.log(JSON.stringify({mode:'applied',articles:articles.size,message:'Public counts initialized; no reader identities were published.'}));
})().catch(()=>{console.error('Public-count migration failed. No credential or reader data is logged. Check authorization and schema.');process.exitCode=1;});
