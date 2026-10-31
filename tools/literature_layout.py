"""Build the public English literature archive from an explicit publication export."""
import copy,hashlib,json,re,datetime
from zoneinfo import ZoneInfo
from html import escape as esc
from pathlib import Path
from lxml import html

def rebuild_literature(root):
    folder=root/'data/literature'
    if not (folder/'index.json').exists():return
    index=json.loads((folder/'index.json').read_text())
    editions=[json.loads((folder/(key+'.json')).read_text()) for key in index['editions']]
    assert len({e['id'] for e in editions})==len(editions)
    for e in editions:
        assert len({a['id'] for a in e['articles']})==len(e['articles'])
        for a in e['articles']:
            assert a['url'].startswith('https://') and a['summary'] and a['topics']
            assert not re.search('[\u4e00-\u9fff]',json.dumps(a,ensure_ascii=False)),a['id']
    latest=next(e for e in editions if e['id']==index['latest'])
    header=copy.deepcopy(html.document_fromstring((root/'publications/index.html').read_bytes()).xpath('//header[contains(@class,"lab-header")]')[0])
    tree=html.document_fromstring('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BioE Radar Beta — Mengdi Han Research Group</title><meta name="description" content="Weekly literature on wireless implants, magnetic systems, wearable devices, bioelectronics and micromechanical sensing."></head><body class="lab-literature-page"></body></html>')
    head=tree.find('head');body=tree.find('body');body.append(header)
    head.append(html.Element('link',rel='canonical',href='https://hanmd1990.github.io/BioE_Radar/'))
    head.append(html.Element('link',rel='icon',href='/images/brand/site-icon.png'))
    for name in ('site.css','hmd-color.css','literature.css'):
        v=hashlib.sha256((root/'static'/name).read_bytes()).hexdigest()[:12]
        head.append(html.Element('link',rel='stylesheet',href='/static/'+name+'?v='+v))
    for name in ('site.js','literature-personalization.js','literature-account.js','literature-email.js','literature.js','analytics.js'):
        v=hashlib.sha256((root/'static'/name).read_bytes()).hexdigest()[:12]
        head.append(html.Element('script',src='/static/'+name+'?v='+v,defer='defer'))
    main=html.fragment_fromstring('''<main class="literature-layout" id="literature-main"><header class="literature-intro"><div class="lit-intro-topline"><h1>BioE Radar <span class="lit-beta">Beta</span></h1><section class="lit-account-panel" aria-label="Personal reading account" data-state="loading"><div class="lit-account-identity"><span class="lit-account-avatar" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="8" r="3.2"></circle><path d="M5.5 20v-1.5a6.5 6.5 0 0 1 13 0V20"></path></svg></span><div class="lit-account-copy"><strong id="lit-account-name">Your reading account</strong><span id="lit-feedback-status" role="status" aria-live="polite">Connecting…</span></div></div><div class="lit-account-actions"><button type="button" id="lit-email-open" disabled>Log in</button><button type="button" id="lit-account-signout" hidden>Sign out</button></div></section></div><div class="lit-intro-details"><p class="lit-intro-sentence">Recent literature related to our research group.</p><div id="lit-sources-panel" class="lit-sources-disclosure"><button type="button" id="lit-sources-toggle" class="lit-detail-toggle" aria-expanded="false" aria-controls="lit-sources-body"><span class="lit-sources-toggle">Sources</span></button><div id="lit-sources-body" class="lit-coverage lit-sources-body" hidden><p class="lit-sources-label">Journals and preprint sources</p><p id="lit-coverage-list"></p><ul class="lit-selection-criteria"><li>Science, Nature and Cell receive broad coverage, including articles beyond our immediate research interests.</li><li>Sister journals related to our lab’s research themes receive broad coverage.</li><li>Specialist journals contribute articles with the closest fit to our research directions.</li></ul><p>Selection criteria evolve with feedback from our lab.</p><p class="lit-personalization-note">Sign in with email to sync personal recommendations and shared reactions.</p></div></div><div class="lit-personalization-help"><button type="button" id="lit-recommendations-toggle" class="lit-detail-toggle" aria-expanded="false" aria-controls="lit-recommendations-body">Sign in for personalized recommendations</button><div id="lit-recommendations-body" class="lit-help-body" hidden><p>Sign in with email to sync your reactions and reading preferences. BioE Radar uses your earlier 'Like' and 'Useful' reactions to recommend related research. 'Not relevant' lowers the priority of similar research without excluding an entire journal or field.</p><p>You can also use BioE Radar without logging in. Community recommendations use readers’ overall preferences when available; otherwise, articles follow editorial relevance.</p></div></div></div><p class="lit-update-note">Weekly updates: <span id="lit-schedule-times"></span></p></header><div class="literature-tools"><label class="lit-search">Search literature<input id="lit-search" type="search" placeholder="Title, author, journal or keyword" autocomplete="off"></label><label>Edition<select id="lit-edition"></select></label><div class="lit-journal-control"><span>Journals included</span><button type="button" id="lit-journals-open" aria-haspopup="dialog">All journals</button></div><label>Sort by<select id="lit-sort"><option value="personal" selected>Recommended</option><option value="relevance">Editorial relevance</option><option value="date">Newest first</option><option value="journal">Journal</option></select></label></div><p class="lit-topics-note">Topics are generated from recent reader preferences and refreshed with each weekly update.</p><div class="lit-topics" role="group" aria-label="Filter by topic"></div><div class="lit-reader-tools"><div class="lit-feedback-tools"><label>Show<select id="lit-feedback-filter"><option value="all">All articles</option><option value="marked">With my feedback</option><option value="useful">Useful</option><option value="more">Like</option><option value="irrelevant">Not relevant</option></select></label></div><div class="lit-version-switch" role="group" aria-label="Recommendation version"><span class="lit-version-option"><button type="button" data-reading-version="personal" aria-pressed="false" aria-describedby="lit-personal-tip" disabled>Personal</button><span id="lit-personal-tip" class="lit-context-tip" role="tooltip">Recommendations based on your personal reading preferences.</span></span><span class="lit-version-option"><button type="button" data-reading-version="community" aria-pressed="true" aria-describedby="lit-community-tip">Community average</button><span id="lit-community-tip" class="lit-context-tip" role="tooltip">Recommendations based on the overall preferences of all readers across the site.</span></span></div></div><p id="lit-version-note" class="lit-version-note" hidden></p><div class="lit-status"><p id="lit-count" role="status" aria-live="polite"></p><p id="lit-window"></p></div><section id="lit-results" aria-label="Literature list"></section><p id="lit-empty" hidden>No articles match these filters. Try another keyword or adjust the filters.</p></main>''')

    # Keep account actions direct, without recommendation copy or a hover disclosure.
    help_section=main.xpath('.//div[@class="lit-personalization-help"]')[0]
    help_section.getparent().remove(help_section)
    main.get_element_by_id('lit-feedback-status').set('class','lit-account-sync-status')
    details=main.xpath('.//div[@class="lit-intro-details"]')[0]
    schedule=main.xpath('.//p[@class="lit-update-note"]')[0]
    schedule.getparent().remove(schedule);details.insert(0,schedule)
    for el in main.xpath('.//p[@class="lit-intro-sentence" or @class="lit-topics-note"]'):
        el.getparent().remove(el)

    # One sorting control selects either recommendation view or metadata order.
    sort_select=main.get_element_by_id('lit-sort')
    sort_select.clear();sort_select.set('id','lit-sort')
    for value,label in [('personal','Personal preference'),('community','Community average'),('date','Latest first'),('journal','Journal')]:
        option=html.Element('option',value=value);option.text=label
        if value=='personal':option.set('disabled','disabled')
        if value=='community':option.set('selected','selected')
        sort_select.append(option)
    for el in main.xpath('.//div[@class="lit-reader-tools"]'):
        el.getparent().remove(el)
    feedback_filters=html.fragment_fromstring('''<fieldset class="lit-mark-filters" aria-label="Filter by my marks"><div class="lit-mark-options"><div class="lit-mark-actions"><button type="button" id="lit-marks-all">All</button><button type="button" id="lit-marks-clear">Clear</button></div><label><input type="checkbox" data-feedback-filter="more" checked>Like</label><label><input type="checkbox" data-feedback-filter="useful" checked>Useful</label><label><input type="checkbox" data-feedback-filter="irrelevant" checked>Not Relevant</label><label><input type="checkbox" data-feedback-filter="later" checked>Read Later</label></div></fieldset>''')
    main.xpath('.//div[@class="literature-tools"]')[0].append(feedback_filters)
    topline=main.xpath('.//div[@class="lit-intro-topline"]')[0]
    details.getparent().remove(details);topline.insert(1,details)
    introduction=html.Element('p',{'class':'lit-intro-description'})
    introduction.text='BioE Radar uses AI to recommend new journal articles relevant to our lab every week.'
    line_break=html.Element('br');introduction.append(line_break)
    line_break.tail='Log in for personalized recommendations based on your reading preferences.'
    topline.remove(topline.find('h1'))
    copy_block=html.Element('div',{'class':'lit-intro-copy'})
    copy_block.append(introduction)
    details.getparent().remove(details);copy_block.append(details)
    topline.insert(0,copy_block)
    body.append(main)
    body.append(html.fragment_fromstring('''<dialog id="lit-email-dialog" aria-labelledby="lit-email-title"><div class="lit-email-heading"><h2 id="lit-email-title">Log in</h2><button type="button" id="lit-email-close" aria-label="Close email sign-in">×</button></div><div class="lit-email-modes" role="group" aria-label="Email account action"><button type="button" data-email-mode="signin" aria-pressed="true">Sign in</button><button type="button" data-email-mode="signup" aria-pressed="false">Create account</button></div><form id="lit-email-form" method="dialog"><label id="lit-email-name-row" hidden>Public display name<input id="lit-email-name" name="displayName" type="text" autocomplete="nickname" maxlength="100" disabled></label><p id="lit-email-privacy" hidden>Your display name appears with reactions. Your email stays private.</p><label>Email address<input id="lit-email-address" name="email" type="email" autocomplete="username" maxlength="254" required></label><label id="lit-email-password-row">Password<input id="lit-email-password" name="password" type="password" autocomplete="current-password" maxlength="128" required></label><p id="lit-email-status" role="status" aria-live="polite"></p><button type="submit" id="lit-email-submit">Sign in</button></form><div class="lit-email-secondary"><button type="button" id="lit-email-forgot">Forgot password?</button><button type="button" id="lit-email-back" hidden>Back to sign in</button></div></dialog>'''))
    # Server-render the upcoming schedule; the browser refreshes it in local DST rules.
    now=datetime.datetime.now(ZoneInfo('Asia/Shanghai'))
    friday=now.replace(hour=3,minute=30,second=0,microsecond=0)+datetime.timedelta(days=(4-now.weekday())%7)
    if friday<=now:friday+=datetime.timedelta(days=7)
    main.get_element_by_id('lit-schedule-times').text=' / '.join(friday.astimezone(ZoneInfo(z)).strftime('%A %H:%M')+' '+name for z,name in [('Asia/Shanghai','Beijing'),('America/New_York','New York'),('Europe/London','London')])
    dialog=html.fragment_fromstring('''<dialog id="lit-journals-dialog" aria-labelledby="lit-journals-title"><div class="lit-dialog-heading"><div><h2 id="lit-journals-title">Journals included</h2><p>Select one or more journals and preprint sources.</p></div><button id="lit-journals-close" type="button" aria-label="Close journal selection">×</button></div><div class="lit-dialog-actions"><button type="button" id="lit-journals-all">Select all</button><button type="button" id="lit-journals-none">Clear all</button><span id="lit-journals-selection" role="status" aria-live="polite"></span></div><div id="lit-journals-options"></div><div class="lit-dialog-footer"><button type="button" id="lit-journals-cancel">Cancel</button><button type="button" id="lit-journals-apply">Apply selection</button></div></dialog>''')
    body.append(dialog)
    select=main.get_element_by_id('lit-edition')
    all_option=html.Element('option',value='all');all_option.text='All';select.append(all_option)
    for e in editions:
        opt=html.Element('option',value=e['id']);opt.text=e['id']
        if e==latest:opt.set('selected','selected')
        select.append(opt)
    def article(a):
        card=html.Element('article',{'class':'lit-paper','data-id':a['id']})
        meta=html.Element('p',{'class':'lit-meta'});j=html.Element('span',{'class':'lit-journal'});j.text=a['journal'];meta.append(j)
        date=html.Element('time',datetime=a['date']) if a.get('date') else html.Element('span');date.text=a.get('dateLabel') or a.get('date') or 'Publication date unverified';meta.append(date)
        card.append(meta)
        h=html.Element('h2');link=html.Element('a',href=a['url'],target='_blank',rel='noopener noreferrer');link.text=a['title'];h.append(link);card.append(h)
        summ=html.Element('p',{'class':'lit-summary'});summ.text=a['summary'];card.append(summ)
        bottom=html.Element('div',{'class':'lit-paper-bottom'})
        tags=html.Element('p',{'class':'lit-tags'});tags.text=' / '.join(a['topics']);bottom.append(tags)
        authors=html.Element('p',{'class':'lit-author-line'})
        authors.text=', '.join(a['authors']) if a['authors'] else 'Author list unavailable.'
        if not a.get('authorsComplete'):authors.text+=' (Complete author list not verified.)'
        card.insert(2,authors)
        card.append(bottom);return card
    listing=main.get_element_by_id('lit-results')
    for a in sorted(latest['articles'],key=lambda a:(-a['relevance'],a['journal'],a['title'])):listing.append(article(a))
    main.get_element_by_id('lit-count').text=f"{len(latest['articles'])} selected articles"
    main.get_element_by_id('lit-window').text=latest['start']+' – '+latest['end']+' (Beijing time)'
    source_names=sorted({c['journal'].replace('bioRxiv - Bioengineering','bioRxiv · Bioengineering').replace('Arxiv - Applied Physics','arXiv · Applied Physics') for c in latest['coverage']} | {a['journal'].replace('bioRxiv - Bioengineering','bioRxiv · Bioengineering').replace('Arxiv - Applied Physics','arXiv · Applied Physics') for a in latest['articles']})
    main.get_element_by_id('lit-coverage-list').text='; '.join(j for j in source_names if j!='Small')+'.'
    payload=html.Element('template',id='lit-data')
    payload.text=json.dumps({'latest':index['latest'],'editions':editions},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    body.append(payload)
    path=root/'BioE_Radar/index.html';path.parent.mkdir(exist_ok=True);path.write_bytes(html.tostring(tree,encoding='utf-8',doctype='<!doctype html>'))
    # Preserve bookmarks to the original archive URL.
    legacy=root/'literature/index.html';legacy.parent.mkdir(exist_ok=True)
    legacy.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BioE Radar</title><link rel="canonical" href="https://hanmd1990.github.io/BioE_Radar/"><meta http-equiv="refresh" content="0;url=/BioE_Radar/"></head><body><p>BioE Radar has moved. <a href="/BioE_Radar/">Open BioE Radar</a>.</p></body></html>',encoding='utf-8')
    # Add the public page to shared navigation after all other generators finish.
    for path in root.rglob('index.html'):
        if any(p in path.relative_to(root).parts for p in ('tools','work','outputs','.git','.github')):continue
        t=html.document_fromstring(path.read_bytes())
        for nav in t.xpath('//header[contains(@class,"lab-header")]//nav[@id="lab-navigation"]'):
            for old in nav.xpath('./a[@href="/literature/" or @href="/BioE_Radar/"]'):nav.remove(old)
        for h in t.xpath('//header[contains(@class,"lab-header")]'):
            brand=h.xpath('.//a[contains(concat(" ",normalize-space(@class)," ")," lab-brand ")]')
            if not brand:continue
            for old in h.xpath('.//a[contains(concat(" ",normalize-space(@class)," ")," lab-radar-link ")]'):old.getparent().remove(old)
            b=brand[0]
            if b.getparent().get('class')=='lab-title-row':row=b.getparent()
            else:
                row=html.Element('div',{'class':'lab-title-row'});b.getparent().replace(b,row);row.append(b)
            a=html.Element('a',href='/BioE_Radar/',attrib={'class':'lab-radar-link','aria-label':'BioE Radar — weekly literature'})
            a.text='BioE Radar'
            if path.parent.name=='BioE_Radar':a.set('aria-current','page')
            row.append(a)
        path.write_bytes(html.tostring(t,encoding='utf-8',doctype='<!doctype html>'))
    print('Literature archive:',len(editions),'edition(s),',len(latest['articles']),'selected articles')
