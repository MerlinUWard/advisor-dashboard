---
description: Open the team-level dashboard
allowed-tools: "Read, Write, Bash"
---

Open the Advisor Dashboard team view. This is the top-level view showing all clients, advisor tasks, and MOI scores.

## Instructions

1. **Read Dashboard/config/setup.json** using the Read tool to get supabase_url, supabase_service_key, team_name, and advisors list.

2. **Fetch data from Supabase** using Bash:
   - Sync state: `GET /rest/v1/sync_state?id=eq.singleton&select=*`
   - All clients: `GET /rest/v1/clients?select=*&order=name.asc`
   - All projects: `GET /rest/v1/projects?select=*`
   - Tasks due within 7 days: `GET /rest/v1/tasks?completed=eq.false&due_date=lte.[today+7days]&select=*&order=due_date.asc`
   - Tasks due today: `GET /rest/v1/tasks?completed=eq.false&due_date=eq.[today]&select=*`

3. **Compute summary stats:**
   - Count active projects across all clients
   - Find all tasks due within 7 days, sorted ascending
   - Find all tasks due today per advisor
   - Gather MOI scores from clients.moi_score

4. **Read `${CLAUDE_PLUGIN_ROOT}/skills/dashboard-context/references/ui-design.md`** for visual specs before rendering.

5. **Render the team dashboard** as a single self-contained HTML file written to the outputs folder. The dashboard must include:

   **Header bar:**
   - Greeting: "Good [morning/afternoon/evening], [OA first name]"
   - Subtitle: current date + team name
   - Last Gong sync timestamp and last MOI sync timestamp (from sync_state)
   - No action buttons (syncs are run as commands: /sync-gong, /sync-moi)
   - If `sync_state.moi_access_error` is set: display a red warning banner "⚠ MOI sheet access error — showing last known values."
   - If `sync_state.gong_sync_error` is set: display a yellow banner "⚠ Last Gong sync failed: [error]."

   **MOI Sentiment Strip:**
   - Sort all clients alphabetically by name
   - Split into **three equal columns by count**: `colSize = ceil(n / 3)`. Column 1 = items 0 to colSize-1, column 2 = colSize to 2*colSize-1, column 3 = remainder.
   - Each entry: color-coded pill with client name + MOI label
   - Color coding from ui-design.md sentiment scale
   - If a client has no MOI value yet: show gray "No data" pill

   **Today's Tasks — three columns (Ops / Finance / Marketing):**
   - Each column shows tasks due today assigned to that advisor
   - Each task row: client name → project name → task title → due date
   - Empty column message: "No tasks due today"

   **Upcoming (Next 7 Days):**
   - Table: Due Date | Client | Project | Task | Advisor
   - Sorted ascending by due date
   - Highlight overdue tasks in red

   **Active Clients:**
   - Card grid, one card per client
   - Each card: client name, MOI badge, active project count, next due date, [Open] button

6. **Write** the rendered HTML to `/outputs/team-dashboard.html` and link to it.

7. **Tell the user** the dashboard is ready and show a one-line summary: "X clients, Y active projects, Z tasks due this week."
