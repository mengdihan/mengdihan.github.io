(() => {
  'use strict';
  const byId=id=>document.getElementById(id),dialog=byId('lit-email-dialog');
  if(!dialog)return;
  const form=byId('lit-email-form'),email=byId('lit-email-address'),password=byId('lit-email-password'),name=byId('lit-email-name'),submit=byId('lit-email-submit'),status=byId('lit-email-status');
  let mode='signin',busy=false;
  const setMode=next=>{
    mode=next;password.value='';status.textContent='';
    const signup=mode==='signup',reset=mode==='reset';
    byId('lit-email-name-row').hidden=!signup;name.required=signup;name.disabled=!signup;
    byId('lit-email-password-row').hidden=reset;password.required=!reset;password.disabled=reset;password.minLength=signup?8:1;
    password.autocomplete=signup?'new-password':'current-password';
    byId('lit-email-title').textContent=reset?'Reset your password':signup?'Create your reading account':'Log in';
    submit.textContent=reset?'Send reset email':signup?'Create account':'Sign in';
    byId('lit-email-forgot').hidden=reset;byId('lit-email-back').hidden=!reset;
    byId('lit-email-privacy').hidden=!signup;
    dialog.querySelectorAll('[data-email-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.emailMode===mode)));
  };
  byId('lit-email-open').addEventListener('click',()=>{setMode('signin');dialog.showModal();email.focus();});
  window.BioERadarAccount.subscribe(state=>{if(state.user&&dialog.open)dialog.close();});
  byId('lit-email-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('cancel',event=>{if(busy)event.preventDefault();});
  dialog.addEventListener('close',()=>{form.reset();password.value='';status.textContent='';});
  dialog.querySelectorAll('[data-email-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.emailMode)));
  byId('lit-email-forgot').addEventListener('click',()=>setMode('reset'));
  byId('lit-email-back').addEventListener('click',()=>setMode('signin'));
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(busy||!form.reportValidity())return;
    busy=true;status.textContent=mode==='reset'?'Sending…':'Connecting…';
    const controls=dialog.querySelectorAll('button');controls.forEach(b=>b.disabled=true);
    try{
      const account=window.BioERadarAccount;
      const result=mode==='signup'?await account.registerEmail(email.value,password.value,name.value):mode==='reset'?await account.resetEmailPassword(email.value):await account.signInEmail(email.value,password.value);
      if(result.ok&&mode!=='reset')dialog.close();else status.textContent=result.message||'Could not sign in. Please try again.';
    }catch(error){status.textContent='Could not connect. Please try again.';}
    finally{busy=false;password.value='';controls.forEach(b=>b.disabled=false);}
  });
})();
