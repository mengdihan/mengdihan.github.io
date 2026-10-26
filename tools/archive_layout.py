"""Publish the approved clean academic archives from the canonical year sources."""
import copy,hashlib,json,re,unicodedata
from html import escape
from urllib.parse import quote,urljoin,urlparse
from lxml import html

def title_key(value):
    return ''.join(c for c in unicodedata.normalize('NFKC',value).casefold() if c.isalnum())

def news_inline(paragraph):
    raw=paragraph.text_content();prefix=re.match(r'^\s*20\d\d/\d+:\s*',raw);skip=prefix.end() if prefix else 0
    def text(value):
        nonlocal skip
        value=value or '';take=min(skip,len(value));skip-=take
        return escape(value[take:])
    def inline(node):
        result=text(node.text)
        for child in node:
            content=inline(child);tag=child.tag.lower() if isinstance(child.tag,str) else ''
            if tag=='a':
                href=urljoin('https://hanmd1990.github.io/',child.get('href',''))
                if urlparse(href).scheme in ('http','https','mailto','tel'):
                    if child.get('data-lightbox')=='compact':
                        # Keep the image local and preserve the small popup in every News view.
                        content='<a href="'+escape(child.get('href',''),quote=True)+'" data-lightbox="compact" aria-label="'+escape(child.get('aria-label','Open news image'),quote=True)+'" aria-haspopup="dialog">'+content+'</a>'
                    else:
                        content='<a href="'+escape(href,quote=True)+'" target="_blank" rel="noopener noreferrer">'+content+'</a>'
            elif tag in ('strong','b','em','i','sup','sub'):content='<'+tag+'>'+content+'</'+tag+'>'
            elif tag=='br':content='<br>'+content
            result+=content+text(child.tail)
        return result
    # Ignore editor-inserted blank lines at the boundaries of a news entry.
    return re.sub(r"^(?:\s*<br>)+|(?:<br>\s*)+$", "", inline(paragraph).strip()).strip()

from selected_publications import selected_paper_ids

def rebuild_archives(root,bibliography,scholar,today):
    authors=json.loads((root/'data/publication-full-authors.json').read_text())['records']
    def citation(item):
        doi=re.search(r'10\.\d{4,9}/[^?#]+',item['url'],re.I)
        return (scholar['records'].get('doi:'+doi[0].rstrip('/').lower()) if doi else None) or scholar['records'].get(title_key(item['title']))
    papers=[]
    for number,paper in sorted(bibliography.items(),reverse=True):
        cached=authors.get(str(number));full=', '.join(paper['authors'])
        # Never apply cached identities to a different paper that reused a number.
        if cached and title_key(cached['title'])==title_key(paper['title']):full=cached['authors']
        meta=copy.deepcopy(paper['metadata'])
        for journal in meta.xpath('.//em'):
            if title_key(journal.text_content())==title_key(paper['journal']):journal.set('class','archive-journal')
        meta_html=(escape(meta.text or '')+''.join(html.tostring(c,encoding='unicode') for c in meta))
        item=dict(id=number,title=paper['title'],url=paper['url'],year=paper['year'],authors=full,journal=paper['journal'],meta=' '.join(meta.text_content().split()),meta_html=meta_html)
        item['citation']=citation(item);item['citation_search']='https://scholar.google.com/scholar?hl=en&q='+quote('"'+item['title']+'"');papers.append(item)
    covers=[];images={}
    cover_tree=html.document_fromstring((root/'publications/covers/index.html').read_text(encoding='utf-8'))
    for i,card in enumerate(cover_tree.xpath('//article[@class="lab-cover-card"]')):
        key='cover-'+str(i);images[key]=card.xpath('.//img/@src')[0]
        item=dict(image=key,journal=card.xpath('string(.//h2)'),year=int(re.search(r'20\d\d',card.xpath('string(.//p[@class="lab-cover-year"])'))[0]),title=card.xpath('string(.//p[@class="lab-cover-title"])'),url=card.xpath('.//a[@class="lab-cover-article"]/@href')[0])
        item['citation']=citation(item);item['citation_search']='https://scholar.google.com/scholar?hl=en&q='+quote('"'+item['title']+'"');covers.append(item)
    news=[];news_images={}
    for path in sorted(root.glob('news/[0-9]*/index.html'),reverse=True):
        if not re.fullmatch(r'\d{4}',path.parent.name):continue
        tree=html.document_fromstring(path.read_text(encoding='utf-8'));year=int(path.parent.name[-4:]);gallery=[]
        for i,image in enumerate(tree.xpath('//*[@id="s-content"]//img')):
            src=image.get('src','')
            if not (root/src.lstrip('/')).is_file():raise ValueError('Missing News image '+src)
            key='news-'+str(year)+'-'+str(i);images[key]=src;gallery.append(dict(image=key,alt=image.get('alt') or f'News image {i+1} from {year}'))
        news_images[str(year)]=gallery
        for p in tree.xpath('//*[@id="s-content"]//p'):
            value=' '.join(p.text_content().split());match=re.match(r'(20\d\d)/(\d+):\s*(.*)',value)
            if not match:continue
            y,month=int(match[1]),int(match[2]);news.append(dict(date=f'{y} / {month:02}',year=y,month=month,text=match[3],html=news_inline(p)))
    data=dict(papers=papers,covers=covers,news=news,newsImages=news_images,images=images,selectedPaperIds=selected_paper_ids(papers,json.loads((root/'data/selected-publications.json').read_text())),scholar=dict(source=scholar['source'],profile=scholar['profile'],checked_on=scholar['checked_on']))
    header=copy.deepcopy(html.document_fromstring((root/'publications/index.html').read_text(encoding='utf-8')).xpath('//header[contains(@class,"lab-header")]')[0])
    def badge(item):
        record=item.get('citation');count=record.get('count') if record else None
        url=(record.get('cited_by') or record.get('scholar_article')) if record else item['citation_search']
        label='Citations ('+(str(count)+('*' if record.get('estimated') else '') if count is not None else '—')+')'
        return f'<a class="citation-badge" href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer" title="Google Scholar">{label}</a>'
    def in_range(year,mode):return mode=='all' or (today-1<=year<=today if mode=='latest' else str(year)==mode)
    def year_select(kind,mode,years):
        options='<option value="all"'+(' selected' if mode=='all' else '')+'>Full List</option>'
        for y in sorted(set([today,*years]),reverse=True):options+=f'<option value="{y}"'+(' selected' if str(y)==(str(today) if mode=='latest' else mode) else '')+f'>{y}</option>'
        return f'<select id="{kind}-year" aria-label="{("Publication" if kind=="pub" else "News")} year">{options}</select>'
    def controls(kind,mode,view):
        result='<div class="archive-tools'+(' news-years' if kind=='news' else '')+'">'
        if kind=='pub':result+='<input id="archive-search" aria-label="Search publications" placeholder="Search Full List: title, author or journal" value="">'
        result+=year_select(kind,mode,[i['year'] for i in (papers if kind=='pub' else news)])
        for key,label in [('all','Full List'),('latest','Latest')]:result+=f'<button data-{kind}-range="{key}" class="'+('active' if view=='list' and mode==key else '')+f'" aria-pressed="{str(view=="list" and mode==key).lower()}">{label}</button>'
        if kind=='pub':
            for key,label in [('selected','Selected Publications'),('covers','Covers')]:result+=f'<button data-mode="{key}" class="'+('active' if view==key else '')+f'" aria-pressed="{str(view==key).lower()}">{label}</button>'
        return result+'</div>'
    def label(mode):return 'across all years' if mode=='all' else f'in {today-1}–{today}' if mode=='latest' else 'in '+mode
    def image(key,alt):return f'<img src="{escape(images[key],quote=True)}" alt="{escape(alt,quote=True)}" loading="lazy">'
    def server_content(kind,mode,view):
        result=''
        if kind=='publication':
            result=f'<p class="paper-note publication-top-note">*Corresponding authors; ¹ Authors contributed equally; Citations: <a href="{escape(scholar["profile"],quote=True)}" target="_blank" rel="noopener noreferrer">Google Scholar</a>; · Automatically updated {escape(scholar["checked_on"])}</p>'+controls('pub',mode,view)
            if view=='selected' and not data['selectedPaperIds']:return result+'<section class="selected-placeholder"><h2>Selected Publications</h2><p>The selected publication list will be added here.</p></section>'
            if view=='covers':
                result+='<div class="cover-grid">'
                for c in covers:result+=f'<figure><a class="cover-tile" href="{escape(c["url"],quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Read article: {escape(c["title"],quote=True)}">{image(c["image"],c["journal"]+" cover")}</a></figure>'
                return result+'</div>'
            ps=[p for p in papers if in_range(p['year'],mode) and (view!='selected' or p['id'] in data['selectedPaperIds'])]
            result+=f'<p class="archive-summary">{len(ps)} articles {label(mode)}</p>'
            groups=[None] if view=='selected' else sorted({p['year'] for p in ps},reverse=True)
            for year in groups:
                subset=ps if year is None else [p for p in ps if p['year']==year]
                result+='<section class="selected-papers"><div>' if year is None else f'<section class="paper-layout"><aside class="year-rail"><strong>{year}</strong><p>{len(subset)} articles</p></aside><div>'
                for p in subset:
                    names=escape(p['authors'])
                    result+=f'<article class="paper-row"><span class="paper-number">{p["id"]}</span><div><a class="paper-title" href="{escape(p["url"],quote=True)}" target="_blank" rel="noopener noreferrer">{escape(p["title"])}</a><p class="authors">{names}</p><div class="journal-row"><p class="journal">{p["meta_html"]}</p>{badge(p)}</div></div></article>'
                result+='</div></section>'
        else:
            ns=[n for n in news if in_range(n['year'],mode)];result=controls('news',mode,view)+f'<p class="archive-summary">{len(ns)} updates {label(mode)}</p>'
            for year in sorted({n['year'] for n in ns},reverse=True):
                result+=f'<section class="news-year-group"><h2>{year}</h2><div class="news-year-layout"><div class="news-feed">'
                for n in ns:
                    if n['year']==year:result+=f'<article class="news-row"><div class="news-date">{n["date"]}</div><p>{n["html"]}</p></article>'
                result+='</div><aside class="news-gallery" aria-label="News images from '+str(year)+'">'
                for photo in news_images[str(year)]:result+=f'<a class="news-photo-open" href="{escape(images[photo["image"]],quote=True)}" data-lightbox="true" aria-label="Enlarge {escape(photo["alt"],quote=True)}">{image(photo["image"],photo["alt"])}</a>'
                result+='</aside></div></section>'
        return result
    routes=[('publications','publication','latest','list'),('publications/all','publication','all','list'),('publications/covers','publication','all','covers'),('publications/selected','publication','all','selected'),('news','news','latest','list'),('news/all','news','all','list')]
    routes += [('publications/'+str(y),'publication',str(y),'list') for y in sorted({p['year'] for p in papers},reverse=True)]
    routes += [('news/'+str(y),'news',str(y),'list') for y in sorted({n['year'] for n in news},reverse=True)]
    versions={name:hashlib.sha256((root/'static'/name).read_bytes()).hexdigest()[:12] for name in ('site.css','hmd-color.css','archive.css','site.js','archive.js','analytics.js')}
    for route,kind,mode,view in routes:
        tree=html.document_fromstring('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body class="lab-modern-archive"></body></html>');head=tree.find('head');body=tree.find('body')
        title=html.Element('title');title.text=('Publications' if kind=='publication' else 'News')+' — '+('Latest' if mode=='latest' else 'Full List' if mode=='all' else mode)+' — Mengdi Han Research Group';head.append(title)
        head.append(html.Element('link',rel='canonical',href='https://hanmd1990.github.io/'+route+'/'));head.append(html.Element('link',rel='icon',href='/images/brand/site-icon.png'))
        for name in ('site.css','hmd-color.css','archive.css'):head.append(html.Element('link',rel='stylesheet',href='/static/'+name+'?v='+versions[name]))
        for name in ('site.js','archive.js','analytics.js'):head.append(html.Element('script',src='/static/'+name+'?v='+versions[name],defer='defer'))
        nav=copy.deepcopy(header)
        for a in nav.xpath('.//a[@href="/'+('publications' if kind=='publication' else 'news')+'/"]'):a.set('aria-current','page')
        body.append(nav);main=html.Element('main',{'id':'s-content','class':'hmd-archive','data-kind':kind,'data-range':mode,'data-mode':view})
        for child in html.fragments_fromstring(server_content(kind,mode,view)):main.append(child)
        body.append(main);payload=html.Element('template',id='hmd-archive-data');payload.text=json.dumps(data,ensure_ascii=False,separators=(',',':'));body.append(payload)
        path=root/route/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(html.tostring(tree,encoding='utf-8',doctype='<!doctype html>'))
    return dict(latest_years=[today,today-1],publication_full_names=sum(title_key(authors.get(str(p['id']),{}).get('title',''))==title_key(p['title']) for p in papers),news_items=len(news),news_images=sum(map(len,news_images.values())))
