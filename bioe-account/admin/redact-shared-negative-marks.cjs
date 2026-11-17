// Trusted one-time privacy migration; private reader feedback is never accessed.
const {initializeApp,applicationDefault}=require('firebase-admin/app');
const {getFirestore}=require('firebase-admin/firestore');
const projectId=process.env.GOOGLE_CLOUD_PROJECT,apply=process.argv.includes('--apply');
if(!projectId)throw Error('Set GOOGLE_CLOUD_PROJECT to the intended project.');
initializeApp({projectId,...(process.env.FIRESTORE_EMULATOR_HOST?{}:{credential:applicationDefault()})});
const db=getFirestore();
(async()=>{
 let found=0,changed=0;
 for(const collection of ['communityReactions','reactionEvents']){
  const snapshot=await db.collection(collection).where('signals','array-contains','irrelevant').get();
  found+=snapshot.size;if(!apply)continue;
  for(let i=0;i<snapshot.docs.length;i+=400){
   const batch=db.batch();
   for(const doc of snapshot.docs.slice(i,i+400))batch.update(doc.ref,{signals:[]});
   await batch.commit();changed+=Math.min(400,snapshot.docs.length-i);
  }
 }
 console.log(JSON.stringify({mode:apply?'applied':'dry-run',recordsFound:found,recordsChanged:changed,message:'No reader names, IDs or private marks are logged.'}));
})().catch(()=>{console.error('Shared-negative redaction failed. Check permissions and retry; no private feedback is modified.');process.exitCode=1;});
