"""Build archive navigation and full lists from editable year pages. No network."""
import copy,datetime,hashlib,json,re,subprocess,sys,unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlparse,quote
from lxml import html
from alumni_layout import rebuild_alumni,bibliography_authors
from join_layout import rebuild_join
from member_publications import read_bibliography,add_alumni_publications

ROOT=Path(sys.argv[1]).resolve()
# Fingerprint the self-hosted map assets as well as the outer iframe.
map_folder=ROOT/'static/maps/amap'
for page_name in ('amap.html','map.html'):
    map_page=html.document_fromstring((map_folder/page_name).read_bytes())
    for element in map_page.xpath('//script[@src]|//link[@rel="stylesheet"]'):
        attribute='src' if element.tag=='script' else 'href'
        name=element.get(attribute).split('?')[0]
        version=hashlib.sha256((map_folder/name).read_bytes()).hexdigest()[:12]
        element.set(attribute,name+'?v='+version)
    (map_folder/page_name).write_bytes(html.tostring(map_page,encoding='utf-8',doctype='<!doctype html>'))
map_version=hashlib.sha256((map_folder/'map.html').read_bytes()).hexdigest()[:12]
# Source folders are organized independently of historical public URLs.
# Normalize links in the isolated deployment output before reading metadata.
route_moves={**{'publications'+p.name:'publications/'+p.name for p in ROOT.glob('publications/[0-9]*') if p.is_dir()},
             **{'news'+p.name:'news/'+p.name for p in ROOT.glob('news/[0-9]*') if p.is_dir()},
             'all':'publications/all','covers':'publications/covers',
             'microrobot':'publications/microrobot','news-all':'news/all',
             'selected-publications':'publications/selected'}
for source in [*ROOT.rglob('*.html'),ROOT/'images/catalog.json',ROOT/'images/catalog.csv']:
    if not source.is_file():continue
    original=source.read_text(encoding='utf8');updated=original
    # Match root-relative or full website URLs, never image subdirectories.
    for old,new in route_moves.items():
        pattern=r'(?:(?<=https://hanmd1990.github.io)|(?<![\w/-]))/'+re.escape(old)+r'(?=/|["\'?#])'
        updated=re.sub(pattern,'/'+new,updated)
        updated=re.sub(r'(?<![\w/-])'+re.escape(old)+r'(?=/index\.html|["\'])',new,updated)
    if updated!=original:source.write_text(updated,encoding='utf8')

member_roster=json.loads((ROOT/'data/member-publications.json').read_text(encoding='utf8'))
member_bibliography=read_bibliography(ROOT)
# Rebuild selected papers on every deployment, including manually edited years.
# Author identity evidence is cached in the roster; this build needs no network.
subprocess.run([sys.executable,str(Path(__file__).with_name('build_member_preview.py')),str(ROOT),'--publish'],check=True)
alumni_authors=bibliography_authors(ROOT)
color_version=hashlib.sha256((ROOT/'static/hmd-color.css').read_bytes()).hexdigest()[:12]
script_version=hashlib.sha256((ROOT/'static/site.js').read_bytes()).hexdigest()[:12]
today=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).year
citations_path=ROOT/'data/scholar-citations.json'
citations=json.loads(citations_path.read_text(encoding='utf-8')) if citations_path.exists() else {'records':{},'checked_on':None}
def title_key(s):return ''.join(c for c in unicodedata.normalize('NFKC',s).casefold() if c.isalnum())
def citation_record(link):
    doi=re.search(r'10\.\d{4,9}/[^?#]+',link.get('href',''),re.I)
    if doi:
        found=citations['records'].get('doi:'+doi[0].rstrip('/').lower())
        if found:return found
    return citations['records'].get(title_key(text(link)))
def read(path):return html.document_fromstring(path.read_text(encoding='utf-8'))
def write(path,tree):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(html.tostring(tree,encoding='utf-8',doctype='<!DOCTYPE html>'))
def years(kind):
    return sorted([int(p.parent.name) for p in ROOT.glob(kind+'/[0-9]*/index.html') if re.fullmatch(r'\d{4}',p.parent.name)],reverse=True)
pub_years=years('publications');news_years=years('news')
assert pub_years and news_years,'Year pages are required'
def paper_key(href):
    doi=re.search(r'10\.\d{4,9}/[^?#]+',href,re.I)
    return 'doi:'+doi[0].rstrip('/').lower() if doi else href.split('?')[0].rstrip('/')
publication_index={}
for year in pub_years:
    for p in read(ROOT/f'publications/{year}/index.html').xpath('//p'):
        if not re.match(r'^\(\d+\)',p.text_content().strip()):continue
        links=p.xpath('.//a[@href]')
        if not links:continue
        journal='';following=p.getnext()
        for _ in range(3):
            if following is None:break
            for em in following.xpath('.//em'):
                value=' '.join(em.text_content().split())
                if value and not re.fullmatch(r'et\s*al\.?|\d+',value,re.I):journal=value;break
            if journal:break
            following=following.getnext()
        publication_index[paper_key(links[0].get('href'))]={'title':' '.join(links[0].text_content().split()),'journal':journal,'year':year,'number':int(re.match(r'^\((\d+)\)',p.text_content().strip())[1])}
def current(ys):return today if today in ys else next((y for y in ys if y<=today),ys[0])
def text(e):return ' '.join(''.join(e.itertext()).split())
def citation_badge(record,title):
    count=record.get('count') if record else None
    url=(record.get('cited_by') or record.get('scholar_article')) if record else 'https://scholar.google.com/scholar?hl=en&q='+quote('"'+title+'"')
    badge=html.Element('span',{'class':'lab-citation-badge'})
    anchor=html.Element('a',href=url,attrib={'class':'lab-citation-link','target':'_blank','rel':'noopener noreferrer','data-link-kind':'citation','title':('Google Scholar · checked '+record['checked_on'] if record else 'Not yet matched in Google Scholar; search by article title')})
    anchor.text='Citations ('+(str(count)+('*' if record.get('estimated') else '') if count is not None else '—')+')';badge.append(anchor)
    return badge
def add_class(e,name):
    classes=e.get('class','').split()
    if name not in classes:classes.append(name)
    e.set('class',' '.join(classes))
def article_link(href):
    u=urlparse(href);host=(u.hostname or '').lower();path=u.path
    if '/doi/toc/' in path:return False
    if re.search(r'/doi/(?:abs/|full/|epdf/|pdf/)?10\.\d{4,9}/',path):return True
    if host in ('doi.org','dx.doi.org') and path.startswith('/10.'):return True
    return any(host.endswith(domain) and re.search(pattern,path) for domain,pattern in [
        ('nature.com',r'^/articles/[^/]+'),('sciencedirect.com',r'/science/article/'),
        ('link.springer.com',r'/article/'),('pnas.org',r'^/content/\d+/'),
        ('ieeexplore.ieee.org',r'^/document/\d+'),('pubmed.ncbi.nlm.nih.gov',r'^/\d+'),
        ('ieeexplore.ieee.org',r'^/stamp/stamp.jsp'),('iopscience.iop.org',r'^/article/'),
        ('pubs.rsc.org',r'/content/articlelanding/'),('cambridge.org',r'/core/journals/.*/article/'),
        ('frontiersin.org',r'/articles/10\.'),('mdpi.com',r'^/\d{4}-\d{4}/\d+/\d+/\d+'),
        ('academic.oup.com',r'/article/'),('pubs.aip.org',r'/article/')])
def paper_id(e):
    m=re.match(r'^\((\d+)\)',text(e));return int(m[1]) if m else None
def sort_member_publications(tree):
    # Use the bibliography number, not year/title or the curated selection order.
    # Keep each title and all of its metadata/citations together when moving it.
    numbers={title_key(record['title']):record['number'] for record in publication_index.values()}
    for listing in tree.xpath('//ol[@class="member-paper-list"]'):
        for item in sorted(list(listing),key=lambda item:int(item.get('data-paper-id','-1')),reverse=True):
            listing.append(item)
    for listing in tree.xpath('//div[@class="alumni-publications"]'):
        groups=[]
        for node in list(listing):
            if 'alumni-paper-title' in node.get('class','').split():
                number=numbers.get(title_key(text(node)),-1)
                if number>=0:node.set('data-paper-id',str(number))
                groups.append((number,[node]))
            elif groups:
                groups[-1][1].append(node)
        for number,nodes in sorted(groups,key=lambda group:group[0],reverse=True):
            for node in nodes:listing.append(node)
def paper_wrapper(tree):
    candidates=[e for e in tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," s-rich-text-wrapper ")]') if any(paper_id(c) for c in e)]
    assert len(candidates)==1,'Expected one publication content block'
    return candidates[0]
def slides(tree):
    return tree.xpath('//ul[contains(concat(" ",normalize-space(@class)," ")," slides ")]')[0]

# Publication year pages are the sole source of the full list.
pub=read(ROOT/f'publications/{pub_years[0]}/index.html')
destination=paper_wrapper(pub);destination.clear();destination.set('class','s-rich-text-wrapper');destination.set('style','display:block')
legend=html.Element('p',{'class':'lab-publication-legend'});legend.text='*Corresponding authors; ¹Authors contributed equally';destination.append(legend)
paper_ids=[];counts={}
for year in pub_years:
    source=paper_wrapper(read(ROOT/f'publications/{year}/index.html'))
    elements=list(source);start=next(i for i,e in enumerate(elements) if paper_id(e))
    heading=html.Element('h2',id='year-'+str(year),attrib={'class':'lab-year-heading'});heading.text=str(year);destination.append(heading)
    n=0;previous_blank=False
    # Preserve titles, authors, journal details, notes, links and images together.
    for element in elements[start:]:
        pid=paper_id(element)
        if pid:paper_ids.append(pid);n+=1
        blank=not text(element) and not element.xpath('.//img')
        if blank and previous_blank:continue
        destination.append(copy.deepcopy(element));previous_blank=blank
    while len(destination) and not text(destination[-1]) and not destination[-1].xpath('.//img'):destination.remove(destination[-1])
    counts[str(year)]=n
assert len(paper_ids)==len(set(paper_ids)),'Duplicate publication numbers across year pages'
write(ROOT/'publications/all/index.html',pub)

# News full list preserves complete sections, including their photographs.
news=read(ROOT/f'news/{news_years[0]}/index.html');target=slides(news)
for child in list(target):target.remove(child)
style_texts={e.text for e in news.xpath('//style')}
for year in news_years:
    source=read(ROOT/f'news/{year}/index.html')
    for style in source.xpath('//style'):
        if style.text not in style_texts:news.find('head').append(copy.deepcopy(style));style_texts.add(style.text)
    for section in slides(source):
        section=copy.deepcopy(section)
        for element in section.iter():
            if element.get('id'):element.set('id','news-'+str(year)+'-'+element.get('id'))
        section.set('id','year-'+str(year));target.append(section)
write(ROOT/'news/all/index.html',news)

# Stable entry links open the current calendar year when available.
for kind,ys in [('publications',pub_years),('news',news_years)]:
    write(ROOT/kind/'index.html',read(ROOT/f'{kind}/{current(ys)}/index.html'))

def archive_nav(kind,active):
    ys=pub_years if kind=='publications' else news_years
    nav=html.Element('nav',{'class':'lab-archive-nav','aria-label':kind.capitalize()+' years'})
    year_rows=html.Element('div',{'class':'lab-archive-years'})
    for decade in sorted({year//10*10 for year in ys},reverse=True):
        group=[year for year in ys if year//10*10==decade]
        row=html.Element('div',{'class':'lab-decade-row','data-decade':str(decade),'aria-label':f'{decade}s'})
        row.set('style',f'--year-count:{len(group)}')
        label=html.Element('span',{'class':'lab-decade-label'});label.text=f'{decade}s';row.append(label)
        for year in group:
            a=html.Element('a',href=f'/{kind}{year}/');a.text=str(year)
            if active==str(year):a.set('aria-current','page')
            row.append(a)
        year_rows.append(row)
    nav.append(year_rows)
    actions=html.Element('div',{'class':'lab-archive-actions'})
    primary=html.Element('div',{'class':'lab-archive-action-row'})
    for label,route in [('Full List','publications/all' if kind=='publications' else 'news/all')]+([('Covers','publications/covers')] if kind=='publications' else []):
        a=html.Element('a',href='/'+route+'/',attrib={'class':'lab-archive-feature'});a.text=label
        if active==route:a.set('aria-current','page')
        primary.append(a)
    actions.append(primary)
    if kind=='publications':
        secondary=html.Element('div',{'class':'lab-archive-action-row'})
        scholar=html.Element('a',href='https://scholar.google.com/citations?user=rjC8MUQAAAAJ&hl=en',target='_blank',rel='noopener noreferrer',attrib={'class':'lab-archive-feature lab-scholar-link'});scholar.text='Google Scholar Profile';secondary.append(scholar);actions.append(secondary)
    nav.append(actions)
    if kind=='publications' and active!='covers':
        note=html.Element('p',{'class':'lab-publication-legend lab-publication-notes'});note.text='*Corresponding authors; ¹ Authors contributed equally'
        if citations.get('checked_on'):
            note.text+='; Citations: Google Scholar; · Automatically updated '+citations['checked_on']
        nav.append(note)
    return nav

for path in ROOT.rglob('index.html'):
    if any(p in path.relative_to(ROOT).parts for p in ('tools','work','outputs','.git','.github')):continue
    tree=read(path);actual_route=path.parent.relative_to(ROOT).as_posix()
    route=re.sub(r'^(publications|news)/(\d{4})$',r'\1\2',actual_route)
    route={'publications/all':'all','publications/covers':'covers','publications/microrobot':'microrobot','news/all':'news-all'}.get(route,route)
    for footer in tree.xpath('//*[@id="s-footer-section-container"] | //*[@id="s-footer-logo-wrapper"] | //*[contains(concat(" ",normalize-space(@class)," ")," members-footer ")]'):
        if footer.getparent() is not None:footer.getparent().remove(footer)
    for old in tree.xpath('//*[contains(concat(" ",@class," ")," lab-citation-badge ")]'):old.getparent().remove(old)
    page_class={'.':'lab-home-page','current':'lab-current-page','alumni':'lab-alumni-page','bio':'lab-bio-page','contact':'lab-contact-page','join':'lab-join-page'}.get(route)
    if page_class:add_class(tree.find('body'),page_class)
    for link in tree.xpath('//a[@href]'):
        link.set('class',' '.join(c for c in link.get('class','').split() if c!='lab-publication-link'))
        if not route.startswith('news') and route!='covers' and text(link).lower() not in ('cover','covers') and (link.get('data-link-kind')=='article' or article_link(link.get('href'))):add_class(link,'lab-publication-link')
    if re.fullmatch(r'publications\d{4}',route) or route in ('publications','all'):
        content=paper_wrapper(tree);add_class(content,'lab-publication-body')
        while len(content) and not text(content[0]) and not content[0].xpath('.//img'):content.remove(content[0])
        for year in content.xpath('./p|./h4|./h5|./h6'):
            if re.fullmatch(r'\d{4}',text(year)):
                year.tag='h2';year.attrib.pop('style',None);add_class(year,'lab-content-year')
                following=year.getnext()
                if following is not None and not text(following) and not following.xpath('.//img'):content.remove(following)
        for paragraph in tree.xpath('//*[@id="s-content"]//p'):
            links=paragraph.xpath('.//a[@href]')
            if paper_id(paragraph) and links:add_class(links[0],'lab-publication-link')
    for em in tree.xpath('//*[@id="s-content"]//p//em'):
        if re.fullmatch(r'et\s*al\.?',text(em),re.I):add_class(em,'lab-author-note')
        if re.fullmatch(r'\d+(?:[.\-–]\d+)?',text(em)):
            add_class(em,'lab-volume')
    if route=='.':
        for heading in tree.xpath('//h1|//h2|//h3|//h4|//h5|//h6'):
            if text(heading).lower() in ('our mission','open positions','recent highlights'):add_class(heading,'lab-section-accent')
        for subtitle in tree.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," s-item-subtitle ")]'):add_class(subtitle,'lab-home-citation')
        for em in tree.xpath('//*[contains(concat(" ",@class," ")," lab-home-citation ")]//em'):add_class(em,'lab-home-journal')
    if route=='current':
        for strong in tree.xpath('//*[@id="s-content"]//strong'):
            if re.fullmatch(r'(?:Princip(?:al|le) Investigator|Postdoctoral Fellows?|Undergrads? & Visiting Students|Ph\.D\. Students?|Master Students?|Research Assistants?|课题组长|博士后研究员|本科生 & 访问学生|博士研究生)',text(strong),re.I):
                element=next((a for a in strong.iterancestors() if a.tag in ('p','h1','h2','h3','h4','h5','h6')),strong);add_class(element,'lab-section-accent')
    if route in ('alumni','join'):
        for item in list(tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," s-kit-collapse-item ")]')):
            headers=item.xpath('./div[contains(concat(" ",@class," ")," s-kit-collapse-header ")]');contents=item.xpath('./div[contains(concat(" ",@class," ")," s-kit-collapse-content ")]')
            if not headers or not contents:continue
            details=html.Element('details',{'class':'lab-disclosure'});summary=html.Element('summary')
            header=headers[0]
            for attr in ('role','tabindex','aria-expanded','aria-disabled'):header.attrib.pop(attr,None)
            for icon in header.xpath('.//div[contains(@class,"s-kit-collapse-expand-icon")]'):icon.getparent().remove(icon)
            summary.append(header);details.append(summary)
            content=contents[0];content.set('class','lab-disclosure-content');content.attrib.pop('style',None);details.append(content)
            item.getparent().replace(item,details)
        if route=='join':
            for heading in tree.xpath('//details[@class="lab-disclosure"]/summary//h4'):
                add_class(heading,'lab-position-title')
        if route=='alumni':
            for strong in tree.xpath('//details[@class="lab-disclosure"]/summary//strong'):add_class(strong,'lab-alumni-name')
            for strong in tree.xpath('//details[@class="lab-disclosure"]//strong'):
                if text(strong).lower().rstrip(':')=='selected publications':add_class(strong,'lab-alumni-label')
    for carousel in tree.xpath('//div[contains(concat(" ",@class," ")," lab-carousel ")]'):
        for controls in carousel.xpath('./div[contains(@class,"lab-carousel-controls") or contains(@class,"lab-carousel-dots")]'):carousel.remove(controls)
        slides_list=carousel.xpath('./figure');dots=html.Element('div',{'class':'lab-carousel-dots','role':'group','aria-label':'Choose research highlight'})
        for image in carousel.xpath('./figure//img'):image.set('loading','eager')
        for index in range(len(slides_list)):
            dots.append(html.Element('button',{'class':'lab-carousel-dot','type':'button','data-slide':str(index),'aria-label':f'Show slide {index+1} of {len(slides_list)}','aria-pressed':'true' if index==0 else 'false'}))
        carousel.append(dots)
    if route=='join':
        rebuild_join(tree,ROOT)
        for old_script in tree.xpath('//script[starts-with(@src,"/static/join.js")]'):old_script.getparent().remove(old_script)
        join_version=hashlib.sha256((ROOT/'static/join.js').read_bytes()).hexdigest()[:12]
        tree.find('head').append(html.Element('script',src='/static/join.js?v='+join_version,defer='defer'))
    if route=='alumni':
        rebuild_alumni(tree,alumni_authors)
        add_alumni_publications(tree,member_bibliography,member_roster)
        for old_script in tree.xpath('//script[starts-with(@src,"/static/alumni.js")]'):old_script.getparent().remove(old_script)
        alumni_script_version=hashlib.sha256((ROOT/'static/alumni.js').read_bytes()).hexdigest()[:12]
        tree.find('head').append(html.Element('script',src='/static/alumni.js?v='+alumni_script_version,defer='defer'))
    if route in ('current','alumni'):
        sort_member_publications(tree)
    if route=='microrobot':
        # Use the same bibliography, full author evidence and typography as Publications.
        paper=member_bibliography[89]
        paragraphs=tree.xpath('//*[@id="s-content"]//p')
        title,authors,metadata=paragraphs[:3]
        title.clear();title.set('class','paper-title')
        link=html.Element('a',href=paper['url'],target='_blank',rel='noopener noreferrer');link.text=paper['title'];title.append(link)
        authors.clear();authors.set('class','authors')
        full=json.loads((ROOT/'data/publication-full-authors.json').read_text())['records']['89']['authors']
        authors.text=full
        metadata.clear();metadata.set('class','journal')
        meta=copy.deepcopy(paper['metadata'])
        # This is the movie page itself; omit the duplicate parenthetical self-link.
        for movie in meta.xpath('.//a[@href="/publications/microrobot" or @href="/publications/microrobot/"]'):
            wrapper=movie.getparent()
            if wrapper.tag=='span' and len(wrapper)==1:
                before,after=wrapper.getprevious(),wrapper.getnext()
                if before is not None and (before.text or '').endswith(' ('):before.text=before.text[:-2]
                if after is not None and (after.text or '').strip()==')':after.getparent().remove(after)
                wrapper.getparent().remove(wrapper)
        metadata.text=meta.text
        for child in list(meta):metadata.append(child)
        section=html.Element('section',{'class':'hmd-archive microrobot-citation','aria-label':'Publication details'})
        title.addprevious(section)
        for node in (title,authors,metadata):section.append(node)
        version=hashlib.sha256((ROOT/'static/archive.css').read_bytes()).hexdigest()[:12]
        tree.find('head').append(html.Element('link',rel='stylesheet',href='/static/archive.css?v='+version))
    if route=='contact':
        contact=tree.xpath('//*[@id="s-content"]')[0]
        profile_names=['Curriculum Vitae','Biography','PKU Profile [CN]','PKU Profile [EN]','Google Scholar','ResearcherID','ORCID','X (Twitter)','LinkedIn','ResearchGate']
        profile_links={text(a):a.get('href') for a in contact.xpath('.//a[@href]') if text(a) in profile_names}
        profile_links['PKU Profile [CN]']='https://future.pku.edu.cn/szll/jyxln/9a4bd0e17e044037b0228a4dbcaf3875.htm'
        profile_links['PKU Profile [EN]']='https://future.pku.edu.cn/en/Faculty_/Teaching_Research_Series/4b920575a0244a4e827b1b36d536c167.htm'
        contact.clear();contact.set('id','s-content')
        layout=html.fragment_fromstring('''<main class="lab-contact-layout">
          <div class="lab-contact-grid">
            <section class="lab-contact-profile" aria-labelledby="contact-name"><div class="lab-contact-person"><div class="lab-contact-portrait"><img src="/images/people/mengdi-han/mengdi-han-portrait.jpg" alt="Mengdi Han"></div><div><h2 id="contact-name">Mengdi Han</h2><p>Assistant Professor<br>Associate Department Chair</p></div></div><div class="lab-contact-email"><span>Email</span><p>hmd[at]pku.edu.cn</p></div><nav class="lab-contact-profiles" aria-label="Profiles and resources"></nav><div class="lab-contact-address"><p>Department of Biomedical Engineering<br>College of Future Technology<br>Peking University<br>Beijing 100871, China</p></div></section>
            <section class="lab-contact-visit" aria-labelledby="contact-visit"><h2 id="contact-visit">Visit our lab</h2><figure class="lab-contact-map" id="contact-map"><iframe class="lab-contact-map-frame" title="Laboratory location — Google Maps or Amap" src="/static/maps/amap/map.html" width="800" height="300" loading="eager" referrerpolicy="strict-origin-when-cross-origin"></iframe></figure><p class="lab-contact-directions"><strong>Navigation:</strong> No. 116 Zhongguancun North Street · 中关村北大街116号，北京大学新奥工学大楼</p><nav class="lab-contact-navigation" aria-label="Navigate to ENN Engineering Building"><a href="https://www.google.com/maps/dir/?api=1&amp;destination=%E5%8C%97%E4%BA%AC%E5%B8%82%E6%B5%B7%E6%B7%80%E5%8C%BA%E4%B8%AD%E5%85%B3%E6%9D%91%E5%8C%97%E5%A4%A7%E8%A1%97116%E5%8F%B7&amp;travelmode=driving" target="_blank" rel="noopener noreferrer" aria-label="Navigate to 中关村北大街116号 with Google Maps">Google Maps</a><a href="https://j.map.baidu.com/86/7Spi" target="_blank" rel="noopener noreferrer" aria-label="Open 北京大学新奥工学大楼 in 百度地图">百度地图</a><a href="https://surl.amap.com/4fO0iYusb3Nn" target="_blank" rel="noopener noreferrer" aria-label="Open 北京大学新奥工学大楼 in 高德地图">高德地图</a></nav></section>
          </div></main>''')
        layout.xpath('.//iframe')[0].set('src','/static/maps/amap/map.html?v='+map_version)
        directions=layout.xpath('.//p[@class="lab-contact-directions"]')[0]
        navigation=layout.xpath('.//nav[@class="lab-contact-navigation"]')[0]
        label=directions.find('strong')
        address=label.tail or ''
        label.tail=None
        directions.remove(label)
        directions.text=address.strip()
        directions.tag='span'
        directions.set('class','lab-contact-directions-address')
        row=html.Element('div',{'class':'lab-contact-directions-row'})
        row.extend([label,navigation,directions])
        layout.xpath('.//section[@class="lab-contact-visit"]')[0].append(row)
        profile_nav=layout.xpath('.//nav[@class="lab-contact-profiles"]')[0]
        profile_icons=['contact-02.png','contact-03.png','contact.png','contact.png','contact-06.png','contact-04.png','contact-05.png','contact-07.png','contact-08.png','contact-09.png']
        for name,icon in zip(profile_names,profile_icons):
            if name in profile_links:
                link=html.Element('a',href=profile_links[name],target='_blank',rel='noopener noreferrer');link.append(html.Element('img',src='/images/people/mengdi-han/'+icon,alt='',attrib={'aria-hidden':'true','width':'18','height':'18'}));label=html.Element('span');label.text=name;link.append(label);profile_nav.append(link)
        contact.append(layout)
        # Remove the former optional Apple MapKit enhancement.
        for name in ('apple-maps-config','contact-map'):
            for old_script in tree.xpath('//script[starts-with(@src,"/static/'+name+'.js")]'):
                old_script.getparent().remove(old_script)
        # The platform snapshot nests the right column inside the left column.
        for right in tree.xpath('//div[contains(concat(" ",@class," ")," col-7 ")]'):
            rows=right.xpath('ancestor::div[contains(concat(" ",@class," ")," s-row-content ")]')
            if rows:rows[-1].append(right)
        for spacer in tree.xpath('//div[contains(concat(" ",@class," ")," s-element-spacer ")]'):
            spacer.getparent().remove(spacer)
        for image in tree.xpath('//img[@src]'):
            if image.get('src')=='/images/people/mengdi-han/contact-02.jpg':
                image.set('alt','Peking University campus map and laboratory location');image.set('loading','eager')
                if image.getparent().tag!='a':
                    parent=image.getparent();link=html.Element('a',href=image.get('src'),attrib={'data-lightbox':'true','aria-label':'Enlarge laboratory location map'});parent.replace(image,link);link.append(image)
    if route=='covers':
        content=tree.xpath('//*[@id="s-content"]')[0]
        existing_cards=content.xpath('.//article[@class="lab-cover-card"]')
        covers=[(card.xpath('.//img')[0].get('src'),card.xpath('.//a[@class="lab-cover-article"]')[0].get('href')) for card in existing_cards] if existing_cards else [(image.get('src'),image.getparent().get('href')) for image in content.xpath('.//img') if image.getparent().tag=='a']
        content.clear();content.set('id','s-content')
        gallery=html.fragment_fromstring('<main class="lab-covers-layout"><header><h1>Journal covers</h1><p>Explore the covers featuring our research.</p></header><div class="lab-covers-grid"></div></main>')
        grid=gallery.xpath('.//div')[0]
        def cover_info(href):
            info=publication_index.get(paper_key(href),{}).copy()
            record=citations['records'].get(title_key(info.get('title','')))
            if record and record.get('year'):info['year']=record['year']
            return info
        covers.sort(key=lambda item:cover_info(item[1]).get('year',0),reverse=True)
        for src,href in covers:
            info=cover_info(href)
            card=html.Element('article',{'class':'lab-cover-card'})
            image_link=html.Element('a',href=href,attrib={'target':'_blank','rel':'noopener noreferrer','class':'lab-cover-image','aria-label':'Read article: '+info.get('title','Journal cover')});image_link.append(html.Element('img',src=src,alt=info.get('journal','Journal')+' cover',loading='lazy'));card.append(image_link)
            caption=html.Element('div',{'class':'lab-cover-caption'})
            heading=html.Element('h2');heading.text=info.get('journal') or 'Journal cover';caption.append(heading)
            if info.get('year'):
                year=html.Element('p',{'class':'lab-cover-year'});year.text='Publication · '+str(info['year']);caption.append(year)
            if info.get('title'):
                title=html.Element('p',{'class':'lab-cover-title'});title.text=info['title'];caption.append(title)
            article=html.Element('a',href=href,attrib={'target':'_blank','rel':'noopener noreferrer','class':'lab-cover-article'});article.text='View article ↗';caption.append(article)
            paper=html.Element('a',href=href);paper.text=info.get('title','Journal cover');caption.append(citation_badge(citation_record(paper),paper.text))
            card.append(caption);grid.append(card)
        content.append(gallery)
    # Research navigation is authored centrally, so every page uses the same four entries.
    research_routes = [('overview', 'Overview'), ('wireless-implants', 'Wireless implants'), ('actuators-microrobotics', 'Actuators & microrobotics'), ('wearable-devices-eskins', 'Wearable devices & e-skins')]
    for menu in tree.xpath('//header[contains(@class,"lab-header")]//details'):
        if text(menu.find('summary')).strip().upper() == 'RESEARCH':
            panel = menu.find('div')
            if panel is not None:
                panel.clear(); panel.set('class', 'lab-menu-items')
                for target, label in research_routes:
                    entry = html.Element('a', href='/' + target + '/'); entry.text = label; panel.append(entry)
    retired_research = {'/smart-implants': '/wireless-implants/', '/electronic-skins': '/wearable-devices-eskins/', '/wearable-devices': '/wearable-devices-eskins/'}
    for link in tree.xpath('//a[@href]'):
        target = link.get('href').rstrip('/')
        if target in retired_research: link.set('href', retired_research[target])
    for menu in tree.xpath('//header[contains(@class,"lab-header")]//details'):
        label=text(menu.find('summary')).replace('⌄','').strip().upper()
        if label not in ('PUBLICATIONS','NEWS'):continue
        a=html.Element('a',href='/'+label.lower()+'/');a.text=label;menu.getparent().replace(menu,a)
    kind=None;active=None
    if re.fullmatch(r'publications\d{4}',route):kind='publications';active=route[len(kind):]
    elif re.fullmatch(r'news\d{4}',route):kind='news';active=route[4:]
    elif route in ('publications','news'):kind=route;active=str(current(pub_years if kind=='publications' else news_years))
    elif route in ('all','covers'):kind='publications';active=route
    elif route=='news-all':kind='news';active=route
    if kind:
        body=tree.find('body');body.set('class',(body.get('class','')+' lab-archive-page '+('lab-news-page' if kind=='news' else 'lab-publications-page')).strip())
        for old in tree.xpath('//nav[contains(@class,"lab-archive-nav")]'):old.getparent().remove(old)
        header=tree.xpath('//header[contains(@class,"lab-header")]')[0]
        header.addnext(archive_nav(kind,active))
        title=tree.find('head/title')
        if title is not None:title.text=('Publications' if kind=='publications' else 'News')+' — '+('Full List' if active in ('all','news-all') else 'Covers' if active=='covers' else active)+' — Mengdi Han Research Group'
        for meta in tree.xpath('//meta[@property="og:url"]'):meta.set('content','https://hanmd1990.github.io/'+actual_route+'/')
        for canonical in tree.xpath('//link[@rel="canonical"]'):canonical.set('href','https://hanmd1990.github.io/'+actual_route+'/')
        # Avoid a duplicate Covers link left from the old archive layout.
        for heading in tree.xpath('//h5[.//a[contains(@href,"scholar.google.com")]]'):
            heading.getparent().remove(heading)
        for note in tree.xpath('//*[@id="s-content"]//h5|//*[@id="s-content"]//p'):
            if 'Corresponding authors' in text(note) and 'Authors contributed equally' in text(note):note.getparent().remove(note)
        for element in tree.xpath('//*[@id="s-content"]//h1|//*[@id="s-content"]//h2|//*[@id="s-content"]//h3|//*[@id="s-content"]//h4|//*[@id="s-content"]//h5|//*[@id="s-content"]//h6|//*[@id="s-content"]//p'):
            if re.fullmatch(r'\d{4}',text(element)):add_class(element,'lab-content-year')
    if not route.startswith('news') and route not in ('.','covers','overview','electronic-skins','wearable-devices','smart-implants'):
        for link in tree.xpath('//a[contains(concat(" ",@class," ")," lab-publication-link ")]'):
            if not text(link):
                if route=='.':
                    feature=next((e for e in link.iterancestors() if 's-block-feature' in e.get('class','').split()),None)
                    info=publication_index.get(paper_key(link.get('href','')))
                    if feature is not None and info:
                        subtitles=feature.xpath('.//*[contains(concat(" ",@class," ")," lab-home-citation ")]')
                        if subtitles:
                            paper=html.Element('a',href=link.get('href'));paper.text=info['title'];subtitles[0].append(citation_badge(citation_record(paper),paper.text))
                continue
            paragraph=next((a for a in link.iterancestors() if a.tag=='p'),None)
            if paragraph is None:continue
            if (route in ('all','publications') or re.fullmatch(r'publications\d{4}',route)) and (not paper_id(paragraph) or paragraph.xpath('.//a[@href]')[0] is not link):continue
            record=citation_record(link)
            target=paragraph;next_element=paragraph.getnext()
            for _ in range(3):
                if next_element is None or paper_id(next_element) or next_element.xpath('.//a[contains(@class,"lab-publication-link")]'):break
                if next_element.tag=='p' and next_element.xpath('.//em[not(contains(@class,"lab-author-note"))]'):target=next_element
                next_element=next_element.getnext()
            if target.xpath('./span[contains(@class,"lab-citation-badge")]'):continue
            target.append(citation_badge(record,text(link)))
    for stylesheet in tree.xpath('//link[starts-with(@href,"/static/member-preview.css")]'):
        stylesheet.set('href','/static/member-preview.css?v='+hashlib.sha256((ROOT/'static/member-preview.css').read_bytes()).hexdigest()[:12])
    for stylesheet in tree.xpath('//link[starts-with(@href,"/static/hmd-color.css")]'):
        stylesheet.getparent().remove(stylesheet)
    tree.find('head').append(html.Element('link',rel='stylesheet',href='/static/hmd-color.css?v='+color_version))
    for script in tree.xpath('//script[starts-with(@src,"/static/site.js")]'):script.set('src','/static/site.js?v='+script_version)
    for old_script in tree.xpath('//script[starts-with(@src,"/static/analytics.js")]'):
        old_script.getparent().remove(old_script)
    analytics_version=hashlib.sha256((ROOT/'static/analytics.js').read_bytes()).hexdigest()[:12]
    tree.find('head').append(html.Element('script',src='/static/analytics.js?v='+analytics_version,defer='defer'))
    write(path,tree)

from archive_layout import rebuild_archives
archive_details=rebuild_archives(ROOT,member_bibliography,citations,today)

from literature_layout import rebuild_literature
rebuild_literature(ROOT)

# Render these public pages last, keeping editable source text and media intact.
from research_layout import rebuild_research
rebuild_research(ROOT)

report={'archive_design':'clean-academic',**archive_details,'current_year':today,'publications_entry_year':current(pub_years),'news_entry_year':current(news_years),'publication_years':pub_years,'news_years':news_years,'publication_counts':counts,'total_publications':len(paper_ids)}
(ROOT/'archive-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))

