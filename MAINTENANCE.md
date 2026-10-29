# 图片与网站维护

本站是独立静态网站，不再加载“上线了”的脚本、API、图片或字体。布局样式已保存在 static/styles，交互代码为 static/site.js。

Home、Research 的五个页面与 Bio 页面在发布时由 `tools/research_layout.py` 重新排版，使用独立的 `static/research.css` 和 `static/research.js`，不再加载旧主题。文字、图片和论文链接仍编辑原来的 `index.html`、`overview/index.html`、`electronic-skins/index.html`、`wearable-devices/index.html`、`smart-implants/index.html`、`bio/index.html`。Bio 保留完整中英文简介，以分区排版和页内语言链接展示。首页展示图通过 Previous / Next 手动切换，不自动播放。`tools/check_research.py` 在发布前核对原文、图片与链接，避免重新排版遗漏内容。

## 图片分类
- images/brand：网站标识与分享图
- images/people：成员、韩梦迪老师和课题组活动
- images/research：各研究方向
- images/publications：论文插图和期刊封面
- images/news：按年份归档的新闻图片
- images/lab-tour：实验室与设备
- images/home：首页图
- images/pages：其他页面

同一图片在多个页面使用时只保留一个路径。images/catalog.csv 和 catalog.json 列出图片路径、说明和使用页面；打开 /images/ 可浏览缩略图并搜索。

## 替换图片
1. 在图片目录找到目标图片，打开仓库内相应文件。
2. 上传新图片覆盖同一路径，保留文件名、扩展名，建议维持相同宽高比。GIF 应保留为 GIF，避免丢失动画。
3. 提交到 main。GitHub Actions 会验证并自动发布，完成后刷新网页（必要时强制刷新）。
4. 若增加或重命名图片，更新对应栏目 index.html 中的 src 和相关背景 URL，并同步图片目录记录。

内容直接在各栏目 index.html 中编辑。首页为 index.html，2026 新闻为 news/2026/index.html，2026 论文为 publications/2026/index.html。外部论文链接仍指向出版商；点击外链与页面自身加载依赖是两回事。

原域名与阿里云 DNS 未变更。历史迁移记录仍可通过 Git 历史恢复；当前发布不再执行抓取。

## 年份导航和 Full List 自动维护

顶部 Publications 和 News 直接打开当年的页面；如果当年页面尚未创建，则打开最近的已有年份。页面第一行自动列出已存在的年份，并高亮当前年份；Full List 与 Covers 为突出显示的入口。

论文内容只编辑 publications/YYYY/index.html；News 内容只编辑 news/YYYY/index.html。GitHub Actions 发布时运行 tools/build_site.py，从各年份论文页生成 /publications/all/，从各年份新闻页生成 /news/all/，并更新所有年份链接。不要单独维护 Full List，生成结果会覆盖旧版本。

新增年份时创建 publications/YYYY/index.html 或 news/YYYY/index.html，保留相应类型页面结构即可；导航会自动发现新目录。论文条目延续现有的 (数字) 编号，编号在所有年份中应保持唯一，以避免重复收录。

## 目录结构（2026-10-24）

- `publications/YYYY/index.html`：各年份论文的唯一可编辑源。
- `publications/all/`、`publications/selected/`、`publications/covers/`：完整列表、精选论文、封面。
- `publications/microrobot/`：Science Robotics 论文视频页，视频文件位于其 `videos/`。
- `news/YYYY/index.html`：各年份新闻的唯一可编辑源；`news/all/` 为生成的完整新闻列表。
- `publications/` 和 `news/` 的栏目入口由构建生成。不要把构建结果覆盖回可编辑源。
- 已删除 `preview/`；正式构建不再生成预览页，发布包排除该目录。正式页面仍使用的 member-preview.css 等样式文件需要保留。
- 根目录 `404.html` 和 `static/legacy-routes.js` 将旧年份、Full List、封面和 microrobot 链接跳转到新地址，并保留查询参数和锚点。GitHub Pages 的兼容跳转依赖浏览器 JavaScript，旧链接的首次响应是 404；新站内部链接全部直接使用新地址。

目录规则以本节为准，取代旧维护文档中的根目录年份路径。历史源页面中的旧链接在隔离发布构建中统一转换为新路径；不需要手工重写整份页面。

## 本人访问排除（2026-10-29）

访问 `/analytics-device/`，在每个常用浏览器中设置设备并启用排除。`static/analytics.js` 在加载百度和 GA4 前读取 `hmd-owner-analytics-v1=exclude`，命中时两套采集均不加载。`hmd-owner-device-v1` 只保存 office/laptop/phone 标签，不上传。标记不依赖 IP；清除网站数据或换浏览器后需重设。设置页不参与访问统计。恢复按钮可撤销，历史数据不变。此标记仅是统计偏好，不是登录或访问控制。
