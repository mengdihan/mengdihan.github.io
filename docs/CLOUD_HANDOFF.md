# HMD Lab website — cloud handoff, updated 2026-10-20

## Scholar automation rules — 2026-10-20 (supersedes older automation notes)

Read [SCHOLAR_AUTOMATION.md](SCHOLAR_AUTOMATION.md) before every maintenance run. The existing cloud task is enabled at Friday 03:30 Asia/Shanghai, starting 2026-10-23. New/updated publication metadata is restricted to 2026 onward; citations refresh for all listed years. Exclude patents and independent Wiley cover records, while preserving real articles’ Cover links. Incomplete volume/page metadata displays YEAR, accepted.; replace it in-place when Scholar provides both volume and pages/article number. Update complete author names and explicit co-first markers, both member groups, and shared citation data. Use the isolated build and verify deployment before claiming publication. The task is an agent-based cloud automation, not a scheduled Scholar scraper in GitHub Actions; publish.yml deploys on main pushes.

Current/Alumni now display verified full first/co-first author names from data/publication-full-authors.json (followed by et al.). Keep the raw author tokens for identity/position matching. News journal mentions use normal text color and italic where marked, including Soft Science; its gallery is capped at 180px. Publication volumes are black italic. Title font is still 18px; the suggested 16px change was not authorized or applied.

## Cover gallery and member volume colors — 2026-10-20

Covers displays only the 14 cover images below the archive controls: no journal/title/year captions, citation badges, counts or author/Scholar legend. The images remain accessible with descriptive alt/aria labels and click-to-enlarge. Use 5 columns on desktop, 3 at tablet widths, 2 on phones; preserve natural images without cropping. Hover/focus gives a subtle lift/zoom and stronger shadow, with reduced-motion support. Both server-generated and client-rendered galleries must match. Underlying cover metadata may remain in the archive data for lookup, but is not rendered.

Member bibliography metadata preserves the lab-volume class on numeric emphasis tags before cloning into Current/Alumni. The shared stylesheet forces these volumes to black italic; only journal names retain gold. Do not strip the numeric volume marker during regeneration.

## Contact directions — 2026-10-20

Visit our lab has four separate numbered sections, in order: ① Location of our lab (Google, Baidu and Amap links), ② Nearest metro station (~350 m), ③ Nearest bus station (~350 m), ④ Driving & taxi navigation (full English/Chinese address). Do not combine ① and ④. Display the four sections in a compact two-column grid below the map (one column on small phones). Desktop Contact columns stretch to the same natural row height; the left address stays at the bottom of its card. Mobile columns retain natural heights. Preserve the portrait, exact Assistant Professor / Associate Department Chair roles, plain email, profiles, map and click-to-enlarge behavior.

## Recruitment availability — 2026-10-20

Join Us availability: Postdocs 1–2 positions in 2027; Ph.D. students 1–2 positions for Fall 2028, no positions in 2027; Undergraduates unchanged; Research Assistants no positions in 2027 (including body text). Page updated is 2026-10-20, the actual edit date. Keep intro text and this date centered. Remove the separate Contact Mengdi Han mailto CTA. Recruitment notice is permanently removed from data and renderer; never append it in future updates. Keep application instructions and their existing email links inside the recruitment ads. Preserve tab switching and no large Join Us title.

## Contact link behavior — 2026-10-20

The three map-service buttons (Google Map, 百度地图, 高德地图) form one equal-width row, with matching button height and centered text. Do not render an Apple Maps button. All nine profile/resource links (CV, Biography, PKU Profile, Scholar, ResearcherID, ORCID, X, LinkedIn, ResearchGate) open in a new tab with target=_blank and rel=noopener noreferrer, including the local Biography page. PKU Profile is exactly https://future.pku.edu.cn/en/Faculty_/Teaching_Research_Series/4b920575a0244a4e827b1b36d536c167.htm . Preserve the four separate directions and desktop equal-height columns.

## Recruitment tab wording — 2026-10-20 latest

The four tab labels are Postdocs, Ph.D. Students, Undergraduates, Research Assistants (restored to full names at the user’s request). Availability wording is exactly: Postdoc “2027: 1–2 positions”; Ph.D. two lines “Fall 2028: 1–2 positions” then “Fall 2027: no positions”; Undergrad “Multiple positions”; RA “No positions” (no year). Panel availability matches tab availability. RA body has no year. Preserve the undergraduate advertisement text and all existing application instructions. This supersedes older count wording in this document; data/join-us.json is canonical.

## Published academic archives (2026-10-19; supersedes earlier archive designs)

Publications and News now use the approved clean academic preview design on the official GitHub Pages site. Preserve the original shared lab header/navigation. Do not add the preview theme selector, brand, page heading or introductory description: Publications starts with the centered author/Scholar note; News starts with the year selector. Home, Research, Current, Alumni, Contact and Join are unchanged.

`tools/archive_layout.py` runs at the end of `tools/build_site.py`. It reads the editable year pages plus the shared Scholar cache, and generates all existing publication/news entry, year and full-list routes, Covers, and `/selected-publications/`. Do not overwrite the editable year sources with generated archive pages. `static/archive.css` and `static/archive.js` own the archive layout and interactions. Both `/publications/` and `/news/` default to Latest: the current and preceding calendar years. The year selector has Full List and individual years only; Latest is a button and displays the current year in the selector. Search always switches to Full List and searches title, full author name and journal across all years. Covers always opens all years. News has no categories; retain its original hyperlinks and year-specific right-hand image galleries (114 links, 66 pictures at this revision).

Publications use full names with superscript 1/co-first and */corresponding markers, without special bolding for Mengdi Han. `data/publication-full-authors.json` stores the 126 verified lists and per-paper sources; only reuse a cached entry when its title still matches the numbered paper. For new/updated papers, verify full names in the PI's Scholar article detail, use publisher metadata when unavailable, retain markers from the editable bibliography, and update this cache. Do not infer identities from initials alone. The top note is `*Corresponding authors; ¹ Authors contributed equally; Citation counts: Google Scholar; · Automatically updated YYYY-MM-DD`; use the real `data/scholar-citations.json` checked date, never the deployment date. All article counts/links use the same Scholar cache as other pages. Only the journal name uses HMD gold #A1662F; year, volume, pages/article number and surrounding metadata use black. Retain functional Cover, bioRxiv and Supplementary Movies links.

Selected Publications now contains the 9 papers confirmed by the user on 2026-10-20: bibliography IDs 114, 112, 110, 109, 89, 67, 66, 56, 44 (descending order). The 2024 Science Advances selections are the modular 3D micro strain gauges (Xu/Wang) and magnetic implants (Wan/Nie); the omnidirectional strain-gauge paper 113 is not selected. Store this curated list in `data/selected-publications.json` (`paper_ids`); do not add future papers without the user choosing them. Metadata and citations update from the canonical bibliography/shared caches.

Verification: build into a fresh copied/archive output, run `python tools/verify_site.py OUTPUT`, `node tools/check_archive_ui.cjs OUTPUT`, and relevant member-publication tests. The official build now checks 44 HTML pages. The separate private Sites design preview remains independent; its project is appgprj_6ad5a83ac2d081919939eb25eadbba38, with source at /workspace/sites/hmd-lab-design-preview and URL https://hmd-lab-design-preview.hanmd1990.chatgpt.site. Do not change the original hmd-lab.com domain or DNS.

Repository: https://github.com/hanmd1990/hanmd1990.github.io
Website: https://hanmd1990.github.io/
Latest website implementation before this documentation update: adbeff28d3f255e147050b3dfe6ede843154b7f5.

## Purpose of this handoff

Continue maintenance in a real Codex Cloud task bound to this GitHub repository, so work can resume from another computer. This is distinct from a general ChatGPT cloud conversation.
Check out the latest main branch rather than an older local snapshot. Do not replay old design requests: the current designs listed below have already been published and verified.
The complete original local chat history is not copied by selecting this environment. This file and the latest source are the durable handoff.

## Environment setup

Python 3.12 with lxml 5.3.0 and timezone data is sufficient for the static-site build. Node is optional for checking JavaScript syntax. No paid hosting service or new API key is required to build the website.
Install dependencies, then build a separate output folder using the same procedure as .github/workflows/publish.yml:
mkdir -p outputs/hmd-lab-site
git archive HEAD | tar -x -C outputs/hmd-lab-site --exclude='.github' --exclude='work' --exclude='tools' --exclude='.gitignore' --exclude='README.md'
python tools/build_site.py outputs/hmd-lab-site
python tools/verify_site.py outputs/hmd-lab-site
Do not mistake editable source HTML in the repository for the final rendered site: the GitHub Pages workflow runs tools/build_site.py before publishing.

For Current membership edits, change data/member-publications.json, regenerate with python tools/build_member_preview.py . --publish, then run the main builder. The member generator imports tools/member_gallery.py. The main builder imports tools/alumni_layout.py.
Build member pages before the main builder so shared citation data is injected. Avoid broad unnecessary regeneration of unrelated editable source files.

## Completed design and content — preserve

- The website and images are independent of the original platform. Do not reintroduce original-platform asset dependencies.
- DNS and migration of hmd-lab.com are deferred. Do not change the domain or its Aliyun DNS.
- HMD palette: navy #142B55, gold #A1662F, text #252A34, medium blue #547DA6, light gray #EFF1F5, pale yellow #F9DF93, white #FFFFFF, black #000000.
- Article links hover medium blue; all other links hover gold.
- No Copyright © 2021 footer or Chinese ICP footer is displayed. Current also has no group name/affiliation/check-date footer.
- Home and every Research page have no citation badges. Preserve their article links, journal information and hover colors.
- Publication and News enter at the current year; decade navigation uses 2020s/2010s. Publication year typography and top alignment are consistent. Full List automatically aggregates all year pages. Preserve Covers and Scholar profile buttons.
- Current introduction must read exactly: “Our group consists of a diverse mix of students, including people from electrical engineering, biomedical engineering, mechanical engineering, materials science and engineering, life science, and medicine.” Preserve it in both current/index.html and tools/build_member_preview.py.
- Current has 21 equally weighted text member cards with no individual portraits or large role-group headings. Role is small text after the English name. English university comes next, then Chinese name/university on the next line. No school-label prefixes.
- Mengdi Han (PI) is removed from Current. Current starts with Chong Zhang, followed immediately by Wai Hong Chong / 张伟鸿, Universiti Sains Malaysia / 马来西亚理科大学. Wai Hong Chong has no selected publications; show a hyphen, and his role is Postdoc, confirmed by the user on 2026-10-16.
- Yujie Shang: Visiting Student, Nanjing University of Aeronautics and Astronautics / 南京航空航天大学. Other undergraduates are at Peking University.
- Xiaowen Zhang / 张晓雯 was removed from Current. Penglai Yao / 姚朋来 and Junjie Wang / 王俊洁 were appended as Peking University undergraduates.
- Current Selected Publications include only verified first/co-first-author research papers and reviews, ordered exactly as Full List. Article text is 14px. Display all source author tokens carrying ¹ before et al.; otherwise display the first author. Preserve source journal/year/volume/page or article number and Scholar badges.
- Editorial 104 is excluded from member selections only, not the global bibliography. Do not omit Yiran Wang’s 88 (Materials Today Physics) or Zhongyi Nie’s 114 (Advanced Materials review). Never infer a person from ambiguous initials. Empty member disclosures show only a hyphen.
- Current right sidebar is a compact album: one full-resolution image, caption/date, Previous/Next, and a 16-image thumbnail index with abbreviated dates (e.g. Dec. 2023). The main image uses contain and white background, not gray letterboxing. Source captions and images are recorded in data/group-photos.json. Keep the album shorter than the member list. Member styles receive a content-hash cache version in the main builder.
- Alumni has 7 expandable profiles and 12 original selected publications. Desktop retains two members per row; at widths up to 760px use one member per row. Prior education → Role in the group → Next position run left to right, connected by decorative right arrows; narrow screens scroll the three-stage row horizontally. Prior education uses “Undergraduate at [school]” or “Ph.D. at [school]”, with the major below. Xinyan Chen and Yuefang Zhao destinations spell out Chinese Academy of Sciences. Jie Xu destination is Faculty Member at the Chinese Institute for Brain Research, Beijing; Pengcheng Zhao is Engineer at Neweastech. Each card shows the name, then Prior education, Role in the group (role and years), and Next position, followed by the Selected Publications toggle. Use Joint Ph.D. Student, Postdoctoral Researcher and Faculty Member rather than the earlier abbreviated labels. Keep school, major, tenure and destination facts unchanged. Prior education and Next position use white backgrounds; Role in the group uses HMD light gray #EFF1F5 with a navy heading and emphasized role. Name typography matches Current exactly: Segoe UI/Arial, 17px bold (16px at widths up to 960px); school and Chinese text are 15.5px, role/year details 13px, publications 14px.
- Alumni members with no selected publications show only a hyphen when expanded, matching Current.
- Alumni publications match Current typography: Segoe UI/Arial, 14px titles and metadata, italic et al. and journal names, 600-weight titles, and separate 12px Scholar badges. Do not display paper numbers. Citation matching must stop at the next article title even when titles have no number.
- Contact email is plain hmd[at]pku.edu.cn, no mailto link. “Mailing address” heading is removed, while the full address remains. Profiles & resources icons visually blend with the gray background using CSS mix-blend-mode: multiply. Preserve maps and all resource links.
- Join Us redesign is ONLY a preview at /preview/join-us/. Keep original recruitment content, dates and availability unchanged. Do not replace the official /join/ page without further user approval.
- Preserve the Home smooth translucent-dot carousel, hover dropdown navigation and Covers gallery.

## Scholar data and existing weekly automation

Scholar profile: https://scholar.google.com/citations?user=rjC8MUQAAAAJ&hl=en
data/scholar-citations.json is the shared data cache. Its profile_metrics, verified on 2026-10-14, contains total_citations 15699, h_index 64, i10_index 120. These cached totals are not displayed. Never substitute a sum of listed papers for Scholar profile metrics.
Publication statistics caption is “Citation counts: Google Scholar · automatically updated YYYY-MM-DD”. Do not advance the date after an unsuccessful check.
Citations are displayed on Publications, Full List, Current, Alumni and Covers, but never on Home or Research.
The independent Ji Wan Nano Energy 2020 article has been removed and must not be restored or tracked. data/scholar-extra-articles.json is empty.
The existing enabled cloud task is named “更新 HMD Lab Scholar”, id 6ad18f879bc08190b1957f23e877be83. Its 2026-10-20 instructions and exact Friday 03:30 Asia/Shanghai schedule are documented in SCHOLAR_AUTOMATION.md. Do not create a duplicate or restart the older local heartbeat. Configuration success alone does not establish successful execution.

## Remaining task: deploy and validate private analytics

User requested a separate private login-protected dashboard with site total pageviews and visits, IP addresses, approximate country/region/city, timestamps, visited pages, per-browser visit number, trends, and export.
Cloudflare was chosen for the backend; the public website stays on GitHub. No domain/DNS migration is authorized. No paid service may be enabled without cost approval.
The repository already contains an UNDEPLOYED analytics/ implementation: Worker, dashboard, tracker source, D1 migration, example Wrangler configuration, README and security tests. This was verified against current main. No production Worker, D1 database, Access application, or tracker integration has been deployed, and no historic visitor logs are available. Read analytics/README.md and preserve the existing implementation; do not build a duplicate from scratch.
Review the existing backend/dashboard and run analytics npm ci, npm test and the documented Wrangler dry run. Then prepare any missing reviewable deployment configuration. Use real server-side authorization; a secret URL or front-end password check is not enough. Keep visitor logs and secrets out of this public repository.
IP location is approximate, not a street address; an IP may be shared or change. Use anonymous browser identifiers/session rules for repeat visits, without pretending they uniquely identify a person. Counts start when tracking is enabled.
The original local browser was logged in to Cloudflare, but its cookies and sign-ins must not be copied. Request an appropriate interactive login only if deployment needs it; never request passwords/OTP in chat.

## Authorization and reporting

User authorized necessary website edits, testing and main-branch publication. Keep each requested preview isolated where specified. Before pushing, read the latest remote head and avoid overwriting concurrent work; compare-and-swap updates are preferred.
Report results in Chinese. Verify builds, resource links, relevant browser behavior and deployment success. Do not claim an account/environment/task exists merely because a creation request was issued.

Alumni design refinement (2026-10-16): Current and Alumni typography shares CSS rules in static/hmd-color.css; do not maintain competing name/role font rules. Alumni uses inline bilingual nameplates, blue top rules, compact horizontal education/role/destination stages and a small gray role panel with blue left accent. Only the separate Selected Publications disclosure is clickable; profiles use article.alumni-member, with nested details.alumni-publication-disclosure. Preserve 7 profiles, 12 papers, and hyphens for the two empty disclosures.

Alumni update (2026-10-16, supersedes the original 12-paper selection): Bold Alumni page title. Prior and Next match Role typography: 13px normal navy first line (degree or job title), 12px muted secondary line (school or organization; tenure years also 12px), with the major retained as a further secondary line. Keep the two-column member layout, white Prior/Next backgrounds and gray Role background. Selected papers must have the member as verified first/co-first author AND Mengdi Han as coauthor. Validate each curated title against the PI yearly bibliography and its author markers; do not assign new titles merely from initials. Remove Ji Wan’s independent Nano Energy 2020 paper from Alumni and extra Scholar tracking. The remaining 11 existing selected articles satisfy both author conditions; keep hyphens for empty disclosures.

Alumni final simplification (2026-10-16): Remove all majors/discipline lines from Prior; retain only degree then school. Expand Yuefang Zhao’s Prior school to Institute of Microelectronics, Chinese Academy of Sciences, identical to the Next institution. Use Postdoc everywhere on Alumni instead of Postdoctoral Researcher. This supersedes older wording about retaining majors or expanded postdoc titles.

Publication/Contact update (2026-10-16): Remove the total citations/h-index/i10-index display (cached metrics may remain for update purposes). Combine corresponding/co-first author notes and Google Scholar checked date in one line on desktop; wrap naturally on mobile. Contact has no introductory eyebrow, Contact heading, or department tagline. Use images/people/mengdi-han/mengdi-han-portrait.jpg (user-supplied original portrait), with natural proportions. Beside Mengdi Han show Assistant Professor of Biomedical Engineering, then Associate Department Chair. Email remains plain hmd[at]pku.edu.cn at normal body size/weight. Remove the Profiles & resources heading, preserve the nine resource links/icons and address/maps.

Alumni alignment / Contact titles (2026-10-16): Alumni Prior and Next are equal-width side columns; Role is 1.4 times either side. Shared subgrid rows align the nameplate, career stages and publications footer across each pair despite wrapping organizations. Use natural-height degree/position labels and normal line spacing; do not reserve empty lines. Role supports a subtle hover lift/shadow and gold left accent, with reduced-motion support. Contact roles are exactly Assistant Professor, then Associate Department Chair.

Degree spelling: all visible doctoral degree references use Ph.D., including Joint Ph.D. Student. Preserve internal identifiers such as phd-students and external URLs.

Alumni publications / Contact Email label (2026-10-16): Selected Publications is now a button INSIDE each gray Role column. It controls a hidden region below all three columns, spanning the member card width. static/alumni.js synchronizes aria-expanded and panel.hidden; preserve keyboard activation, author filters and the hyphen empty state. This supersedes the earlier nested details layout. Email label is 16px/600; address remains 14px/400 plain text.

Alumni degree label uses Undergraduate (not Undergrad).

Alumni spacing: All text flows naturally from the top. No minimum heights on headings or degree/position lines, and no flex expansion between tenure and the publication button. Any equal-height surplus remains below the content; retain shared card rows and the wider Role column.

Alumni text spacing: Role title and years have zero flex gap and zero paragraph margins; Prior and Next primary/secondary lines also have zero paragraph margins. Keep normal line height only, e.g. Joint Ph.D. Student immediately followed by 2021–2025.

## Recruitment and Apple Maps — 2026-10-16

- The owner has now authorized the official `/join/` redesign. This supersedes
  the earlier instruction that only the Join Us preview could be changed.
  `tools/join_layout.py` renders the official page from `data/join-us.json`.
  Four top category tabs show roles, counts and original years.
  Clicking switches the single advertisement panel in place without scrolling.
  The top Join Us heading was removed at the owner’s request.
  `static/join.js` supports arrow/Home/End keys and category hash URLs. Master applicants are a Ph.D. application route,
  not a newly invented master's opening.
- Owner explicitly chose to retain original counts/years: postdocs 2–3 in 2025,
  Ph.D. 1–2 for Fall 2026, undergraduates multiple, RA no positions in 2025.
  The page separately displays page update date and original notice 2025-01-24.
  When recruitment content or page design changes, update `updated_on`; only
  change `notice_updated_on` when the owner supplies a refreshed notice.
  Do not advance dates on unrelated deployments.
- Contact has an Apple Maps link and a prepared MapKit JS enhancement in
  `static/contact-map.js`, configured by `static/apple-maps-config.js`.
  It is **not activated**: no Maps token is available. The current campus map
  remains the fallback. Follow `docs/APPLE_MAPS.md` to authorize and verify the
  exact building marker, drag and zoom before claiming completion.

## Alumni / photos / recruitment typography — 2026-10-16

- Alumni retains two people per row, equal Prior/Next widths and a wider Role
  column. Remove all inter-column arrows. The owner subsequently removed the shared bottom arrow and its legend too.
  Do not reintroduce arrows between columns or at the bottom. Do not add blank lines
  between role and years; spare height remains below content.
- Current group-photo captions are centered and bold; dates are centered with
  normal weight. The Group photos heading is bold.
- Join Us category advertisements have no 01/02/03/04 numbering. Preserve
  original source semantic emphasis: CV, transcripts, representative
  publications and the four Ph.D. applicant attributes. Explicit scoped strong
  styling restores these weights despite the legacy theme reset.

## Publication note and faculty link — 2026-10-16

- Center the combined publication note at all screen widths. Exact wording:
  `*Corresponding authors; ¹ Authors contributed equally; Citation counts: Google Scholar; · Automatically updated YYYY-MM-DD`.
  Keep using the actual Scholar cache check date; do not hard-code a newer date.
- Contact PKU Profile points to the English faculty profile:
  https://future.pku.edu.cn/en/Faculty_/Teaching_Research_Series/4b920575a0244a4e827b1b36d536c167.htm

## Alumni reference layout — 2026-10-16 evening

This supersedes earlier no-arrow instructions: the owner supplied a new visual
reference. Each member now has three centered labels OUTSIDE the boxes, with
one fine left-to-right arrow immediately below the labels and above the boxes.
Prior/Next use equal-width white boxes with fine neutral borders; Role remains
wider with a light-gray background and its Selected Publications control.
Remove the thick blue dividers above/below members. Keep two members per row,
compact role/year text without spacer lines, and full-width publication panels
below all three boxes. There is no shared page-bottom arrow or legend.

## Selected publication order — 2026-10-17

Current and Alumni Selected Publications follow the main Publication bibliography
numbers in descending order, highest first, including articles in the same year.
`build_site.py` enforces ordering on both final routes on every deployment.
Title/author/journal/citation metadata stay together. `build_member_preview.py`
also sorts numeric paper IDs descending for newly generated Current cards.
Do not change article eligibility, membership, counts or visual layout to sort.

## Automatic member publication synchronization — 2026-10-17

Every website build now regenerates Current from the canonical year pages and
adds all independently verified eligible articles to Alumni. The shared offline
matcher is `tools/member_publications.py`. `build_member_preview.py` scans all
bibliography IDs, not just the old manual `member_paper_ids`. `build_site.py`
automatically invokes it for the output copy and adds Alumni selections before
sorting/citation injection. Do not run the main builder against editable source.

For every newly added or author-updated publication, the maintainer/Scholar task
must verify the complete author list and first/co-first markers using the publisher
or formal paper. Store full ordered names in `data/member-publications.json` under
`evidence[paper_number]` with doi, full_authors, publisher_metadata and checked_on.
Names are matched exactly after normalization, then checked against the abbreviated
bibliography author at the same position. Explicit user-confirmed author positions
remain valid. Matching initials alone is never enough. If a member identity or
co-first status cannot be verified, report the affected article/member as pending;
do not silently count it as checked or invent an attribution. Full unabbreviated
author names in a bibliography entry can also provide direct identity evidence.

Selection requires member first or marked co-first AND Mengdi Han as a coauthor.
Respect `excluded_representative_paper_ids` and the removed independent Nano Energy
article. Keep the curated Alumni identity evidence for existing selections; new
additions require full-name evidence. Current/Alumni rosters and the published
layouts remain authoritative. Sync both groups, not just Current. Keep descending
bibliography numbering, selected-article counts, complete metadata/citations and
empty `-` states. Avoid duplicates when running again.

The existing cloud Scholar automation has been updated with these rules; its
schedule is unchanged. Manual bibliography maintenance uses the same build path.
`python tools/test_member_publications.py` checks first/co-first matching, false
initial matches, missing PI, excluded articles, changed markers, duplicate handling,
empty states and Current regeneration despite an empty old manual selection list.
Run these regression checks before publishing changes to synchronization logic.

## Member outer cards — 2026-10-18

Owner supplied a new annotated reference. Current and Alumni each person now
uses one white rounded outer frame with subtle exterior shadow and hover
emphasis. Cards themselves have no click handler or pointer cursor; only
Selected Publications expands. Remove internal dividers, inner shadows and
Alumni Role's blue left border. Preserve Alumni's three color areas and make
Prior/Next content vertically centered; each area has background-only hover.
The per-person timeline arrow above the stages remains and is now 2px thick.
Prior's Ph.D. text is now Ph.D. Student as explicitly annotated by the owner.
Keep the existing member columns, typography, first/co-first/PI filtering,
automatic synchronization and descending publication order.

## Independent member cards and centered stages — 2026-10-18

Alumni must use ordinary top-aligned cards, not shared row subgrids: opening
one person's publications must not enlarge the neighboring person's outer card.
Keep two columns on desktop. Current also keeps independent cards.
All three Alumni stage areas use the same light-gray background and center
content horizontally and vertically. Their three external headings share the
same normal font weight; degree/job primary lines (including Role) are bold.
Role, years and publication button use the same compact 4px item gap; tenure
is display:contents, with no margin or padding before the publication control.
Outer cards have a visible hover lift/shadow; no general card click action.
Only publication controls expand. Keep reduced-motion support and keyboard focus.

## Pointer hover clarification — 2026-10-18

Member frame emphasis must activate immediately with CSS :hover, without any
click/focus dependency or a primary-pointer hover media gate. Remove outer-card
:focus-within shadow persistence; retain visible keyboard focus on publication
controls. Hover uses gold border, stronger shadow and a small lift (no lift for
reduced motion). A click still only expands the publication control.
Alumni heading includes `(in chronological order)` as 14px normal-weight text
on the same line where space allows. Do not change member order for this note.

## CAS abbreviation and menu hover — 2026-10-18

Owner now requests `CAS` in Alumni's prior/next institutions, superseding the
older full-name requirement for Chinese Academy of Sciences. Both fields use
this abbreviation consistently. Research/Group menus open on actual mouse
pointer entry without a primary-pointer hover media-query gate. They close on
mouse exit unless a visible keyboard focus remains inside. Touch click, native
keyboard toggle, outside click and Escape remain supported.

## Mobile archive buttons and Contact font — 2026-10-18

Full List, Covers and Google Scholar Profile action links use flex alignment to
center text horizontally and vertically, with border-box sizing. On screens up
to 800px, News Full List uses a compact 111px row (same width as one of the two
Publication action buttons), instead of stretching across the old 230px row.
Action rows never exceed their available container width. Contact content and
headings use Segoe UI / Arial, consistent with Current, Alumni and Join Us;
keep existing font sizes, weights, icons, portrait and layout hierarchy.


## Google Analytics — 2026-10-20
- Owner chose GA4 country/region/city reports instead of storing visitor IPs. Cloudflare analytics remains undeployed and must not be enabled.
- Account: HMD Lab; property: HMD Lab Website; stream: HMD Lab Official Website, https://hanmd1990.github.io; measurement ID: G-WPKN8C626L. Owner: hanmd1990@gmail.com; timezone Asia/Shanghai.
- Optional account sharing disabled during setup. No additional users or advertising integrations added.
- Main and archive builders load static/analytics.js on all 44 generated pages. Production hostname only; analytics loads after explicit consent; DNT/GPC opt-out honored. Privacy & analytics control allows withdrawal. Google signals and ad personalization disabled. Query strings/fragments stripped from page_location/referrer.
- Consent/blocked requests reduce counts. Reports start after deployment, cannot recover past visits; city is approximate.
- Keep measurement ID in source (public by design); never add account credentials or API secrets.


## Covers click behavior — 2026-10-20
- All cover tiles open the corresponding research article URL in a new tab. No cover lightbox. Keep image-only grid and hover styling. Applies both to server-rendered /covers/ and dynamic Covers tab.


## Cover cursor and analytics prompt — 2026-10-20
- Cover tiles use a pointer cursor for article links.
- Analytics preference panel no longer opens automatically; footer Privacy & analytics opens it on request. Existing accepted consent continues collecting; new visitors remain untracked until they explicitly opt in. DNT/GPC and decline still respected.


## Automatic analytics — 2026-10-20, supersedes previous prompt behavior
- Owner explicitly requested removal of Privacy & analytics control and automatic visit measurement.
- No popup or preferences button; GA tag loads automatically on production, except DNT/GPC or an existing explicit declined preference. No consent state is fabricated or stored on behalf of visitors.
- Noninteractive footer disclosure links to Google data-use information. Google signals/ad personalization stay disabled; sanitized URLs, owner-only reports, and country/region/city collection remain.

- Follow-up owner request: remove the footer data-use sentence as well. Analytics injects no visible UI; automatic collection and opt-outs remain as above.


## Baidu Tongji — 2026-10-20
- Owner supplied screenshot of site-specific tracking installation page for hanmd1990.github.io. Tracking ID e387d8beff78853986f3b7b31860f890 (public identifier).
- Shared static/analytics.js initializes window._hmt and asynchronously loads the exact hm.baidu.com/hm.js URL on all generated pages, alongside GA4. No visible UI. Production hostname only; existing explicit refusal and DNT/GPC respected for both providers; duplicate tags avoided.
- Do not claim Baidu dashboard has received data until verified there. Installation screenshot says reports generally appear about 20 minutes after installation.
