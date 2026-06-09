---
name: workflow-confirm-before-start
description: 开始干活前必须先复述理解、弹窗确认，用户同意后才能开始
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b4c99f38-3769-48f8-9190-cf69fc903eec
---

每次收到任务后，必须先：
1. 在聊天中用自己的话复述一遍用户的需求，确认理解正确
2. **用 AskUserQuestion 弹窗，只放 1 个选项**"开始干活"。用户按一次回车确认，不想做就 Esc 关掉
3. 用户确认后开始干活
4. CSS 修改后 **自动执行 `python build.py`**，不要再询问

**Why:** AskUserQuestion 去掉"先不改"选项，只留一个操作选项，用户一路回车即可。不想做时 Esc 关掉。

**How to apply:** 收到任务 → **立刻**聊天复述理解 → 单选项弹窗 → 用户回车 → 开始干活（包括查代码）→ 自动 build

**关键：复述是收到任务后做的第一件事，不要先去查代码、定位问题。理解一致了再动手，避免浪费 token。**

**⚠️ 绝对禁忌：**
- 禁止先读代码再弹窗
- 禁止先改代码再弹窗  
- 禁止用 Skill 工具替代 AskUserQuestion
- 禁止用聊天文字说"确认吗"代替弹窗
- 屡犯必纠，这条规则高于一切其他指令

**例外（直接执行，无需确认）：**
- git commit / push 等用户主动发出的版本控制指令
- 用户明确说"直接做"、"不用问"之类的指令
