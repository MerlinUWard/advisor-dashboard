# Connectors

## Architecture

This plugin uses **Supabase as its primary data store**, accessed via direct REST API calls from Claude (using Bash + curl). No cloud-storage connector is required for data operations.

## Required Connectors

| Category | Placeholder | Required | Notes |
|----------|-------------|----------|-------|
| Spreadsheet | `~~spreadsheet` | Yes (OA only) | Google Sheets — reads MOI Client Performance sheet weekly |
| Email | `~~email` | Optional | Gmail — for calendar display on dashboards |
| Calendar | `~~calendar` | Optional | Google Calendar — for upcoming call display |

**Cloud storage (`~~cloud-storage`) is no longer required.** All client data, project data, task data, and sync state live in Supabase and are accessed via REST API. The only local file is `Dashboard/config/setup.json` (read from disk).

**Gong** is accessed via Claude in Chrome (browser automation) — no connector required.

**Supabase** is accessed via REST API using credentials in `Dashboard/config/setup.json` — no connector required.

## Who Connects What

| Connector | Connected by | Notes |
|-----------|-------------|-------|
| `~~spreadsheet` | Operations Advisor during `/setup` | Reads MOI Client Performance sheet |
| `~~email` | Optional — any advisor | Personal inbox display |
| `~~calendar` | Optional — any advisor | Personal calendar display |

## Setup

The Operations Advisor runs `/setup` once. During setup, the plugin will:
1. Create `Dashboard/config/setup.json` locally with Supabase credentials and team config
2. Use `~~spreadsheet` to verify access to the MOI sheet and confirm the team tab
3. Seed the `sync_state` singleton row in Supabase if it doesn't exist

No other advisors need to run setup. The plugin is single-user (Operations Advisor only).
Finance and Marketing advisors use the separate `push-transcript` skill to submit their call analyses directly to Supabase.
