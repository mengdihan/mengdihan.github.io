# HMD 私有访问统计 — 待部署

网站仍由 GitHub Pages 托管。不需要改 hmd-lab.com DNS。
此目录仅包含源代码与示例配置，没有访问日志、数据库或密钥。追踪脚本尚未接入。

## 审查设计
- Worker `/collect`：仅允许本站 Origin；记录服务端时间、CF-Connecting-IP 和 Cloudflare 国家/省/城市字段。不采集查询字符串、表单、页面内容或精确位置。
- `/admin` 及 `/admin/*`：Cloudflare Access 登录；Worker 再验证 RS256 签名、issuer、audience、exp、iat、sub 和唯一管理员邮箱。缺配置/认证失败默认拒绝。不要配置 bypass。
- D1：浏览量 events、会话 sessions、匿名浏览器 visitors。匿名 UUID 经 Worker HMAC 后入库；共享 IP 不合并为一个人。30 分钟无新页面加载形成新会话；刷新为新浏览量。同会话可包含多页面。禁用存储、DNT/GPC、拦截脚本的访问不计，因此不是服务器全量访问日志。机器人或伪造客户端可污染公开采集数据，Origin 不是防作弊认证。
- 计数从启用起开始；无历史日志。后台提供总量、近 30 天 UTC 日趋势、北京时间明细及分页 CSV（每批最多 500 条）。CSV 已处理公式注入；明细通过 textContent 渲染。
- 当前不自动删除数据；需要部署时约定保留期限。不要把生产日志导出到本仓库。免费额度耗尽应停止采集，不能自动升级。

## 部署前步骤（尚未执行）
1. 用户在云端浏览器登录 Cloudflare；注册和条款由用户完成。核实账号 Workers/D1/Access 均使用免费方案；如已有付费计划，先停下确认费用风险。
2. `npm ci`；复制 `wrangler.example.jsonc` 为被忽略的 `wrangler.jsonc`。
3. 创建名为 `hmd-analytics` 的 D1，将返回 ID 填入本地配置，执行 `npx wrangler d1 migrations apply hmd-analytics --remote`。
4. 为 Worker 分配 workers.dev 地址；创建 hostname/path Access 应用，保护 `/admin` 和 `/admin/*`，只允许用户指定邮箱。`/collect` 必须保持公开。填入 issuer、AUD 和管理员邮箱。禁用 preview URLs。
5. 通过 Wrangler secret 或控制台设置随机至少 32 字节 `VISITOR_SECRET`；不得入仓库、聊天或日志。
6. `npm test`；`npx wrangler deploy --dry-run --config wrangler.jsonc`；部署 Worker。
7. 实测匿名后台/API/导出均拒绝，指定账号登录后可用，其他账号拒绝；跨源请求拒绝；提交明确标记的测试事件验证计数、回访、地理字段和导出，再清空测试数据库后启用。验证完毕前不要安装追踪器。
8. 把 tracker.js 放入网站 static，使用 `<script src="/static/analytics.js" data-endpoint="https://实际Worker地址/collect" defer></script>` 接入主生成器和成员生成器；加简短统计说明。重新生成并保持其它页面内容。
9. 真正访问开始后保存不含 IP 的验证摘要。更新 `docs/CLOUD_HANDOFF.md`，记录 Worker/Access/D1 资源名称，不记录密钥。

官方参考：
- https://developers.cloudflare.com/changelog/post/2025-10-03-one-click-access-for-workers/
- https://developers.cloudflare.com/workers/configuration/cloudflare-access/
- https://developers.cloudflare.com/workers/platform/pricing/

## 当前验证
`npm test` 测试未认证/伪造身份拒绝、采集来源限制、缺少密钥拒绝、CSV 公式转义。
部署后仍必须完成真实 Access 与 D1 端到端验收；本地测试不能替代它。
