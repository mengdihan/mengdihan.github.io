"""Render recruitment content and dated availability from one editable data file."""
import datetime
import json
from lxml import html, etree


def rebuild_join(tree, root):
    data = json.loads((root / 'data/join-us.json').read_text(encoding='utf8'))
    content = tree.xpath('//*[@id="s-content"]')[0]
    content.clear()
    content.set('id', 's-content')
    main = etree.SubElement(content, 'main', {'class': 'lab-join-layout'})
    intro = etree.SubElement(main, 'header', {'class': 'lab-join-intro'})
    etree.SubElement(intro, 'p').text = data['intro']
    dates = etree.SubElement(intro, 'p', {'class': 'lab-join-updated'})
    dates.text = 'Page updated: '
    datetime.date.fromisoformat(data['updated_on'])
    etree.SubElement(dates, 'time', datetime=data['updated_on']).text = data['updated_on']
    nav = etree.SubElement(main, 'div', {'class': 'lab-join-nav', 'role': 'tablist', 'aria-label': 'Recruitment categories'})
    for index, role in enumerate(data['roles'], 1):
        link = etree.SubElement(nav, 'button', {'type': 'button', 'role': 'tab', 'id': 'tab-'+role['id'], 'aria-controls': role['id'], 'aria-selected': 'true' if index == 1 else 'false', 'tabindex': '0' if index == 1 else '-1'})
        etree.SubElement(link, 'span', {'class': 'lab-join-category'}).text = role['label']
        etree.SubElement(link, 'span', {'class': 'lab-join-count'}).text = role['count']
    for index, role in enumerate(data['roles'], 1):
        section = etree.SubElement(main, 'section', {'class': 'lab-join-role', 'id': role['id'], 'role': 'tabpanel', 'aria-labelledby': 'tab-'+role['id'], 'tabindex': '0'})
        if index != 1:
            section.set('hidden', 'hidden')
        header = etree.SubElement(section, 'header', {'class': 'lab-join-role-heading'})
        title = etree.SubElement(header, 'div')
        etree.SubElement(title, 'h2', id=role['id']+'-title').text = role['title']
        etree.SubElement(title, 'p').text = role['count']
        body = etree.SubElement(section, 'div', {'class': 'lab-join-role-body'})
        for node in html.fragments_fromstring(role['body']):
            body.append(node)
