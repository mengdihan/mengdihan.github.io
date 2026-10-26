# Scholar 自动更新规则

2026-10-20 更新。此文件是自动更新任务的现行规则；冲突时优先于旧交接说明。

云端任务：更新 HMD Lab Scholar，ID `6ad18f879bc08190b1957f23e877be83`。
每周五北京时间 03:30（Asia/Shanghai）运行，下一计划日期为 2026-10-23。
任务配置已启用；配置成功不代表已成功完成检索或发布。

维护 Mengdi Han（韩梦迪）的实验室网站 https://hanmd1990.github.io/ 。用户已授权将核实的更新提交到 GitHub 仓库 hanmd1990/hanmd1990.github.io 的最新 main 并自动发布。先读取最新 docs/CLOUD_HANDOFF.md、README.md、.github/workflows/publish.yml 和 docs/SCHOLAR_AUTOMATION.md；以本规则和最新已发布设计为准，不恢复旧布局或作者缩写，不依赖原电脑开机、旧工作目录或本地 heartbeat。

数据来源：Google Scholar 主页 https://scholar.google.com/citations?user=rjC8MUQAAAAJ&hl=en 。完整分页核对列表，打开文章详情读取完整作者和 1/¹ 共一、* 通讯标记；不要只用列表里的截断作者。必要时用出版商文章页或正式 PDF 核实姓名全称、身份或作者标记并保存证据。不得根据首字母或姓名全称本身推断共一。无法访问、需验证码或证据不足时保留上次有效数据并明确报告，不能称为“没有更新”，不能绕过验证码。

1. 仅新增或更新发表年份为 2026 年及以后的 Mengdi Han 共同署名论文；不收录专利，也不把 Wiley 的 Front Cover、Inside Cover、Back Cover、Cover Image/Picture 等独立封面记录当作论文。真实论文已有的 Cover 超链接及 Covers 展示保留。以 DOI 和规范化标题去重，预印本与正式版不得重复新建；核对正式版身份后合并，保留有用的 bioRxiv 等链接。2025 年及更早论文内容不改动，引用数量除外；不删除 Scholar 暂未收录的已有论文。

2. 对所有已有 2026 年及以后条目重新检查，不仅看新增文章。主动核对出版商官网的正式引文/元数据及 Crossref；Scholar 暂未补齐但出版商已提供完整卷号与页码/文章编号时，也据此更新并将来源和核对日期保存到 data/publication-metadata-evidence.json，不能只等 Scholar 更新。出版商与 Scholar 冲突时以已核实的正式出版元数据为准并报告差异。保留标题、完整作者及标记、期刊、年份；当卷号与页码/文章编号尚未齐全时，出版信息统一显示“YEAR, accepted.”，不得猜测卷页，也不展示半套卷页。Scholar 或出版商官网后续提供完整卷号与页码或文章编号时，在原条目更新为“YEAR, VOLUME, PAGE/ARTICLE_NUMBER.”，不另建重复论文，不写期号。期刊名称继续保留；完整格式为标题、作者名单、期刊名、年份、卷号、页码/文章编号。仅期刊名使用棕金；卷号黑色斜体，年份及页码黑色。保留已核实 DOI、链接与补充资源。Scholar 年份和正式卷期年份有冲突时核查出版商并报告，不静默迁移或覆盖。

3. 修改所属年份的可编辑 publicationsYYYY/index.html；新年份需建立对应源页面。保持已有编号稳定，新论文使用全站未使用的下一编号，展示时编号大的在前。生成器 tools/build_site.py 自动生成年份页、Full List、Latest（本年及前一年）及搜索数据，不手写多个副本。更新 data/publication-full-authors.json，按编号及规范化标题校验，保存完整姓名、共一/通讯标记、来源和核对日期，不特别加粗 Mengdi Han。保留用户已确认的 Selected Publications 主页面名单（data/selected-publications.json，9 篇）；同步其出版信息和引用数，但未经用户指定不要自动增删选文。

4. 每当论文新增或更新时，检查全部第一作者和明确标记 1/¹ 的共同第一作者是否位于 Group > Current 或 Alumni。以 data/member-publications.json 和最新 Alumni 名单为准；成员为一作/共一且 Mengdi Han 为共同作者时，加入该成员 Selected Publications，所有符合成员都要同步。将必要的完整有序姓名及核查证据写入 data/member-publications.json 的 evidence，保留明确确认和排除项。只列一作或共一，不加入普通合作者论文；姓名有歧义先查 Scholar 详情，再查出版商/PDF，不猜测。已移除的 Ji Wan Nano Energy 2020 独立文章不得恢复。两页选文使用同一份最新标题、完整一作/共一姓名（之后 et al.）、期刊、accepted/卷页及引用数，按全站编号降序；无论文展开仅显示 -。保留当前成员名单、双列卡片、独立展开和悬停效果。

5. 同步网站所有年份已收录论文的 Google Scholar citation 数量及真实 Cited by 链接，存入 data/scholar-citations.json，使用同一数据同步 Publication 年份页、Full List、Latest 和 Current/Alumni Selected Publications；Covers 保留现有共用数据，Home/Research 不加 citation。按 DOI、规范化标题及已验证别名匹配，保存 count、estimated、cited_by、scholar_article、checked_on。无可靠计数时保留上次值和原核对日期，不能以零覆盖失败或未收录；无匹配继续显示破折号。只有实际成功检查后才更新日期。顶部居中说明保持“*Corresponding authors; ¹ Authors contributed equally; Citation counts: Google Scholar; · Automatically updated YYYY-MM-DD”。不显示 Total citations、h-index、i10-index 总指标；已有缓存可以保留，不以网站引用数求和冒充 Scholar 总数。

6. 在新的隔离输出副本构建，不把 tools/build_site.py 用于可编辑源目录。运行 build_site.py、verify_site.py、node tools/check_archive_ui.cjs 和 tools/test_member_publications.py；核对新增文章的年份/Full List/Latest、全部符合成员的选文、完整姓名/标记、排序、accepted/卷页和引用数，检查实际 Cited by 链接。用 GitHub 连接器提交，更新 main 时使用最新 expected_sha，避免覆盖并行变更；检查 GitHub Pages 部署成功后才称为上线。保持现有设计、News 图片/链接、Contact 和招聘页；不改 hmd-lab.com 域名、DNS、仓库可见性。

云端执行中若缺少联网、GitHub 或构建能力，保存可核实结果并明确报告具体阻碍，不虚称完成。没有新增或有意义变更时保持安静；完成更新后简要报告新增论文、卷页补全、成员同步和引用变化，附来源及网站链接；失败或待核实问题也需报告。

## 用户固定维护规则（2026-10-20 22:50 确认）

- 每周五北京时间 03:30 检索 Mengdi Han 的 Google Scholar；自动新增 2026 年及之后论文，排除专利和 Wiley 独立期刊封面记录。
- 没有完整卷号与页码/文章编号时统一标注 accepted；后续补齐时更新原条目。保持标题、作者名单、期刊名、年份、卷号、页码/文章编号顺序；期刊名沿用现有格式，不省略。
- 新增/修改须同步所属年份列表和 Full List，并核对第一作者及所有以 1/¹ 标记的共同第一作者。若其位于 Group → Current 或 Alumni，须同步至每一位匹配成员的 Selected Publications；每人只列自己一作/共一文章，不列普通合作论文。成员选文不按年份分组，按全站编号降序。
- 同一时间从 Google Scholar 更新所有已收录论文的 citation，并同步 Publications 各列表以及 Current/Alumni Selected Publications。读取失败时保留旧值，不能用零覆盖。
