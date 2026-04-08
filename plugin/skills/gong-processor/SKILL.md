---
name: gong-processor
description: >
  This skill should be used when running /sync-gong, processing Gong call transcripts,
  extracting projects and tasks from advisor calls, or when the daily-gong-sync agent
  is operating. Loads automatically during any Gong-related operation.
version: 0.4.0
---

# Gong Processor Skill

Governs how to process advisor call transcripts into structured Supabase data.

**Chrome role:** Pull raw transcript text from Gong only. No writes.
**Claude role:** All analysis, scoring, dedup, and Supabase writes via REST API.

---

## Step 1 — Locate Transcripts (Chrome)

### For Merlin Ward (OPS) — Home page method
1. Navigate to `https://us-63171.app.gong.io/home`
2. Click the "Your meetings" tab — shows Merlin's own recent calls
3. Filter by date to the sync window (since `sync_state.last_gong_sync`)
4. Open each call → Transcript tab → `get_page_text`
5. Record: call date, participants, recording URL

### For other advisors (Mike Jensen / Justin Cook / Quinn Karney) — Participant filter method
1. Navigate to `https://us-63171.app.gong.io/conversations`
2. Focus the participant input via JavaScript (avoids Chrome extension conflicts):
   ```js
   document.getElementById('react-select-2-input').focus()
   ```
3. Type advisor name → wait for autocomplete → select from "People at Cardone Ventures"
4. Apply date filter: from `sync_state.last_gong_sync` to today
5. Open each call → Transcript tab → `get_page_text`
6. Record: call date, participants, recording URL

**Chrome returns raw transcript text + metadata only. All analysis and writes happen in Claude.**

### Local transcript files
Naming: `CLIENTYYMMDD.txt`
- Date: `YYMMDD` → `20YY-MM-DD`
- Client: everything before the 6-digit date
- `gong_call_id` = filename without extension (e.g., `bakker260303`)

---

## Step 2 — Load Aliases + Clients

```bash
curl -s "{supabase_url}/rest/v1/aliases?select=*" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}"

curl -s "{supabase_url}/rest/v1/clients?select=id,name" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}"
```

Apply alias corrections to every client name, advisor name, and project name encountered.

---

## Step 3 — Client Identification

1. Use Gong "Company" field or filename prefix
2. Apply alias corrections from Step 2
3. Fuzzy-match corrected name against all client slugs/names
4. ≥85% → proceed with that client_id
5. 60–84% → flag as `unmatched_client`; do not write; skip call
6. <60% → flag as `unmatched_client`; do not write; skip call

---

## Step 4 — Full Analysis (gong-review framework)

Run all 7 sections for every call. Do not skip or abbreviate.

### 4.1 Sentiment (per speaker)
- **Tone**: positive / neutral / negative / mixed
- **Energy**: engaged / passive / distracted / resistant
- **Key emotional signals** with brief characterization (transcript-grounded)
- Weight client speaker statements more heavily than advisor statements
- Default to "neutral" — never default to "positive" without evidence

### 4.2 Projects Mentioned
For each distinct project: name (client's language), status (NEW / ongoing), short description (NEW only), who mentioned it.

**Strong signals** (create/match): explicit "project" label, named initiative, campaign name, proper noun + action noun.
**Not a project**: one-time tasks, recurring processes, past events.

### 4.3 Tasks Per Project

| Transcript signal | due_date |
|---|---|
| "ASAP" / "right away" / "this week" | call_date + 1 business day |
| "next session" / "next week" / "next call" | call_date + 7 days |
| "end of month" | last day of call's month |
| "next month" | last day of following month |
| "by [weekday]" | next occurrence of that weekday after call date |
| "by [specific date]" | parse exact date |
| No time signal | `null` — renders as red "NO DATE" badge on dashboard |

**High-confidence task patterns:**
- "[Name] is going to / will [verb]..." → task for that advisor
- "We need to [verb]..." → task for call participant advisor
- "I'll [verb]..." → task for speaking advisor
- "Action item:", "Follow up on...", "Send...", "Draft...", "Review..." → tasks

**Do not create tasks for**: completed past actions ("we sent that last week"), hypotheticals ("we could potentially..."), client commitments that are not advisor actions.

### 4.4 MOI Scorecard (8 categories, baseline 4.0, cap 6.9)

Score each with: score (float), rationale (transcript-grounded), deduction_triggers (what cost points).

1. **Strategic Value Delivered** — Did the advisor move meaningful work forward?
2. **Clarity & Communication** — Were action items, timelines, and expectations communicated crisply?
3. **Client Engagement & Buy-In** — Did the client actively engage? Was buy-in secured?
4. **Follow-Up Readiness** — Were specific next steps and owners defined?
5. **Depth vs. Breadth** — Was time spent on high-impact topics vs. scattered across surface issues?
6. **Meaning** — Did the advisor connect the work to the client's larger goals?
7. **Outcome** — Was there a clear outcome or decision from this call?
8. **Impact** — Will this call measurably improve the client's trajectory?

**Overall MOI** = average of 8 scores, rounded to 1 decimal.

Deduction triggers (apply −0.2 to −0.6 per instance):
- Vague action items without owner or date
- Client confusion or unresolved questions
- Advisor talking past client signals
- Missed opportunity to deepen strategic discussion

Excellence signals (apply +0.2 to +0.6 per instance):
- Specific, time-bound commitments secured from client
- Advisor identified a risk or opportunity the client hadn't seen
- Clear energy shift — client went from skeptical to engaged
- Advisor proactively connected dots across multiple projects

### 4.5 Reflection Questions (3 required — transcript evidence mandatory)

1. What was the single most important moment in this call, and why?
2. Where did the advisor create the most value — and where did they leave value on the table?
3. If you could replay one minute of this call differently, what would it be and why?

### 4.6 Strategic Summary
2–3 sentences: call strengths and top improvement opportunities. Factual, no editorializing. Written from the perspective of briefing a team lead who wasn't on the call.

### 4.7 Top 3 Core Values Demonstrated
Choose from: Inspirational, Disciplined, Accountable, Transparent, Aligned, Results-Oriented.
Evidence-based only — cite the transcript moment that demonstrates each value.

---

## Step 5 — Deduplication (REQUIRED before any writes)

### 5.1 Project Dedup

```bash
# Fetch all existing projects for this client
curl -s "{supabase_url}/rest/v1/projects?client_id=eq.{slug}&select=id,name,status" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}"
```

For each extracted project name:
- **≥85% fuzzy match** → use existing project ID → route tasks to **Output 2** (existing project)
- **60–84% fuzzy match** → flag as `ambiguous_project`; still process tasks but add flag note; do not merge
- **<60% match** → create new project → route tasks to **Output 1** (new project)

### 5.2 Task Dedup (per project)

```bash
# Fetch all existing tasks for this project
curl -s "{supabase_url}/rest/v1/tasks?project_id=eq.{pid}&select=id,title,completed&order=created_at.desc" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}"
```

For each extracted task:
- **>85% title similarity with PENDING task** → SKIP creation; PATCH `due_date` only if new date is earlier
- **>85% title similarity with COMPLETED task** → CREATE new (recurring action)
- **No match** → CREATE new task

---

## Step 6 — Build 3 Output Objects

### Output 1 — New Projects + Tasks
Projects from transcript with <60% match to existing (new).

```json
{
  "project": {
    "id": "[new uuid]",
    "client_id": "[slug]",
    "name": "[project name from transcript]",
    "status": "active",
    "adv": "[O/F/M based on advisor role]",
    "sort_order": 0
  },
  "tasks": [
    {
      "id": "[new uuid]",
      "project_id": "[project uuid above]",
      "title": "[task title]",
      "due_date": "YYYY-MM-DD or null",
      "completed": false,
      "adv": "[O/F/M]",
      "sort_order": 0,
      "gong_call_id": "[call id]",
      "gong_recording_link": "[URL or null]"
    }
  ]
}
```

### Output 2 — New Tasks on Existing Projects
Tasks from transcript where project matched ≥85%.

```json
{
  "project_id": "[existing project uuid]",
  "project_name": "[matched project name]",
  "match_confidence": 0.92,
  "tasks": [
    {
      "id": "[new uuid]",
      "project_id": "[existing project uuid]",
      "title": "[task title]",
      "due_date": "YYYY-MM-DD or null",
      "completed": false,
      "adv": "[O/F/M]",
      "sort_order": 0,
      "gong_call_id": "[call id]",
      "gong_recording_link": "[URL or null]"
    }
  ]
}
```

### Output 3 — MOI Call Datapoint (advisor_call_summaries)

Sentiment derived from moi_score: ≥4.0=positive, 3.0–3.9=neutral, 2.0–2.9=cautious, <2.0=negative.

```json
{
  "client_id": "[client-slug]",
  "advisor_id": "[uuid from setup.json advisors[]]",
  "role": "operations",
  "call_date": "YYYY-MM-DD",
  "gong_call_id": "[call id or filename stem]",
  "summary": "[2-4 sentence strategic summary]",
  "key_topics": ["project name 1", "project name 2"],
  "sentiment": "positive",
  "gong_recording_link": "[URL or null]",
  "moi_score": 4.2,
  "call_summary_detail": {
    "moi_scorecard": [
      {
        "category": "Strategic Value Delivered",
        "score": 4.5,
        "rationale": "[transcript-grounded evidence]",
        "deduction_triggers": "[what cost points]"
      },
      {
        "category": "Clarity & Communication",
        "score": 4.2,
        "rationale": "...",
        "deduction_triggers": "..."
      },
      {
        "category": "Client Engagement & Buy-In",
        "score": 4.0,
        "rationale": "...",
        "deduction_triggers": "..."
      },
      {
        "category": "Follow-Up Readiness",
        "score": 4.3,
        "rationale": "...",
        "deduction_triggers": "..."
      },
      {
        "category": "Depth vs. Breadth",
        "score": 4.1,
        "rationale": "...",
        "deduction_triggers": "..."
      },
      {
        "category": "Meaning",
        "score": 4.0,
        "rationale": "...",
        "deduction_triggers": "..."
      },
      {
        "category": "Outcome",
        "score": 4.2,
        "rationale": "...",
        "deduction_triggers": "..."
      },
      {
        "category": "Impact",
        "score": 4.0,
        "rationale": "...",
        "deduction_triggers": "..."
      }
    ],
    "reflection_questions": [
      {
        "question": "What was the single most important moment in this call, and why?",
        "answer": "[specific transcript evidence]"
      },
      {
        "question": "Where did this advisor create the most value — and where did they leave value on the table?",
        "answer": "[specific transcript evidence]"
      },
      {
        "question": "If you could replay one minute of this call differently, what would it be and why?",
        "answer": "[specific transcript evidence]"
      }
    ],
    "strategic_summary": "[2-3 sentences: strengths + improvement opportunities]",
    "core_values": ["Disciplined", "Accountable", "Transparent"]
  }
}
```

---

## Step 7 — Write to Supabase

**Standard headers (all curl calls):**
```
-H "apikey: {supabase_service_key}"
-H "Authorization: Bearer {supabase_service_key}"
-H "Content-Type: application/json"
```

**Insert new projects (Output 1):**
```bash
curl -s -X POST "{supabase_url}/rest/v1/projects" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '{...project row...}'
```

**Insert new tasks (Output 1 + Output 2, after dedup check):**
```bash
curl -s -X POST "{supabase_url}/rest/v1/tasks" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '{...task row...}'
```

**PATCH existing task due_date (dedup: earlier date found):**
```bash
curl -s -X PATCH "{supabase_url}/rest/v1/tasks?id=eq.{task_id}" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -d '{"due_date": "YYYY-MM-DD"}'
```

**Upsert MOI call summary (Output 3, on conflict: gong_call_id → replace):**
```bash
curl -s -X POST "{supabase_url}/rest/v1/advisor_call_summaries" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates" \
  -d '{...call summary row...}'
```

**Recompute next_due_date for each affected project:**
```bash
# Get earliest pending task with a due date
curl -s "{supabase_url}/rest/v1/tasks?project_id=eq.{pid}&completed=eq.false&due_date=not.is.null&order=due_date.asc&limit=1&select=due_date" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}"

# PATCH project
curl -s -X PATCH "{supabase_url}/rest/v1/projects?id=eq.{pid}" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -d '{"next_due_date": "[date]"}'
```

---

## Step 8 — Update sync_state

```bash
curl -s -X PATCH "{supabase_url}/rest/v1/sync_state?id=eq.singleton" \
  -H "apikey: {KEY}" -H "Authorization: Bearer {KEY}" \
  -H "Content-Type: application/json" \
  -d '{"last_gong_sync":"[ISO datetime]","gong_sync_in_progress":false,"gong_sync_error":null}'
```

If flagged items exist: read current `flagged_items` array, append new entries, PATCH back.

---

## Reference Files

- `references/extraction-rules.md` — additional project/task extraction heuristics
- `references/ambiguity-handling.md` — uncertain client/project match handling
- `references/document-linking.md` — finding and linking Drive documents mentioned in calls
