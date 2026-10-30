const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const P=require('../../static/literature-personalization.js');
const paper=(id,relevance=1)=>({id,doi:id,title:id,summary:id,topics:['MEMS'],journal:'Science',date:'2026-10-29',authors:['Fixture Author'],authorsComplete:true,url:'https://example.test/'+id,relevance});

test('personal marks outrank editorial priority; both > single > neutral > negative',()=>{
 const articles=[paper('neutral',100),paper('negative',1000),paper('like',1),paper('useful',2),paper('both',0)];
 const feedback={negative:{signals:['irrelevant']},like:{signals:['more']},useful:{signals:['useful']},both:{signals:['more','useful']}};
 const result=P.rankPersonal(articles,feedback).map(a=>a.id);
 assert.equal(result[0],'both');assert.deepEqual(new Set(result.slice(1,3)),new Set(['like','useful']));assert.deepEqual(result.slice(3),['neutral','negative']);
 assert.equal(P.rankPersonal(articles,{both:{signals:[]}})[0].id,'negative');
});
test('community uses current totals, counts a double mark twice, and handles undo/duplicates',()=>{
 const r=(uid,key,signals,t=1)=>({uid,key,signals,updatedAt:t});
 const votes=[r('a','one',['more']),r('b','one',['useful']),r('c','two',['more','useful']),r('d','one',['irrelevant']),r('e','negative',['irrelevant'])];
 assert.equal(P.communityTotals(votes).one.score,1);assert.equal(P.communityTotals(votes).two.score,2);
 assert.deepEqual(P.rankCommunity([paper('one'),paper('two'),paper('neutral'),paper('negative')],votes).map(a=>a.id),['two','one','neutral','negative']);
 assert.equal(P.communityTotals([...votes,r('c','two',[],2)]).two.score,0);
 assert.equal(P.communityTotals([...votes,r('a','one',['more'],3)]).one.like,1);
 const many=[r('a','sparse',['more','useful']),...['b','c','d'].map(uid=>r(uid,'popular',['more']))];
 assert.equal(P.rankCommunity([paper('sparse',10),paper('popular',0)],many)[0].id,'popular');
});

// Small DOM fixture: runs the real page script with fake accounts, no browser or live data.
function ui(initial){
 let document;
 class Element{
  constructor(tag='div'){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.style={};this.attributes={};this.handlers={};this.value='';this.textContent='';this.className='';this.isConnected=true;}
  append(...children){for(const c of children){this.children.push(c);if(c&&typeof c==='object')c.parent=this;}}
  replaceChildren(...children){this.children.forEach(c=>c.isConnected=false);this.children=[];this.append(...children);}
  setAttribute(k,v){this.attributes[k]=String(v);}
  getAttribute(k){return this.attributes[k]??null;}
  addEventListener(k,fn){(this.handlers[k]??=[]).push(fn);}
  async dispatch(k){for(const fn of this.handlers[k]||[])await fn({target:this});}
  matches(s){if(s[0]==='.')return this.className.split(' ').includes(s.slice(1));const m=s.match(/^(\w+)?(?:\[([^=\]]+)(?:="([^"]*)")?\])?$/);if(!m)return false;if(m[1]&&this.tagName!==m[1].toUpperCase())return false;if(m[2])return m[2].startsWith('data-')?this.dataset[m[2].slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]===m[3]:this.attributes[m[2]]===m[3];return true;}
  querySelectorAll(s){return this.children.flatMap(c=>[...(c.matches(s)?[c]:[]),...c.querySelectorAll(s)]);}
  querySelector(s){return this.querySelectorAll(s)[0]||null;}
  closest(s){return this.matches(s)?this:this.parent?.closest(s)||null;}
  focus(){document.activeElement=this;}
  getBoundingClientRect(){return {left:0,right:1000,top:0,bottom:10,height:10};}
  showModal(){this.open=true;}close(){this.open=false;}
 }
 const ids=new Map(),roots=[];const add=(id,tag='div',cls='')=>{const e=new Element(tag);e.id=id;e.className=cls;ids.set(id,e);roots.push(e);return e;};
 const names=['lit-data','lit-search','lit-edition','lit-sort','lit-results','lit-journals-dialog','lit-journals-open','lit-version-note','lit-count','lit-empty','lit-window','lit-coverage-list','lit-journals-options','lit-journals-selection','lit-journals-all','lit-journals-none','lit-journals-apply','lit-journals-close','lit-journals-cancel','lit-marks-all','lit-marks-clear','lit-sources-toggle','lit-sources-body','lit-recommendations-toggle','lit-recommendations-body','lit-account-signout','lit-account-name','lit-email-open','lit-feedback-status','lit-schedule-times'];
 names.forEach(id=>add(id));const topics=add('topics','div','lit-topics'),panel=add('account-panel','div','lit-account-panel'),help=add('help','div','lit-account-help');help.append(ids.get('lit-recommendations-toggle'),ids.get('lit-recommendations-body'));
 const boxes=['more','useful','irrelevant','later'].map(signal=>{const box=add('mark-'+signal,'input');box.dataset.feedbackFilter=signal;box.checked=true;return box;});
 const option=new Element('option');option.setAttribute('value','personal');ids.get('lit-sort').append(option);
 ids.get('lit-edition').value='2026-10-30';ids.get('lit-sort').value='community';
 ids.get('lit-data').content={textContent:JSON.stringify({editions:[{id:'2026-10-30',start:'2026-10-23 03:30',end:'2026-10-30 03:30',publishedAt:'2026-10-30T03:30:00+08:00',coverage:[{journal:'Science'}],articles:[paper('a',4),paper('b',3),paper('c',2),paper('d',1)]}]})};
 document={activeElement:null,getElementById:id=>ids.get(id),createElement:tag=>new Element(tag),querySelector:s=>roots.find(e=>e.matches(s))||null,querySelectorAll:s=>s==='.lit-topics button'?topics.children:s==='[data-feedback-filter]'?boxes:[],addEventListener(){}};
 let state=initial||{status:'signed-in',user:{uid:'alice',displayName:'Alice'},feedback:{},reactions:[],events:[],communityStatus:'ready',message:'Synced across your devices.'};let subscriber;
 const emit=patch=>{state={...state,...patch};subscriber(state);};
 const account={subscribe(fn){subscriber=fn;fn(state);},async save(entry){const feedback={...state.feedback,[entry.key]:{...entry,updatedAt:Date.now()}};emit({feedback});const others=state.reactions.filter(r=>!(r.uid===state.user.uid&&r.key===entry.key));emit({reactions:[...others,{...entry,uid:state.user.uid,name:state.user.displayName,updatedAt:Date.now()}]});return true;},signOut(){emit({status:'signed-out',user:null,feedback:{},reactions:[],communityStatus:'signed-out'});}};
 const window={BioERadarAccount:account,BioERadarPersonalization:P,matchMedia:()=>({matches:true}),addEventListener(){}};
 vm.runInNewContext(fs.readFileSync(path.resolve(__dirname,'../../static/literature.js'),'utf8'),{window,document,ResizeObserver:class{observe(){}},Intl,Date,innerWidth:1000,innerHeight:800});
 const order=()=>ids.get('lit-results').children.map(e=>e.dataset.id);
 const button=(id,signal)=>ids.get('lit-results').children.find(e=>e.dataset.id===id).querySelector('button[data-signal="'+signal+'"]');
 return {ids,boxes,order,button,emit,get state(){return state;},async trigger(id,event){await ids.get(id).dispatch(event);},async click(id,signal){const b=button(id,signal);assert.equal(b.disabled,false);b.focus();await b.dispatch('click');}};
}
test('clicks/undo sync controls without jumping; search, sort, source Apply and reload use latest marks',async()=>{
 const app=ui();assert.deepEqual(app.order(),['a','b','c','d']);
 await app.click('d','more');assert.deepEqual(app.order(),['a','b','c','d']);assert.equal(app.button('d','more').getAttribute('aria-pressed'),'true');
 await app.trigger('lit-search','input');assert.equal(app.order()[0],'d');
 await app.click('c','useful');await app.click('c','more');assert.equal(app.order()[0],'d');
 await app.trigger('lit-sort','change');assert.equal(app.order()[0],'c');
 await app.click('c','irrelevant');assert.equal(app.order()[0],'c');
 await app.trigger('lit-journals-open','click');await app.trigger('lit-journals-apply','click');assert.deepEqual(app.order(),['d','a','b','c']);
 await app.click('d','more');assert.equal(app.order()[0],'d');assert.equal(app.button('d','more').getAttribute('aria-pressed'),'false');
 await app.trigger('lit-marks-all','click');assert.deepEqual(app.order(),['a','b','d','c']);
 await app.click('d','useful');const reloaded=ui(app.state);assert.equal(reloaded.order()[0],'d');
});
test('community totals update on explicit filter changes; switching account clears personal ordering',async()=>{
 const app=ui();app.ids.get('lit-sort').value='community';await app.trigger('lit-sort','change');
 app.emit({reactions:[{uid:'bob',name:'Bob',key:'d',signals:['more','useful'],updatedAt:Date.now()}]});assert.equal(app.order()[0],'a');
 await app.trigger('lit-search','input');assert.equal(app.order()[0],'d');
 app.ids.get('lit-sort').value='personal';await app.trigger('lit-sort','change');await app.click('d','useful');await app.trigger('lit-search','input');assert.equal(app.order()[0],'d');
 app.emit({user:{uid:'bob',displayName:'Bob'},feedback:{},reactions:[],communityStatus:'ready'});assert.equal(app.order()[0],'a');
});
test('feedback stays disabled during initial loading, then initial data establishes its order once',()=>{
 const app=ui({status:'syncing',user:{uid:'alice',displayName:'Alice'},feedback:{},reactions:[],communityStatus:'loading',message:'Loading'});
 assert.equal(app.button('d','more').disabled,true);
 app.emit({status:'signed-in',feedback:{d:{signals:['more']}},communityStatus:'loading'});assert.equal(app.button('d','more').disabled,true);
 app.emit({communityStatus:'ready'});assert.equal(app.order()[0],'d');assert.equal(app.button('d','more').disabled,false);
});

test('Read Later persists privately, can coexist with reactions, and ranks between positives and neutral',async()=>{
 const entry={signals:['more'],note:'legacy text'};
 const saved=P.toggleReadLater(entry);assert.equal(P.readLater(saved),true);assert.equal(JSON.parse(saved.note).legacyNote,'legacy text');assert.deepEqual(saved.signals,['more']);
 assert.equal(P.readLater(P.toggleReadLater(saved)),false);assert.equal(P.readLater({note:'legacy'}),false);
 const structured=P.toggleReadLater({note:JSON.stringify({other:'retained'}),signals:[]});assert.equal(JSON.parse(structured.note).other,'retained');
 const feedback={both:{signals:['more','useful']},positive:{signals:['useful']},later:{signals:[],note:saved.note},negative:{signals:['irrelevant'],note:saved.note}};
 assert.deepEqual(P.rankPersonal(['neutral','negative','later','positive','both'].map(id=>paper(id,id==='neutral'?100:0)),feedback).map(a=>a.id),['both','positive','later','neutral','negative']);
 const app=ui();await app.click('d','later');assert.equal(P.readLater(app.state.feedback.d),true);assert.deepEqual(app.order(),['a','b','c','d']);
 await app.trigger('lit-sort','change');assert.equal(app.order()[0],'d');
 await app.click('d','useful');assert.equal(P.readLater(app.state.feedback.d),true);await app.click('d','later');assert.equal(P.readLater(app.state.feedback.d),false);assert.deepEqual(Array.from(app.state.feedback.d.signals),['useful']);
});
test('mark filters use OR; select all checks all four including unmarked; undo preserves membership until explicit changes',async()=>{
 const app=ui();await app.click('b','more');await app.click('c','useful');await app.click('d','later');
 for(const box of app.boxes)box.checked=['more','later'].includes(box.dataset.feedbackFilter);
 await app.trigger('mark-more','change');assert.deepEqual(new Set(app.order()),new Set(['b','d']));
 await app.click('d','later');assert.deepEqual(new Set(app.order()),new Set(['b','d']));assert.equal(app.button('d','later').getAttribute('aria-pressed'),'false');
 await app.trigger('lit-search','input');assert.deepEqual(app.order(),['b']);
 for(const box of app.boxes)box.checked=false;await app.trigger('mark-more','change');assert.deepEqual(app.order(),[]);
 await app.trigger('lit-marks-all','click');assert.equal(app.boxes.every(box=>box.checked),true);assert.equal(app.order().length,4);
 for(const box of app.boxes)box.checked=box.dataset.feedbackFilter==='irrelevant';await app.trigger('mark-irrelevant','change');assert.deepEqual(app.order(),[]);
 app.emit({feedback:{...app.state.feedback,a:{signals:['irrelevant']}}});assert.deepEqual(app.order(),[]);
 await app.trigger('lit-sort','change');assert.deepEqual(app.order(),['a']);
});

test('production account adapter saves bookmarks only in owner feedback and preserves shared reactions',async()=>{
 const writes=[],records=new Map();let privateListener;
 const user={uid:'alice',displayName:'Alice'};
 const auth={currentUser:user};
 const F={getFirestore:()=>({}),collection:(_db,...parts)=>parts.join('/'),doc:(...args)=>({path:args.slice(1).join('/')}),serverTimestamp:()=>123,
  onSnapshot(collection,...args){const cb=args.find(x=>typeof x==='function');if(collection==='readers/alice/feedback'){privateListener=()=>cb({forEach:fn=>records.forEach(data=>fn({data:()=>data})),metadata:{}});privateListener();}else cb({docs:[]});return()=>{};},
  writeBatch(){const batch=[];return {set(ref,data){batch.push({path:ref.path,data});},async commit(){writes.push(batch);for(const w of batch)if(w.path.startsWith('readers/'))records.set(w.data.key,w.data);privateListener();}};}};
 const A={getAuth:()=>auth,onAuthStateChanged(_auth,fn){fn(user);}};
 const window={};
 const source=fs.readFileSync(path.resolve(__dirname,'../../static/literature-account.js'),'utf8').replace("await Promise.all([import(base+'firebase-app.js'),import(base+'firebase-auth.js'),import(base+'firebase-firestore.js')])","await Promise.resolve([mock.app,mock.A,mock.F])");
 vm.runInNewContext(source,{window,mock:{app:{initializeApp:()=>({})},A,F},crypto:require('node:crypto').webcrypto,TextEncoder});
 await new Promise(resolve=>setImmediate(resolve));
 const account=window.BioERadarAccount;
 let entry={key:'paper',id:'paper',doi:'',title:'Test paper',journal:'Science',signals:[],note:''};
 entry=P.toggleReadLater(entry);assert.equal(await account.save(entry),true);assert.equal(writes[0].length,1);assert.match(writes[0][0].path,/^readers\/alice\/feedback\/[a-f0-9]{64}$/);assert.equal(P.readLater(writes[0][0].data),true);
 entry={...entry,signals:['more']};assert.equal(await account.save(entry),true);assert.equal(writes[1].length,3);for(const w of writes[1].slice(1))assert.equal('note' in w.data,false);
 entry=P.toggleReadLater(entry);assert.equal(await account.save(entry),true);assert.equal(writes[2].length,1);assert.equal(P.readLater(writes[2][0].data),false);assert.deepEqual(Array.from(writes[2][0].data.signals),['more']);
});

test('All/Clear change only mark filters and retain search and sort',async()=>{
 const app=ui();app.ids.get('lit-search').value='b';app.ids.get('lit-sort').value='date';
 await app.trigger('lit-marks-clear','click');assert.equal(app.boxes.some(b=>b.checked),false);assert.deepEqual(app.order(),[]);
 await app.trigger('lit-marks-all','click');assert.equal(app.boxes.every(b=>b.checked),true);assert.deepEqual(app.order(),['b']);
 assert.equal(app.ids.get('lit-search').value,'b');assert.equal(app.ids.get('lit-sort').value,'date');
});
