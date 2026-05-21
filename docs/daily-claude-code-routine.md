# Setting Up a Daily Claude Code Routine

## Why

Claude Code gives you a token budget that resets every 5 hours. The window starts when you send your first message, floored to the clock hour.

So if you start at 8:30 AM and burn through your budget by 11, you're locked out until 1 PM. Two dead hours in the middle of your morning.

The fix is dumb and it works: fire a throwaway message before you start working. A GitHub Actions cron sends "hi" to Haiku at 6:15 AM. The window floors to 6 AM, runs until 11. By the time you've hit the limit, it resets right away. Your next message anchors a fresh window through 4 PM.

Example schedule:

```markdown
            6am    7     8     9    10    11    12    1pm    2     3     4     5    6pm
             |     |     |     |     |     |     |     |     |     |     |     |     |

Before:                  [========== window 1 =========]
                          work ~8:30am-11am  ░░ dead ░░
                                                       [========== window 2 =========]
                                                                work ~1pm-6pm
          cron trigger
               │
               ▼
After:       [========== window 1 =========]
              ░░ idle ░░  work ~8:30am-11am
                                           [========== window 2 =========]
                                                   work ~11am-4pm
                                                                         [== win 3 ==]
                                                                         work ~4pm-6pm
```

> As you can see, we are able to squeeze another fresh window starting at 4pm in this case.

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
