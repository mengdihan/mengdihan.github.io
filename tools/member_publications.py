"""Offline author matching and Alumni additions from the canonical bibliography."""
import copy
import json
import re
import unicodedata
from lxml import html


def name_key(value):
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def read_bibliography(root):
    papers = {}
    cache_path = root / "data/publication-full-authors.json"
    full_names = json.loads(cache_path.read_text(encoding="utf8"))["records"] if cache_path.exists() else {}
    for path in root.glob('publications/[0-9]*/index.html'):
        if not re.fullmatch(r'\d{4}', path.parent.name):
            continue
        for paragraph in html.document_fromstring(path.read_text(encoding='utf8')).xpath('//p'):
            match = re.match(r'^\((\d+)\)', paragraph.text_content().strip())
            links = paragraph.xpath('.//a[@href]')
            if not match or not links:
                continue
            following = paragraph.getnext()
            if following is None:
                continue
            authors = [a.strip() for a in following.text_content().split(',')]
            journal = ''
            for _ in range(3):
                if following is None:
                    break
                for em in following.xpath('.//em'):
                    value = ' '.join(em.text_content().split())
                    if value and not re.fullmatch(r'et\s*al\.?|\d+(?:\.\d+)?', value, re.I):
                        journal = value
                        break
                if journal:
                    break
                following = following.getnext()
            metadata = copy.deepcopy(following) if journal and following is not None else html.Element('p')
            for badge in metadata.xpath('.//*[contains(@class,"lab-citation-badge")]'):
                badge.getparent().remove(badge)
            for node in metadata.iter():
                node.attrib.pop('style', None)
                node.attrib.pop('class', None)
            for em in metadata.xpath('.//em'):
                if re.fullmatch(r'\d+(?:[.\-–]\d+)?', ' '.join(em.text_content().split())):
                    em.set('class', 'lab-volume')
            papers[int(match[1])] = dict(metadata=metadata, title=' '.join(links[0].text_content().split()),
                url=links[0].get('href'), journal=journal, year=int(path.parent.name[-4:]), authors=authors)
    for pid, paper in papers.items():
        cached = full_names.get(str(pid), {})
        paper["display_authors"] = ([a.strip() for a in cached["authors"].split(",")]
            if name_key(cached.get("title", "")) == name_key(paper["title"]) else paper["authors"])
    return papers


def is_member_first_author(name, pid, papers, roster):
    if str(pid) in roster.get('excluded_representative_paper_ids', {}):
        return False
    paper = papers[pid]
    tokens = paper['authors']
    # The PI must also be an author; no independent member papers are added.
    if not any(name_key(re.sub('[¹*]', '', a)) in ('mhan', 'mengdihan') for a in tokens):
        return False
    words = name.split()
    initials = ''.join(w[0] for w in words[:-1]) + ' ' + words[-1]
    confirmation = roster.get('confirmed_author_positions', {}).get(str(pid), {}).get(name)
    evidence = roster.get('evidence', {}).get(str(pid), {})
    full = evidence.get('full_authors', [])
    # Reject stale DOI evidence if a bibliography number was accidentally reused.
    doi = evidence.get('doi')
    linked_doi = re.search(r'10\.\d{4,9}/[^?#]+', paper['url'], re.I)
    if doi and linked_doi and doi.casefold() != linked_doi[0].rstrip('/').casefold():
        full = []
    for index, token in enumerate(tokens):
        clean = name_key(re.sub('[¹*]', '', token))
        if index != 0 and '¹' not in token:
            continue
        if clean == name_key(name):
            return True
        if clean != name_key(initials):
            continue
        if confirmation and confirmation['author_index'] == index:
            return True
        if index < len(full) and name_key(full[index]) == name_key(name):
            return True
    return False


def add_alumni_publications(tree, papers, roster):
    additions = []
    for card in tree.xpath('//article[@class="alumni-member"]'):
        name = card.get('data-member')
        panel = card.xpath('./div[@class="alumni-publications"]')[0]
        existing = {name_key(a.text_content()) for a in panel.xpath('./p[@class="alumni-paper-title"]//a')}
        for pid in sorted(papers, reverse=True):
            paper = papers[pid]
            if name_key(paper['title']) in existing or not is_member_first_author(name, pid, papers, roster):
                continue
            if not existing:
                for child in list(panel):
                    panel.remove(child)
            title = html.Element('p', {'class': 'alumni-paper-title', 'data-paper-id': str(pid)})
            link = html.Element('a', href=paper['url'], target='_blank', rel='noopener noreferrer',
                attrib={'class': 'lab-publication-link', 'data-link-kind': 'article'})
            link.text = paper['title']; title.append(link); panel.append(title)
            metadata = html.Element('p', {'class': 'alumni-paper-meta'})
            authors = [a for a in paper.get('display_authors', paper['authors']) if '¹' in a] or paper.get('display_authors', paper['authors'])[:1]
            metadata.text = ', '.join(authors) + ', '
            note = html.Element('em', {'class': 'lab-author-note'})
            note.text = 'et al.'; note.tail = ', ' + (paper['metadata'].text or '')
            metadata.append(note)
            for child in paper['metadata']:
                metadata.append(copy.deepcopy(child))
            panel.append(metadata)
            existing.add(name_key(paper['title']))
            additions.append({'member': name, 'paper_id': pid})
        # Refresh curated selections too, without changing their eligibility or order.
        by_title = {name_key(p['title']): p for p in papers.values()}
        for title in panel.xpath('./p[@class="alumni-paper-title"]'):
            paper = by_title.get(name_key(title.text_content()))
            metadata = title.getnext()
            if paper is None or metadata is None or metadata.get('class') != 'alumni-paper-meta':
                continue
            metadata.clear(); metadata.set('class', 'alumni-paper-meta')
            names = paper.get('display_authors', paper['authors'])
            metadata.text = ', '.join([a for a in names if '¹' in a] or names[:1]) + ', '
            note = html.Element('em', {'class': 'lab-author-note'})
            note.text = 'et al.'; note.tail = ', ' + (paper['metadata'].text or '')
            metadata.append(note)
            for child in paper['metadata']:
                metadata.append(copy.deepcopy(child))
        toggle = card.xpath('.//button[@class="alumni-publications-toggle"]')[0]
        toggle.text = 'Selected Publications' + (' ('+str(len(existing))+')' if existing else '')
    return additions
