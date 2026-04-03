"""
sync_gong.py — Gong → Supabase sync
=====================================
Fetches recent Gong call transcripts, extracts new projects and tasks
mentioned by advisors, and upserts them into Supabase.

NOTE: This script requires a Gong API key. Until one is available,
the Gong sync is handled manually via the advisor-dashboard plugin
(Claude-in-Chrome approach). This script is ready to activate once
Gong API access is provisioned.

Required environment variables (set as GitHub Secrets):
  SUPABASE_URL              — your project URL
  SUPABASE_SERVICE_KEY      — service role key for write access
  GONG_ACCESS_KEY           — Gong API access key
  GONG_ACCESS_SECRET        — Gong API access secret
  DRIVE_CLIENTS_FOLDER_ID   — used to load advisor + client maps from Drive (optional)

Usage:
  python sync_gong.py                        # sync last 7 days of calls
  python sync_gong.py --days 30              # sync last 30 days
  python sync_gong.py --dry-run              # print extracted tasks, no writes
  python sync_gong.py --call-id <id>         # process one specific call
"""

import os
import sys
import json
import argparse
import base64
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# ── args ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--days", type=int, default=7, help="How many days back to look")
parser.add_argument("--call-id", help="Process a single Gong call ID")
args = parser.parse_args()

DRY_RUN = args.dry_run
LOOKBACK_DAYS = args.days
SPECIFIC_CALL = args.call_id

if DRY_RUN:
    print("🔍 DRY RUN — no changes will be written\n")

# ── credentials check ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
GONG_ACCESS_KEY = os.environ.get("GONG_ACCESS_KEY", "")
GONG_ACCESS_SECRET = os.environ.get("GONG_ACCESS_SECRET", "")

missing = []
if not SUPABASE_URL:           missing.append("SUPABASE_URL")
if not SUPABASE_SERVICE_KEY:   missing.append("SUPABASE_SERVICE_KEY")
if not GONG_ACCESS_KEY:        missing.append("GONG_ACCESS_KEY")
if not GONG_ACCESS_SECRET:     missing.append("GONG_ACCESS_SECRET")

if missing:
    if not DRY_RUN:
        print(f"⚠️  Gong sync skipped — missing credentials: {', '.join(missing)}")
        print("   To activate: add these as GitHub Secrets and request a Gong API key")
        print("   Gong API access: https://help.gong.io/hc/en-us/articles/360049248631")
        print("\n   Falling back to manual sync — no changes made.")
        sys.exit(0)  # Exit 0 (not an error) — this is expected until key is provisioned
    else:
        print(f"⚠️  DRY RUN: would need {', '.join(missing)} to run\n")

# ── imports ────────────────────────────────────────────────────────────────────
try:
    from supabase import create_client
except ImportError:
    print("❌ Missing supabase. Install: pip install supabase")
    sys.exit(1)

# ── Gong API client ────────────────────────────────────────────────────────────
GONG_API_BASE = "https://api.gong.io/v2"

def gong_headers() -> dict:
    """Build Basic Auth header for Gong API."""
    token = base64.b64encode(f"{GONG_ACCESS_KEY}:{GONG_ACCESS_SECRET}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }

def gong_get(path: str, params: dict = None) -> dict:
    """Make a GET request to the Gong API."""
    url = f"{GONG_API_BASE}{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url, headers=gong_headers())
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def gong_post(path: str, body: dict) -> dict:
    """Make a POST request to the Gong API."""
    url = f"{GONG_API_BASE}{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=gong_headers(), method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def fetch_recent_calls(days: int) -> list[dict]:
    """Fetch calls from the last N days."""
    from_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    result = gong_post("/calls/extensive", {
        "filter": {
            "fromDateTime": from_date,
            "toDateTime": to_date,
        },
        "contentSelector": {
            "exposedFields": {
                "parties": True,
                "content": {"trackers": True},
            }
        }
    })
    return result.get("calls", [])

def fetch_transcript(call_id: str) -> list[dict]:
    """Fetch the transcript for a single call."""
    result = gong_post("/calls/transcript", {
        "filter": {"callIds": [call_id]}
    })
    transcripts = result.get("callTranscripts", [])
    return transcripts[0].get("transcript", []) if transcripts else []

# ── extraction logic ───────────────────────────────────────────────────────────
# Keyword patterns that suggest a new task or action item was discussed
ACTION_PATTERNS = [
    r"\b(need to|we need to|you need to|going to|will|should)\b.{5,80}",
    r"\b(action item|follow up|follow-up|next step|deliverable|by next week|by end of week)\b",
    r"\b(complete|finish|send|create|build|set up|schedule|review|implement|launch)\b.{5,60}",
]

def extract_tasks_from_transcript(transcript: list[dict], call_meta: dict) -> list[dict]:
    """
    Heuristic extraction: scan transcript sentences for action-oriented language.
    Returns candidate task dicts — these are SUGGESTIONS that need review before upserting.

    NOTE: The advisor-dashboard Gong processor skill (Claude-in-Chrome) does a much
    more sophisticated extraction using Claude AI. This script uses simple regex patterns
    as a fallback for automated nightly runs.
    """
    tasks = []
    patterns = [re.compile(p, re.IGNORECASE) for p in ACTION_PATTERNS]

    for sentence_group in transcript:
        speaker_id = sentence_group.get("speakerId", "")
        sentences = sentence_group.get("sentences", [])

        for sentence in sentences:
            text = sentence.get("text", "").strip()
            if len(text) < 15 or len(text) > 200:
                continue

            if any(p.search(text) for p in patterns):
                tasks.append({
                    "raw_text": text,
                    "speaker_id": speaker_id,
                    "start_time": sentence.get("start", 0),
                    "call_id": call_meta.get("id"),
                    "call_title": call_meta.get("title", ""),
                    "call_date": call_meta.get("started", ""),
                })

    return tasks

def match_client(call_title: str, client_names: list[str]) -> str | None:
    """Try to match a call title to a known client name."""
    title_lower = call_title.lower()
    for name in client_names:
        if name.lower() in title_lower or any(
            word in title_lower for word in name.lower().split() if len(word) > 4
        ):
            return name
    return None

# ── Supabase helpers ───────────────────────────────────────────────────────────
def get_known_call_ids(sb) -> set[str]:
    """Get Gong call IDs already processed (from sync_log)."""
    result = sb.table("sync_log").select("summary").eq("source", "gong").execute()
    ids = set()
    for row in result.data or []:
        # Extract call IDs embedded in summary strings like "call:abc123"
        matches = re.findall(r"call:(\S+)", row.get("summary", ""))
        ids.update(matches)
    return ids

def get_client_names(sb) -> list[str]:
    """Get all client names from Supabase."""
    result = sb.table("clients").select("id,name").execute()
    return [(r["id"], r["name"]) for r in (result.data or [])]

def log_sync(sb, summary: str):
    if DRY_RUN:
        return
    sb.table("sync_log").insert({
        "source": "gong",
        "summary": summary,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

# ── main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"🚀 Starting Gong sync — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Looking back {LOOKBACK_DAYS} days\n")

    if GONG_ACCESS_KEY and not DRY_RUN:
        sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        client_names = get_client_names(sb)
        processed_call_ids = get_known_call_ids(sb)
    else:
        sb = None
        client_names = []
        processed_call_ids = set()

    # --- Fetch calls ---
    if SPECIFIC_CALL:
        calls = [{"id": SPECIFIC_CALL, "title": "Manual call", "started": ""}]
    else:
        print("📞 Fetching recent calls from Gong API...")
        calls = fetch_recent_calls(LOOKBACK_DAYS)
        print(f"   Found {len(calls)} calls")

    new_calls = [c for c in calls if c.get("id") not in processed_call_ids]
    print(f"   {len(new_calls)} new (not yet processed)\n")

    total_tasks = 0
    for call in new_calls:
        call_id = call.get("id")
        call_title = call.get("title", call_id)
        print(f"  📋 Processing: {call_title}")

        # --- Match to client ---
        matched_client = match_client(call_title, [n for _, n in client_names])
        if not matched_client:
            print(f"     ⚠️  Could not match to a client — skipping")
            continue

        print(f"     Client: {matched_client}")

        # --- Fetch transcript ---
        transcript = fetch_transcript(call_id)
        if not transcript:
            print(f"     ⚠️  No transcript available")
            continue

        # --- Extract tasks ---
        candidate_tasks = extract_tasks_from_transcript(transcript, call)
        print(f"     Extracted {len(candidate_tasks)} candidate tasks (regex heuristic)")

        if DRY_RUN:
            for t in candidate_tasks[:3]:
                print(f"       • {t['raw_text'][:80]}...")

        total_tasks += len(candidate_tasks)

        # NOTE: Unlike the Claude-in-Chrome approach which uses AI to intelligently
        # extract and deduplicate tasks, this regex approach generates many false positives.
        # In a production setup, you'd want to either:
        #   a) Use an LLM API call here to process the transcript
        #   b) Queue candidates for manual review before upserting
        #   c) Rely on the Claude-in-Chrome sync for the initial extraction
        #
        # For now, this script logs that the call was processed without upserting tasks.
        if sb and not DRY_RUN:
            log_sync(sb, f"Processed call:{call_id} ({call_title}) — {len(candidate_tasks)} candidates (review needed)")

    print(f"\n✅ Processed {len(new_calls)} calls, {total_tasks} candidate tasks found")
    print("\n💡 NOTE: For full AI-powered extraction, use the advisor-dashboard")
    print("   Gong sync plugin (Claude-in-Chrome) which uses Claude to intelligently")
    print("   extract and classify tasks from transcripts.")
    if not DRY_RUN and sb:
        log_sync(sb, f"Gong sync complete: {len(new_calls)} calls processed")

if __name__ == "__main__":
    main()
