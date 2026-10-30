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
 const names=['lit-data','lit-search','lit-edition','lit-sort','lit-results','lit-journals-dialog','lit-journals-open','lit-version-note','lit-count','lit-empty','lit-window','lit-coverage-list','lit-journals-options','lit-journals-selection','lit-journals-all','lit-journals-none','lit-journals-apply','lit-journals-close','lit-journals-cancel','lit-reset','lit-sources-toggle','lit-sources-body','lit-recommendations-toggle','lit-recommendations-body','lit-account-signout','lit-account-name','lit-email-open','lit-feedback-status','lit-schedule-times'];
 names.forEach(id=>add(id));const topics=add('topics','div','lit-topics'),panel=add('account-panel','div','lit-account-panel'),help=add('help','div','lit-account-help');help.append(ids.get('lit-recommendations-toggle'),ids.get('lit-recommendations-body'));
 const option=new Element('option');option.setAttribute('value','personal');ids.get('lit-sort').append(option);
 ids.get('lit-edition').value='2026-10-30';ids.get('lit-sort').value='community';
 ids.get('lit-data').content={textContent:JSON.stringify({editions:[{id:'2026-10-30',start:'2026-10-23 03:30',end:'2026-10-30 03:30',publishedAt:'2026-10-30T03:30:00+08:00',coverage:[{journal:'Science'}],articles:[paper('a',4),paper('b',3),paper('c',2),paper('d',1)]}]})};
 document={activeElement:null,getElementById:id=>ids.get(id),createElement:tag=>new Element(tag),querySelector:s=>roots.find(e=>e.matches(s))||null,querySelectorAll:s=>s==='.lit-topics button'?topics.children:[],addEventListener(){}};
 let state=initial||{status:'signed-in',user:{uid:'alice',displayName:'Alice'},feedback:{},reactions:[],events:[],communityStatus:'ready',message:'Synced across your devices.'};let subscriber;
 const emit=patch=>{state={...state,...patch};subscriber(state);};
 const account={subscribe(fn){subscriber=fn;fn(state);},async save(entry){const feedback={...state.feedback,[entry.key]:{...entry,updatedAt:Date.now()}};emit({feedback});const others=state.reactions.filter(r=>!(r.uid===state.user.uid&&r.key===entry.key));emit({reactions:[...others,{...entry,uid:state.user.uid,name:state.user.displayName,updatedAt:Date.now()}]});return true;},signOut(){emit({status:'signed-out',user:null,feedback:{},reactions:[],communityStatus:'signed-out'});}};
 const window={BioERadarAccount:account,BioERadarPersonalization:P,matchMedia:()=>({matches:true}),addEventListener(){}};
 vm.runInNewContext(fs.readFileSync(path.resolve(__dirname,'../../static/literature.js'),'utf8'),{window,document,ResizeObserver:class{observe(){}},Intl,Date,innerWidth:1000,innerHeight:800});
 const order=()=>ids.get('lit-results').children.map(e=>e.dataset.id);
 const button=(id,signal)=>ids.get('lit-results').children.find(e=>e.dataset.id===id).querySelector('button[data-signal="'+signal+'"]');
 return {ids,order,button,emit,get state(){return state;},async trigger(id,event){await ids.get(id).dispatch(event);},async click(id,signal){const b=button(id,signal);assert.equal(b.disabled,false);b.focus();await b.dispatch('click');}};
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
 await app.trigger('lit-reset','click');assert.deepEqual(app.order(),['a','b','d','c']);
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
