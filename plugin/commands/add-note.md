---
description: Add a manual note to a client or project
allowed-tools: "Read, Write, Bash"
argument-hint: "[client name] or [client name / project name]"
---

Add a manual note to a client or project. Notes added this way are sourced as "manual" or "team_meeting" (not Gong).

## Instructions

1. **Read Dashboard/config/setup.json** using the Read tool to get supabase_url and supabase_service_key. Use Bash to fetch aliases from Supabase (GET /rest/v1/aliases?select=*).

2. **Resolve the target** from $ARGUMENTS:
   - If $ARGUMENTS is empty: ask "Are you adding this note to a client or a project? And which one?"
   - If $ARGUMENTS is provided: use Bash to query Supabase and resolve client (GET /rest/v1/clients?name=ilike.*[name]*&select=*) and optionally project, applying alias matching
   - Confirm the target with the user before proceeding

3. **Ask for note details** in one message:
   - "What would you like to note?" (the note content)
   - "What type of note is this?" — offer: Team Meeting Update / Sentiment / Challenge / Risk / Milestone / General
   - "What's the source?" — offer: Manual (you're typing it now) / Team Meeting

4. **Build the note object:**
   ```json
   {
     "id": "[generate uuid]",
     "parent_type": "[client or project]",
     "parent_id": "[resolved id]",
     "content": "[note content]",
     "source": "[manual or team_meeting]",
     "gong_call_id": null,
     "gong_timestamp_seconds": 0,
     "gong_recording_link": null,
     "advisor_id": null,
     "created_at": "[current ISO datetime]",
     "tags": ["[selected type tag]"]
   }
   ```

5. **Insert the note** via Bash:
   ```
   POST /rest/v1/advisor_call_summaries
   Headers: apikey, Authorization Bearer, Content-Type: application/json, Prefer: return=representation
   Body: [note object as JSON]
   ```

6. **Confirm:** "Note added to [target name]. Would you like to open the [client/project] dashboard to see it?"
