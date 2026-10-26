const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../../static/maps/amap/switcher.js'),'utf8');
function setup(){
 const r={frames:[]};
 vm.runInNewContext(source,{document:{getElementById(){return {replaceChildren(f){r.frames.push(f)}}},createElement(){return {}}},Image:class{constructor(){r.probe=this}},setTimeout(cb,ms){r.timeout=cb;r.deadline=ms;return 1},clearTimeout(){}});
 return r;
}
test('Google starts immediately using the street address',()=>{const r=setup();assert.equal(r.frames.length,1);assert.equal(new URL(r.frames[0].src).searchParams.get('q'),'北京市海淀区中关村北大街116号');assert.equal(r.frames[0].className,'google-map');assert.equal(r.deadline,3000)});
test('successful probe and frame keep Google in either completion order',()=>{for(const first of ['probe','frame']){const r=setup();if(first==='probe'){r.probe.onload();r.frames[0].onload()}else{r.frames[0].onload();r.probe.onload()}r.timeout();assert.equal(r.frames.length,1)}});
test('probe failure and three-second timeout replace Google with Amap',()=>{for(const fail of ['error','timeout']){const r=setup();fail==='error'?r.probe.onerror():r.timeout();assert.equal(r.frames.length,2);assert.match(r.frames[1].src,/amap.html/);assert.equal(r.frames[1].className,'amap')}});
test('iframe load alone is not proof of connectivity',()=>{const r=setup();r.frames[0].onload();r.timeout();assert.match(r.frames[1].src,/amap.html/)});
test('late callbacks cannot restore Google after fallback',()=>{const r=setup();const success=r.probe.onload;r.timeout();success();r.frames[0].onload();assert.equal(r.frames.length,2);assert.match(r.frames[1].src,/amap.html/)});
