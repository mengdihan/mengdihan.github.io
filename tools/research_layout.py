"""Render Home, Research and Bio from editable content, without the legacy theme."""
import copy
import hashlib
import re
from lxml import html


ROUTES = ('', 'overview', 'wireless-implants', 'actuators-microrobotics', 'wearable-devices-eskins', 'bio')
AREAS = [('wireless-implants', 'Wireless implants'), ('actuators-microrobotics', 'Actuators and microrobots'), ('wearable-devices-eskins', 'Wearables and e-skins')]


def text(node):
    return ' '.join(node.text_content().split())


def element(tag, value=None, **attrs):
    node = html.Element(tag, {key.replace('_', '-'): str(value) for key, value in attrs.items()})
    node.text = value
    return node


def clean(node):
    node = copy.deepcopy(node)
    node.tail = None
    for child in node.iter():
        for attr in ('style', 'class', 'id'):
            child.attrib.pop(attr, None)
    return node


def image(source, alt, eager=False):
    img = clean(source)
    img.set('alt', alt)
    img.set('loading', 'eager' if eager else 'lazy')
    img.set('decoding', 'async')
    if eager:
        img.set('fetchpriority', 'high')
    return img


def area_nav(active):
    nav = element('nav', aria_label='Research areas', **{'class': 'rd-area-nav'})
    for route, label in [('overview', 'Overview'), *AREAS]:
        link = element('a', label, href='/' + route + '/')
        if route == active:
            link.set('aria-current', 'page')
        nav.append(link)
    return nav


def rebuild_research(root):
    sources = {route: html.document_fromstring((root / route / 'index.html').read_bytes()) for route in ROUTES}
    for route, source in sources.items():
        content = copy.deepcopy(source.get_element_by_id('s-content'))
        for node in content.xpath('.//style|.//script'):
            node.getparent().remove(node)
        page = html.document_fromstring('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body class="lab-research-design"></body></html>')
        head, body = page.find('head'), page.find('body')
        for node in source.xpath('//head/title|//head/meta[@name="description" or @name="keywords" or @property]|//head/link[@rel="canonical" or @rel="icon" or @rel="shortcut icon"]'):
            head.append(copy.deepcopy(node))
        styles = ('site.css', 'hmd-color.css', 'research.css')
        if not route:
            body.set('class', 'lab-research-design lab-home-design')
            styles += ('home.css',)
        for name in styles:
            version = hashlib.sha256((root / 'static' / name).read_bytes()).hexdigest()[:12]
            head.append(element('link', rel='stylesheet', href='/static/' + name + '?v=' + version))
        scripts = ('site.js', 'home.js', 'analytics.js') if not route else ('site.js', 'research.js', 'analytics.js')
        for name in scripts:
            version = hashlib.sha256((root / 'static' / name).read_bytes()).hexdigest()[:12]
            head.append(element('script', src='/static/' + name + '?v=' + version, defer='defer'))
        skip = element('a', 'Skip to content', href='#s-content', **{'class': 'rd-skip'})
        body.append(skip)
        header = copy.deepcopy(source.xpath('//header[contains(@class,"lab-header")]')[0])
        for link in header.xpath('.//a[@aria-current]'):
            link.attrib.pop('aria-current')
        for link in header.xpath('.//a[@href=$href]', href='/' if not route else '/' + route + '/'):
            link.set('aria-current', 'page')
        body.append(header)
        main = element('main', id='s-content', **{'class': 'rd-main'})
        body.append(main)
        if not route:
            build_home(main, content)
        elif route == 'overview':
            build_overview(main, content)
        elif route == 'bio':
            build_bio(main, content)
        else:
            build_area(main, content, route)
        (root / route / 'index.html').write_bytes(html.tostring(page, encoding='utf-8', doctype='<!doctype html>'))
    print('Home, Research and Bio: rebuilt 6 pages with original content and local styles')


def build_home(main, content):
    # HOME is authored directly; preserve the carousel captions and section order.
    for child in content:
        main.append(copy.deepcopy(child))


def build_overview(main, content):
    authored = content.find('.//*[@class="rd-overview-authored"]')
    if authored is not None:
        main.append(copy.deepcopy(authored))
        return
    main.append(area_nav('overview'))
    paragraphs = [node for node in content.xpath('.//p') if text(node)]
    intro = element('section', **{'class': 'rd-overview-intro'})
    intro.append(element('h1', 'Overview'))
    intro.append(element('p', next(text(node) for node in paragraphs if text(node).startswith('Bioelectronics offers'))))
    main.append(intro)
    images = content.xpath('.//img')
    figure = element('figure', **{'class': 'rd-overview-image'})
    figure.append(image(images[0], 'Overview of the group’s bioelectronics research', True))
    main.append(figure)
    section = element('section', **{'class': 'rd-areas'})
    section.append(element('h2', 'Explore three of our research areas'))
    grid = element('div', **{'class': 'rd-area-grid'})
    for (route, title), img in zip(AREAS, images[1:]):
        link = element('a', href='/' + route + '/', **{'class': 'rd-area'})
        link.append(image(img, title))
        link.append(element('h3', title))
        grid.append(link)
    section.append(grid)
    main.append(section)


def build_area(main, content, route):
    authored = content.find('.//*[@class="rd-research-authored"]')
    if authored is not None:
        main.append(area_nav(route))
        main.append(copy.deepcopy(authored))
        return
    title = dict(AREAS)[route]
    main.append(area_nav(route))
    paragraphs = [node for node in content.xpath('.//p') if text(node)]
    intro = element('section', **{'class': 'rd-area-intro'})
    intro.append(element('h1', title))
    intro.append(element('p', text(paragraphs[1])))
    main.append(intro)
    gallery = element('div', aria_label=title + ' research images', **{'class': 'rd-research-gallery'})
    for img in content.xpath('.//img'):
        link = clean(img.xpath('ancestor::a')[0])
        for child in list(link):
            link.remove(child)
        link.set('aria-label', title + ' — read the related publication')
        link.append(image(img, title + ' research', not len(gallery)))
        gallery.append(link)
    main.append(gallery)
    section = element('section', aria_label='Representative Publications', **{'class': 'rd-publications'})
    section.append(element('h2', 'Representative Publications'))
    listing = element('div', **{'class': 'rd-paper-list'})
    current = None
    for paragraph in paragraphs[2:]:
        value = text(paragraph)
        if re.match(r'^\(\d+\)', value):
            current = element('article', **{'class': 'rd-paper'})
            listing.append(current)
            heading = clean(paragraph)
            heading.tag = 'h3'
            current.append(heading)
        elif current is not None:
            metadata = clean(paragraph)
            journals = metadata.xpath('.//em')
            if journals:
                journals[0].set('class', 'rd-journal-name')
            current.append(metadata)
    assert len(listing) == 3, f'Expected three representative publications: {route}'
    section.append(listing)
    main.append(section)


def build_bio(main, content):
    paragraphs = [node for node in content.xpath('.//p') if text(node)]
    english = next(node for node in paragraphs if text(node).startswith('Dr. Mengdi Han'))
    chinese = next(node for node in paragraphs if text(node).startswith('韩梦迪，北京大学'))
    chinese_heading = next(text(node) for node in paragraphs if text(node).startswith('Bio (Chinese version'))
    for index, (identity, language, heading, paragraph) in enumerate([
        ('bio-english', 'en', 'Bio', english),
        ('bio-chinese', 'zh-Hans', chinese_heading, chinese),
    ]):
        section = element('section', id=identity, lang=language, aria_labelledby=identity + '-title', **{'class': 'rd-bio-section'})
        section.append(element('h1' if index == 0 else 'h2', heading, id=identity + '-title'))
        prose = clean(paragraph)
        prose.set('class', 'rd-bio-prose')
        section.append(prose)
        main.append(section)
