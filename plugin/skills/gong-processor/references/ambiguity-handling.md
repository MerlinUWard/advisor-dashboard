# Ambiguity Handling Rules

How to handle uncertain matches, missing data, and edge cases during Gong processing.

---

## Confidence Thresholds

| Match Type          | Threshold | Action                                      |
|--------------------|-----------|---------------------------------------------|
| Client name        | >85%      | Auto-match, mention in sync report          |
| Client name        | 60–85%    | Flag as `unmatched_client`, skip call       |
| Client name        | <60%      | Flag as `unmatched_client`, skip call       |
| Project name       | >85%      | Auto-match existing project                 |
| Project name       | 60–85%    | Flag as `ambiguous_project`, still process tasks but don't merge |
| Project name       | <60%      | Create new project                          |
| Advisor name       | >85%      | Auto-match                                  |
| Advisor name       | <85%      | Flag as `unmatched_advisor`, use OA as fallback |

---

## Flagged Item Format

Flagged items are written to `meta.flagged_items`. Each item:

```json
{
  "id": "uuid",
  "type": "ambiguous_project | missing_doc | unmatched_client | unmatched_advisor",
  "description": "human-readable description of what was found and why it's ambiguous",
  "gong_call_id": "string",
  "gong_call_date": "ISO 8601",
  "advisor_name": "string",
  "raw_mention": "exact text from transcript that triggered this",
  "candidates": ["list of possible matches with similarity scores"],
  "created_at": "ISO 8601",
  "resolved": false
}
```

---

## Specific Scenarios

### New Client Mentioned
A call references a company name not in the clients/ folder.
- If it's clearly a new client (the advisor is talking TO them): flag as `unmatched_client` with raw name
- Include the raw company name and a note: "New client? If so, run /setup to add them."
- Do NOT auto-create clients without confirmation

### Project Exists Under Different Name
Transcript says "the rebrand" but existing project is "Q2 Brand Refresh".
- If learn.md already maps this alias: auto-match (no flag)
- If similarity is 60–85%: flag as `ambiguous_project`, display both names, ask: "Is 'the rebrand' the same as 'Q2 Brand Refresh'?"
- If user confirms: add alias to learn.md + merge

### Same Project Mentioned Across Two Clients
Rarely, an advisor may discuss a project that spans clients or mention one client's work on another client's call.
- Do not cross-attribute tasks/notes
- Flag with description: "Project '[name]' mentioned on [Client A] call but name closely matches project under [Client B]. Please review."

### Task Owner Unclear
Transcript: "We need to send the updated contract."
- No clear owner name mentioned
- Assign to the advisor who is the call participant
- Add note in description: "Owner inferred from call participant — please verify"

### Duplicate Task Detection
Before creating a task, check if a similar task already exists in the same project:
- Same or very similar title (>85% similarity)
- Same advisor owner
- Status is pending or in_progress
→ Update the existing task's due date if a newer date was mentioned; do not create duplicate
→ If status is completed: create a new task (it's a recurring action)

### Multiple Projects in One Call
A single call may touch multiple projects. This is normal. Process each project independently. Assign tasks and notes to the specific project they were discussed in context of.

### No Projects Mentioned
Some calls are check-ins with no project-specific content.
- Still generate a call summary
- Still detect any tasks mentioned
- If tasks exist but no project context: create or find a generic "General / Ongoing" project for that client, or ask the OA which project to assign them to (flag)

---

## Post-Sync Review Workflow

After sync completes, present flagged items to the user grouped by type:

1. **Unmatched clients** — "Found [N] calls where I couldn't identify the client. Please confirm:"
   - Show: advisor name, call date, company name from transcript
   - Options: [Match to existing client] [Create new client] [Skip]

2. **Ambiguous projects** — "Found [N] project mentions that might be duplicates:"
   - Show: transcript mention vs. existing project name, client, similarity score
   - Options: [They're the same — merge] [They're different — keep separate] [Skip]

3. **Missing documents** — "Found [N] document references I couldn't locate in Drive:"
   - Show: document type, transcript mention, client
   - Options: [Paste Drive link] [Skip]

4. **Unmatched advisors** — "Found [N] speaker names I couldn't match to an advisor:"
   - Show: name as it appeared in transcript, call date
   - Options: [Match to existing advisor] [Add as alias in learn.md] [Skip]
