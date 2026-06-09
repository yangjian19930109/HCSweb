---
name: commit-permission-rule
description: "用户主动说\"提交代码\"时直接执行，不用弹框确认"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c5381be6-ca84-46bf-9aa4-afde9f84a901
---

当用户主动说出"提交代码"、"commit"、"帮我提交"等明确指令时，直接执行 git add + git commit，不要使用 AskUserQuestion 或等待确认。git push 同理。

**Why:** 用户觉得每次 commit/push 都弹框很烦，主动要求提交时说明已经确认过了。
**How to apply:** 识别用户主动的提交指令 → 直接 git add -A && git commit，不再问。如果是 AI 自己判断需要提交（用户没主动说），才需要询问。
