# data-sync/

Sync scripts that pull data into Supabase from external sources.
Run automatically by GitHub Actions on a nightly schedule, or triggered manually.

## Scripts

| Script | Source | Status |
|--------|--------|--------|
| `sync_drive.py` | Google Drive client JSON files | ✅ Ready — needs credentials |
| `sync_gong.py` | Gong call transcripts | ⏳ Stub — needs Gong API key |

## Required GitHub Secrets

Add these in **Settings → Secrets and variables → Actions**:

### For Drive sync
| Secret | Value |
|--------|-------|
| `SUPABASE_URL` | `https://tmszsjmscxdvtaeztaqh.supabase.co` ✅ already set |
| `SUPABASE_SERVICE_KEY` | Supabase service role key (Settings → API → service_role) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full contents of the service account `.json` file |
| `DRIVE_CLIENTS_FOLDER_ID` | Google Drive folder ID containing `clients/` JSON files |
| `DRIVE_META_FILE_ID` | File ID of `meta.json` (for MOI scores) |

### For Gong sync
| Secret | Value |
|--------|-------|
| `GONG_ACCESS_KEY` | Gong API access key |
| `GONG_ACCESS_SECRET` | Gong API access secret |

## Google Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Enable **Google Drive API**
4. Create a **Service Account** under IAM & Admin
5. Download the service account JSON key
6. Share your advisor dashboard Drive folder with the service account email
7. Paste the full JSON contents as the `GOOGLE_SERVICE_ACCOUNT_JSON` GitHub Secret

## Running Locally

```bash
cd data-sync
pip install -r requirements.txt

# Set env vars
export SUPABASE_URL="https://tmszsjmscxdvtaeztaqh.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
export DRIVE_CLIENTS_FOLDER_ID="your-folder-id"

# Dry run first
python sync_drive.py --dry-run

# Full sync
python sync_drive.py

# MOI scores only
python sync_drive.py --moi-only

# Single client
python sync_drive.py --client bakker-construction
```

## Triggering Manually via GitHub Actions

1. Go to **github.com/MerlinUWard/advisor-dashboard/actions**
2. Click **Nightly Data Sync**
3. Click **Run workflow** → **Run workflow**
