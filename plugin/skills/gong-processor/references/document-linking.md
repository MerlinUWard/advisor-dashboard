# Document Linking Rules

How to find, match, and link Google Drive documents mentioned in Gong transcripts.

---

## Search Strategy

When a document reference is detected in a transcript:

1. **Normalize the reference** using learn.md Document Name Aliases
   - "our sheet" → `our_dashboard`
   - "the budget doc" → `budget`
   - "the dashboard" → `our_dashboard`

2. **Search the client's Google Drive folder** via ~~cloud-storage:
   - List all files in `client.google_drive_folder_id` (recursively, including subfolders)
   - Match file names against the document type and reference phrase

3. **Matching logic:**

   | Reference Type | Search Strategy |
   |---------------|----------------|
   | `budget` | Files containing "budget" in name; prefer spreadsheets |
   | `our_dashboard` | Files containing "dashboard" or "tracker" or matching team name |
   | `proposal` | Files containing "proposal" in name |
   | `report` | Files containing "report" + current month/quarter |
   | `contract` / `sow` | Files containing "contract", "agreement", or "SOW" |
   | Specific file name | Exact or near-exact file name match |

4. **If multiple matches found:** prefer the most recently modified file. Flag if more than 2 candidates exist.

5. **If no match found:**
   - Add to `meta.flagged_items` as `missing_doc`
   - Include: document type, transcript phrase, client name, which project the document was mentioned in
   - The advisor will be prompted after sync to paste the correct Drive link

---

## Drive Doc Object on Creation

When a document is successfully linked, create a `drive_doc` object:

```json
{
  "id": "[generate uuid]",
  "name": "[file name from Drive]",
  "url": "[shareable view link from Drive]",
  "type": "[normalized document type]",
  "parent_type": "project | client",
  "parent_id": "[project or client id]",
  "added_by": "gong_auto",
  "added_at": "[current ISO datetime]"
}
```

Attach to:
- The **project** if the document was mentioned in the context of a specific project
- The **client** (top-level `drive_docs`) if mentioned generally without a specific project context

---

## Manual Link Prompt

When a document cannot be found automatically, after sync is complete present the user with:

```
📎 Missing Document Links ([N] items)

[Client Name] — [Project Name or "General"]
Reference: "the budget doc" (mentioned in [Advisor] call on [date])
→ [ Paste Drive link here ] or [Skip]
```

When a link is pasted:
1. Infer document type from the URL or ask the user to confirm
2. Create the drive_doc object
3. Write back to the client file
4. Mark the flagged item as resolved

---

## Deduplication

Before adding a new drive_doc:
- Check if the same URL already exists in the parent's `drive_docs` array
- If yes: do not add a duplicate; update `added_at` if more recent
- If a different file for the same `type` exists: keep both unless the user explicitly wants to replace
