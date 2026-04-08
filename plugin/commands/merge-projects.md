---
description: Merge two projects into one
allowed-tools: "Read, Write, Bash"
argument-hint: "[project A] into [project B]"
---

Merge two projects into one. All tasks, notes, and documents from the source project are moved into the target project. A merge history record is written to the target.

## Instructions

1. **Read Dashboard/config/setup.json** using the Read tool to get supabase_url and supabase_service_key. Use Bash to fetch aliases from Supabase (GET /rest/v1/aliases?select=*).

2. **Identify the two projects** from $ARGUMENTS:
   - Parse "A into B" or "A and B" patterns
   - If only one or no names given: ask "Which two projects would you like to merge? Tell me the source (the one to absorb) and the target (the one to keep)."
   - Resolve each via Bash: GET /rest/v1/projects?name=ilike.*[name]*&select=* applying alias matching
   - They may belong to different clients — fetch client details for each

3. **Display a side-by-side comparison** before any changes:
   ```
   SOURCE (will be absorbed)          TARGET (will be kept)
   ─────────────────────────          ─────────────────────
   Name: [A]                          Name: [B]
   Client: [client]                   Client: [client]
   Tasks: [N]                         Tasks: [N]
   Notes: [N]                         Notes: [N]
   Created: [date]                    Created: [date]
   ```

   Ask: "Merge [Source] INTO [Target]? All tasks and notes from [Source] will be moved to [Target]. [Source] will be marked as archived. Type YES to confirm."

4. **Only proceed after explicit YES confirmation.**

5. **Perform the merge** via Bash:
   - PATCH all tasks: /rest/v1/tasks?project_id=eq.[source_id] with project_id set to target_id
   - PATCH all notes/summaries: /rest/v1/advisor_call_summaries?project_ids=cs.{[source_id]} — update project_ids array to replace source with target
   - PATCH source project: /rest/v1/projects?id=eq.[source_id] with status "archived" and append merge record to merge_history
   - Recompute target next_due_date: query pending tasks, find earliest due_date, PATCH target project

6. **Record the alias** via Bash:
   - POST /rest/v1/aliases with source project name → target project name mapping (type: "project", client_id: source client)
   - This ensures future Gong mentions of the source name route to the target

7. **Confirm:** "Merge complete. [N tasks, N notes] moved from [Source] to [Target]. [Source] is now archived. [Source]'s name has been added as an alias so future Gong mentions of it will automatically route to [Target]."

   Ask: "Would you like to open [Target] project dashboard?"
