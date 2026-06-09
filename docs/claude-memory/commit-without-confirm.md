---
name: commit-without-confirm
description: 用户要求提交代码时不弹框确认，直接执行
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ea33cd65-4e22-4a51-93fe-faec05084291
---

用户明确说"提交代码"或类似表述时，直接 `git add -A && git commit` 即可，不需要弹窗确认。

**Why:** 用户觉得提交是常规操作，不需要额外确认步骤。
**How to apply:** 遇到"提交"、"commit"、"提交代码"等指令，直接执行，不弹 AskUserQuestion。
