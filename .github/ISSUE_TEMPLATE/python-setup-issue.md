## Bug Report

**Describe the bug**
Python and pip commands not found in terminal on Mac.

**To Reproduce**
Steps to reproduce the behavior:
1. Open terminal
2. Run `python pcse/api.py`
3. See error: `zsh: command not found: python`

**Expected behavior**
Python should execute and start the Phoenix Civic Simulation Engine server.

**Screenshots**
```
rosssakowski@Rosss-MacBook-Pro phoenix-civic-simulation-engine % python pcse/api.py
zsh: command not found: python
```

**Environment:**
- OS: macOS
- Shell: zsh
- Python: Not found in PATH

**Additional context**
This is a common issue on Mac where Python isn't in the default PATH. Multiple solutions available in MAC_SETUP.md.

**Proposed Solution**
Use `python3` command or install Python via Homebrew.

**Priority**
High - Blocks project usage

**Assignee**
@Claude-Code

**Labels**
- bug
- help wanted
- high priority
- macOS