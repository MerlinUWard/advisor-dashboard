---
description: Sync MOI sentiment scores from the Client Performance sheet
allowed-tools: "Read, Bash, mcp__spreadsheet__*"
---

Sync MOI sentiment scores from the Google Sheets Client Performance sheet into Supabase. Runs automatically every Monday, or manually via /sync-moi.

## Instructions

1. **Read local setup.json:**
   ```
   Read: Dashboard/config/setup.json
   ```

2. **Access the MOI sheet** via ~~spreadsheet:
   - Sheet ID: `{setup.moi_sheet_id}`
   - Tab name: `{setup.moi_sheet_tab}`

   **If access fails:**
   ```bash
   curl -s -X PATCH "{supabase_url}/rest/v1/sync_state?id=eq.singleton" \
     -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
     -H "Content-Type: application/json" \
     -d '{"moi_access_error": "[error message] — [ISO datetime]"}'
   ```
   Tell the user: "⚠ Could not access the MOI sheet. Dashboard will show last known MOI values."
   Stop here.

3. **Read the team's tab:**
   - Identify client name column and MOI score/label columns from the header row
   - Fetch all clients from Supabase: `GET /rest/v1/clients?select=id,name`
   - Match each client name against the sheet name column (exact → case-insensitive → fuzzy)
   - If matched: read MOI score and label
   - If not matched: note as unmatched (do not error)

4. **Write MOI values to Supabase:**

   Update `clients.moi_score` for each matched client:
   ```bash
   curl -s -X PATCH "{supabase_url}/rest/v1/clients?id=eq.{slug}" \
     -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
     -H "Content-Type: application/json" \
     -d '{"moi_score": [score]}'
   ```

   Update `sync_state` with full snapshot and clear error:
   ```bash
   curl -s -X PATCH "{supabase_url}/rest/v1/sync_state?id=eq.singleton" \
     -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
     -H "Content-Type: application/json" \
     -d '{
       "last_moi_sync": "[ISO datetime]",
       "moi_access_error": null,
       "moi_last_values": {
         "[client-slug]": {"score": [value], "label": "[label]", "synced_at": "[ISO datetime]"}
       }
     }'
   ```

5. **Report results:**
   ```
   ✅ MOI Sync Complete — [date]
   ─────────────────────────────
   Clients matched:    [N] / [total]
   Clients unmatched:  [N]
   ─────────────────────────────
   ```
   List any unmatched clients and suggest checking their name in the MOI sheet.
