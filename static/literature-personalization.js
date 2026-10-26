(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.BioERadarPersonalization=factory();})(typeof window==='object'?window:this,function(){
  'use strict';
  const key=a=>String(a.doi||a.id).trim().toLowerCase().replace(/^https?:\/\/(?:dx\.)?doi\.org\//,'').replace(/(10\.21203\/.*|10\.1101\/.*)\/v\d+$/,'$1');
  const stop=new Set('a an the of for to in on and or with by from as is are was were this that these those we our using via into study new based'.split(' '));
  const terms=a=>[...new Set(((a.title||'')+' '+(a.summary||'')).toLowerCase().match(/[a-z][a-z0-9-]{2,}/g)||[])].filter(t=>!stop.has(t));
  function rank(articles,feedback={},history=articles){
    const docs=new Map(history.map(a=>[key(a),a]));articles.forEach(a=>docs.set(key(a),a));
    const sets=new Map([...docs].map(([k,a])=>[k,terms(a)])),df=new Map();
    sets.forEach(ts=>ts.forEach(t=>df.set(t,(df.get(t)||0)+1)));
    const vectors=new Map([...sets].map(([k,ts])=>{const v=new Map(ts.map(t=>[t,Math.log((docs.size+1)/((df.get(t)||0)+1))+1]));return[k,{v,n:Math.hypot(...v.values())||1}];}));
    const training=Object.entries(feedback).filter(([k,f])=>docs.has(k)&&(f.signals?.length||Number.isFinite(f.weight))).map(([k,f])=>[k,Number.isFinite(f.weight)?f.weight:signalWeight(f.signals)]);
    const scored=articles.map(a=>{
      const k=key(a),v=vectors.get(k),own=feedback[k]?.signals||[];let total=0,weight=0;
      for(const [other,w] of training){if(other===k)continue;const b=docs.get(other),u=vectors.get(other);let dot=0;v.v.forEach((n,t)=>dot+=n*(u.v.get(t)||0));const tags=new Set(b.topics||[]),ats=a.topics||[],overlap=ats.filter(t=>tags.has(t)).length/Math.max(1,new Set([...ats,...tags]).size);const similarity=.8*dot/(v.n*u.n)+.2*overlap;total+=w*similarity;weight+=Math.abs(w);}
      const adjustment=Math.max(-1.5,Math.min(1.5,weight?3*total/weight:0));
      return{article:a,score:(Number(a.relevance)||0)+adjustment+(own.includes('more')?.5:0)+(own.includes('useful')?.35:0),negative:own.includes('irrelevant')};
    });
    return scored.sort((a,b)=>Number(a.negative)-Number(b.negative)||b.score-a.score||a.article.title.localeCompare(b.article.title)).map(x=>x.article);
  }
  const signalWeight=signals=>signals.includes('irrelevant')?-1:(signals.includes('more')?1:0)+(signals.includes('useful')?2:0);
  const millis=value=>typeof value==='number'?value:value?.toMillis?value.toMillis():Date.parse(value)||Infinity;
  const cutoff=edition=>Date.parse(edition.publishedAt||edition.end.replace(' ','T')+':00+08:00');
  const interestTitle=title=>String(title||'').normalize('NFKC').trim().replace(/\s+/g,' ').toLocaleLowerCase();
  function interests(feedback,end=Infinity){
    const latest=new Map();
    for(const entry of Object.values(feedback)){
      let f=entry;try{const p=JSON.parse(entry.note);if(p.v===2)f={...entry,note:p.action,profile:p};}catch(error){}
      if(!f.key?.startsWith('interest:')||!['add','remove'].includes(f.note))continue;
      const time=millis(f.updatedAt),id=interestTitle(f.title);
      if(!Number.isFinite(time)||time>end||!id)continue;
      const prior=latest.get(id);
      if(!prior||time>millis(prior.updatedAt)||(time===millis(prior.updatedAt)&&f.key>prior.key))latest.set(id,f);
    }
    return [...latest.values()].filter(f=>f.note==='add');
  }
  function withInterests(baseline,feedback,edition,history){
    const active=interests(feedback,cutoff(edition)).filter(f=>f.profile?.text&&f.profile.terms?.length>=8),training={...baseline};
    const extra=active.map(f=>{const id='interest-title:'+interestTitle(f.title);training[id]={signals:['more']};return {id,title:f.title,summary:f.profile.text+' '+f.profile.terms.join(' '),topics:[]};});
    return {feedback:training,history:[...history,...extra]};
  }
  function beforeEdition(events,edition,uid,legacy={}){
    const end=cutoff(edition),latest=new Map();
    for(const e of events){const time=millis(e.createdAt);if(time>end||(uid&&e.uid!==uid))continue;const id=e.uid+'\n'+e.key;if(!latest.has(id)||time>millis(latest.get(id).createdAt))latest.set(id,e);}
    const result=Object.create(null);
    if(uid){for(const [k,f] of Object.entries(legacy))if(millis(f.updatedAt)<=end)result[k]=f;for(const e of latest.values())result[e.key]=e;}
    else{const grouped=new Map();for(const e of latest.values()){if(!e.signals.length)continue;const g=grouped.get(e.key)||[];g.push(signalWeight(e.signals));grouped.set(e.key,g);}for(const [k,weights] of grouped)result[k]={signals:[],weight:weights.reduce((a,b)=>a+b,0)/weights.length};}
    return result;
  }
  return{key,rank,cutoff,beforeEdition,signalWeight,interestTitle,interests,withInterests};
});
