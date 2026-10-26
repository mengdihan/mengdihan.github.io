from lxml import html
from datetime import datetime

def build_gallery(entries):
    aside=html.Element('aside',{'class':'member-photos member-gallery','aria-label':'Group photos'})
    heading=html.Element('h2');heading.text='Group Photos';aside.append(heading)
    slides=html.Element('div',{'class':'member-gallery-slides','aria-live':'polite'});aside.append(slides)
    for i,entry in enumerate(entries):
        figure=html.Element('figure',id='group-photo-'+str(i+1),attrib={'class':'member-gallery-slide'})
        link=html.Element('a',href=entry['image'],attrib={'data-lightbox':'true','aria-label':'Enlarge '+entry['caption']+' — '+entry['date']})
        photo=html.Element('img',src=entry['image'],alt=entry['caption'],loading='eager' if i==0 else 'lazy',decoding='async');link.append(photo);figure.append(link)
        caption=html.Element('figcaption');caption.text=entry['caption'];date=html.Element('span',{'class':'photo-date'});date.text=entry['date'];caption.append(date);figure.append(caption);slides.append(figure)
    controls=html.Element('div',{'class':'member-gallery-controls','hidden':'hidden'})
    for action,label in [('previous','Previous'),('next','Next')]:
        button=html.Element('button',type='button',attrib={'data-gallery-action':action,'aria-label':label+' group photograph'});button.text=label
        if action=='next':
            count=html.Element('span',{'class':'member-gallery-count','aria-live':'polite'});count.text='1 / '+str(len(entries));controls.append(count)
        controls.append(button)
    aside.append(controls)
    thumbs=html.Element('div',{'class':'member-gallery-thumbs','aria-label':'Choose a group photograph'});aside.append(thumbs)
    for i,entry in enumerate(entries):
        link=html.Element('a',href='#group-photo-'+str(i+1),attrib={'data-gallery-index':str(i),'aria-label':entry['caption']+' — '+entry['date'],'title':entry['caption']+' — '+entry['date']})
        link.append(html.Element('img',src=entry.get('thumbnail',entry['image']),alt='',loading='lazy',decoding='async'))
        date=html.Element('span',{'class':'member-thumb-date'});date.text=datetime.strptime(entry['date'],'%B %Y').strftime('%b. %Y');link.append(date);thumbs.append(link)
    return aside
