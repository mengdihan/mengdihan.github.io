from pathlib import Path
from lxml import html
import copy,re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
source=html.document_fromstring((root/'join/index.html').read_text(encoding='utf8'))
page=html.document_fromstring('<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Join Us — Design Preview</title><link rel="stylesheet" href="/static/site.css"><link rel="stylesheet" href="/static/hmd-color.css"><link rel="stylesheet" href="/static/join-preview.css?v=20261014"><script src="/static/site.js" defer></script></head><body class="lab-join-preview"><div id="s-content"></div></body></html>')
page.find('body').insert(0,copy.deepcopy(source.xpath('//header[contains(@class,"lab-header")]')[0]))
main=html.Element('main',{'class':'join-preview-layout'});intro=html.Element('header',{'class':'join-preview-intro'})
title=html.Element('h1');title.text='Join Us';intro.append(title)
note=html.fragment_fromstring('<p class="join-preview-note">Design preview · <a href="/join/">View the current page</a></p>');intro.append(note)
for paragraph in source.xpath('//*[@id="s-content"]//p[not(ancestor::details)]'):
    if paragraph.text_content().strip():intro.append(copy.deepcopy(paragraph))
main.append(intro)
for old in source.xpath('//details[@class="lab-disclosure"]'):
    details=html.Element('details',{'class':'join-role-card'})
    summary=html.Element('summary');value=' '.join(old.xpath('./summary')[0].text_content().split())
    match=re.match(r'(.+?)\s*(\(.+\))$',value)
    heading=html.Element('h2');heading.text=match[1] if match else value;summary.append(heading)
    if match:
        availability=html.Element('p',{'class':'join-availability'});availability.text=match[2];summary.append(availability)
    details.append(summary)
    body=copy.deepcopy(old.xpath('./div')[0]);body.set('class','join-role-content')
    for child in body.iter():
        child.attrib.pop('style',None)
        if child is not body:child.attrib.pop('class',None)
    details.append(body);main.append(details)
for child in intro.iter():
    child.attrib.pop('style',None)
    if child not in (intro,note) and child.tag!='h1':child.attrib.pop('class',None)
page.xpath('//*[@id="s-content"]')[0].append(main)
out=root/'preview/join-us/index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(html.tostring(page,encoding='utf8',doctype='<!DOCTYPE html>'))
print('Generated Join Us preview; formal join/ unchanged.')
