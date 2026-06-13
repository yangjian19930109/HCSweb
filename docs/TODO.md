# 待办清单

> 最后更新: 2026-06-13

1. **客户访问信息记录** — 记录访客地区等客户信息
2. **管理页面安全** — 防外部访问，仅限内部人员使用
3. **多用户登录 + 操作日志分类** — 不同人登录记录，日志分登录/编辑/删除/新建等类别，精确到时间
4. **全站字号加大** — 客户群体偏年长，对老花眼不友好，整体字体需要放大
5. **网站部署** — 上线流程
6. **首页六边形填充内容** — banner 区域的六边形蜂巢目前是占位，需要填入实际产品内容
7. **serve.py 上传安全加固** — 两个问题：
   - Content-Length 无上限校验，恶意大 Content-Length 可致 OOM，需加 50MB 上限
   - `body.split(boundary)` 在二进制数据中可能误匹配，需改用标准库 `email.parser` 或 `cgi.FieldStorage` 解析 multipart
 8. **~~serve.py 构建不阻塞请求~~** ✅ 已修复 — `auto_build()` 改为 `threading.Thread(target=auto_build, daemon=True).start()` 后台执行
