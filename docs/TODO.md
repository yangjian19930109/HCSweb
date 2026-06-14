# 待办清单

> 最后更新: 2026-06-13

1. **客户访问信息记录** — 记录访客地区等客户信息
2. **管理页面安全** — 防外部访问，仅限内部人员使用
3. **多用户登录 + 操作日志分类** — 不同人登录记录，日志分登录/编辑/删除/新建等类别，精确到时间
4. **全站字号加大** — 客户群体偏年长，对老花眼不友好，整体字体需要放大
5. **网站部署** — 上线流程
6. **首页六边形填充内容** — banner 区域的六边形蜂巢目前是占位，需要填入实际产品内容
7. **serve.py 安全加固** — 两个问题：
   - Content-Length 无上限校验（影响所有 POST/PUT 接口：contact、add-product、update-product、save-categories、batch-delete），恶意大 Content-Length 可致 OOM，需加 50MB 上限
   - `body.split(boundary)` 在二进制数据中可能误匹配（影响 add-product 和 update-product 的图片上传），需改用标准库 `email.parser` 或 `multipart` 解析 multipart
 8. **~~serve.py 构建不阻塞请求~~** ✅ 已修复 — `auto_build()` 改为 `threading.Thread(target=auto_build, daemon=True).start()` 后台执行
 9. **图片压缩** — 引用图过大，需压缩为 WebP：
    - `banner-bg.jpg` 6.0 MB → < 300 KB
    - `1030837-main2.jpg` 3.3 MB、`1030837-chart.png` 1.7 MB
    - `1030896-chart.png` 2.9 MB
    - `1061418_f979050c.png` 1.9 MB、`1061418_76c943c4.png` 3.3 MB、`1061418_0b86438a.png` 3.0 MB
    - `logo.jpg` + `logo.png` 各 587 KB，去重保留一个
10. **SMTP 启动验证 + 异步发送** — 两个问题：
    - `serve.py` 启动时不验证 SMTP 连接，配置错误只能等客户提交表单才发现
    - `send_email(timeout=15)` 同步阻塞表单 POST 请求线程，SMTP 不通时客户要等 15 秒
    - 应启动时测试连接并打印结果，发送邮件用后台线程
11. **静态资源无文件指纹** — `build.py` 不生成哈希文件名/查询参数：
    - `banner-bg.jpg`、`logo.png`、`motor-*.jpg` 等静态图无版本号
    - 构建更新后浏览器继续用缓存，用户看到旧资源
    - 需 `build.py` 对静态资源引用追加 `?v=BUILD_TIME` 查询参数
