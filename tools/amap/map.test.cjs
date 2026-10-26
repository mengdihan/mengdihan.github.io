const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../../static/maps/amap/map.js'),'utf8');
function setup(config,conversion='complete'){
  const result={scripts:[],maps:[],markers:[],events:{},status:{hidden:false,textContent:''}};
  const position={lng:116.316,lat:39.994};
  const sdk={
    convertFrom(coords,kind,cb){result.coords=coords;result.kind=kind;cb(conversion,{locations:conversion==='complete'?[position]:[]});},
    Map:class{constructor(id,options){result.maps.push({id,options});}add(marker){result.added=marker;}on(event,cb){result.events[event]=cb;}},
    Marker:class{constructor(options){result.markers.push(options);}},
    Pixel:class{constructor(x,y){this.x=x;this.y=y;}}
  };
  result.context={window:{HMD_AMAP_CONFIG:config,AMap:sdk},document:{getElementById(){return result.status;},createElement(){return {};},head:{append(s){result.scripts.push(s);}}},setTimeout(){return 1;},clearTimeout(){},encodeURIComponent};
  vm.runInNewContext(source,result.context);
  if(result.scripts.length)result.scripts[0].onload();
  return result;
}
test('one Chinese map, converted location and a non-interactive pin',()=>{
  const r=setup({key:'test-key',securityJsCode:'test-code'});
  assert.equal(r.maps.length,1);assert.equal(r.maps[0].options.languageCode,undefined);
  assert.equal(r.maps[0].options.logoLanguage,undefined);
  assert.equal(r.maps[0].options.lang,undefined);
  assert.equal(r.maps[0].options.isHotspot,false);
  assert.equal(JSON.stringify(r.coords),'[116.3101824,39.9929816]');assert.equal(r.kind,'gps');
  assert.equal(r.markers.length,1);assert.equal(r.markers[0].position,r.maps[0].options.center);
  assert.equal(r.markers[0].clickable,false);assert.equal(r.markers[0].label,undefined);
  r.events.complete();assert.equal(r.status.hidden,true);
  assert.equal(r.context.window._AMapSecurityConfig.securityJsCode,'test-code');
});
test('missing key loads no SDK; conversion failure never guesses a location',()=>{
  const missing=setup({});assert.equal(missing.scripts.length,0);assert.match(missing.status.textContent,/Map unavailable/);
  const failed=setup({key:'test-key',securityJsCode:'test-code'},'error');assert.equal(failed.maps.length,0);assert.match(failed.status.textContent,/Map unavailable/);
});
test('service proxy takes priority and SDK failure has a readable fallback',()=>{
  const r=setup({key:'test-key',serviceHost:'https://maps.example.test/_AMapService',securityJsCode:'unused'});
  assert.equal(r.context.window._AMapSecurityConfig.serviceHost,'https://maps.example.test/_AMapService');
  assert.equal(r.context.window._AMapSecurityConfig.securityJsCode,undefined);
  r.scripts[0].onerror();assert.match(r.status.textContent,/navigation buttons below/);
});
