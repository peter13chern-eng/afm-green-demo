# afm-green-demo Codex Rules

- 先遵守全局规则：读取 `/Users/Peter/Documents/Codex/规矩文档.rtf` 和 `/Users/Peter/Documents/Codex/踩坑日志.rtf` 后再执行项目任务。
- 只处理当前仓库 `/Users/Peter/Documents/Codex/搭建网站/afm-green-demo`；Git 操作不得触碰父目录或兄弟仓库。
- 修改网站内容时同时检查 HTML、CSS、`script.js`、语言字典和运行时覆盖逻辑；不要只改静态 HTML fallback。
- 可见文案、导航、按钮、卡片、详情页字段和语言切换相关内容必须与现有语言列表保持一致。
- Blog 任务优先使用 `blog.html`、`blog-article.html`、`blog-imported-data.js`、`script.js`、`styles.css` 的现有结构。
- Case 任务优先使用 `cases.html`、`case-*.html`、`script.js`、`styles.css`、`assets/cases-generated/` 的现有结构。
- 视觉或交互改动必须用本地 HTTP 服务和真实浏览器验证；不要依赖 `file://` 判断网页效果。
- 发布或推送前至少运行 `node --check script.js` 和 `git diff --check`；如命令不适用，说明原因。
- 线上发布后必须用真实线上 URL 校验关键页面，并注意缓存、hash 路由、标题和语言切换。
- 不要打印密钥、Token、访问凭证或敏感配置；认证或网络失败只报告失败类型。
