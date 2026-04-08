---
description: Open a client dashboard by name
allowed-tools: "Read, Write, Bash"
argument-hint: "[client name]"
---

Open the dashboard for a specific client. $ARGUMENTS is the client name (may be partial or an alias).

## Instructions

1. **Read Dashboard/config/setup.json** using the Read tool to get supabase_url, supabase_service_key, and advisors list. Use Bash to fetch aliases from Supabase (GET /rest/v1/aliases?select=*).

2. **Resolve the client name** from $ARGUMENTS:
   - Check aliases for client name corrections
   - Query Supabase: `GET /rest/v1/clients?name=ilike.*[query]*&select=*`
   - Find the best fuzzy match between $ARGUMENTS and available client names
   - If match confidence is below 85%, show a list of closest matches and ask the user to confirm
   - If no match found: tell the user and list all available clients

3. **Fetch all client data** using Bash:
   - Client: `GET /rest/v1/clients?id=eq.[client_slug]&select=*`
   - Projects: `GET /rest/v1/projects?client_id=eq.[client_slug]&select=*&order=status.asc`
   - Tasks: `GET /rest/v1/tasks?project_id=in.([project_ids])&select=*&order=due_date.asc`
   - Call summaries: `GET /rest/v1/advisor_call_summaries?client_id=eq.[client_slug]&select=*&order=call_date.desc`

4. **Read `${CLAUDE_PLUGIN_ROOT}/skills/dashboard-context/references/ui-design.md`** for visual specs.

5. **Render the client dashboard** as a self-contained HTML file. Include:

   **Client Header:**
   - Client name (large)
   - MOI score badge (from `client.moi_score`) with last synced date
   - Last updated timestamp
   - [+ Add Note] [+ Add Task] [Sync Gong] buttons

   **Advisor Call Summaries — three panels side by side:**
   For each role (operations, finance, marketing):
   - Advisor name + role color badge
   - Most recent call: date + sentiment badge
   - 2–3 sentence summary
   - Key topics as chips/tags
   - If no calls yet: "No calls recorded yet"

   **Projects:**
   For each project sorted by status (active first, then on_hold, then completed/archived):
   - Project block with: name, status badge, advisor owner badge (role color), next due date
   - Task count (pending/total)
   - Top 3 upcoming tasks listed inline
   - [Open Project] button
   - Completed/archived projects collapsed by default under "Completed Projects (N)"

   **Client Notes:**
   - All notes where parent_type is "client" from advisor_call_summaries, sorted newest first
   - Each note: date, source badge (Gong / Manual / Team Meeting), tag chips, content
   - [+ Add Note] button

6. Write to `/outputs/client-dashboard.html` and link to it.
