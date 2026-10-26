"""Convert the checked-in public snapshot into a platform-independent static site.

One-time migration: python independent.py SOURCE DESTINATION
Requires lxml. No browser or original-platform runtime is used by the result.
"""
import base64, csv, gzip, hashlib, html as html_std, json, re, shutil, sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from lxml import html, etree

SRC=Path(sys.argv[1]).resolve(); OUT=Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
HERE=Path(__file__).resolve().parent
CACHE=json.loads((HERE/'resource-cache.json').read_text(encoding='utf-8'))
PLATFORM=re.compile(r'(?:sxlcdn|sxldns|strikinglycdn|strikingly|sxl\.cn|weitie)',re.I)
URL_RE=re.compile(r'url\(\s*([\"\']?)(.*?)\1\s*\)',re.I)
def cls(e,c): return c in e.get('class','').split()
def select(t,c): return t.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," '+c+' ")]')
def remove(e):
    if e.getparent() is not None: e.drop_tree()
def slug(s):
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:85] or 'image'
def write(p,data):
    p=OUT/p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(data if isinstance(data,bytes) else data.encode('utf-8'))

pages={}; resources={}; usages=[]; errors=[]; css_map={}; css_hashes={}
def resource(raw):
    raw=html_std.unescape(raw.strip())
    if raw.startswith('/assets/'):raw=raw.split('>')[0]
    if not raw or raw.startswith(('data:','#','mailto:','javascript:')): return None
    u=urlparse(urljoin('https://hanmd1990.github.io/',raw))
    if u.hostname in ('hanmd1990.github.io','hmd-lab.com','www.hmd-lab.com'):
        local=SRC/unquote(u.path.lstrip('/'))
        if local.is_file():
            key=str(local.relative_to(SRC)).replace('\\','/')
            if key not in resources:resources[key]={'data':local.read_bytes(),'source':key,'ext':local.suffix.lower()}
            return key
    if u.scheme in ('http','https') and PLATFORM.search(u.hostname or ''):
        key=u.geturl()
        if key not in resources:
            try:
                data=gzip.decompress(base64.b64decode(CACHE[key]))
                resources[key]={'data':data,'source':key,'ext':Path(u.path).suffix.lower()}
            except Exception as e: errors.append({'url':key,'error':str(e)});return None
        return key
    return None

def category(route,e=None):
    if e is not None and (e.tag=='meta' or e.tag=='link' and e.get('rel') in ('icon','shortcut icon') or e.get('alt')=='thumbnail image'):return 'brand'
    if route in ('contact','bio'):return 'people/mengdi-han'
    if route in ('current','alumni'):return 'people/'+route
    if route in ('overview','electronic-skins','smart-implants','wearable-devices','microrobot'):return 'research/'+route
    if route.startswith('news'):return 'news/'+route[4:]
    if route.startswith('publications'):return 'publications/'+route[12:]
    if route in ('covers','all'):return 'publications/'+route
    if route=='lab-tour':return 'lab-tour'
    if not route:return 'home'
    return 'pages/'+route

def label(e,route):
    s=e.get('alt') or e.get('title') or e.get('data-description') or ''
    if not s and e.tag=='a' and e.xpath('.//img'):
        child=e.xpath('.//img')[0];s=child.get('alt') or child.get('title') or ''
    if s.lower() in ('background image','section image','thumbnail image',''):s=''
    if not s:
        for p in e.iterancestors():
            if p.tag in ('body','html'):break
            texts=p.xpath('.//h1//text()|.//h2//text()|.//h3//text()|.//h4//text()|.//h6//text()')
            if texts:
                s=' '.join(texts).strip()[:150];break
    return s or ('site-share' if e.tag=='meta' else 'site-icon' if e.tag=='link' else route or 'home')

def register(raw,route,e):
    key=resource(raw)
    if key:
        usages.append({'key':key,'category':category(route,e),'caption':label(e,route),'page':'/'+route+'/' if route else '/'})
    return key

def css_resource(raw,base=''):
    if raw.startswith(('data:','#')):return raw
    if raw.startswith('/') or '://' in raw or raw.startswith('//'): key=resource(raw)
    else: key=resource(urljoin(base,raw))
    if not key: raise RuntimeError('Unresolved stylesheet resource: '+raw)
    r=resources[key]; data=r['data']; digest=hashlib.sha256(data).hexdigest()[:12]
    ext=r['ext']; folder='fonts' if ext in ('.woff','.woff2','.ttf','.eot') else 'icons'
    filename=f'static/{folder}/{digest}{ext}'
    write(filename,data)
    return '/'+filename

def stylesheet(raw):
    key=resource(raw)
    if not key:raise RuntimeError('Stylesheet unavailable: '+raw)
    if key in css_map:return css_map[key]
    data=resources[key]['data'].decode('utf-8')
    # The original theme contains an unused, broken Bebas Neue font family.
    data=re.sub(r'@font-face\s*\{[^{}]*bebasneue[^{}]*\}', '',data,flags=re.I)
    data=re.sub(r'/\*#\s*sourceMappingURL=.*?\*/','',data,flags=re.S)
    data=re.sub(r'@import\s*\("\./new_feature_list"\);','',data)
    data=URL_RE.sub(lambda m:'url('+css_resource(m[2],raw)+')',data)
    digest=hashlib.sha256(data.encode()).hexdigest()[:12]
    dest=css_hashes.setdefault(digest,'static/styles/theme-'+digest+'.css')
    write(dest,data);css_map[key]='/'+dest;return '/'+dest

for file in sorted(SRC.rglob('index.html')):
    if any(x in file.relative_to(SRC).parts for x in ('work','outputs','.git')):continue
    route=str(file.parent.relative_to(SRC)).replace('\\','/').replace('.','')
    t=html.document_fromstring(file.read_bytes());pages[route]=t
    for e in t.xpath('//script|//noscript'):remove(e)
    for e in t.xpath('//meta[@name="asset-url"]|//meta[@name="support-helper"]'):remove(e)
    for c in ('s-cookie-notification-bar','navigation-buttons','s-floated-components','social-thumbnail'):
        for e in select(t,c):remove(e)
    for ident in ('s-support-widget-container','fb-root','app-script-root','app-view-root'):
        for e in t.xpath('//*[@id="'+ident+'"]'):remove(e)
    for link in list(t.xpath('//link')):
        rel=link.get('rel','')
        if 'stylesheet' in rel:
            link.set('href',stylesheet(link.get('href')));link.set('rel','stylesheet');link.set('media','all')
        elif rel in ('preload','preconnect','dns-prefetch'):remove(link)
    for e in t.iter():
        if not isinstance(e.tag,str):continue
        for a in list(e.attrib):
            if a.startswith('on') or a in ('data-react-style','data-reactid','data-reactroot'):del e.attrib[a]
        for a in ('src','poster','data-src','data-bg','data-background'):
            if e.get(a):register(e.get(a),route,e)
        if e.tag=='meta' and 'image' in (e.get('property','')+e.get('name','')+e.get('itemprop','')) and e.get('content'):register(e.get('content'),route,e)
        if e.tag=='link' and 'icon' in e.get('rel',''):register(e.get('href'),route,e)
        if e.tag=='a' and e.get('href','').startswith('/assets/'):register(e.get('href'),route,e)
        for m in URL_RE.finditer(e.get('style','')):register(m[2],route,e)
        if e.tag=='style':
            for m in URL_RE.finditer(e.text or ''):register(m[2],route,e)

# Assign each shared source image one stable, descriptive file path.
groups={}
for u in usages:groups.setdefault(u['key'],[]).append(u)
rank={'brand':0,'people':1,'research':2,'publications':3,'news':4,'lab-tour':5,'home':6,'pages':7}
image_map={};catalog=[];used=set()
for key,items in groups.items():
    item=min(items,key=lambda u:(rank.get(u['category'].split('/')[0],9),u['caption'] in ('home','contact','bio')))
    r=resources[key];ext=r['ext'] or '.png';base=slug(item['caption']);dest='images/'+item['category']+'/'+base+ext;n=2
    while dest in used:dest='images/'+item['category']+'/'+base+'-'+str(n).zfill(2)+ext;n+=1
    used.add(dest);image_map[key]='/'+dest;write(dest,r['data'])
    catalog.append({'file':dest,'category':item['category'],'description':item['caption'],'pages':sorted(set(u['page'] for u in items)),'previous_file':key})

def mapped(raw):
    key=resource(raw)
    return image_map.get(key,raw)
def fixstyle(s):return URL_RE.sub(lambda m:'url("'+mapped(m[2])+'")',s)
def link(label,url):return f'<a href="{url}">{label}</a>'
def menu(label,items):return '<details class="lab-menu"><summary>'+label+'</summary><div class="lab-menu-items">'+''.join(items)+'</div></details>'
nav=link('HOME','/')+menu('RESEARCH',[link(l,'/'+p+'/') for l,p in [('OVERVIEW','overview'),('ELECTRONIC SKINS','electronic-skins'),('WEARABLE DEVICES','wearable-devices'),('SMART IMPLANTS','smart-implants')]])+menu('GROUP',[link('CURRENT','/current/'),link('ALUMNI','/alumni/')])+menu('PUBLICATIONS',[link(str(y),'/publications'+str(y)+'/') for y in range(2026,2012,-1)]+[link('FULL LIST','/all/'),link('COVERS','/covers/')])+menu('NEWS',[link(str(y),'/news'+str(y)+'/') for y in range(2026,2019,-1)])+link('CONTACT','/contact/')+link('JOIN US','/join/')
header='<header class="lab-header"><a class="lab-brand" href="/">Mengdi Han Research Group<span>（韩梦迪课题组）</span></a><button class="lab-menu-toggle" aria-expanded="false" aria-controls="lab-navigation">Menu</button><nav id="lab-navigation" aria-label="Main navigation">'+nav+'</nav></header>'

for route,t in pages.items():
    for e in select(t,'s-nav'):remove(e)
    body=t.find('body');head=t.find('head')
    if route!='home':body.insert(0,html.fragment_fromstring(header))
    for e in t.iter():
        if not isinstance(e.tag,str):continue
        for a in ('src','poster','data-src','data-bg','data-background'):
            if e.get(a):e.set(a,mapped(e.get(a)))
        if e.tag=='meta' and 'image' in (e.get('property','')+e.get('name','')+e.get('itemprop','')) and e.get('content'):e.set('content',mapped(e.get('content')))
        if e.tag=='link' and 'icon' in e.get('rel',''):e.set('href',mapped(e.get('href')))
        if e.get('style'):e.set('style',fixstyle(e.get('style')))
        if e.tag=='style' and e.text:e.text=fixstyle(e.text)
        if e.get('data-bg'):
            s=e.get('style','');e.set('style',s+';background-image:url("'+e.get('data-bg')+'")')
        if e.tag=='img':
            if e.get('data-src'):e.set('src',e.get('data-src'))
            for a in ('data-src','srcset','data-srcset'):e.attrib.pop(a,None)
            e.set('decoding','async');e.set('loading','lazy')
        if cls(e,'lazyload'):e.set('class',e.get('class').replace('lazyload','lazyloaded'))
        if cls(e,'blurred-layer'):e.set('class',e.get('class')+' loaded')
        if e.tag=='a':
            href=e.get('href','')
            if href.startswith('/assets/'):
                e.set('href',mapped(href));e.set('data-lightbox','true')
            if href.startswith(('https://hmd-lab.com','http://hmd-lab.com','https://www.hmd-lab.com','http://www.hmd-lab.com')):
                u=urlparse(href);e.set('href',u.path+('?' +u.query if u.query else '')+('#'+u.fragment if u.fragment else ''))
            if e.get('target')=='_blank':e.set('rel','noopener noreferrer')
            if href.startswith('javascript:'):
                images=e.xpath('.//img[@src]')
                if images:e.set('href',images[0].get('src'));e.set('data-lightbox','true')
                else:e.attrib.pop('href',None)
    # Replace the platform carousel with semantic static slides and a tiny local controller.
    for slider in select(t,'slick-slider'):
        slides=[e for e in slider.xpath('.//*[@data-index]') if cls(e,'slick-slide') and not cls(e,'slick-cloned')]
        if not slides:continue
        carousel=html.Element('div',{'class':'lab-carousel','aria-label':'Research highlights','aria-roledescription':'carousel'})
        for i,e in enumerate(slides):
            imgs=e.xpath('.//img[@src]');anchors=e.xpath('.//a[@href]')
            if not imgs:continue
            figure=html.Element('figure',{'class':'lab-carousel-slide','aria-label':f'{i+1} / {len(slides)}'})
            if i:figure.set('hidden','hidden')
            im=html.Element('img',src=imgs[0].get('src'),alt='Research highlight '+str(i+1));im.set('loading','eager' if i==0 else 'lazy')
            if anchors:
                a=html.Element('a',href=anchors[0].get('href'),target='_blank',rel='noopener noreferrer');a.append(im);figure.append(a)
            else:figure.append(im)
            carousel.append(figure)
        controls=html.fragment_fromstring('<div class="lab-carousel-controls"><button data-direction="-1" aria-label="Previous slide">‹</button><button class="lab-pause" aria-label="Pause slideshow">Pause</button><button data-direction="1" aria-label="Next slide">›</button></div>');carousel.append(controls)
        parent=slider
        for a in slider.iterancestors():
            if cls(a,'s-slider'):parent=a;break
        parent.getparent().replace(parent,carousel)
    for e in select(t,'s-gallery-item'):
        ims=e.xpath('.//img[@src]')
        if ims:
            im=ims[0]
            if not any(a.tag=='a' for a in im.iterancestors()):
                p=im.getparent();a=html.Element('a',href=im.get('src'),attrib={'data-lightbox':'true'});p.replace(im,a);a.append(im)
    for e in t.xpath('//meta[@property="og:url"]'):e.set('content','https://hanmd1990.github.io/'+route+('/' if route else ''))
    head.append(html.Element('link',rel='stylesheet',href='/static/site.css'))
    script=html.Element('script',src='/static/site.js',defer='defer');body.append(script)
    # No legacy platform data attributes can initiate requests after removal of its runtime.
    for e in t.iter():
        if isinstance(e.tag,str):
            for a in list(e.attrib):
                if a.startswith('data-') and a not in ('data-lightbox','data-direction') :del e.attrib[a]
    output=html.tostring(t,encoding='unicode',doctype='<!DOCTYPE html>')
    output=re.sub(r'<!--.*?-->','',output,flags=re.S)
    write((route+'/' if route else '')+'index.html',output)

for name in ('site.js','site.css'):write('static/'+name,(HERE/name).read_bytes())
write('.nojekyll','')
write('images/catalog.json',json.dumps(catalog,ensure_ascii=False,indent=2))
with (OUT/'images/catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['图片路径','分类','说明','使用页面','旧文件（仅供追溯）'])
    for r in catalog:w.writerow([r['file'],r['category'],r['description'],' | '.join(r['pages']),r['previous_file']])
cards=''.join('<article><a href="/'+r['file']+'"><img loading="lazy" src="/'+r['file']+'" alt="'+html_std.escape(r['description'],quote=True)+'"></a><h2>'+html_std.escape(r['description'])+'</h2><code>'+r['file']+'</code><p>'+html_std.escape('、'.join(r['pages']))+'</p></article>' for r in catalog)
write('images/index.html','<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>图片目录 — HMD Lab</title><style>body{font:15px system-ui;max-width:1400px;margin:40px auto;padding:20px;background:#f6f8fa}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}article{background:white;padding:18px;overflow-wrap:anywhere;border:1px solid #ddd;border-radius:8px}img{width:100%;height:180px;object-fit:contain}h2{font-size:16px}code{font-size:12px}input{padding:12px;width:min(90%,500px);margin:20px 0}</style><h1>网站图片目录</h1><p>按文件名、说明或页面路径搜索。替换图片时保留原路径和扩展名。</p><input id="search" placeholder="搜索图片或栏目" aria-label="搜索图片"><main>'+cards+'</main><script>document.getElementById("search").addEventListener("input",e=>{let q=e.target.value.toLowerCase();document.querySelectorAll("article").forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(q))})</script></html>')
write('MAINTENANCE.md','''# 图片与网站维护

本站是独立静态网站，不再加载“上线了”的脚本、API、图片或字体。布局样式已保存在 static/styles，交互代码为 static/site.js。

## 图片分类
- images/brand：网站标识与分享图
- images/people：成员、韩梦迪老师和课题组活动
- images/research：各研究方向
- images/publications：论文插图和期刊封面
- images/news：按年份归档的新闻图片
- images/lab-tour：实验室与设备
- images/home：首页图
- images/pages：其他页面

同一图片在多个页面使用时只保留一个路径。images/catalog.csv 和 catalog.json 列出图片路径、说明和使用页面；打开 /images/ 可浏览缩略图并搜索。

## 替换图片
1. 在图片目录找到目标图片，打开仓库内相应文件。
2. 上传新图片覆盖同一路径，保留文件名、扩展名，建议维持相同宽高比。GIF 应保留为 GIF，避免丢失动画。
3. 提交到 main。GitHub Actions 会验证并自动发布，完成后刷新网页（必要时强制刷新）。
4. 若增加或重命名图片，更新对应栏目 index.html 中的 src 和相关背景 URL，并同步图片目录记录。

内容直接在各栏目 index.html 中编辑。首页为 index.html，2026 新闻为 news2026/index.html，2026 论文为 publications2026/index.html。外部论文链接仍指向出版商；点击外链与页面自身加载依赖是两回事。

原域名与阿里云 DNS 未变更。历史迁移记录仍可通过 Git 历史恢复；当前发布不再执行抓取。
''')
write('independence-report.json',json.dumps({'pages':len(pages),'images':len(catalog),'resource_errors':errors},ensure_ascii=False,indent=2))
print(json.dumps({'pages':len(pages),'images':len(catalog),'errors':errors},ensure_ascii=False))

