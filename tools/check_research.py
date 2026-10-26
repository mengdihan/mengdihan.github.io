"""Check that redesigned pages preserve editable Home, Research and Bio content."""
from collections import Counter
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, urlunsplit
from lxml import html


def normalize_text(value):
    return re.sub(r'\s+', '', value)


def normalize_link(value):
    url = urlsplit(value)
    path = url.path.rstrip('/')
    path = {'/smart-implants': '/wireless-implants', '/electronic-skins': '/wearable-devices-eskins', '/wearable-devices': '/wearable-devices-eskins'}.get(path, path)
    if path == '/microrobot':
        path = '/publications/microrobot'
    return urlunsplit((url.scheme, url.netloc, path, url.query, url.fragment))


source_root = Path(__file__).resolve().parent.parent
output_root = Path(sys.argv[1]).resolve()
for route in ('', 'overview', 'wireless-implants', 'actuators-microrobotics', 'wearable-devices-eskins', 'bio'):
    source = html.document_fromstring((source_root / route / 'index.html').read_bytes()).get_element_by_id('s-content')
    page = html.document_fromstring((output_root / route / 'index.html').read_bytes())
    output = page.get_element_by_id('s-content')
    for node in source.xpath('.//style|.//script|.//*[@id="s-footer-section-container"]|.//*[@id="s-footer-logo-wrapper"]|.//*[contains(@class,"lab-carousel-controls")]'):
        node.getparent().remove(node)
    rendered_text = normalize_text(output.text_content())
    for paragraph in source.xpath('.//p'):
        assert normalize_text(paragraph.text_content()) in rendered_text, (route, paragraph.text_content())
    assert Counter(source.xpath('.//img/@src')) == Counter(output.xpath('.//img/@src')), route
    links = {normalize_link(value) for value in output.xpath('.//a/@href')}
    assert all(normalize_link(value) in links for value in source.xpath('.//a/@href')), route
    assert len(page.xpath('//main')) == len(page.xpath('//h1')) == 1, route
    assert not page.xpath('//link[contains(@href,"/static/styles/theme-")]'), route
    assert all(image.get('alt') for image in output.xpath('.//img')), route
    assert len(output.xpath('.//article[@class="rd-paper"]')) == (0 if source.xpath('.//*[@class="rd-research-authored"]') or route in ('', 'overview', 'bio') else 3), route
    if route == 'bio':
        assert len(output.xpath('.//section[@lang="en"]')) == 1
        assert len(output.xpath('.//section[@lang="zh-Hans"]')) == 1
print('PASS: Home, four Research pages and Bio preserve text, images and links; semantic headings and independent styles verified.')
