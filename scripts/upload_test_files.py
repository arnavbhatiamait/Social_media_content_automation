"""
scripts/upload_test_files.py
-----------------------------
Uploads the two test assets to GCP Cloud Storage with full logging.

  • person Output.jpg   → images/person_output.jpg
  • Recording 2026-06-11 165341.mp4 → videos/recording_test.mp4

Run from the project root:
    python scripts/upload_test_files.py

Required .env variables:
    USE_CLOUD_SAVE=True
    GCP_BUCKET_NAME=<your-bucket>
    GCP_CREDENTIALS_PATH=<path-to-service-account.json>
"""

import os
import sys
import time
import logging

# ------------------------------------------------------------------ #
#  Add project root to sys.path so imports resolve correctly
# ------------------------------------------------------------------ #

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ------------------------------------------------------------------ #
#  Load .env before anything else
# ------------------------------------------------------------------ #

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# ------------------------------------------------------------------ #
#  Logger — writes to logs/upload_test.log AND stdout
# ------------------------------------------------------------------ #

from logs_setup.logger import Logger

_file_logger = Logger(
    name="UploadTestFiles",
    log_file="logs/upload_test.log",
).get_logger()


def _make_console_logger() -> logging.Logger:
    """Attach a StreamHandler so logs also appear in the terminal."""
    log = logging.getLogger("UploadTestFiles")
    if not any(isinstance(h, logging.StreamHandler) for h in log.handlers):
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.DEBUG)
        console.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
        )
        log.addHandler(console)
    return log


logger = _make_console_logger()

# ------------------------------------------------------------------ #
#  File definitions
# ------------------------------------------------------------------ #

FILES = [
    {
        "label": "Test image",
        "local_path": os.path.join(PROJECT_ROOT, "person Output.jpg"),
        "blob_name": "images/person_output.jpg",
        "make_public": True,
    },
    {
        "label": "Test video",
        "local_path": os.path.join(PROJECT_ROOT, "Recording 2026-06-11 165341.mp4"),
        "blob_name": "videos/recording_test.mp4",
        "make_public": True,
    },
]


# ------------------------------------------------------------------ #
#  Helpers
# ------------------------------------------------------------------ #

def _check_env() -> bool:
    """Validate that all required env variables are present."""
    required = ["GCP_BUCKET_NAME", "GCP_CREDENTIALS_PATH"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        logger.error(
            f"Missing required env variable(s): {', '.join(missing)}. "
            "Add them to your .env file and retry."
        )
        return False

    if os.getenv("USE_CLOUD_SAVE", "").strip().upper() != "TRUE":
        logger.error(
            "USE_CLOUD_SAVE is not set to TRUE in .env. "
            "Set USE_CLOUD_SAVE=True to enable GCP uploads."
        )
        return False

    return True


def _check_files() -> bool:
    """Verify that all local files exist before attempting uploads."""
    ok = True
    for f in FILES:
        if os.path.exists(f["local_path"]):
            size_mb = os.path.getsize(f["local_path"]) / (1024 * 1024)
            logger.info(
                f"  ✓ {f['label']}: {f['local_path']}  ({size_mb:.2f} MB)"
            )
        else:
            logger.error(f"  ✗ {f['label']}: NOT FOUND → {f['local_path']}")
            ok = False
    return ok


# ------------------------------------------------------------------ #
#  Main upload logic
# ------------------------------------------------------------------ #

def upload_files() -> None:
    logger.info("=" * 60)
    logger.info("GCP Upload Script — Test Assets")
    logger.info("=" * 60)

    # 1. Env check
    logger.info("Step 1/3 — Checking environment variables …")
    if not _check_env():
        sys.exit(1)
    logger.info(
        f"  Bucket : {os.getenv('GCP_BUCKET_NAME')}\n"
        f"  Creds  : {os.getenv('GCP_CREDENTIALS_PATH')}"
    )

    # 2. File existence check
    logger.info("Step 2/3 — Verifying local files …")
    if not _check_files():
        sys.exit(1)

    # 3. Upload
    logger.info("Step 3/3 — Uploading files to GCP …")

    from gcp_upload.gcp_bucket_upload import GCPBucketUpload
    try:
        gcp = GCPBucketUpload()
        logger.info("  GCP client initialised successfully.")
    except Exception as exc:
        logger.exception(f"  Failed to initialise GCP client: {exc}")
        sys.exit(1)

    results = []
    for f in FILES:
        logger.info(f"  ▶ Uploading '{f['label']}' …")
        t0 = time.monotonic()
        try:
            result = gcp.upload_file(
                local_file_path=f["local_path"],
                destination_blob_name=f["blob_name"],
                make_public=f["make_public"],
            )
            elapsed = time.monotonic() - t0
            logger.info(
                f"  ✓ Done in {elapsed:.1f}s\n"
                f"     gs_url     : {result['gs_url']}\n"
                f"     public_url : {result['public_url']}\n"
                f"     size       : {result['size_bytes'] / (1024*1024):.2f} MB"
            )
            results.append({"file": f["label"], "success": True, **result})

        except Exception as exc:
            elapsed = time.monotonic() - t0
            logger.exception(
                f"  ✗ FAILED after {elapsed:.1f}s — {f['label']}: {exc}"
            )
            results.append({"file": f["label"], "success": False, "error": str(exc)})

    # 4. Summary
    logger.info("=" * 60)
    logger.info("Upload Summary")
    logger.info("=" * 60)
    for r in results:
        status = "✓ SUCCESS" if r["success"] else "✗ FAILED "
        logger.info(f"  {status}  {r['file']}")
    
    failed = [r for r in results if not r["success"]]
    if failed:
        logger.error(f"{len(failed)} upload(s) failed. Check logs/upload_test.log for details.")
        sys.exit(1)
    else:
        logger.info("All uploads completed successfully.")


if __name__ == "__main__":
    upload_files()
