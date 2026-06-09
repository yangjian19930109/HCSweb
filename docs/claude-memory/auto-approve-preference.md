---
name: auto-approve-preference
description: 用户要求所有弹窗询问直接执行，不需要确认
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8acf3f43-a247-407f-a591-089e05ffff67
---

用户要求所有权限弹窗/确认询问都不要弹出，直接执行，不需要反复确认。

**Why:** 用户信任执行结果，不想被反复打断。

**How to apply:** 所有 Bash 命令、文件编辑等操作直接执行，不调用 AskUserQuestion，不做二次确认。

**例外：** git 操作（commit、push、merge、rebase、branch 切换等）如果不是用户主动要求的，必须先弹窗确认。用户主动说"提交""推送"等不算被动触发。
