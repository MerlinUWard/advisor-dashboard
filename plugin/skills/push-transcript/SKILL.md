---
name: push-transcript
description: >
  Submit an advisor call transcript for analysis and push the results directly to the
  Advisor Dashboard in Supabase. Use when a finance or marketing advisor wants to log
  a call. Triggers: "push my transcript", "submit a call", "log my Gong call",
  "analyze and save this call", or when a user provides a .txt transcript file.
version: 1.0.0
---

# Push Transcript Skill

Allows any advisor (finance, marketing, or additional ops advisors) to submit a call transcript for full gong-review analysis and push the result directly to the Supabase Advisor Dashboard — without needing the full plugin installed.

---

## Step 1 — Get the Transcript

Ask the user to provide the transcript in one of two ways:
- **Paste it** directly into the conversation
- **Provide a file path** to a local .txt file (read it with the Read tool)

Also ask (if not obvious from context):
- **Advisor name** — who ran the call (to look up their role and ID)
- **Call date** — if not embedded in the filename or transcript header

---

## Step 2 — Load Config

Read the local setup file:
```
Read: Dashboard/config/setup.json
```

This provides: `supabase_url`, `supabase_service_key`, `advisors[]` (to look up the submitting advisor's ID and role).

Match the provided advisor name to `setup.json.advisors[].name` (fuzzy match allowed).
Record: `advisor_id` (uuid) and `role` ("operations" / "finance" / "marketing").

---

## Step 3 — Identify the Client

1. Parse the client name from the transcript content (look for company mentions in the first few exchanges, or in a header line)
2. Fetch all clients from Supabase:
   ```bash
   curl -s "{supabase_url}/rest/v1/clients?select=id,name" \
     -H "apikey: {supabase_service_key}" \
     -H "Authorization: Bearer {supabase_service_key}"
   ```
3. Also fetch aliases:
   ```bash
   curl -s "{supabase_url}/rest/v1/aliases?select=*" \
     -H "apikey: {supabase_service_key}" \
     -H "Authorization: Bearer {supabase_service_key}"
   ```
4. Fuzzy-match client name against existing slugs:
   - ≥85% → proceed automatically
   - 60–84% → ask user to confirm the client
   - <60% → ask user to specify the client name

---

## Step 4 — Full gong-review Analysis

Run the complete analysis (same as gong-processor Step 4):

- **Sentiment Summary** — per-person tone and energy
- **Projects Mentioned** — name, status (NEW/ongoing), description
- **Tasks Per Project** — with due dates per the due date intuition rules
- **MOI Scorecard** — all 8 categories, Overall MOI (average, 1 decimal)
- **Reflection Questions** — 3 questions with transcript evidence
- **Strategic Summary** — 2–3 sentences
- **Top 3 Core Values** — from CV core values list

---

## Step 5 — Build and Push to Supabase

**Standard headers:**
```
apikey: {supabase_service_key}
Authorization: Bearer {supabase_service_key}
Content-Type: application/json
```

**Upsert call summary** (on conflict: client_id + role + call_date → replace):
```bash
curl -s -X POST "{supabase_url}/rest/v1/advisor_call_summaries" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '{
    "client_id": "[slug]",
    "advisor_id": "[uuid]",
    "role": "[role]",
    "call_date": "YYYY-MM-DD",
    "gong_call_id": "[filename or null]",
    "summary": "...",
    "key_topics": ["..."],
    "sentiment": "positive|neutral|cautious|negative",
    "moi_score": 4.2,
    "call_summary_detail": { ... },
    "gong_recording_link": null
  }'
```

**Upsert projects extracted from the call:**
```bash
curl -s -X POST "{supabase_url}/rest/v1/projects" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '[...project rows...]'
```

**Upsert tasks** (check for existing tasks with same title first):
```bash
curl -s "{supabase_url}/rest/v1/tasks?project_id=eq.{pid}&select=id,title" -H ...
curl -s -X POST "{supabase_url}/rest/v1/tasks" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '[...task rows...]'
```

**Recompute next_due_date for affected projects** (see gong-processor Step 6 for pattern).

---

## Step 6 — Report Results

```
✅ Call logged — [Client Name] / [Role] / [Date]
────────────────────────────────────────────
MOI Score:        [X.X] ([sentiment])
Projects found:   [N]
Tasks created:    [N]
Tasks updated:    [N]
────────────────────────────────────────────
```

Show the MOI scorecard summary and strategic summary inline so the advisor can see what was logged.

---

## Rules

- Never create a new client — if client not found at ≥85% confidence, ask user to specify
- Never delete existing tasks — only add or update
- Tasks with `completed = true` in Supabase are immutable — do not recreate
- If the advisor provides a recording link, store it in `gong_recording_link`
