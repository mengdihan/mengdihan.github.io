(() => {
 'use strict';
 const $=id=>document.getElementById(id),button=$('lit-interest-save');if(!button)return;
 const input=$('lit-interest-title'),status=$('lit-interest-status'),box=document.createElement('div');box.className='lit-content-results';button.parentElement.after(box);
 button.textContent='Add';input.placeholder='Article title, DOI, or paper link';
 const clean=s=>String(s||'').replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
 const doi=s=>String(s||'').toLowerCase().replace(/^https?:\/\/(dx\.)?doi\.org\//,'').trim();
 const PMC='https://www.ebi.ac.uk/europepmc/webservices/rest/';
 const node=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;return e;};
 let busy=false,revision=0;
 const account=window.BioERadarAccount;
 let uid;account.subscribe(s=>{if(uid!==s.user?.uid){uid=s.user?.uid;revision++;box.replaceChildren();}});
 async function get(url,xml=false){const c=new AbortController(),t=setTimeout(()=>c.abort(),18000);try{const r=await fetch(url,{signal:c.signal,credentials:'omit',referrerPolicy:'no-referrer'});if(!r.ok)throw Error('Source could not connect.');return xml?await r.text():await r.json();}finally{clearTimeout(t);}}
 async function run(task){if(busy||!uid)return;const owner=uid,rev=++revision;busy=true;button.disabled=true;box.querySelectorAll('button').forEach(b=>b.disabled=true);try{await task(()=>uid===owner&&revision===rev);}catch(e){if(uid===owner&&revision===rev)status.textContent=(e.message||'Could not read this article.')+' Nothing has been saved.';}finally{busy=false;button.disabled=!uid;box.querySelectorAll('button').forEach(b=>b.disabled=!uid);}}
 const stop=new Set('this that these those their there which where were have with from into using used also more such than each both other been will would could should may our study results methods showed data analysis based figure table supplementary article copyright author abstract introduction discussion conclusion between through under after before during for and the are was not but has had all its'.split(' '));
 function profile(text,basis,url){const counts=new Map();for(const w of text.toLowerCase().match(/[a-z][a-z-]{3,29}/g)||[])if(!stop.has(w))counts.set(w,(counts.get(w)||0)+1);const terms=[...counts].sort((a,b)=>b[1]-a[1]).slice(0,55).map(x=>x[0]);if(text.length<200||text.split(/\s+/).length<35||terms.length<8)throw Error('No sufficient abstract or open full text was found.');const p={v:2,action:'add',basis,url,terms,text:text.slice(0,850)};while(JSON.stringify(p).length>1900)p.text=p.text.slice(0,-50);return p;}
 function pmc(r){return {title:clean(r.title),journal:clean(r.journalInfo?.journal?.title||r.journalTitle),doi:doi(r.doi),abstract:clean(r.abstractText),year:r.pubYear||'',authors:r.authorString||'',pmcid:r.pmcid,open:r.isOpenAccess==='Y',url:'https://europepmc.org/article/'+encodeURIComponent(r.source||'MED')+'/'+encodeURIComponent(r.id||'')};}
 async function read(a){return run(async valid=>{
  status.textContent='Reading available article content…';
  if(a.doi&&!a.pmcid)try{const d=await get(PMC+'search?format=json&resultType=core&pageSize=1&query='+encodeURIComponent('DOI:"'+a.doi+'"'));const r=d.resultList?.result?.find(x=>doi(x.doi)===a.doi);if(r){const p=pmc(r);a={...a,...p,abstract:p.abstract||a.abstract};}}catch(e){}
  let text=a.abstract||'',basis='abstract';
  if(a.open&&/^PMC\d+$/.test(a.pmcid||''))try{const xml=await get(PMC+a.pmcid+'/fullTextXML',true),doc=new DOMParser().parseFromString(xml,'text/xml');const body=doc.querySelector('body');if(!doc.querySelector('parsererror')&&body&&body.textContent.length>300){text=clean(a.abstract+' '+body.textContent);basis='open-full-text';}}catch(e){}
  const p=profile(text,basis,a.doi?'https://doi.org/'+a.doi:a.url);if(!valid())return;
  const card=node('section',''),link=node('a',a.title);link.href=p.url;link.target='_blank';link.rel='noopener noreferrer';card.append(link,node('p',a.journal),node('p',basis==='abstract'?'Abstract read':'Open full text read'),node('p',p.text),node('p','Content terms: '+p.terms.slice(0,12).join(', ')));
  const save=node('button','Save content preference');save.type='button';save.addEventListener('click',()=>run(async stillValid=>{status.textContent='Saving…';const ok=await account.saveInterest(a.title,'add',{...p,doi:a.doi,journal:a.journal});if(!stillValid())return;status.textContent=ok?'Article content saved for future recommendations.':'Could not save. Please retry.';if(ok){box.replaceChildren();input.value='';}}));card.append(save);box.replaceChildren(card);status.textContent='Confirm the article and content, then save your preference.';
 });}
 async function search(){const query=input.value.trim();if(!query)return;return run(async valid=>{
  box.replaceChildren();status.textContent='Finding articles…';let parsed=query;try{const link=new URL(query),path=decodeURIComponent(link.pathname),match=path.match(/10\.\d{4,9}\/[^?#]+/i);if(match)parsed=match[0];else if(/(^|\.)nature\.com$/.test(link.hostname)&&path.includes('/articles/'))parsed='10.1038/'+path.split('/articles/')[1].replace(/\.pdf$/,'');}catch(e){}const d=doi(parsed),isDoi=/^10\.\d{4,9}\/\S+$/.test(d);
  const responses=await Promise.allSettled([
   get(isDoi?'https://api.crossref.org/works/'+encodeURIComponent(d):'https://api.crossref.org/works?rows=5&query.title='+encodeURIComponent(query)).then(r=>(isDoi?[r.message]:r.message.items).map(a=>({title:clean(a.title?.[0]),journal:clean(a['container-title']?.[0]),doi:doi(a.DOI),abstract:clean(a.abstract),year:a.published?.['date-parts']?.[0]?.[0]||'',authors:(a.author||[]).slice(0,3).map(x=>[x.given,x.family].filter(Boolean).join(' ')).join(', ')}))),
   get(PMC+'search?format=json&resultType=core&pageSize=5&query='+encodeURIComponent(isDoi?'DOI:"'+d+'"':'TITLE:"'+query.replace(/["\\]/g,' ')+'"')).then(r=>(r.resultList?.result||[]).map(pmc))
  ]);if(!valid())return;if(responses.every(r=>r.status==='rejected'))throw Error('Article sources could not connect.');
  const matches=new Map();for(const r of responses)if(r.status==='fulfilled')for(const a of r.value){if(!a.title||!a.journal)continue;const key=a.doi||a.title,old=matches.get(key);matches.set(key,old?{...old,...a,abstract:a.abstract||old.abstract}:a);}
  for(const a of [...matches.values()].slice(0,8)){const card=node('section','');card.append(node('strong',a.title),node('p',[a.journal,a.year,a.authors].filter(Boolean).join(' · ')));const pick=node('button','Read this article');pick.type='button';pick.addEventListener('click',()=>read(a));card.append(pick);box.append(card);}
  status.textContent=matches.size?'Choose the correct paper and journal.':'No matching paper found. Try a DOI. Nothing has been saved.';
 });}
 button.addEventListener('click',e=>{e.stopImmediatePropagation();search();},true);
 input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.isComposing){e.preventDefault();e.stopImmediatePropagation();search();}},true);
})();
