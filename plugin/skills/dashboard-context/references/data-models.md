# Data Models Reference

Complete JSON schema for all dashboard data files.

## meta.json

```json
{
  "version": "0.1.0",
  "team_name": "string",
  "last_gong_sync": "ISO 8601 | null",
  "last_moi_sync": "ISO 8601 | null",
  "moi_sheet_id": "1nuvNBprAgTKCv-2zAakbTMlonYuGaI6-7XqkEIs",
  "moi_sheet_tab": "string — tab name matching team name",
  "moi_last_values": {
    "[client_uuid]": {
      "score": 0.0,
      "label": "string",
      "synced_at": "ISO 8601"
    }
  },
  "moi_access_error": "string | null",
  "flagged_items": [
    {
      "id": "uuid",
      "type": "ambiguous_project | missing_doc | unmatched_client | unmatched_advisor",
      "description": "string",
      "gong_call_id": "string | null",
      "created_at": "ISO 8601",
      "resolved": false
    }
  ],
  "setup_complete": true
}
```

## setup.json

```json
{
  "team_name": "string",
  "oa_email": "string",
  "data_folder_id": "string — Drive folder ID of Dashboard Data folder",
  "clients_folder_id": "string — Drive folder ID of clients/ subfolder",
  "client_drive_root_folder_id": "string — parent Drive folder containing all client folders",
  "advisors": [
    {
      "id": "uuid",
      "name": "string",
      "role": "operations | finance | marketing",
      "gong_identity": "string — full name as in Gong transcripts",
      "email": "string",
      "aliases": ["string"]
    }
  ]
}
```

## clients/[client-slug].json

```json
{
  "id": "uuid",
  "name": "string — canonical client name",
  "slug": "string — kebab-case, matches filename",
  "aliases": ["string"],
  "last_modified": "ISO 8601",
  "google_drive_folder_id": "string",
  "moi_row_identifier": "string — client name as it appears in MOI sheet",
  "projects": [
    {
      "id": "uuid",
      "client_id": "uuid",
      "name": "string",
      "status": "active | on_hold | completed | archived",
      "advisor_owner": "uuid — references setup.json advisors[].id",
      "created_from": "gong | manual",
      "created_at": "ISO 8601",
      "next_due_date": "ISO 8601 | null — computed: earliest pending task due date",
      "tasks": [
        {
          "id": "uuid",
          "project_id": "uuid",
          "title": "string",
          "description": "string | null",
          "status": "pending | in_progress | completed | cancelled",
          "due_date": "ISO 8601 | null",
          "advisor_owner": "uuid",
          "created_from": "gong | manual",
          "gong_call_id": "string | null",
          "gong_timestamp_seconds": 0,
          "gong_recording_link": "string | null",
          "created_at": "ISO 8601",
          "updated_at": "ISO 8601"
        }
      ],
      "notes": [
        {
          "id": "uuid",
          "parent_type": "project",
          "parent_id": "uuid — project id",
          "content": "string",
          "source": "gong | manual | team_meeting",
          "gong_call_id": "string | null",
          "gong_timestamp_seconds": 0,
          "gong_recording_link": "string | null",
          "advisor_id": "uuid | null",
          "created_at": "ISO 8601",
          "tags": ["sentiment | challenge | risk | milestone | general"]
        }
      ],
      "drive_docs": [
        {
          "id": "uuid",
          "name": "string",
          "url": "string",
          "type": "budget | our_dashboard | proposal | report | contract | other",
          "parent_type": "project",
          "parent_id": "uuid",
          "added_by": "gong_auto | manual",
          "added_at": "ISO 8601"
        }
      ],
      "merge_history": [
        {
          "merged_from_id": "uuid",
          "merged_from_name": "string",
          "merged_at": "ISO 8601"
        }
      ]
    }
  ],
  "manual_notes": [
    {
      "id": "uuid",
      "parent_type": "client",
      "parent_id": "uuid — client id",
      "content": "string",
      "source": "manual | team_meeting",
      "gong_call_id": null,
      "gong_timestamp_seconds": 0,
      "gong_recording_link": null,
      "advisor_id": "uuid | null",
      "created_at": "ISO 8601",
      "tags": ["sentiment | challenge | risk | milestone | general"]
    }
  ],
  "advisor_call_summaries": {
    "operations": [
      {
        "advisor_id": "uuid",
        "call_date": "YYYY-MM-DD",
        "gong_call_id": "string — transcript filename without extension (e.g. 'bakker260303')",
        "summary": "string — 2-4 sentence narrative (Strategic Summary from gong-review)",
        "key_topics": ["string — project names mentioned, max 5"],
        "sentiment": "positive | neutral | cautious | negative",
        "gong_recording_link": "string | null",
        "moi_score": "float | null — Overall MOI 1.0–6.9. null for entries created before this feature.",
        "call_summary_detail": {
          "moi_scorecard": [
            {
              "category": "string — one of 8 categories (Strategic Value Delivered / Clarity & Communication / Client Engagement & Buy-In / Follow-Up Readiness / Depth vs. Breadth / Meaning / Outcome / Impact)",
              "score": "float",
              "rationale": "string — evidence from transcript",
              "deduction_triggers": "string | null"
            }
          ],
          "reflection_questions": [
            {
              "question": "string",
              "answer": "string — with transcript evidence"
            }
          ],
          "strategic_summary": "string — 2-3 sentences on strengths and improvement opportunities",
          "core_values": ["string — up to 3 from: Inspirational, Disciplined, Accountable, Transparent, Aligned, Results-Oriented"]
        }
      }
    ],
    "finance": [],
    "marketing": []
  },
  "drive_docs": [
    {
      "id": "uuid",
      "name": "string",
      "url": "string",
      "type": "budget | our_dashboard | proposal | report | contract | other",
      "parent_type": "client",
      "parent_id": "uuid — client id",
      "added_by": "gong_auto | manual",
      "added_at": "ISO 8601"
    }
  ]
}
```

## Computed Fields

These fields are never stored directly — always recomputed on write:

- `project.next_due_date` — min `due_date` among tasks where `status` is `pending` or `in_progress`
- Dashboard "tasks due today" — filter all tasks across all clients where `due_date = today` and `status != completed && != cancelled`
- Dashboard "upcoming 7 days" — filter tasks where `due_date` is between today and today+7

## MOI Sentiment Derivation

`sentiment` in `advisor_call_summaries` entries is always derived from `moi_score`:

| moi_score | sentiment |
|---|---|
| 4.0 – 6.9 | positive |
| 3.0 – 3.9 | neutral |
| 2.0 – 2.9 | cautious |
| 1.0 – 1.9 | negative |
| null | neutral (default) |
