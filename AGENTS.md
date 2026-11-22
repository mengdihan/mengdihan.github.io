# Repository instructions for Codex

## Scope and design

These instructions apply to the entire repository. Read `DESIGN.md` before designing or updating any website page. Follow the user's latest explicit instructions when they override a default below. `MAINTENANCE.md` describes source/build structure; `SCHOLAR-UPDATES.md` describes Scholar retrieval. For publication updates, the rules in this file govern when older notes differ.

## Publication 更新规则

### 1. 根据题目、DOI 或链接补齐信息

- 用户手动提供文章题目、DOI 或链接时，查找并核实完整 title、author list、journal、year、volume、page，以及 DOI 和出版商链接。优先核对出版商正式文章页面、正式 PDF 及作者贡献说明；检索结果、Crossref 或 Scholar 可辅助匹配，但不能用截断作者列表代替完整作者。
- page 可以是起止页 `xx-xx`，也可以是单个页号或文章编号 `xxx`；按出版商实际信息保留，不自行补造页码范围。
- 尚无最终卷号和页码／文章编号时，网站统一在年份后显示小写 `accepted`。不要用 DOI、空卷号或占位页码代替。DOI 保留在源数据中用于匹配，文章标题继续链接到原出版商页面。
- 必须读取共同第一作者和通讯作者声明：共一用 `¹`，通讯用 `*`，兼具两种贡献用 `¹*`。用户输入的共一标记 `1` 应规范为 `¹`。第一作者按原始作者顺序确定；不要把普通数字、单位上标或其他 equal-contribution 声明误判为共同第一作者。无法核实的贡献应明确说明，不凭作者顺序猜测通讯作者。
- 更新时保留已有唯一论文编号，按 DOI 或已核实的标题去重，记录元数据与贡献标记的核实来源。年份按正式出版信息核对；在线发表年份和卷期年份不同，不擅自移动条目。

### 2. 同步输出 Google Scholar Edit 作者串

- 每次提取或修订作者列表，都在回复中额外提供一份可复制到 Google Scholar Edit 的完整作者字符串；仅输出供用户填写，不自动修改 Scholar 账号。
- 作者顺序与原文一致，使用 `Surname, Given name; Surname, Given name` 格式，以英文分号加空格分隔；保留复姓、姓名拼写及变音符号，不凭空展开缩写。
- `¹` 和 `*` 紧跟姓氏，位于逗号前。韩梦迪姓名用 Unicode 粗体字符 `𝐇𝐚𝐧, 𝐌𝐞𝐧𝐠𝐝𝐢`；如为通讯作者则为 `𝐇𝐚𝐧*, 𝐌𝐞𝐧𝐠𝐝𝐢`，贡献标记同样以核实结果为准。不能用 Markdown 的 `**Han**` 替代这份可复制字符串中的粗体字符。
- 格式示例（示例不代表新文章的作者或贡献）：`Zhang¹, Shaotong; Li¹*, Dan; Liu¹, Tao; Nie, Zhongyi; Wu, Kedong; Lin, Xiang; Zhang, Jingyan; Xu, Jie; Wang, Yiran; Zhong, Ruyue; Zhao, Pengcheng; Wang, Yaozheng; Ding, Shigang; Cui, Guoqing; Wen, Yue; Li*, Baohua; Shang*, Shaomei; 𝐇𝐚𝐧*, 𝐌𝐞𝐧𝐠𝐝𝐢`。

### 3. 新增论文的列表归属

- 添加到相应 `publications/YYYY/index.html` 年份源页面，通过构建同步 Full List；不要单独修改生成的 Full List。
- 若期刊为 Cell、Nature、Science（CNS）及其子刊，或 PNAS、Advanced Materials，同时加入韩梦迪的 Selected Publications。核实期刊身份，维护 `data/selected-publications.json` 等现有精选配置，不能只凭标题含有 Cell/Nature/Science 字样判断，也不能默认扩展到所有同出版商期刊。
- 核对文章的一作及每位共一作者。若作者在 Group → Current 或 Group → Alumni 名单中，将该文章加入其个人 Selected Publications；个人列表只收录该成员作为第一作者或共同第一作者的文章。仅为通讯作者、共同通讯作者或中间作者不足以入选个人列表。
- 成员精选规则独立于韩梦迪精选的期刊筛选：成员的一作／共一文章无需属于上述精选期刊。核对全名、缩写及成员身份，避免同姓同缩写误配，并防止重复添加。

### 4. 状态与元数据的跨页面同步

- 从 `accepted` 变成有卷号页码／文章编号，或题目、作者、年份、链接等发生变更时，同步该论文在年份页、Full List、韩梦迪 Selected Publications、Group Current、Group Alumni 和 Research 相关文章列表中的所有已有展示位置。
- 同一文章各处的状态、卷号、页码／文章编号、作者贡献、DOI 映射及链接必须一致；正式卷页已核实后移除旧 `accepted`。状态变更不代表要将文章加入原本不相关的 Research 方向。
- 优先修订年份源条目及相应规范数据，通过现有生成器传播；Research 等独立维护的列表也要逐一核对，不假设构建会自动修复所有引用。

### 5. 每次 Publication 更新都刷新全站引用数据

- Publication 列表新增、删除、重排、元数据或状态更新时，读取 Google Scholar，核对并更新网站所有年份、所有文章的 citation 数量和 Cited by 链接，而非只查本次变动的文章。
- Publication 年份页、Full List、Selected Publications、Group Current、Group Alumni、Research 及其他文章展示位置共用已核实的引用数据，并显示一致的计数和链接。需要完整处理 Scholar 分页，不能把首屏结果当成全量。
- 数据来源、匹配、核对日期及访问失败处理遵循下文；文件规则本身的编辑不等同于 Publication 列表更新，无需因此抓取引用数据。本规则不会自动创建或更改定时任务。

## Publications and citations: mandatory synchronization

Whenever a change adds, removes, reorders, or edits a publication anywhere on the HMD Lab website, treat publication metadata, citation data, and member-selected publications as one coordinated update. This applies to edits made through Codex, including changes to generated pages or their source data.

1. Inspect the publication source data and `tools/build_site.py` before editing. Update the canonical publication entries, and ensure Publications Full List and year-specific pages reflect the same title, authors, venue, year, DOI, and links. Do not manually patch generated HTML in place of source data.
2. Check the Google Scholar profile https://scholar.google.com/citations?user=rjC8MUQAAAAJ&hl=en for current per-paper citation counts and corresponding "Cited by" URLs. Match by DOI where possible; otherwise carefully verify title, authors, and year. Update the canonical `data/scholar-citations.json` records, including provenance/check dates, only for values actually verified. Never invent counts, infer missing counts as zero, or mark an incomplete scrape as fully synchronized.
3. Inspect both Group Current Members and Group Alumni selected-publication data. Add or remove affected selected publications as appropriate to their actual author/member associations; do not assume every new publication belongs in every member's selected list. Ensure citation badges and "Cited by" links for selected papers use the same canonical citation records as Publications.
4. Preserve existing verified citation values if Google Scholar is inaccessible, blocked, or incompletely paginated. Report which publications or counts could not be verified; do not claim a fresh citation sync or change the global checked date unless the intended scope was fully checked.
5. Run the repository's build and verification procedures (normally `python tools/build_site.py` and `python tools/verify_site.py`, plus any applicable checks). Verify consistency across Publications Full List, year pages, Group Current, and Group Alumni, including titles, DOI mappings, citation counts, and outbound Scholar links. After publishing, check the deployment status and report any failure.

This is an **on-publication-change requirement**, not a request to schedule periodic citation scraping. Do not silently omit citation/member checks when updating the publication list. If source access or verification fails, leave old values intact and state the limitation in the change summary.
