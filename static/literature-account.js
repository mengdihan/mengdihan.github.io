(() => {
  'use strict';
  // Public Firebase web-app identifiers; access is enforced by Firestore rules.
  const config={apiKey:'AIzaSyBVzfqjQ9ws3rjblYOiSs0NK7qpfyl0_wE',authDomain:'bioe-radar.firebaseapp.com',projectId:'bioe-radar',storageBucket:'bioe-radar.firebasestorage.app',messagingSenderId:'790864157367',appId:'1:790864157367:web:90dac5fe58bfcb675d4b32'};
  let state={status:'loading',user:null,feedback:Object.create(null),reactions:[],events:[],communityStatus:'loading',message:'Connecting to your account…'},sdk,auth,db,subscriptions=[],generation=0;
  const listeners=new Set();
  const emit=patch=>{state={...state,...patch};listeners.forEach(fn=>fn(state));};
  const explain=error=>({
    'auth/popup-blocked':'Allow the Google sign-in popup, then try again.',
    'auth/popup-closed-by-user':'Sign-in was closed. You can try again.',
    'auth/unauthorized-domain':'This website is not yet authorized for Google sign-in.',
    'auth/network-request-failed':'Sign-in could not connect. Check your network and retry.',
    'auth/invalid-email':'Enter a valid email address.',
    'auth/invalid-credential':'Email or password is incorrect. Try resetting your password.',
    'auth/wrong-password':'Email or password is incorrect.',
    'auth/user-not-found':'Email or password is incorrect.',
    'auth/email-already-in-use':'This email already has an account. Sign in or reset your password.',
    'auth/weak-password':'Choose a password with at least 8 characters.',
    'auth/password-does-not-meet-requirements':'This password does not meet the account password requirements.',
    'auth/too-many-requests':'Too many attempts. Please wait and try again.',
    'auth/operation-not-allowed':'Email sign-in is unavailable. Please try again later.',
    'auth/user-disabled':'This account is disabled. Contact the site owner.',
    'permission-denied':'Could not access your private feedback. Please sign out and sign in again.'
  }[error.code]||'Could not connect to your account. Check your network and reload.');
  const ready=(async()=>{
    try{
      const base='https://www.gstatic.com/firebasejs/13.1.0/';
      const [app,A,F]=await Promise.all([import(base+'firebase-app.js'),import(base+'firebase-auth.js'),import(base+'firebase-firestore.js')]);
      sdk={A,F};const instance=app.initializeApp(config);auth=A.getAuth(instance);db=F.getFirestore(instance);
      A.onAuthStateChanged(auth,user=>{
        const current=++generation;subscriptions.forEach(unsubscribe=>unsubscribe());subscriptions=[];
        emit({status:user?'syncing':'signed-out',user:user?{uid:user.uid,displayName:user.displayName||'Reader'}:null,feedback:Object.create(null),reactions:[],events:[],communityStatus:user?'loading':'signed-out',message:user?'Loading your private feedback…':'Sign in to save private feedback and sync across devices.'});
        if(!user)return;
        subscriptions.push(F.onSnapshot(F.collection(db,'readers',user.uid,'feedback'),{includeMetadataChanges:true},snapshot=>{
          if(current!==generation)return;
          const feedback=Object.create(null);snapshot.forEach(doc=>{const entry=doc.data();feedback[entry.key]=entry;});
          emit({status:'signed-in',feedback,message:snapshot.metadata.hasPendingWrites?'Saving…':snapshot.metadata.fromCache?'Offline — changes will sync when connected.':'Synced across your devices.'});
        },error=>{if(current===generation)emit({status:'sync-error',feedback:Object.create(null),message:explain(error)});}));
        subscriptions.push(F.onSnapshot(F.collection(db,'communityReactions'),snapshot=>{
          if(current===generation)emit({reactions:snapshot.docs.map(doc=>doc.data()),communityStatus:'ready'});
        },()=>{if(current===generation)emit({communityStatus:'error'});}));
      },error=>emit({status:'error',user:null,feedback:Object.create(null),message:explain(error)}));
      return true;
    }catch(error){emit({status:'error',message:'Account services could not load. Check your network and reload; articles remain available.'});return false;}
  })();
  window.BioERadarAccount={
    subscribe(fn){listeners.add(fn);fn(state);return()=>listeners.delete(fn);},
    getState:()=>state,
    async signIn(){if(!await ready)return;try{const provider=new sdk.A.GoogleAuthProvider();provider.setCustomParameters({prompt:'select_account'});await sdk.A.signInWithPopup(auth,provider);}catch(error){emit({message:explain(error)});}},
    async signOut(){if(!await ready)return;try{await sdk.A.signOut(auth);}catch(error){emit({message:explain(error)});}},
    async signInEmail(email,password){
      if(!await ready)return {ok:false,message:state.message};
      try{await sdk.A.signInWithEmailAndPassword(auth,email.trim(),password);return {ok:true};}
      catch(error){return {ok:false,message:explain(error)};}
    },
    async registerEmail(email,password,displayName){
      if(!await ready)return {ok:false,message:state.message};
      const name=displayName.trim();
      if(!name||name.length>100||name.includes('@'))return {ok:false,message:'Enter a display name of 1–100 characters, rather than an email address.'};
      if(password.length<8)return {ok:false,message:'Choose a password with at least 8 characters.'};
      try{
        const {user}=await sdk.A.createUserWithEmailAndPassword(auth,email.trim(),password);
        await sdk.A.updateProfile(user,{displayName:name});
        // Refresh the name claim before a named reaction is written to Firestore.
        await user.getIdToken(true);
        if(auth.currentUser?.uid===user.uid)emit({user:{uid:user.uid,displayName:name}});
        return {ok:true};
      }catch(error){return {ok:false,message:explain(error)};}
    },
    async resetEmailPassword(email){
      if(!await ready)return {ok:false,message:state.message};
      try{await sdk.A.sendPasswordResetEmail(auth,email.trim());return {ok:true,message:'If this address has a password account, a reset email has been sent. Check your inbox and spam folder.'};}
      catch(error){if(error.code==='auth/user-not-found')return {ok:true,message:'If this address has a password account, a reset email has been sent. Check your inbox and spam folder.'};return {ok:false,message:explain(error)};}
    },
    async saveInterest(title,action='add',profile=null){
      if(action==='add'&&(!profile||profile.v!==2||!['abstract','open-full-text'].includes(profile.basis)||typeof profile.text!=='string'||profile.text.length<200||!Array.isArray(profile.terms)||profile.terms.length<8||JSON.stringify(profile).length>2000))return false;
      if(state.status!=='signed-in'||!auth.currentUser)return false;
      title=String(title||'').trim().replace(/\s+/g,' ');
      if(!title||title.length>500||!['add','remove'].includes(action))return false;
      const uid=auth.currentUser.uid,current=generation,key='interest:'+crypto.randomUUID();
      const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(key));
      if(current!==generation||auth.currentUser?.uid!==uid)return false;
      const id=Array.from(new Uint8Array(hash),x=>x.toString(16).padStart(2,'0')).join('');
      // Append a private event in the existing owner-only validated schema.
      // No shared reaction is written for an entered title.
      try{await sdk.F.setDoc(sdk.F.doc(db,'readers',uid,'feedback',id),{
        key,id:key,doi:String(profile?.doi||'').slice(0,1000),title,journal:String(profile?.journal||'Personal reading interests').slice(0,300),signals:[],note:action==='remove'?'remove':JSON.stringify(profile),updatedAt:sdk.F.serverTimestamp()
      });return true;}
      catch(error){if(current===generation)emit({message:'Reading interest was not saved. '+explain(error)});return false;}
    },
    async save(entry){
      if(state.status!=='signed-in'||!auth.currentUser)return false;
      const user=auth.currentUser.uid,current=generation;
      const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(entry.key));
      if(current!==generation||auth.currentUser?.uid!==user)return false;
      const id=Array.from(new Uint8Array(hash),x=>x.toString(16).padStart(2,'0')).join('');
      const record={key:entry.key,id:String(state.feedback[entry.key]?.id||entry.id||''),doi:String(entry.doi||''),title:entry.title,journal:entry.journal,signals:[...entry.signals],note:entry.note,updatedAt:sdk.F.serverTimestamp()};
      try{
        const F=sdk.F,batch=F.writeBatch(db);batch.set(F.doc(db,'readers',user,'feedback',id),record);
        if(JSON.stringify(entry.signals)!==JSON.stringify(state.feedback[entry.key]?.signals||[])){
          const event=F.doc(F.collection(db,'reactionEvents'));
          const shared={key:entry.key,article:id,uid:user,name:auth.currentUser.displayName||'Reader',signals:[...entry.signals]};
          batch.set(F.doc(db,'communityReactions',user+'_'+id),{...shared,event:event.id,updatedAt:F.serverTimestamp()});
          batch.set(event,{...shared,createdAt:F.serverTimestamp()});
        }
        await batch.commit();return true;
      }
      catch(error){if(current===generation)emit({message:'Feedback was not saved. '+explain(error)});return false;}
    }
  };
})();
