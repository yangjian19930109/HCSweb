# Claude Code CLI 自动发现

## 问题

Claude Code 随 VSCode 扩展安装，路径包含版本号：

```
C:\Users\<用户名>\.vscode\extensions\anthropic.claude-code-2.1.177-win32-x64\resources\native-binary\claude.exe
```

扩展升级后版本号变化，硬编码路径立即失效。

## 方案

### PowerShell（Codex / Windows 自动化）

```powershell
$claude = Get-ChildItem "$env:USERPROFILE\.vscode\extensions\anthropic.claude-code-*\resources\native-binary\claude.exe" |
    Sort-Object { [version]($_.Directory.Parent.Parent.Name -replace 'anthropic.claude-code-','') -replace '-win32-x64','') } |
    Select-Object -Last 1 -ExpandProperty FullName

& $claude -p "Read instruction.md and execute" 2>&1
```

原理：`Get-ChildItem` 通配符匹配所有版本 → 按版本号排序取最新 → 调用。

### Git Bash（终端手动使用）

```bash
claude() {
  local latest=$(ls -d "$HOME/.vscode/extensions/anthropic.claude-code-"*/resources/native-binary/claude.exe 2>/dev/null | sort -V | tail -1)
  if [ -n "$latest" ]; then
    "$latest" "$@"
  else
    echo "claude.exe 未找到"
  fi
}
```

放在 `~/.bashrc`，之后终端直接敲 `claude`。

## 适用场景

| 环境 | 方案 |
|------|------|
| Codex 调 Claude Code | PowerShell 自动发现 |
| Git Bash 终端 | bash 函数 |
| 其他自动化脚本 | 两方案任选，核心逻辑相同 |

## 注意

- 前提：VSCode 已安装 `anthropic.claude-code` 扩展
- 多版本共存时取最新，旧版本可手动清理
- 首次调用有 ~8s 冷启动，`--resume` 可复用会话


