/* Password-encrypted local device preferences. No password or unlocked session is stored. */
(()=>{'use strict';
const password=document.getElementById('password'),button=document.getElementById('unlock'),message=document.getElementById('message');
const decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function unlock(){
 if(!password.value){message.textContent='请输入访问密码。';return;}
 if(!window.crypto?.subtle){message.textContent='此浏览器不支持加密解锁，请使用最新版浏览器通过 HTTPS 访问。';return;}
 button.disabled=true;message.textContent='正在解锁…';
 try{
 const data=JSON.parse(document.getElementById('encrypted-settings').textContent);
 const material=await crypto.subtle.importKey('raw',new TextEncoder().encode(password.value),'PBKDF2',false,['deriveKey']);
 const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:decode(data.salt),iterations:data.iterations,hash:'SHA-256'},material,{name:'AES-GCM',length:256},false,['decrypt']);
 const plain=await crypto.subtle.decrypt({name:'AES-GCM',iv:decode(data.iv)},key,decode(data.ciphertext));
 const content=JSON.parse(new TextDecoder().decode(plain));
 password.value='';const settings=document.getElementById('settings');settings.innerHTML=content.html;
 new Function(content.script)();settings.hidden=false;document.getElementById('login').hidden=true;message.textContent='';
 }catch{password.value='';message.textContent='无法解锁，请检查密码后重试。';password.focus();}
 finally{button.disabled=false;}
}
button.addEventListener('click',unlock);password.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();unlock();}});
})();
