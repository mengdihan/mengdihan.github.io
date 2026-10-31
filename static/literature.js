(() => {
  'use strict';
  const payload=document.getElementById('lit-data');
  if(!payload)return;
  const data=JSON.parse(payload.content.textContent);
  const byId=id=>document.getElementById(id);
  const search=byId('lit-search'),edition=byId('lit-edition'),sort=byId('lit-sort'),results=byId('lit-results');
  const dialog=byId('lit-journals-dialog'),journalOpen=byId('lit-journals-open');
  let topic='',journals=new Set(),draft=new Set(),sources=[];
  // Broad navigation categories; original article tags remain available to search
  // and personalization. A paper may belong to more than one category.
  const topicGroups=[
    ['Magnetics & implants', /magnet|wireless|implant|battery.free|deep.tissue/i],
    ['Wearables & e-skins', /wearab|e.skin|electronic skin|tactile|textile|human.machine|multiaxial force/i],
    ['Bioelectronics & neural', /bioelectronic|neural|neuro|electromyograph|\bEEG\b|\bECG\b|electrochemical|spinal|closed.loop therap/i],
    ['Biomechanics & physiology', /mechanic|resonat|pressure|hemodynamic|cardiac|pulse|physiolog|monitor|rheometr|viscoelastic|free behavior|locomotion|stroke|endothelial|ultrasound|biochemical/i],
    ['Robotics & actuation', /robot|actuat|motor|closed.loop (?:system|control)|origami|shape morph/i],
    ['Materials & fabrication', /material|fabricat|MEMS|microelectronic|microneedle|stretchable|flexible electronic|fatigue|packag/i],
    ['Methods & signals', /method|signal|decod|reconstruct|inverse|model|imaging|readout|artifact|optical|sensor|hardware|comput|energy|digital twin/i]
  ];
  function articleTopicGroups(article){
    const tags=(article.topics||[]).join(' / ');
    const groups=topicGroups.filter(([,pattern])=>pattern.test(tags)).map(([name])=>name);
    return groups.length?groups:['Methods & signals'];
  }

  const node=(tag,cls,value)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(value!==undefined)el.textContent=value;return el;};
  const account=window.BioERadarAccount,personalization=window.BioERadarPersonalization;
  let feedback=Object.create(null),accountState={status:'loading',user:null},tooltipIndex=0;
  let displayedOrder=[],rankingHydrated=false;
  const feedbackBoxes=[...document.querySelectorAll('[data-feedback-filter]')];
  const canReact=()=>accountState.status==='signed-in'&&rankingHydrated;
  const feedbackId=personalization.key;
  function feedbackControls(a){
    const key=feedbackId(a),box=node('div','lit-feedback'),buttons=node('div','lit-feedback-buttons');
    const current=()=>feedback[key]||{key,id:a.id,doi:a.doi||'',title:a.title,journal:a.journal,signals:[],note:''};
    const update=async entry=>{await account.save(entry);};
    for(const [signal,title] of [['more','Like'],['useful','Useful'],['irrelevant','Not relevant'],['later','Read Later']]){
      const voters=(accountState.reactions||[]).filter(r=>r.key===key&&r.signals.includes(signal));
      const names=[...new Map(voters.map(r=>[r.uid,r.name])).values()].sort((a,b)=>a.localeCompare(b));
      const wrap=node('span','lit-reaction-wrap'),tip=node('span','lit-reaction-tip',signal==='later'?'Your private reading list':names.length?names.join(', '):accountState.user?'No reactions yet':'Sign in to see reader reactions');tip.id='lit-reaction-tip-'+(++tooltipIndex);tip.setAttribute('role','tooltip');
      const b=node('button','',title+(signal!=='later'&&names.length?' '+names.length:''));b.setAttribute('aria-label',title);b.setAttribute('aria-describedby',tip.id);b.type='button';b.dataset.signal=signal;b.disabled=!canReact();b.setAttribute('aria-pressed',String(signal==='later'?personalization.readLater(current()):current().signals.includes(signal)));
      b.addEventListener('click',async()=>{let entry={...current(),signals:[...current().signals]};if(signal==='later'){try{entry=personalization.toggleReadLater(entry);}catch(error){byId('lit-feedback-status').textContent=error.message;return;}}else if(entry.signals.includes(signal))entry.signals=entry.signals.filter(x=>x!==signal);else entry.signals=signal==='irrelevant'?['irrelevant']:[...entry.signals.filter(x=>x!=='irrelevant'),signal];b.disabled=true;await update(entry);if(b.isConnected)b.disabled=!canReact();});wrap.append(b,tip);buttons.append(wrap);
    }
    box.append(buttons);return box;
  }
  let allEditions;
  const selected=()=>{
    if(edition.value!=='all')return data.editions.find(e=>e.id===edition.value);
    if(!allEditions){
      const reports=[...data.editions].sort((a,b)=>b.id.localeCompare(a.id)),articles=new Map(),coverage=new Map();
      for(const report of reports){
        for(const article of report.articles)if(!articles.has(feedbackId(article)))articles.set(feedbackId(article),article);
        for(const source of report.coverage){
          const total=coverage.get(source.journal)||{...source,readCount:0};
          total.readCount+=Number.isInteger(source.readCount)&&source.readCount>=0?source.readCount:0;
          coverage.set(source.journal,total);
        }
      }
      allEditions={id:'all',articles:[...articles.values()],coverage:[...coverage.values()],
        start:reports.map(e=>e.start).sort()[0],end:reports.map(e=>e.end).sort().at(-1)};
    }
    return allEditions;
  };
  const sourceName=s=>s.replace('bioRxiv - Bioengineering','bioRxiv · Bioengineering').replace('Arxiv - Applied Physics','arXiv · Applied Physics');
  function row(a){
    const card=node('article','lit-paper');card.dataset.id=a.id;
    const meta=node('p','lit-meta');meta.append(node('span','lit-journal',a.journal));
    const date=node(a.date?'time':'span','',a.dateLabel||a.date||'Publication date unverified');if(a.date)date.dateTime=a.date;meta.append(date);
    const heading=node('h2'),link=node('a','',a.title);link.href=a.url;link.target='_blank';link.rel='noopener noreferrer';heading.append(link);
    const bottom=node('div','lit-paper-bottom');bottom.append(node('p','lit-tags',a.topics.join(' / ')));
    const authors=node('p','lit-author-line',(a.authors.length?a.authors.join(', '):'Author list unavailable.')+(a.authorsComplete?'':' (Complete author list not verified.)'));
    card.append(meta,heading,authors,node('p','lit-summary',a.summary),bottom,feedbackControls(a));return card;
  }
  function render(reorder=true){
    const focused=document.activeElement,focusedArticle=focused?.closest('.lit-paper')?.dataset.id,focusedSignal=focused?.dataset.signal;
    const e=selected(),q=search.value.trim().toLocaleLowerCase();
    const feedbackFilter=new Set(feedbackBoxes.filter(box=>box.checked).map(box=>box.dataset.feedbackFilter)),version=sort.value==='personal'?'personal':'community';
    const positions=new Map(displayedOrder.map((id,i)=>[id,i]));
    // Keep membership as well as order stable when a mark is removed in a filtered list.
    const items=e.articles.filter(a=>(reorder===false?positions.has(a.id):personalization.matchesFeedback(feedback[feedbackId(a)],feedbackFilter))&&(!topic||articleTopicGroups(a).includes(topic))&&journals.has(sourceName(a.journal))&&(!q||[a.title,a.journal,a.summary,a.doi,...a.authors,...a.topics].join(' ').toLocaleLowerCase().includes(q)));
    if(reorder!==false){
      if(sort.value==='personal'){
        const history=data.editions.flatMap(report=>report.articles);
        items.splice(0,items.length,...personalization.rankPersonal(items,feedback,history));
      }else if(sort.value==='community'){
        items.splice(0,items.length,...personalization.rankCommunity(items,accountState.reactions||[]));
      }else items.sort((a,b)=>sort.value==='date'?String(b.date||'').localeCompare(String(a.date||''))||a.title.localeCompare(b.title):sort.value==='journal'?a.journal.localeCompare(b.journal)||String(b.date||'').localeCompare(String(a.date||'')):b.relevance-a.relevance||a.title.localeCompare(b.title));
      displayedOrder=items.map(a=>a.id);
    }else{
      // Sync controls and names without moving any cards after a reaction.
      items.sort((a,b)=>(positions.get(a.id)??Infinity)-(positions.get(b.id)??Infinity));
    }
    tooltipIndex=0;results.replaceChildren(...items.map(row));
    if(focusedArticle&&focusedSignal)Array.from(results.children).find(card=>card.dataset.id===focusedArticle)?.querySelector('button[data-signal="'+focusedSignal+'"]')?.focus({preventScroll:true});
    document.querySelectorAll('[data-reading-version]').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.readingVersion===version));b.disabled=b.dataset.readingVersion==='personal'&&!accountState.user;});
    byId('lit-version-note').textContent=accountState.communityStatus==='error'?'Community feedback is temporarily unavailable. Please try again later.':'';
    byId('lit-version-note').hidden=!byId('lit-version-note').textContent;
    byId('lit-count').textContent=items.length+' of '+e.articles.length+' selected articles';
    byId('lit-empty').hidden=items.length!==0;
    byId('lit-window').textContent=(e.id==='all'?'All editions · ':'')+e.start+' – '+e.end+' (Beijing time)';
    byId('lit-coverage-list').textContent=sources.join('; ')+'.';
    document.querySelectorAll('.lit-topics button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.topic===topic)));
    journalOpen.textContent=journals.size===sources.length?'All '+sources.length+' sources':journals.size+' selected';
  }
  function journalGroup(j){
    if(/^Nature\b|^npj\b|^Microsystems & Nanoengineering$/.test(j))return 'Nature Portfolio';
    if(/^Science(?:$| )/.test(j))return 'Science journals';
    if(['Cell','Neuron','Matter','Device'].includes(j))return 'Cell Press';
    if(/^Advanced /.test(j))return 'Wiley';
    if(/^ACS |^Nano Letters$/.test(j))return 'ACS';
    if(/^Biosensors and Bioelectronics$|^Sensors and Actuators/.test(j))return 'Elsevier';
    if(j==='Journal of Micromechanics and Microengineering')return 'IOP Publishing';
    if(/^IEEE |^Journal of Microelectromechanical Systems$/.test(j))return 'IEEE';
    if(j==='Proceedings of the National Academy of Sciences')return 'PNAS';
    if(/arXiv|bioRxiv|Research Square/.test(j))return 'Preprints';
    return 'Other journals';
  }
  function paintJournals(){
    const e=selected(),coverage=new Map(e.coverage.map(c=>[sourceName(c.journal),c])),counts=new Map();e.articles.forEach(a=>{const j=sourceName(a.journal);counts.set(j,(counts.get(j)||0)+1);});
    const order=['Nature Portfolio','Science journals','Cell Press','Wiley','ACS','Elsevier','IOP Publishing','IEEE','PNAS','Preprints','Other journals'];
    const sections=order.map(group=>{
      const all=sources.filter(j=>journalGroup(j)===group);
      const visible=all;
      if(!visible.length)return null;
      const section=node('section','lit-publisher-group');section.dataset.publisher=group;
      const heading=node('div','lit-publisher-heading'),label=node('label','lit-publisher-toggle'),toggle=node('input');
      toggle.type='checkbox';toggle.checked=all.every(j=>draft.has(j));toggle.indeterminate=!toggle.checked&&all.some(j=>draft.has(j));toggle.setAttribute('aria-label','Select all '+group+' sources');
      toggle.addEventListener('change',()=>{all.forEach(j=>toggle.checked?draft.add(j):draft.delete(j));paintJournals();});
      const title=node('span','',group);label.append(toggle,title);
      heading.append(label,node('span','lit-publisher-count',all.filter(j=>draft.has(j)).length+' / '+all.length+' selected'));
      const grid=node('div','lit-publisher-journals');
      grid.append(...visible.map(j=>{
        const label=node('label','lit-journal-option');
        const input=node('input');input.type='checkbox';input.value=j;input.checked=draft.has(j);
        input.addEventListener('change',()=>{input.checked?draft.add(j):draft.delete(j);selectionCount();
          toggle.checked=all.every(name=>draft.has(name));toggle.indeterminate=!toggle.checked&&all.some(name=>draft.has(name));
          heading.querySelector('.lit-publisher-count').textContent=all.filter(name=>draft.has(name)).length+' / '+all.length+' selected';});
        const record=coverage.get(j),read=Number.isInteger(record?.readCount)&&record.readCount>=0?record.readCount:0;
        const text=node('span','',j);text.append(node('small','',read+' articles, '+(counts.get(j)||0)+' selected'));label.append(input,text);return label;
      }));
      section.append(heading,grid);return section;
    }).filter(Boolean);
    byId('lit-journals-options').replaceChildren(...sections);
    if(!sections.length)byId('lit-journals-options').append(node('p','lit-journal-no-match','No matching journals or publishers.'));
    selectionCount();
  }
  function selectionCount(){byId('lit-journals-selection').textContent=draft.size+' of '+sources.length+' selected';}
  function fitTopics(){
    const bar=document.querySelector('.lit-topics');if(!bar)return;
    const buttons=[...bar.children];buttons.forEach(b=>b.style.display='');
    if(window.matchMedia('(max-width:760px)').matches)return;
    const edge=bar.getBoundingClientRect().right;let full=false,reset=false;
    for(const b of buttons){if(full||b.getBoundingClientRect().right>edge+.5){full=true;b.style.display='none';if(b.dataset.topic===topic)reset=true;}}
    if(reset&&topic){topic='';render();}
  }
  const topicObserver=new ResizeObserver(()=>fitTopics());
  topicObserver.observe(document.querySelector('.lit-topics'));
  function setup(){
    const e=selected();sources=[...new Set([...e.coverage.map(c=>sourceName(c.journal)),...e.articles.map(a=>sourceName(a.journal))])].filter(j=>j!=='Small').sort();
    journals=new Set(sources);topic='';const available=new Set(e.articles.flatMap(articleTopicGroups));const topics=['',...topicGroups.map(([name])=>name).filter(name=>available.has(name))];
    document.querySelector('.lit-topics').replaceChildren(...topics.map(t=>{const b=node('button','',t||'All topics');b.type='button';b.dataset.topic=t;b.setAttribute('aria-pressed',String(!t));b.addEventListener('click',()=>{topic=t;render();});return b;}));render();fitTopics();
  }
  journalOpen.addEventListener('click',()=>{draft=new Set(journals);paintJournals();dialog.showModal();});
  byId('lit-journals-all').addEventListener('click',()=>{draft=new Set(sources);paintJournals();});
  byId('lit-journals-none').addEventListener('click',()=>{draft.clear();paintJournals();});
  byId('lit-journals-apply').addEventListener('click',()=>{journals=new Set(draft);render();dialog.close();});
  for(const id of ['lit-journals-close','lit-journals-cancel'])byId(id).addEventListener('click',()=>dialog.close());
  search.addEventListener('input',render);sort.addEventListener('change',render);edition.addEventListener('change',setup);
  feedbackBoxes.forEach(box=>box.addEventListener('change',render));
  for(const [id,checked] of [['lit-marks-all',true],['lit-marks-clear',false]]){
    byId(id).addEventListener('click',()=>{feedbackBoxes.forEach(box=>box.checked=checked);render();});
  }

  document.querySelectorAll('[data-reading-version]').forEach(b=>b.addEventListener('click',()=>{version=b.dataset.readingVersion;sort.value='personal';render();}));
  const st=byId('lit-sources-toggle');st.addEventListener('click',()=>{const open=st.getAttribute('aria-expanded')==='true';st.setAttribute('aria-expanded',String(!open));byId('lit-sources-body').hidden=open;});
  const googleConnect=byId('lit-google-connect');
  googleConnect?.addEventListener('click',async()=>{
    googleConnect.disabled=true;
    try{
      const result=await account.signIn();
      if(result?.ok===false){const status=byId('lit-feedback-status');status.textContent=result.message;status.classList.remove('lit-account-sync-status');}
    }catch(error){const status=byId('lit-feedback-status');status.textContent='Google sign-in could not connect. Please try again.';status.classList.remove('lit-account-sync-status');}
    finally{googleConnect.disabled=['loading','error'].includes(accountState.status);}
  });
  byId('lit-account-signout').addEventListener('click',()=>account.signOut());
  account.subscribe(state=>{
    const prior=accountState.user?.uid;accountState=state;feedback=state.feedback;
    if(prior!==state.user?.uid)rankingHydrated=false;
    const initialReady=!rankingHydrated&&state.status==='signed-in'&&['ready','error'].includes(state.communityStatus);
    if(initialReady)rankingHydrated=true;
    byId('lit-account-name').textContent=state.user?state.user.displayName:'Your reading account';
    document.querySelector('.lit-account-panel').dataset.state=state.status;
    byId('lit-email-open').hidden=!!state.user;byId('lit-email-open').disabled=['loading','error'].includes(state.status);
    if(googleConnect){googleConnect.hidden=!!state.user;googleConnect.disabled=['loading','error'].includes(state.status);}
    byId('lit-account-signout').hidden=!state.user;
    byId('lit-feedback-status').textContent=state.status==='signed-out'?'Private preferences across devices':state.message==='Synced across your devices.'?'Preferences synced':state.message;
    sort.querySelector('option[value="personal"]').disabled=!state.user;
    if(!state.user&&sort.value==='personal')sort.value='community';
    if(prior!==state.user?.uid)sort.value=state.user?'personal':'community';
    if(edition.value&&(prior!==state.user?.uid||document.activeElement?.tagName!=='TEXTAREA'))render(prior!==state.user?.uid||initialReady);
  });
  // Anchor the recurring schedule in Beijing, then derive both DST-sensitive cities.
  const now=new Date(),parts=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
  const part=t=>Number(parts.find(p=>p.type===t).value),day=new Date(Date.UTC(part('year'),part('month')-1,part('day')));
  let next=new Date(day.getTime()+((5-day.getUTCDay()+7)%7)*86400000-4.5*3600000);
  if(next<=now)next=new Date(next.getTime()+7*86400000);
  byId('lit-schedule-times').textContent=[['Asia/Shanghai','Beijing'],['America/New_York','New York'],['Europe/London','London']].map(([timeZone,city])=>new Intl.DateTimeFormat('en-GB',{timeZone,weekday:'long',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(next)+' '+city).join(' / ');
  setup();
})();
