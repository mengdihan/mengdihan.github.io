"""Fail on missing assets or unapproved third-party runtime dependencies."""
import hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from lxml import html
ROOT=Path(sys.argv[1]).resolve()
errors=[]; count=0
urls=re.compile(r'url\(\s*([\"\']?)(.*?)\1\s*\)',re.I)
def check(raw,file,kind='asset'):
    if not raw or raw.startswith(('data:','#','mailto:','tel:')):return
    u=urlparse(urljoin('https://hanmd1990.github.io/'+file.relative_to(ROOT).as_posix(),raw))
    if re.search(r'(?:sxlcdn|strikingly|sxl\.cn|sxldns|hmd-lab\.com)',u.netloc,re.I):
        errors.append(f'{file.relative_to(ROOT)}: legacy platform link {raw}')
    if u.netloc!='hanmd1990.github.io':
        if kind=='asset':errors.append(f'{file.relative_to(ROOT)}: external resource {raw}')
        return
    p=ROOT/unquote(u.path.lstrip('/'))
    if p.is_dir():p=p/'index.html'
    if not p.is_file():errors.append(f'{file.relative_to(ROOT)}: missing {raw}')
for f in ROOT.rglob('*'):
    if any(x in f.relative_to(ROOT).parts for x in ('.git','.github','work','outputs','tools','analytics')):continue
    if f.suffix=='.html':
        count+=1;t=html.document_fromstring(f.read_bytes())
        for e in t.iter():
            if not isinstance(e.tag,str):continue
            for a in ('src','poster','data','background'):
                if e.get(a):
                    check(e.get(a),f)
            if e.get('srcset'):errors.append(f'{f}: srcset needs explicit verification')
            if e.tag=='link' and e.get('rel')!='canonical':check(e.get('href'),f)
            if e.tag=='a':check(e.get('href'),f,'link')
            if e.tag=='form' and not (f.relative_to(ROOT).as_posix()=='BioE_Radar/index.html' and e.get('id')=='lit-email-form' and e.get('method')=='dialog'):
                errors.append(f'{f}: form requires an independent backend')
            s=e.get('style','')+((e.text or '') if e.tag=='style' else '')
            for m in urls.finditer(s):check(m[2],f)
            if e.tag=='script' and not e.get('src') and re.search(r'fetch\s*\(|XMLHttpRequest|https?://',e.text or ''):errors.append(f'{f}: external inline script')
        if re.search(r'(?:https?:)?//[^\s"<>]*(?:sxlcdn|strikingly|sxl\.cn|sxldns)',f.read_text(encoding='utf-8')):errors.append(f'{f}: legacy platform URL')
    elif f.suffix=='.css':
        s=f.read_text(encoding='utf-8')
        for m in urls.finditer(s):check(m[2],f)
        if re.search(r'@import',s):errors.append(f'{f}: CSS import requires verification')
    elif f.suffix=='.js':
        script=f.read_text(encoding='utf-8')
        # Owner-requested Amap fallback; only the official SDK loader.
        if f.relative_to(ROOT).as_posix()=='static/maps/amap/map.js':
            script=script.replace('https://webapi.amap.com/maps?v=2.0&key=','')
        # Owner-requested Google iframe and image probe; fixed URLs, no remote JS.
        if f.relative_to(ROOT).as_posix()=='static/maps/amap/switcher.js':
            for approved in ('https://www.google.com/maps?q=%E5%8C%97%E4%BA%AC%E5%B8%82%E6%B5%B7%E6%B7%80%E5%8C%BA%E4%B8%AD%E5%85%B3%E6%9D%91%E5%8C%97%E5%A4%A7%E8%A1%97116%E5%8F%B7&z=17&hl=en&output=embed',
                             'https://www.google.com/mapfiles/ms/icons/red-dot.png'):
                script=script.replace(approved,'')
        # Reviewed map renderer: local Leaflet, on-demand OSM tiles and attribution only.
        preview_map_hashes={
            'preview/contact-map/vendor/maplibre-gl.js':'2986bbddce2c7a944775791201fad5108ec8768fc2e3243cac607b23826e4bc0',
            'preview/contact-map/map.js':'3fae06831dbb743daeff69175cfb69c6e5161153091e36fab89cfcf986d707cf',
        }
        preview_hash=preview_map_hashes.get(f.relative_to(ROOT).as_posix())
        if preview_hash:
            if hashlib.sha256(f.read_bytes()).hexdigest()!=preview_hash:
                errors.append(f'{f}: changed local map script requires review')
            continue
        # Official Leaflet 1.9.4 distribution, pinned to the published release.
        if f.relative_to(ROOT).as_posix()=='static/vendor/leaflet/leaflet.js':
            if hashlib.sha256(f.read_bytes()).hexdigest()!='db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a':
                errors.append(f'{f}: unexpected Leaflet version')
            continue
        # Only the requested raster map's tile service and attribution.
        if f.relative_to(ROOT).as_posix()=='static/contact-map-raster.js':
            for approved in ('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                             'https://www.openstreetmap.org/copyright'):
                script=script.replace(approved,'')
        # Requested Apple Maps enhancement; an explicitly approved remote SDK.
        # The empty-token and failure paths retain the local campus map.
        if f.relative_to(ROOT).as_posix()=='static/contact-map.js':
            script=script.replace('https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js','')
        # Owner-authorized GA4 and Baidu tags; production host only, opt-outs respected.
        if f.relative_to(ROOT).as_posix()=='static/analytics.js':
            for approved in ('https://www.googletagmanager.com/gtag/js?id=',
                             'https://policies.google.com/technologies/partner-sites',
                             'https://hm.baidu.com/hm.js?e387d8beff78853986f3b7b31860f890'):
                script=script.replace(approved,'')
        # Owner-requested account login and private sync; official version-pinned SDK.
        if f.relative_to(ROOT).as_posix()=='static/literature-account.js':
            script=script.replace('https://www.gstatic.com/firebasejs/13.1.0/','')
        # User-requested article lookup; fixed public metadata/content hosts only.
        if f.relative_to(ROOT).as_posix()=='static/literature-resolver.js':
            for approved in ('https://api.crossref.org/works',
                             'https://www.ebi.ac.uk/europepmc/webservices/rest/',
                             'https://europepmc.org/article/', 'https://doi.org/'):
                script=script.replace(approved,'')
            script=script.replace('fetch(url,','request(url,')
        if re.search(r'fetch\s*\(|XMLHttpRequest|https?://',script):errors.append(f'{f}: remote script dependency')
report={'checked_html_pages':count,'errors':sorted(set(errors))}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(errors))

