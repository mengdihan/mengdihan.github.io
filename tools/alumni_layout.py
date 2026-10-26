import copy,re,unicodedata
from lxml import html

def title_key(value):
    return ''.join(c for c in unicodedata.normalize('NFKC',value).casefold() if c.isalnum())

def bibliography_authors(root):
    records={}
    for path in root.glob('publications/[0-9]*/index.html'):
        source=html.document_fromstring(path.read_bytes())
        for paragraph in source.xpath('//p'):
            if not re.match(r'^\(\d+\)',paragraph.text_content().strip()):continue
            links=paragraph.xpath('.//a[@href]');following=paragraph.getnext()
            if links and following is not None:
                records[title_key(links[0].text_content())]=[a.strip() for a in following.text_content().split(',')]
    return records

def eligible_paper(name,title,records):
    # The curated member selection supplies the identity; check its author position
    # against the PI bibliography rather than allocating papers by initials alone.
    authors=records.get(title_key(title),[])
    if not any(re.fullmatch(r'M\s+Han[¹*\s]*',a) for a in authors):return False
    words=name.split();member=''.join(w[0] for w in words[:-1])+' '+words[-1]
    return any(re.sub(r'[¹*]','',a).strip()==member and (i==0 or '¹' in a) for i,a in enumerate(authors))

def rebuild_alumni(tree,records):
    old=tree.xpath('//details[contains(concat(" ",normalize-space(@class)," ")," lab-disclosure ")]')
    if not old:return
    main=html.Element('main',{'class':'lab-alumni-layout'})
    heading=html.Element('h1');heading.text='Alumni '
    order_note=html.Element('span',{'class':'alumni-order-note'});order_note.text='(in chronological order)';heading.append(order_note);main.append(heading)
    grid=html.Element('div',{'class':'alumni-grid'});main.append(grid)
    for member in old:
        values=[' '.join(p.text_content().split()) for p in member.xpath('./summary//p') if p.text_content().strip()]
        if not values:continue
        match=re.match(r'(.+?)\s*\(([^)]+)\),\s*(.+)',values[0])
        if not match:continue
        name,zh,role=match.groups()
        role={'Joint Ph.D.':'Joint Ph.D. Student','Postdoctoral Researcher':'Postdoc'}.get(role,role)
        fields={}
        for value in values[1:]:
            key,sep,text=value.partition(':')
            if sep:fields[' '.join(key.lower().split())]=text.strip()
        details=html.Element('article',{'class':'alumni-member','data-member':name})
        profile=html.Element('div',{'class':'alumni-profile'})
        nameplate=html.Element('div',{'class':'alumni-nameplate'})
        title=html.Element('h3');title.text=name;nameplate.append(title)
        chinese=html.Element('p',{'class':'alumni-chinese'});chinese.text=zh;nameplate.append(chinese);profile.append(nameplate)
        pathway=html.Element('div',{'class':'alumni-pathway'})
        labels=html.Element('div',{'class':'alumni-stage-labels'})
        for title_text in ('Prior education','Role in the group','Next position'):
            label=html.Element('h2');label.text=title_text;labels.append(label)
        pathway.append(labels)
        stages=html.Element('div',{'class':'alumni-stages'});pathway.append(stages);profile.append(pathway)
        prior=html.Element('div',{'class':'alumni-prior','role':'group','aria-label':'Prior education'})
        for key,value in fields.items():
            if key.endswith('school'):
                degree='Ph.D. Student' if key.startswith('ph.d.') else ('Master' if key.startswith('master') else 'Undergraduate')
                degree_line=html.Element('p',{'class':'alumni-stage-primary'});degree_line.text=degree;prior.append(degree_line)
                school=html.Element('p',{'class':'alumni-stage-secondary'});school.text=value.replace('Chinese Academy of Sciences','CAS');prior.append(school)
        stages.append(prior)
        identity=html.Element('div',{'class':'alumni-identity','role':'group','aria-label':'Role in the group'})
        tenure=html.Element('div',{'class':'alumni-tenure'});identity.append(tenure)
        position=html.Element('p',{'class':'alumni-role'});position.text=role;tenure.append(position)
        years=html.Element('p',{'class':'alumni-years'});years.text=fields.get('years in group','');tenure.append(years);stages.append(identity)
        next_position=html.Element('div',{'class':'alumni-next','role':'group','aria-label':'Next position'})
        next_value=fields.get('next position','')
        position_name,separator,institution=next_value.partition(' at ')
        position_name={'Faculty Member':'Faculty','Postdoctoral Researcher':'Postdoc'}.get(position_name,position_name)
        if not separator:institution=next_value;position_name=''
        if position_name:
            position_line=html.Element('p',{'class':'alumni-stage-primary'});position_line.text=position_name;next_position.append(position_line)
        destination=html.Element('p',{'class':'alumni-stage-secondary'});destination.text=re.sub(r'^the ','',institution).replace('Chinese Academy of Sciences','CAS');next_position.append(destination);stages.append(next_position)
        details.append(profile)
        paragraphs=member.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," lab-disclosure-content ")]//p')
        content=html.Element('div',{'class':'alumni-publications'})
        count=0
        include=False
        for paragraph in paragraphs:
            if not paragraph.text_content().strip() or 'Selected Publications:'==paragraph.text_content().strip():continue
            clone=copy.deepcopy(paragraph)
            title_link=clone.xpath('.//a[contains(@class,"lab-publication-link")]')
            if title_link:include=eligible_paper(name,title_link[0].text_content(),records)
            if not include:continue
            for node in clone.iter():
                node.attrib.pop('style',None)
                classes=[value for value in node.get('class','').split() if value.startswith('lab-')]
                if classes:node.set('class',' '.join(classes))
                else:node.attrib.pop('class',None)
            clone.set('class','alumni-paper-title' if title_link else 'alumni-paper-meta')
            if title_link:
                link=copy.deepcopy(title_link[0])
                title=link.text_content().strip()
                for child in list(link):link.remove(child)
                link.text=title;link.tail=None
                clone.clear();clone.set('class','alumni-paper-title');clone.append(link)
                count+=1
            else:
                for strong in clone.xpath('.//strong'):strong.drop_tag()
            content.append(clone)
        if not count:
            empty=html.Element('p',{'class':'alumni-paper-meta'});empty.text='-';content.append(empty)
        key=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
        toggle=html.Element('button',{'class':'alumni-publications-toggle','type':'button','id':'alumni-toggle-'+key,'aria-expanded':'false','aria-controls':'alumni-papers-'+key})
        toggle.text='Selected Publications'+(' ('+str(count)+')' if count else '')
        identity.append(toggle)
        content.set('id','alumni-papers-'+key);content.set('hidden','hidden');content.set('role','region');content.set('aria-labelledby',toggle.get('id'))
        details.append(content);grid.append(details)
    target=tree.xpath('//*[@id="s-content"]')[0]
    for child in list(target):target.remove(child)
    target.append(main)
