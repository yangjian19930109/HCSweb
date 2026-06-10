---
name: encoding-garbled-fix
description: Windows终端GBK编码导致Python输出中文乱码的根因及修复
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3af0e7fc-5938-4392-b082-c28ae717535d
---

## 问题

Windows 终端（含 Git Bash）默认编码是 GBK，Python 脚本输出 UTF-8 中文时，终端用 GBK 解析导致乱码。

典型表现：
- `build.py` 输出 `[OK] 已读取 inc/nav.html` 显示为 `[OK] �Ѷ�ȡ inc/nav.html`
- `serve.py` emoji 字符触发 `UnicodeEncodeError: 'gbk' codec can't encode character`
- 中文输出全部变成乱码方块

## 根因

Windows 系统代码页默认 936 (GBK)，Python 3 在 Windows 上检测到终端编码为 GBK 后尝试用 GBK 输出，但脚本中混有 GBK 无法编码的字符（emoji 等），或终端实际接收 UTF-8 但用 GBK 解码。

## 修复

运行 Python 命令时加 `PYTHONIOENCODING=utf-8` 环境变量：

```bash
PYTHONIOENCODING=utf-8 python build.py
PYTHONIOENCODING=utf-8 python serve.py
```

**Why:** 强制 Python 使用 UTF-8 编码输出，与脚本中的 UTF-8 字符串匹配。

**How to apply:** 每次在 Windows 上执行 Python 脚本时，一律带上 `PYTHONIOENCODING=utf-8`。

[[port-conflict-server-lessons]]
[[build-and-fonts-lessons]]
