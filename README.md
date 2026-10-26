# Mengdi Han Research Group

独立静态网站：<https://hmd-lab.com/>

页面、图片、字体、样式和交互代码均由本仓库托管，不需要原建站平台账号或服务。

## 找到并替换图片

打开 [可搜索图片目录](https://hmd-lab.com/images/)，根据缩略图、名称或使用页面定位图片。图片存放在 `images/`，按人物、研究方向、论文、新闻年份和实验室设备分类。

在 GitHub 上传新文件覆盖同一路径即可替换图片；保留扩展名和相近宽高比。提交到 `master` 后，Actions 检查资源和页面链接，成功后自动发布。

- [图片维护说明](MAINTENANCE.md)
- [图片清单 CSV](images/catalog.csv)
- [图片清单 JSON](images/catalog.json)
- `index.html`：首页
- `news/2026/index.html`：2026 年新闻
- `publications/2026/index.html`：2026 年论文
- `static/site.css`、`static/site.js`：导航、轮播、图片放大交互
- `static/styles/`、`static/fonts/`：本地主题样式和字体

`tools/independent.py` 仅记录一次性迁移过程，日常发布不执行抓取。原平台版本可从 Git 历史恢复。


## Publication metadata convention

For journal articles without final volume and page or article numbers, display `accepted` after the year. Do not display a DOI in the citation. Keep the article title linked to its original publisher page. Apply this convention to year pages and all generated publication lists.
