---
name: unexpected-state-ask-dont-assume
description: 发现数据/状态异常时先弹窗确认，不要自行判断并动手修复
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9afa9e23-b839-4c9d-80f1-52eabc70441a
---

**案例：** 发现 products.json 从 9 个产品变成 3 个，直接判定为"数据丢失"并执行恢复操作，实际上用户是手动删除了产品。

**Why:** 我看到的"异常"可能是用户有意为之。自行修复不仅浪费时间，还可能破坏用户的操作结果。

**How to apply:**
1. 发现数据/状态和预期不一致时，用 AskUserQuestion 弹出确认
2. 描述观察到的现象，问"这是预期的还是需要修复？"
3. 用户确认后再动手
4. 绝对禁止在看到异常数据后一声不吭就执行恢复/修复操作

[[workflow-confirm-before-start]]
