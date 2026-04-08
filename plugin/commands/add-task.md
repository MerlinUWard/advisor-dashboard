---
description: Add a task to a project
allowed-tools: "Read, Write, Bash"
argument-hint: "[project name] or [client name / project name]"
---

Add a manual task to a project with a due date and advisor owner.

## Instructions

1. **Read Dashboard/config/setup.json** using the Read tool to get supabase_url and supabase_service_key. Use Bash to fetch aliases from Supabase (GET /rest/v1/aliases?select=*).

2. **Resolve the project** from $ARGUMENTS:
   - If empty: ask "Which project should I add this task to? (You can say 'Client Name / Project Name')"
   - If provided: use Bash to query Supabase GET /rest/v1/projects?name=ilike.*[name]*&select=* and apply alias matching
   - If multiple matches: list them and ask the user to pick
   - Confirm the resolved project with the user

3. **Collect task details** in one message:
   - Task title (required)
   - Description (optional — "any additional context?")
   - Due date (required — if they say something like "end of next week", convert to a specific ISO date and confirm)
   - Advisor owner — offer the three advisors by name + role from setup.json; let them type a name or pick

4. **Build the task object:**
   ```json
   {
     "id": "[generate uuid]",
     "project_id": "[project id]",
     "title": "[title]",
     "description": "[description or null]",
     "completed": false,
     "due_date": "[ISO 8601 date]",
     "advisor_owner": "[advisor uuid from setup.json]",
     "created_from": "manual",
     "gong_call_id": null,
     "gong_timestamp_seconds": 0,
     "gong_recording_link": null,
     "created_at": "[current ISO datetime]",
     "updated_at": "[current ISO datetime]"
   }
   ```

5. **Insert the task** via Bash:
   ```
   POST /rest/v1/tasks
   Headers: apikey, Authorization Bearer, Content-Type: application/json, Prefer: return=representation
   Body: [task object as JSON]
   ```

6. **Update the project's next_due_date** via Bash: query GET /rest/v1/tasks?project_id=eq.[id]&completed=eq.false&select=due_date, find the earliest date, then PATCH /rest/v1/projects?id=eq.[project_id] with next_due_date.

7. **Confirm:** "Task added to [Project Name] → [Client Name], due [date], assigned to [advisor name]. Would you like to open the project dashboard?"
