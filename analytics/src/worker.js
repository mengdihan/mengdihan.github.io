import { createRemoteJWKSet, jwtVerify } from 'jose';
import { dashboard } from './dashboard.js';
const keysets = new Map();
const headers = {'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'};
const response = (body,status=200,extra={}) => new Response(body,{status,headers:{...headers,...extra}});
export async function authorize(request,env) {
  if (!env.ACCESS_ISSUER || !env.ACCESS_AUD || !env.ADMIN_EMAIL) return false;
  const token=request.headers.get('Cf-Access-Jwt-Assertion');
  if(!token) return false;
  try {
    if(!keysets.has(env.ACCESS_ISSUER)) keysets.set(env.ACCESS_ISSUER,createRemoteJWKSet(new URL(env.ACCESS_ISSUER+'/cdn-cgi/access/certs')));
    const {payload}=await jwtVerify(token,keysets.get(env.ACCESS_ISSUER),{issuer:env.ACCESS_ISSUER,audience:env.ACCESS_AUD,algorithms:['RS256'],requiredClaims:['exp','iat','sub','email']});
    return payload.email.toLowerCase()===env.ADMIN_EMAIL.toLowerCase();
  } catch {return false;}
}
export function csvCell(value) {let s=String(value??'');if(/^[=+@\-\t\r]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';}
async function digest(value,secret) {
  const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(secret),{name:'HMAC',hash:'SHA-256'},false,['sign']);
  return Array.from(new Uint8Array(await crypto.subtle.sign('HMAC',key,new TextEncoder().encode(value))),x=>x.toString(16).padStart(2,'0')).join('');
}
const uuid=/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
async function collect(request,env) {
  if(request.headers.get('Origin')!==env.SITE_ORIGIN) return response('Forbidden',403);
  const cors={'Access-Control-Allow-Origin':env.SITE_ORIGIN,'Vary':'Origin'};
  if(request.method==='OPTIONS')return response(null,204,{...cors,'Access-Control-Allow-Methods':'POST','Access-Control-Allow-Headers':'Content-Type'});
  if(request.method!=='POST')return response('Method not allowed',405);
  if(!env.VISITOR_SECRET || env.VISITOR_SECRET.length<32)return response('Not configured',503);
  if(Number(request.headers.get('Content-Length'))>2048)return response('Too large',413);
  const raw=await request.text();if(raw.length>2048)return response('Too large',413);
  let data;try {data=JSON.parse(raw);} catch {return response('Invalid JSON',400);}
  if(!uuid.test(data.visitor)||!uuid.test(data.session)||!uuid.test(data.event)||typeof data.path!=='string'||!data.path.startsWith('/')||data.path.startsWith('//')||data.path.length>500||/[?#\r\n]/.test(data.path))return response('Invalid event',400);
  const visitor=await digest(data.visitor,env.VISITOR_SECRET),token=await digest(data.session,env.VISITOR_SECRET);
  const at=new Date().toISOString(),cf=request.cf||{};
  await env.DB.batch([
    env.DB.prepare('INSERT OR IGNORE INTO visitors VALUES (?,?)').bind(visitor,at),
    env.DB.prepare('INSERT OR IGNORE INTO sessions(visitor,token,started_at) VALUES (?,?,?)').bind(visitor,token,at),
    env.DB.prepare('INSERT OR IGNORE INTO events SELECT ?,?,?,id,?,?,?,?,? FROM sessions WHERE visitor=? AND token=?').bind(data.event,at,visitor,data.path,request.headers.get('CF-Connecting-IP')||'',cf.country||'',cf.region||'',cf.city||'',visitor,token)
  ]);
  return response(null,204,cors);
}
export default {async fetch(request,env) {
  const url=new URL(request.url);
  try {
    if(url.pathname==='/collect')return await collect(request,env);
    if(!await authorize(request,env))return response('Unauthorized. Sign in through Cloudflare Access.',401);
    if(request.method!=='GET')return response('Method not allowed',405);
    if(url.pathname==='/admin/'||url.pathname==='/admin')return response(dashboard,200,{'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"});
    if(url.pathname==='/admin/app.js')return response((await import('./dashboard.js')).app,200,{'Content-Type':'text/javascript'});
    if(url.pathname==='/admin/api/summary') {
      const [totals,trend]=await env.DB.batch([
        env.DB.prepare('SELECT (SELECT COUNT(*) FROM events) pageviews,(SELECT COUNT(*) FROM sessions) visits,(SELECT COUNT(*) FROM visitors) visitors,(SELECT MIN(at) FROM events) since'),
        env.DB.prepare("SELECT substr(at,1,10) day,COUNT(*) pageviews,COUNT(DISTINCT session_id) visits FROM events WHERE at>=? GROUP BY day ORDER BY day").bind(new Date(Date.now()-30*86400000).toISOString())]);
      return response(JSON.stringify({totals:totals.results[0],trend:trend.results}),200,{'Content-Type':'application/json'});
    }
    if(url.pathname==='/admin/api/events'||url.pathname==='/admin/export.csv') {
      const before=url.searchParams.get('before')||'9223372036854775807',limit=500;
      const rows=await env.DB.prepare('SELECT e.rowid cursor,e.at,e.path,e.ip,e.country,e.region,e.city,substr(e.visitor,1,12) visitor,(SELECT COUNT(*) FROM sessions s WHERE s.visitor=e.visitor AND s.id<=e.session_id) visit_number FROM events e WHERE e.rowid<? ORDER BY e.rowid DESC LIMIT ?').bind(before,limit).all();
      const next=rows.results.length===limit?rows.results.at(-1).cursor:null;
      if(url.pathname.endsWith('.csv')) {const cols=['cursor','at','path','ip','country','region','city','visitor','visit_number'];return response('\ufeff'+cols.join(',')+'\r\n'+rows.results.map(r=>cols.map(c=>csvCell(r[c])).join(',')).join('\r\n'),200,{'Content-Type':'text/csv; charset=utf-8','Content-Disposition':'attachment; filename="hmd-visits.csv"','X-Next-Cursor':String(next||'')});}
      return response(JSON.stringify({rows:rows.results,next}),200,{'Content-Type':'application/json'});
    }
    return response('Not found',404);
  }catch{return response('Service unavailable',503);}
}};
