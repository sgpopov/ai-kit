# Setting Up a Daily Claude Code Routine

## Prerequisites

### 1. Plan requirement
Routines require a **Pro, Max, Team, or Enterprise** plan - not available on the free tier.

### 2. Enable Claude Code on the web
Claude Code on the web is on by default for Pro and Max users. For Team and Enterprise, account admins can toggle access under **claude.ai → Settings → Claude Code**.

### 3. Connect your terminal (CLI users only)
Run `/web-setup` in your terminal. The `/schedule` command checks for web access and will prompt you to run `/web-setup` if it isn't configured yet.

---

## Creating the Routine (Web UI)

1. Go to **[claude.ai/code/routines](https://claude.ai/code/routines)** and click **New routine**

2. **Name** - give it a descriptive name
   e.g. *Ping Claude to anchor 5-hour window*

3. **Instructions** - write the prompt Claude should execute on each run
   e.g. `Hello there` or something more useful like `Summarize open GitHub issues and post a daily standup digest`

4. **Model** - Haiku 4.5 is preselected (cheapest); switch to Sonnet if the task needs more reasoning power

5. **Select a trigger** → choose **Weekdays** and set the time (e.g. `9:30 AM`) - your timezone (GMT+3) is picked up automatically

6. **Connectors** *(optional)* - add integrations like GitHub or Slack that Claude can use during the run

7. Click **Save**

---

## Alternative: Create via CLI

Run `/schedule` inside a Claude Code session. Claude walks through the same fields as the web form and saves the routine to your account. Any routine created via CLI appears immediately at `claude.ai/code/routines`.

Useful CLI commands for managing routines:

| Command | Action |
|---|---|
| `/schedule` | Create a new routine |
| `/schedule list` | View all routines |
| `/schedule update` | Edit an existing routine |
| `/schedule run` | Trigger a routine immediately |

---

## Key Things to Know

- Routines run on **Anthropic-managed cloud infrastructure** - they keep working when your laptop is closed.
- You can **combine multiple triggers** on the same routine (schedule + API call + GitHub event).
- Routines are currently in **research preview** - behavior and limits may change.