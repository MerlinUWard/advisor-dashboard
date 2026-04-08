---
description: Open a project dashboard by name
allowed-tools: "Read, Write, Bash"
argument-hint: "[project name] or [client name / project name]"
---

Open the dashboard for a specific project. $ARGUMENTS is the project name, optionally prefixed with the client name separated by a slash or dash.

## Instructions

1. **Read Dashboard/config/setup.json** using the Read tool to get supabase_url and supabase_service_key. Use Bash to fetch aliases from Supabase (GET /rest/v1/aliases?select=*) using apikey and Authorization Bearer headers with the service key.

2. **Resolve the project:**
   - If $ARGUMENTS contains "/" or " - ", split into [client, project]
   - Otherwise, search all client files for a project whose name fuzzy-matches $ARGUMENTS using aliases
   - If multiple projects match across clients, list them and ask the user to pick one
   - Use Bash to query Supabase: GET /rest/v1/projects?name=ilike.*[project]*&select=* to find the project

3. **Fetch all project data** using Bash:
   - Client: GET /rest/v1/clients?id=eq.[client_slug]&select=*
   - Project: GET /rest/v1/projects?id=eq.[project_id]&select=*
   - Tasks: GET /rest/v1/tasks?project_id=eq.[project_id]&select=*&order=due_date.asc
   - Notes/summaries: GET /rest/v1/advisor_call_summaries?project_ids=cs.{[project_id]}&select=*&order=call_date.desc&limit=10

4. **Read `${CLAUDE_PLUGIN_ROOT}/skills/dashboard-context/references/ui-design.md`** for visual specs.

5. **Render the project dashboard** as self-contained HTML. Include:

   **Project Header:**
   - Project name + status badge
   - Client name (breadcrumb: Team > Client > Project)
   - Advisor owner badge (role color)
   - Created date + created from (Gong / Manual)
   - [Edit Status] [Merge Project] [+ Add Task] [+ Add Note] buttons

   **Tasks:**
   - Table with columns: Status | Title | Due Date | Owner | Source | Actions
   - Sorted: overdue first (red), then pending by due date, then in_progress, then completed (collapsed)
   - Each row: checkbox to mark complete, [Edit] [Move] action buttons
   - Source column: "Gong [call date]" or "Manual"
   - WISHLIST: if `gong_recording_link` is set, show a 🔗 link icon next to source
   - [+ Add Task] button at bottom of table

   **Project Notes:**
   - Gong-sourced notes (with advisor name, call date, sentiment badge) and manual notes
   - Each Gong note: "[Advisor] • [Date] • [Sentiment badge]" header, then content
   - WISHLIST: if `gong_recording_link` set, show "🔗 View in Gong" link
   - Manual/Team Meeting notes: "[Date] • [Tag chips]" header, then content
   - [+ Add Note] button

   **Merge / Move Panel (collapsed by default):**
   - "⚠ Error Correction Tools" header
   - [Merge this project into another project] → runs /merge-projects logic
   - [Move a task or note to another project] → runs /move-item logic

6. Write to `/outputs/project-dashboard.html` and link to it.
