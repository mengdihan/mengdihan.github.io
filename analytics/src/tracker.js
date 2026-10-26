/* Install only after Access and collector acceptance checks. */
(()=>{const endpoint=document.currentScript?.dataset.endpoint;if(!endpoint)return;
try{if(navigator.globalPrivacyControl||navigator.doNotTrack==='1')return;
const now=Date.now();let visitor=localStorage.getItem('hmd-visitor');if(!visitor){visitor=crypto.randomUUID();localStorage.setItem('hmd-visitor',visitor);}
let session=JSON.parse(localStorage.getItem('hmd-session')||'null');if(!session||now-session.last>1800000)session={id:crypto.randomUUID()};session.last=now;localStorage.setItem('hmd-session',JSON.stringify(session));
fetch(endpoint,{method:'POST',credentials:'omit',keepalive:true,headers:{'Content-Type':'application/json'},body:JSON.stringify({visitor,session:session.id,event:crypto.randomUUID(),path:location.pathname})}).catch(()=>{});
}catch{/* Storage disabled: do not fingerprint or disrupt the site. */}})();
