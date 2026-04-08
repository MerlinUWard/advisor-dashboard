---
name: dashboard-context
description: >
  This skill should be used when the user asks to "open the dashboard", "show the team view",
  "open a client", "show client dashboard", "view a project", "what's due this week",
  "show my tasks", "update the dashboard", "add a note", "add a task", or any request
  to view or interact with the Advisor Dashboard. Also loads when running /dashboard,
  /client-view, /project-view, /add-note, or /add-task commands.
version: 0.2.0
---

# Dashboard Context Skill

This skill governs how to read data, render views, and write changes for the Advisor Dashboard.

## Data Architecture

All operational data lives in Supabase. Configuration lives in a local file on disk.

**Supabase tables (source of truth):**
- `clients` — id (slug text), name, moi_score
- `projects` — id (uuid), client_id, name, status, adv ("O"/"M"/"F"), sort_order, next_due_date
- `tasks` — id (uuid), project_id, title, due_date, completed (boolean), adv, sort_order, gong_call_id, gong_recording_link
- `advisor_call_summaries` — client_id, advisor_id, role, call_date, summary, key_topics (jsonb), sentiment, moi_score, call_summary_detail (jsonb), gong_recording_link
- `sync_state` — singleton (id="singleton"): last_gong_sync, last_moi_sync, moi_last_values (jsonb), moi_access_error, flagged_items (jsonb), gong_sync_error, gong_sync_in_progress
- `aliases` — type ("client"/"project"/"advisor"), alias (text), canonical (text)

**Local config (read once per session, never changes after setup):**
- `Dashboard/config/setup.json` — team_name, oa_email, supabase_url, supabase_service_key, moi_sheet_id, moi_sheet_tab, advisors[]

---

## Step 0 — Load Config (Every Operation)

**1. Read local setup.json:**
```
Read: Dashboard/config/setup.json
```

**2. Fetch sync state and aliases from Supabase via Bash:**
```bash
curl -s "{supabase_url}/rest/v1/sync_state?id=eq.singleton&select=*" \
  -H "apikey: {supabase_service_key}" \
  -H "Authorization: Bearer {supabase_service_key}"

curl -s "{supabase_url}/rest/v1/aliases?select=*" \
  -H "apikey: {supabase_service_key}" \
  -H "Authorization: Bearer {supabase_service_key}"
```

Apply all alias corrections before any name matching or display.

**Standard Supabase headers (all requests):**
```
apikey: {supabase_service_key}
Authorization: Bearer {supabase_service_key}
Content-Type: application/json
```

---

## Reading Client Data

**Load a specific client:**
```bash
# Client record
curl -s "{supabase_url}/rest/v1/clients?id=eq.{slug}&select=*" -H ...

# Projects with nested tasks
curl -s "{supabase_url}/rest/v1/projects?client_id=eq.{slug}&select=*,tasks(*)&order=sort_order.asc" -H ...

# Call summaries — all roles, most recent first
curl -s "{supabase_url}/rest/v1/advisor_call_summaries?client_id=eq.{slug}&order=call_date.desc" -H ...
```

**Load all clients (team dashboard):**
```bash
curl -s "{supabase_url}/rest/v1/clients?select=*" -H ...
curl -s "{supabase_url}/rest/v1/projects?select=*,tasks(*)" -H ...
```

Client slug = kebab-case of canonical name (e.g., "Acme Corp" → `acme-corp`).
Always apply aliases before matching user-provided names to slugs.

---

## Writing Data

All writes go directly to Supabase REST. No Drive interaction.

**Upsert a project:**
```bash
curl -s -X POST "{supabase_url}/rest/v1/projects" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '{"id":"[uuid]","client_id":"[slug]","name":"[name]","status":"active","adv":"O","sort_order":0}'
```

**Upsert a task:**
```bash
curl -s -X POST "{supabase_url}/rest/v1/tasks" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '{"id":"[uuid]","project_id":"[uuid]","title":"[title]","due_date":null,"completed":false,"adv":"O","sort_order":0}'
```

**Mark a task complete:**
```bash
curl -s -X PATCH "{supabase_url}/rest/v1/tasks?id=eq.{task_id}" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Add an alias (when user confirms a name correction):**
```bash
curl -s -X POST "{supabase_url}/rest/v1/aliases" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=ignore-duplicates" \
  -d '{"type":"client","alias":"[raw name]","canonical":"[slug]"}'
```

---

## MOI Error State

If `sync_state.moi_access_error` is not null:
- Show red warning banner: "⚠ MOI sheet access error — showing last known values as of [last_moi_sync]"
- Use `sync_state.moi_last_values` for all MOI score displays
- Do not re-read the sheet during dashboard render (only /sync-moi does that)

---

## View Rendering

Read `${CLAUDE_PLUGIN_ROOT}/skills/dashboard-context/references/ui-design.md` before rendering any HTML view. That file is the authoritative visual spec — follow it exactly.

Each view is a self-contained HTML file with all CSS inline. No external CDN dependencies. Data actions are triggered by the user talking to Claude. MOI chart uses inline JS for hover tooltips and click-to-open call summary modals. All JS fully self-contained.

See `references/ui-design.md` for colors, layout, and the MOI chart spec.
See `references/sentiment-scoring.md` for MOI score interpretation.
See `references/data-models.md` for the complete schema reference.

---

## Client Page Section Order

1. **Page header** — client name (h1), breadcrumb ("← Dashboard"), last sync timestamp
2. **MOI Score Charts** — 3-panel row (Operations / Finance / Marketing), 12-week SVG line chart each
3. **Advisor Call Summaries** — 3-panel row
4. **Projects** — one block per project
5. **Manual Notes** — client-level notes
6. **Drive Docs** — linked documents

---

## MOI Chart Rendering Logic

For each advisor role `[operations, finance, marketing]`:

1. Collect entries from `advisor_call_summaries` where `client_id = slug` and `role = [role]`
2. Filter to last 84 days (12 weeks)
3. Sort ascending by `call_date`
4. Filter out entries where `moi_score` is null
5. 0 valid entries → render empty state card (see ui-design.md)
6. ≥1 entry → render SVG chart per ui-design.md:
   - Draw gridlines, polyline, circles
   - `onclick="showCallSummary('[role]', '[call_date]')"` on each circle
   - Hover tooltip handlers
7. Embed full `advisor_call_summaries` array (all entries, not just 12 weeks) as JSON in `<script id="callData-[role]" type="application/json">`
8. Include `showCallSummary()`, `closeCallSummary()`, `showTooltip()`, `hideTooltip()` JS once per page

---

## Fuzzy Name Matching

1. Check `aliases` table first (exact match on alias → use canonical)
2. Normalize both strings (lowercase, remove punctuation, trim)
3. Score similarity (substring containment, word overlap, edit distance)
4. > 85% → match automatically, mention it
5. 60–85% → list top 3 candidates, ask user to confirm
6. < 60% → no match, list all available names

When user confirms a match not in aliases, POST it to Supabase `aliases`.

---

## Adding New Clients

1. Slug = kebab-case of canonical name
2. POST to `clients`: `{"id":"[slug]","name":"[canonical name]"}`
3. Note `moi_row_identifier` (name as in MOI sheet) — store in `sync_state.moi_last_values` keyed by slug as a placeholder entry
4. Ask user if moi_row_identifier differs from canonical name
