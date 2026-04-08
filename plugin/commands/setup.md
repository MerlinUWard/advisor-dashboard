---
description: First-run setup for the Advisor Dashboard (OA only)
allowed-tools: "Read, Write, Bash, mcp__spreadsheet__*"
argument-hint: "[reconfigure]"
---

You are running the Advisor Dashboard first-time setup. This must be completed by the Operations Advisor (OA) who will own this plugin. Walk through each step carefully and confirm before proceeding.

## Step 1 — Confirm OA Identity

Greet the user and explain that this setup creates the local config file and seeds the Supabase database for the whole team. Ask them to confirm they are the Operations Advisor and that they have:
- A Supabase project set up (they'll need the project URL and service role key)
- Google Sheets accessible (for MOI data)
- A Gong.io account

If any of these are missing, explain what they need to set up first and stop.

## Step 2 — Collect Team Information

Ask the following in a single conversational message (do not ask one at a time):

1. **Team name** — What is your team name? (Used to find the correct tab in the MOI sheet)
2. **Supabase project URL** — The URL from your Supabase project settings (e.g. https://xxxxx.supabase.co)
3. **Supabase service role key** — The service role key from Supabase project settings → API
4. **OA details** — Your full name, your email address, and your full name exactly as it appears in Gong call transcripts
5. **Finance Advisor** — Their full name, email address, and full name as it appears in Gong
6. **Marketing Advisor** — Same three fields

Wait for the response. Confirm all values back to the user in a clean summary table before proceeding. Mask the service key (show only first 8 characters + ...).

Ask: "Does this look correct? Type yes to continue or correct any errors."

## Step 3 — MOI Sheet Tab Confirmation

Access the Google Sheets file with ID `1nuvNBprAgTKCv-2zAakbTMlonYuGaI6-7XqkEI4FeIs` via the spreadsheet connector.

List all available tab names from the sheet. Ask the OA: "Which tab corresponds to your team?"

Store the exact tab name they select as `moi_sheet_tab`.

## Step 4 — Write Local Setup File

Write the following to `Dashboard/config/setup.json` (create the config directory if needed):

```json
{
  "team_name": "[collected team name]",
  "oa_email": "[OA email]",
  "supabase_url": "[collected supabase URL]",
  "supabase_service_key": "[collected service key]",
  "moi_sheet_id": "1nuvNBprAgTKCv-2zAakbTMlonYuGaI6-7XqkEI4FeIs",
  "moi_sheet_tab": "[selected tab]",
  "advisors": [
    {
      "id": "[generate uuid]",
      "name": "[OA name]",
      "role": "operations",
      "gong_identity": "[OA Gong name]",
      "email": "[OA email]",
      "aliases": []
    },
    {
      "id": "[generate uuid]",
      "name": "[Finance name]",
      "role": "finance",
      "gong_identity": "[Finance Gong name]",
      "email": "[Finance email]",
      "aliases": []
    },
    {
      "id": "[generate uuid]",
      "name": "[Marketing name]",
      "role": "marketing",
      "gong_identity": "[Marketing Gong name]",
      "email": "[Marketing email]",
      "aliases": []
    }
  ]
}
```

Tell the user: "Config saved locally. This file is never committed to GitHub or shared."

## Step 5 — Seed Supabase

Using the supabase_url and service key collected above, use Bash to check if sync_state row exists and seed it if not:

```bash
# Check if singleton row exists
curl -s "{supabase_url}/rest/v1/sync_state?id=eq.singleton&select=id" \
  -H "apikey: {service_key}" -H "Authorization: Bearer {service_key}"
```

If the response is `[]` (empty), insert the seed row:

```bash
curl -s -X POST "{supabase_url}/rest/v1/sync_state" \
  -H "apikey: {service_key}" -H "Authorization: Bearer {service_key}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"id":"singleton","team_name":"[team name]","last_gong_sync":null,"last_moi_sync":null,"moi_access_error":null,"gong_sync_error":null,"moi_last_values":{}}'
```

Tell the user: "Supabase sync_state seeded."

## Step 6 — Initial MOI Sync

Run the MOI sync automatically as part of setup. Execute the full `/sync-moi` logic now:
- Access the MOI sheet and read the team's tab
- Match clients from Supabase against sheet rows
- Write MOI scores to `clients.moi_score` in Supabase

Tell the user: "📊 Pulling MOI sentiment scores from the Client Performance sheet..."

Report the result inline: "✅ MOI sync complete — [N] clients loaded."

If the MOI sync fails, set moi_access_error in sync_state and continue to Step 7 regardless.

## Step 7 — Initial Gong Sync (Last 90 Days)

Run the Gong sync automatically, with a 90-day lookback window. This is the initial backfill.

Tell the user:
"📞 Starting initial Gong sync — pulling the last 90 days of calls for all advisors. This may take a few minutes..."

Launch the `daily-gong-sync` agent with `initial_sync: true` and `lookback_days: 90`.

## Step 8 — Install Scheduled Tasks

Create two scheduled tasks using the `mcp__scheduled-tasks__create_scheduled_task` tool:

**Task 1 — Weekly MOI Sync:**
- taskId: `[team-name-slug]-moi-sync` (e.g. `disciplined-moi-sync`)
- cronExpression: `30 8 * * 1` (every Monday at 8:30 AM local time)
- description: `Weekly MOI sentiment sync — [Team Name], every Monday 8:30 AM`
- prompt: Full instructions to read Dashboard/config/setup.json, access the MOI sheet tab `[moi_sheet_tab]`, read client sentiment scores, and update Supabase clients table with moi_score values.

**Task 2 — Daily Gong Sync:**
- taskId: `[team-name-slug]-gong-sync` (e.g. `disciplined-gong-sync`)
- cronExpression: `0 9 * * 1-5` (weekdays at 9:00 AM local time)
- description: `Daily Gong transcript sync — [Team Name], weekdays 9:00 AM`
- prompt: Full instructions to read Dashboard/config/setup.json, check Chrome availability, navigate Gong.io, process each advisor's new calls, and write results to Supabase. Include all advisor Gong identities so the task is fully self-contained.

Tell the user: "⏰ Scheduled tasks installed — MOI syncs every Monday at 8:30 AM, Gong syncs weekdays at 9:00 AM."

## Step 9 — Confirm Setup Complete

Tell the user:
"✅ Setup complete! Your Advisor Dashboard is ready.

**Going forward:**
- MOI syncs automatically every Monday morning
- Gong syncs automatically every weekday at 9:00 AM
- Run /sync-gong any time to pull new calls immediately
- Run /dashboard to open your team dashboard"

## If $ARGUMENTS contains "reconfigure"

Skip the Supabase seeding step. Re-collect advisor info and update setup.json only. Do not delete any data from Supabase.
