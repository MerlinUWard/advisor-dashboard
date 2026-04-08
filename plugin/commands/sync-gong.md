---
description: Sync new Gong calls and update the dashboard
allowed-tools: "Read, Bash, mcp__Claude_in_Chrome__*"
---

Trigger a Gong transcript sync. Launches the daily-gong-sync agent to process all new calls since the last sync and write directly to Supabase — no Drive interaction.

## Lookback Window

- **Initial sync** (from `/setup` with `initial_sync: true`): all calls from the **last 90 days** (backfill)
- **Ongoing sync**: all calls since `sync_state.last_gong_sync`. Default to 30 days if null.

## Pre-flight Checks

1. Read local `Dashboard/config/setup.json`.

2. GET sync state and aliases from Supabase:
   ```bash
   curl -s "{supabase_url}/rest/v1/sync_state?id=eq.singleton&select=*" \
     -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}"

   curl -s "{supabase_url}/rest/v1/aliases?select=*" \
     -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}"
   ```

3. Check Chrome is available.

4. If called manually (not from `/setup`), confirm with user: "I'm about to sync Gong calls since [last_gong_sync or 'the last 30 days']. This requires an active Gong.io session in your browser. Ready to proceed?"

5. Set `gong_sync_in_progress = true`:
   ```bash
   curl -s -X PATCH "{supabase_url}/rest/v1/sync_state?id=eq.singleton" \
     -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
     -H "Content-Type: application/json" \
     -d '{"gong_sync_in_progress": true}'
   ```

## Launch the Sync Agent

Launch the `daily-gong-sync` agent as a subagent, passing:
- `setup.json` contents (team config, Supabase credentials)
- `sync_state` contents (last_gong_sync timestamp)
- Aliases (from Supabase)
- `lookback_days` (90 for initial, computed days since last_gong_sync for ongoing)

## If Chrome or Gong Is Unavailable

```bash
curl -s -X PATCH "{supabase_url}/rest/v1/sync_state?id=eq.singleton" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -d '{"gong_sync_error":"Chrome unavailable — [ISO datetime]","gong_sync_in_progress":false}'
```

Tell the user: "⚠ Gong sync couldn't run — [reason]. Run /sync-gong manually when ready."

## After the Agent Completes

Present the sync report:

```
✅ Gong Sync Complete
─────────────────────
Calls processed:      [N]
Clients updated:      [N]
Projects created:     [N]
Projects updated:     [N]
Tasks created:        [N]
Tasks updated:        [N]
─────────────────────
⚠ Items needing review: [N]
[List each flagged item]
```

If flagged items exist, ask: "Would you like to review the flagged items now?"

The agent handles updating `sync_state.last_gong_sync` and clearing `gong_sync_in_progress`. No further writes needed here.
