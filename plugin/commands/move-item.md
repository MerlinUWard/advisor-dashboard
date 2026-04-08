---
description: Move a task or note to a different project
allowed-tools: "Read, Write, Bash"
argument-hint: "[task/note description] to [project name]"
---

Move an individual task or note from one project to another. Used to correct misattributed items from Gong syncs.

## Instructions

1. **Read Dashboard/config/setup.json** using the Read tool to get supabase_url and supabase_service_key. Use Bash to fetch aliases from Supabase (GET /rest/v1/aliases?select=*).

2. **Identify the source item** from $ARGUMENTS:
   - If not specified: ask "What would you like to move? Describe the task or note and which project it's currently in."
   - If provided: resolve the source project via Bash (GET /rest/v1/projects?name=ilike.*[name]*&select=*) with alias matching
   - Fetch tasks: GET /rest/v1/tasks?project_id=eq.[project_id]&select=*
   - Fetch notes: GET /rest/v1/advisor_call_summaries?project_ids=cs.{[project_id]}&select=*
   - List matching items and ask the user to confirm which one

3. **Identify the destination project:**
   - If not specified in $ARGUMENTS: ask "Which project should this be moved to?"
   - Resolve via Bash with alias matching
   - The destination may belong to a different client

4. **Confirm the move:**
   ```
   Move: "[item title/excerpt]"
   From: [Source Project] → [Source Client]
   To:   [Destination Project] → [Destination Client]
   ```
   Ask: "Confirm? Type YES to proceed."

5. **Perform the move** via Bash:
   - For a task: PATCH /rest/v1/tasks?id=eq.[task_id] with project_id set to destination project id
   - For a note: PATCH /rest/v1/advisor_call_summaries?id=eq.[note_id] — update project_ids array to replace source with destination
   - Recompute next_due_date on both source and destination projects (query pending tasks, find earliest due_date, PATCH each project)

6. **Confirm:** "[Item type] moved to [Destination Project]. Would you like to open that project?"
