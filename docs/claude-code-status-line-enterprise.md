# Claude Code Statusline Setup - Enterprise

**What it shows**
Model · context % · session cost · today's total cost · 5-hour block cost & time remaining · burn rate · monthly cost · git branch

---

## Legend

Example output:
```
🤖 Sonnet 4.6 | 💰 $0.04 session / $1.23 today / $0.45 block (2h 45m left) | 🔥 $0.08/hr | 🧠 12% | 📅 $1247.92/mo | main
```

| Field | Example | What it means |
|---|---|---|
| 🤖 Model | `Sonnet 4.6` | Active Claude model |
| 💰 Session | `$0.04 session` | Cost for the current open conversation. Resets when you start a new session. |
| 💰 Today | `$1.23 today` | Total spend across all sessions today. Closest thing to a running daily bill. |
| 💰 Block | `$0.45 block (2h 45m left)` | Cost within the current rolling 5-hour window, with time remaining. Useful for tracking burn in a focused work block. |
| 🔥 Burn rate | `$0.08/hr` | How fast you're spending right now based on recent token activity. Green = normal, yellow = moderate, red = high. Useful for catching runaway agentic tasks. |
| 🧠 Context | `12%` | How much of the context window is used in the current session. When this climbs above 80%, consider running `/compact` to compress history and free up space. |
| 📅 Monthly | `$1247.92` | Total spend for the current calendar month across all sessions. Updated once at session start. |
| Git branch | `main` | Current git branch. Helps with orientation when working across multiple worktrees or repos. |

---

## Step 1 - Create the scripts

### macOS / Linux

Save to `~/.claude/statusline.sh`:
```bash
#!/bin/bash
BRANCH=$(git -C "$(pwd)" rev-parse --abbrev-ref HEAD 2>/dev/null)
MONTHLY=$(cat /tmp/cc_monthly_cost.txt 2>/dev/null || echo "?")
CCUSAGE=$(bun x ccusage statusline --cost-source ccusage)
echo "$CCUSAGE | 📅 $MONTHLY/mo | $BRANCH"
```

Save to `~/.claude/update-monthly.sh`:
```bash
#!/bin/bash
CURRENT_MONTH=$(date +%Y-%m)
COST=$(bun x ccusage monthly --json | jq -r --arg m "$CURRENT_MONTH" '.monthly[] | select(.period == $m) | "$" + (.totalCost * 100 | round / 100 | tostring)')
echo "${COST:-?}" > /tmp/cc_monthly_cost.txt
```

Make both executable:
```bash
chmod +x ~/.claude/statusline.sh ~/.claude/update-monthly.sh
```

### Windows

Save to `%USERPROFILE%\.claude\statusline.ps1`:
```powershell
$input_data = $input | Out-String
$branch = git -C (Get-Location) rev-parse --abbrev-ref HEAD 2>$null
$monthly = Get-Content "$env:TEMP\cc_monthly_cost.txt" -ErrorAction SilentlyContinue
if (-not $monthly) { $monthly = "?" }
$ccusage = $input_data | bun x ccusage statusline --cost-source ccusage
Write-Output "$ccusage | 📅 $monthly/mo | $branch"
```

Save to `%USERPROFILE%\.claude\update-monthly.ps1`:
```powershell
$month = Get-Date -Format "yyyy-MM"
$json = bun x ccusage monthly --json | ConvertFrom-Json
$cost = $json | Where-Object { $_.month -eq $month } | Select-Object -ExpandProperty totalCost
"`$$cost" | Out-File "$env:TEMP\cc_monthly_cost.txt" -Encoding utf8
```

---

## Step 2 - Configure settings.json

Add both the statusline and the session hook to `~/.claude/settings.json` (macOS/Linux) or `%USERPROFILE%\.claude\settings.json` (Windows).

### macOS / Linux
```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  },
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "~/.claude/update-monthly.sh"
      }
    ]
  }
}
```

### Windows
```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"%USERPROFILE%\\.claude\\statusline.ps1\""
  },
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"%USERPROFILE%\\.claude\\update-monthly.ps1\""
      }
    ]
  }
}
```

---

## Step 3 - Verify

Restart Claude Code. You should see something like:
```
🤖 Sonnet 4.6 | 💰 $0.04 session / $1.23 today / $0.45 block (2h 45m left) | 🔥 $0.08/hr | 🧠 12% | 📅 $1247.92/mo | main
```

If the monthly figure shows `?`, start a new session to trigger the hook, or run the update script manually once:

- macOS/Linux: `~/.claude/update-monthly.sh`
- Windows: `powershell -File %USERPROFILE%\.claude\update-monthly.ps1`

---

## Notes

- Requires `bun` installed - macOS: `brew install bun` · Windows: `winget install Oven-sh.Bun` or `npm install -g bun`
- Also requires `jq` on macOS/Linux - `brew install jq` · `apt install jq`
- If Claude Code was installed via npm, `bun x` is the correct runner - if native install, replace `bun x` with `BUN_BE_BUN=1 claude x` (macOS/Linux) or `claude x` (Windows)
- Windows users may need to allow script execution first: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- The monthly figure updates once per session start - it won't change mid-session
- For a full monthly breakdown by model: `ccusage monthly --breakdown`
- For daily spend: `ccusage daily`
