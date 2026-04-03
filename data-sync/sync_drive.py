"""
sync_drive.py — Google Drive → Supabase sync
=============================================
Reads all client JSON files from the advisor dashboard Drive folder
and upserts the full data model (clients, projects, tasks) into Supabase.

Also reads meta.json to pull the latest MOI scores.

Required environment variables (set as GitHub Secrets):
  SUPABASE_URL              — your project URL
  SUPABASE_SERVICE_KEY      — service role key (not anon!) for write access
  GOOGLE_SERVICE_ACCOUNT_JSON — full contents of service account .json file
  DRIVE_CLIENTS_FOLDER_ID   — Google Drive folder ID containing client .json files
  DRIVE_META_FILE_ID        — Google Drive file ID of meta.json (optional)

Usage:
  python sync_drive.py               # full sync
  python sync_drive.py --dry-run     # print what would be synced, no writes
  python sync_drive.py --moi-only    # only sync MOI scores, skip projects/tasks
"""

import os
import sys
import json
import argparse
import io
from datetime import datetime, timezone

# ── args ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
parser.add_argument("--moi-only", action="store_true", help="Only sync MOI scores")
parser.add_argument("--client", help="Only sync this client slug")
args = parser.parse_args()

DRY_RUN = args.dry_run
MOI_ONLY = args.moi_only
ONLY_CLIENT = args.client

if DRY_RUN:
    print("🔍 DRY RUN — no changes will be written\n")

# ── credentials check ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
GOOGLE_SA_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
DRIVE_CLIENTS_FOLDER_ID = os.environ.get("DRIVE_CLIENTS_FOLDER_ID", "")
DRIVE_META_FILE_ID = os.environ.get("DRIVE_META_FILE_ID", "")

missing = []
if not SUPABASE_URL:        missing.append("SUPABASE_URL")
if not SUPABASE_SERVICE_KEY: missing.append("SUPABASE_SERVICE_KEY")
if not GOOGLE_SA_JSON:      missing.append("GOOGLE_SERVICE_ACCOUNT_JSON")
if not DRIVE_CLIENTS_FOLDER_ID: missing.append("DRIVE_CLIENTS_FOLDER_ID")

if missing and not DRY_RUN:
    print(f"❌ Missing required environment variables: {', '.join(missing)}")
    print("   Set these as GitHub Secrets (Settings → Secrets → Actions)")
    sys.exit(1)
elif missing and DRY_RUN:
    print(f"⚠️  DRY RUN: would need these secrets: {', '.join(missing)}\n")

# ── imports ────────────────────────────────────────────────────────────────────
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
except ImportError:
    print("❌ Missing google-api-python-client. Install with:")
    print("   pip install google-api-python-client google-auth")
    sys.exit(1)

try:
    from supabase import create_client
except ImportError:
    print("❌ Missing supabase. Install with: pip install supabase")
    sys.exit(1)

# ── Google Drive client ────────────────────────────────────────────────────────
def build_drive_client():
    sa_info = json.loads(GOOGLE_SA_JSON)
    creds = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

def download_json_file(drive, file_id: str) -> dict:
    """Download a JSON file from Drive by file ID."""
    request = drive.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buf.seek(0)
    return json.loads(buf.read().decode("utf-8"))

def list_client_files(drive, folder_id: str) -> list[dict]:
    """List all .json files in the clients Drive folder."""
    results = drive.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/json' and trashed=false",
        fields="files(id, name)",
        pageSize=100,
    ).execute()
    return results.get("files", [])

# ── Supabase client ────────────────────────────────────────────────────────────
def build_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ── sync helpers ───────────────────────────────────────────────────────────────
def sync_client(sb, client_data: dict, advisor_map: dict):
    """Upsert one client and all their projects + tasks to Supabase."""
    slug = client_data.get("slug") or client_data.get("id")
    name = client_data.get("name", "Unknown")

    if ONLY_CLIENT and slug != ONLY_CLIENT:
        return

    print(f"  → {name} ({slug})")

    if not DRY_RUN:
        # Upsert client row
        sb.table("clients").upsert({
            "id": slug,
            "name": name,
            # MOI score is synced separately from meta.json
        }, on_conflict="id").execute()

    for project in client_data.get("projects", []):
        p_id = project.get("id")
        p_name = project.get("name", "")
        p_status = project.get("status", "active")
        p_adv_id = project.get("advisor_owner")
        # Resolve UUID → short label (O/M/F)
        p_adv = _resolve_adv(p_adv_id, advisor_map)

        if not DRY_RUN:
            sb.table("projects").upsert({
                "id": p_id,
                "client_id": slug,
                "name": p_name,
                "status": p_status,
                "adv": p_adv,
                "sort_order": 0,
            }, on_conflict="id").execute()

        for i, task in enumerate(project.get("tasks", [])):
            t_id = task.get("id")
            t_title = task.get("title", "")
            t_due = task.get("due_date")
            t_status = task.get("status", "pending")
            t_completed = t_status in ("completed", "cancelled")
            t_adv_id = task.get("advisor_owner")
            t_adv = _resolve_adv(t_adv_id, advisor_map)

            if not DRY_RUN:
                sb.table("tasks").upsert({
                    "id": t_id,
                    "project_id": p_id,
                    "title": t_title,
                    "due_date": t_due,
                    "completed": t_completed,
                    "adv": t_adv,
                    "sort_order": i,
                }, on_conflict="id").execute()

def sync_moi_scores(sb, meta_data: dict):
    """Sync MOI scores from meta.json → clients table."""
    moi_values = meta_data.get("moi_last_values", {})
    print(f"\n📊 Syncing {len(moi_values)} MOI scores...")

    for client_id, moi in moi_values.items():
        score = moi.get("score")
        if score is None:
            continue
        print(f"  → {client_id}: {score}")
        if not DRY_RUN:
            sb.table("clients").update({"moi_score": score}).eq("id", client_id).execute()

def _resolve_adv(adv_uuid: str | None, advisor_map: dict) -> str | None:
    """Map advisor UUID → short label (O, M, F) for the dashboard pill."""
    if not adv_uuid or not advisor_map:
        return None
    adv = advisor_map.get(adv_uuid, {})
    role = adv.get("role", "")
    role_to_label = {"operations": "O", "marketing": "M", "finance": "F"}
    return role_to_label.get(role)

def log_sync(sb, summary: str, client_count: int):
    """Write a sync_log entry."""
    if DRY_RUN:
        return
    sb.table("sync_log").insert({
        "source": "drive",
        "summary": summary,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

# ── main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"🚀 Starting Drive sync — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")

    if DRY_RUN:
        print("📂 Would connect to Google Drive and read client JSON files")
        print("📂 Would read meta.json for MOI scores")
        print("📂 Would upsert all clients, projects, tasks to Supabase")
        return

    drive = build_drive_client()
    sb = build_supabase_client()

    # --- Load setup data to get advisor map ---
    # (If DRIVE_META_FILE_ID is set, also read meta.json for MOI scores)
    advisor_map = {}
    meta_data = {}

    if DRIVE_META_FILE_ID:
        try:
            meta_data = download_json_file(drive, DRIVE_META_FILE_ID)
            print(f"✅ Loaded meta.json")
        except Exception as e:
            print(f"⚠️  Could not load meta.json: {e}")

    if MOI_ONLY:
        if meta_data:
            sync_moi_scores(sb, meta_data)
        else:
            print("❌ --moi-only requires DRIVE_META_FILE_ID to be set")
            sys.exit(1)
        return

    # --- List and sync all client files ---
    print(f"\n📂 Listing client files in folder: {DRIVE_CLIENTS_FOLDER_ID}")
    files = list_client_files(drive, DRIVE_CLIENTS_FOLDER_ID)
    print(f"   Found {len(files)} client files\n")

    synced = 0
    errors = []

    for f in files:
        try:
            client_data = download_json_file(drive, f["id"])
            sync_client(sb, client_data, advisor_map)
            synced += 1
        except Exception as e:
            errors.append(f"{f['name']}: {e}")
            print(f"  ⚠️  Error syncing {f['name']}: {e}")

    # --- MOI scores ---
    if meta_data:
        sync_moi_scores(sb, meta_data)

    # --- Sync log ---
    summary = f"Synced {synced}/{len(files)} clients from Google Drive"
    if errors:
        summary += f" | {len(errors)} errors: {'; '.join(errors[:3])}"
    log_sync(sb, summary, synced)

    print(f"\n✅ {summary}")
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
