---
name: port-conflict-server-lessons
description: 多进程占用同一端口导致 serve.py 不生效的排查经验
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9afa9e23-b839-4c9d-80f1-52eabc70441a
---

**问题现象：** 网页顶端导航栏消失、产品页面布局全乱，看起来像大规模故障。

**根因：** 多个 HTTP 服务器进程同时占用 8080 端口。之前在切换不同 commit 时分别启动了 `python -m http.server 8080`（提供源文件，无构建）和 `python serve.py`（正确提供 dist/），旧进程没被杀死，新旧共存。浏览器请求时命中了旧进程，拿到了未构建的源文件——`<!-- #include nav.html -->`、`{{BUILD_TIME}}` 等占位符全未替换。

**Why:** 
- `python -m http.server` 直接提供当前目录原始文件，不经 build.py 处理
- `python serve.py` 会 `os.chdir(dist/)` 再提供服务，所有 `<!-- #include ... -->` 已被替换
- 切换 commit 时启动的服务器进程不会自动终止，会与新进程抢占端口
- 多个进程同时 LISTEN 同一端口时行为不确定，可能命中任意一个

**How to apply:**
1. 启动服务器前先 `netstat -ano | grep 8080` 检查端口占用
2. 如有残留进程，`taskkill /F /PID <pid>` 全部清理后再启动
3. 启动后用 `curl -s http://localhost:8080/products.html | grep "include"` 验证：如果输出中有 `<!-- #include` 占位符，说明服务器没正确提供 dist/ 构建后的文件
4. 切 commit 后必须重启服务器，因为 serve.py 可能在新 commit 中不存在或行为不同
