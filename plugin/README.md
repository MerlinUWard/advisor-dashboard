# Advisor Dashboard Plugin

An intelligent client/project dashboard for advisory teams. Automatically populated from Gong call transcripts, with data stored in Google Drive and MOI sentiment scores pulled from Google Sheets.

---

## What It Does

- **Team Dashboard** — top-line view of all clients, advisor tasks due today, upcoming deadlines, and MOI sentiment scores
- **Client Dashboard** — advisor call summaries, project blocks, manual notes, and document links for each client
- **Project Dashboard** — tasks, Gong-sourced notes, document links, and error correction tools for each project
- **Gong Sync** — daily (or on-demand) processing of Gong transcripts to auto-create and update projects and tasks
- **MOI Sync** — weekly pull of MOI sentiment scores from the team's Google Sheets tracker (every Monday)
- **Learning System** — corrections you make (wrong client name, duplicate project, etc.) are remembered in `learn.md` and never repeated

---

## Requirements

### For the Operations Advisor (plugin owner)
- Claude Cowork desktop app
- Google Drive connector installed and authorized
- Google Sheets connector installed and authorized
- Active Gong.io browser session (for syncing transcripts)

### For all advisors
- Claude Cowork desktop app
- This plugin installed (`.plugin` file)
- Gmail connector (optional — for email surface on dashboards)
- Google Calendar connector (optional — for upcoming call display)

---

## Installation

1. In Claude Cowork, go to Plugins and install `advisor-dashboard.plugin`
2. **Operations Advisor only:** Run `/setup` to configure the team and create the shared Google Drive data folder
3. Share the created `*[Team Name] - Dashboard Data` folder with your Finance and Marketing Advisors
4. Each advisor installs the plugin and connects their Gmail and Google Calendar connectors

---

## Commands

| Command | Description |
|---------|-------------|
| `/setup` | First-run setup (OA only). Collects team info, creates Drive data folder, writes config files. Add `reconfigure` argument to update advisor info without deleting data. |
| `/dashboard` | Open the team-level dashboard. Shows all clients, MOI scores, today's tasks, and upcoming deadlines. |
| `/client-view [name]` | Open the dashboard for a specific client. Accepts partial names and aliases. |
| `/project-view [name]` | Open the dashboard for a specific project. Accepts "Client / Project" format. |
| `/sync-gong` | Pull and process new Gong transcripts. Requires an active Gong.io browser session. |
| `/sync-moi` | Sync MOI sentiment scores from the Google Sheets tracker. Runs automatically every Monday. |
| `/add-note [target]` | Add a manual note (team meeting, observation, sentiment) to a client or project. |
| `/add-task [project]` | Add a task with a due date and advisor owner to a project. |
| `/merge-projects` | Merge two projects into one. Moves all tasks, notes, and docs. Writes audit history. |
| `/move-item` | Move an individual task or note from one project to another. |

---

## Data Storage

All data lives in a shared Google Drive folder: `*[Team Name] - Dashboard Data`

```
*[Team Name] - Dashboard Data/
  ├── setup.json      — team configuration (read-only after setup)
  ├── meta.json       — sync timestamps, MOI scores, error state
  ├── learn.md        — name corrections and learned aliases
  └── clients/
      └── [client-slug].json   — one file per client
```

This folder is created by the OA during `/setup` and must be shared with all advisors in Google Drive.

---

## The learn.md System

The `learn.md` file remembers corrections so they're never repeated. It updates automatically when you:
- Correct a client name that was misspelled in a Gong transcript
- Merge two duplicate projects (the old name becomes an alias)
- Confirm that an ambiguous Gong match is correct

You can also edit `learn.md` directly in Google Drive to add corrections manually.

---

## MOI Sheet

The plugin reads MOI sentiment scores from:
`https://docs.google.com/spreadsheets/d/1nuvNBprAgTKCv-2zAakbTMlonYuGaI6-7XqkEIs/edit`

- Syncs automatically every Monday morning
- Tab is matched to the team name set during `/setup`
- If the sheet becomes inaccessible, the dashboard shows the last known values and emails the OA automatically

---

## Gong Sync

Gong calls are processed via your browser (Claude in Chrome). The sync:
1. Navigates to Gong.io and reads transcripts since the last sync
2. Identifies clients and projects from transcript content
3. Creates/updates projects, tasks, and notes
4. Links Google Drive documents mentioned in calls
5. Flags anything uncertain for your review

You must have an active Gong.io session in your browser when running `/sync-gong`.

---

## Wishlist Features (Future)

- Deep Gong recording links that start playback at the exact second a task or note was mentioned
- Real-time conflict detection for simultaneous Drive writes

---

## Connectors

See `CONNECTORS.md` for details on tool placeholders and how to customize for a different tool stack.
