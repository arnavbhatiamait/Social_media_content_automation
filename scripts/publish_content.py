"""
scripts/publish_content.py
---------------------------
Full pipeline script: upload a video/image to GCP, YouTube, and Instagram.

Usage examples
--------------
# Upload a reel/short to all platforms:
  python scripts/publish_content.py --type reel --file "Recording 2026-06-11 165341.mp4" --title "My Reel" --caption "Check this out! #shorts #ai"

# Upload an image post to GCP + Instagram only:
  python scripts/publish_content.py --type image --file "person Output.jpg" --caption "AI generated art 🎨" --skip-yt

# Upload to YouTube only (no GCP, no Insta):
  python scripts/publish_content.py --type reel --file video.mp4 --title "My Short" --caption "desc" --skip-gcp --skip-insta

Flags
-----
  --type        reel | image          (required)
  --file        local file path       (required)
  --title       YouTube video title   (required for reel, ignored for image)
  --caption     Instagram caption / YT description
  --tags        comma-separated tags  (default: AI,Shorts,Reels)
  --thumbnail   local path to thumbnail image (optional, reel only)
  --skip-gcp    skip GCP upload
  --skip-yt     skip YouTube upload
  --skip-insta  skip Instagram upload
"""

import argparse
import io
import logging
import os
import sys
import time

# Force UTF-8 on Windows so Unicode symbols don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ------------------------------------------------------------------ #
#  Project root on sys.path
# ------------------------------------------------------------------ #

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# ------------------------------------------------------------------ #
#  Logger — file + console
# ------------------------------------------------------------------ #

from logs_setup.logger import Logger

_base = Logger(
    name="PublishContent",
    log_file="logs/publish_content.log",
).get_logger()


def _add_console(log: logging.Logger) -> logging.Logger:
    # RotatingFileHandler is a subclass of StreamHandler, so we check type exactly
    has_console = any(type(h) is logging.StreamHandler for h in log.handlers)
    if not has_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
        )
        log.addHandler(ch)
    return log


logger = _add_console(_base)


# ================================================================== #
#  Individual platform steps
# ================================================================== #

def step_gcp(local_path: str, content_type: str) -> dict | None:
    """Upload file to GCP bucket. Returns result dict or None on failure."""
    logger.info(f"[GCP] Uploading '{os.path.basename(local_path)}' …")
    t0 = time.monotonic()
    try:
        from gcp_upload.gcp_bucket_upload import GCPBucketUpload
        gcp = GCPBucketUpload()

        folder = "videos" if content_type == "reel" else "images"
        blob_name = f"{folder}/{os.path.basename(local_path)}"

        result = gcp.upload_file(
            local_file_path=local_path,
            destination_blob_name=blob_name,
            make_public=False,          # bucket has public-access-prevention enforced
        )
        elapsed = time.monotonic() - t0
        logger.info(
            f"[GCP] OK Done in {elapsed:.1f}s  ->  {result['gs_url']}"
        )
        return result

    except Exception as exc:
        elapsed = time.monotonic() - t0
        logger.exception(f"[GCP] ✗ FAILED after {elapsed:.1f}s: {exc}")
        return None


def step_youtube_reel(
    local_path: str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: str | None,
) -> str | None:
    """Upload a Short to YouTube. Returns video_id or None on failure."""
    logger.info(f"[YT] Uploading Short: '{title}' …")
    t0 = time.monotonic()
    try:
        from yt_uploader.Youtube import YoutubeUploader
        yt = YoutubeUploader()

        video_id = yt.upload_short(
            video_path=local_path,
            title=title,
            description=description,
            tags=tags,
        )
        elapsed = time.monotonic() - t0
        logger.info(
            f"[YT] OK Done in {elapsed:.1f}s  ->  https://youtu.be/{video_id}"
        )

        if thumbnail_path and os.path.exists(thumbnail_path):
            logger.info(f"[YT] Uploading thumbnail …")
            yt.upload_thumbnail(video_id, thumbnail_path)
            logger.info("[YT] Thumbnail uploaded.")

        return video_id

    except Exception as exc:
        elapsed = time.monotonic() - t0
        logger.exception(f"[YT] ✗ FAILED after {elapsed:.1f}s: {exc}")
        return None


def step_instagram_reel(video_url: str, caption: str) -> dict | None:
    """
    Post a reel to Instagram.
    video_url must be a publicly accessible URL (e.g. signed GCP URL or CDN link).
    """
    logger.info(f"[INSTA] Publishing reel …")
    t0 = time.monotonic()
    try:
        from insta_configuration.insta_setup import InstaSetup
        insta = InstaSetup()
        result = insta.publish_reel(video_url=video_url, caption=caption)
        elapsed = time.monotonic() - t0
        logger.info(f"[INSTA] ✓ Reel published in {elapsed:.1f}s  →  {result}")
        return result

    except Exception as exc:
        elapsed = time.monotonic() - t0
        logger.exception(f"[INSTA] ✗ FAILED after {elapsed:.1f}s: {exc}")
        return None


def step_instagram_image(image_url: str, caption: str) -> dict | None:
    """
    Post an image to Instagram.
    image_url must be a publicly accessible URL.
    """
    logger.info(f"[INSTA] Publishing image post …")
    t0 = time.monotonic()
    try:
        from insta_configuration.insta_setup import InstaSetup
        insta = InstaSetup()
        result = insta.publish_image(image_url=image_url, caption=caption)
        elapsed = time.monotonic() - t0
        logger.info(f"[INSTA] ✓ Image published in {elapsed:.1f}s  →  {result}")
        return result

    except Exception as exc:
        elapsed = time.monotonic() - t0
        logger.exception(f"[INSTA] ✗ FAILED after {elapsed:.1f}s: {exc}")
        return None


def _get_signed_url(blob_name: str) -> str | None:
    """Return a short-lived signed URL for a GCP blob (needed for Instagram)."""
    try:
        from gcp_upload.gcp_bucket_upload import GCPBucketUpload
        gcp = GCPBucketUpload()
        url = gcp.get_signed_url(blob_name, expiration_time=3600)
        logger.info(f"[GCP] Signed URL generated for '{blob_name}'")
        return url
    except Exception as exc:
        logger.exception(f"[GCP] Failed to get signed URL: {exc}")
        return None


# ================================================================== #
#  Orchestrator
# ================================================================== #

def run(args: argparse.Namespace) -> None:
    logger.info("=" * 60)
    logger.info(f"Publish Pipeline — type={args.type}  file={args.file}")
    logger.info(
        f"Targets -> GCP:{not args.skip_gcp}  "
        f"YouTube:{not args.skip_yt}  "
        f"Instagram:{not args.skip_insta}"
    )
    logger.info("=" * 60)

    # Resolve absolute file path
    local_path = args.file
    if not os.path.isabs(local_path):
        local_path = os.path.join(PROJECT_ROOT, local_path)

    if not os.path.exists(local_path):
        logger.error(f"File not found: {local_path}")
        sys.exit(1)

    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    logger.info(f"File: {local_path}  ({size_mb:.2f} MB)")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    gcp_result = None
    signed_url = None

    # ── Step 1: GCP ──────────────────────────────────────────────── #
    if not args.skip_gcp:
        gcp_result = step_gcp(local_path, args.type)
        if gcp_result and not args.skip_insta:
            # Generate signed URL so Instagram can fetch the media
            signed_url = _get_signed_url(gcp_result["blob_name"])
    else:
        logger.info("[GCP] Skipped.")

    # ── Step 2: YouTube ──────────────────────────────────────────── #
    yt_video_id = None
    if not args.skip_yt:
        if args.type == "reel":
            thumbnail = args.thumbnail
            if thumbnail and not os.path.isabs(thumbnail):
                thumbnail = os.path.join(PROJECT_ROOT, thumbnail)

            yt_video_id = step_youtube_reel(
                local_path=local_path,
                title=args.title or os.path.basename(local_path),
                description=args.caption,
                tags=tags,
                thumbnail_path=thumbnail,
            )
        else:
            logger.info("[YT] Skipping — image posts are not supported on YouTube.")
    else:
        logger.info("[YT] Skipped.")

    # ── Step 3: Instagram ────────────────────────────────────────── #
    insta_result = None
    if not args.skip_insta:
        if signed_url is None:
            logger.warning(
                "[INSTA] No signed URL available. "
                "Instagram requires a publicly accessible URL. "
                "Re-run with --skip-gcp=False or provide a URL manually."
            )
        else:
            if args.type == "reel":
                insta_result = step_instagram_reel(
                    video_url=signed_url,
                    caption=args.caption,
                )
            else:
                insta_result = step_instagram_image(
                    image_url=signed_url,
                    caption=args.caption,
                )
    else:
        logger.info("[INSTA] Skipped.")

    # ── Summary ──────────────────────────────────────────────────── #
    gcp_status    = ("OK  " + gcp_result["gs_url"]) if gcp_result else ("--  skipped" if args.skip_gcp else "!!  FAILED")
    yt_skipped    = args.skip_yt or args.type == "image"
    yt_status     = ("OK  https://youtu.be/" + yt_video_id) if yt_video_id else ("--  skipped" if yt_skipped else "!!  FAILED")
    insta_skipped = args.skip_insta or signed_url is None
    insta_status  = ("OK  " + str(insta_result.get("id", insta_result))) if insta_result else ("--  skipped" if insta_skipped else "!!  FAILED")

    sep = "-" * 60
    print(f"\n{sep}")
    print("  PIPELINE RESULTS")
    print(sep)
    print(f"  GCP       {gcp_status}")
    print(f"  YouTube   {yt_status}")
    print(f"  Instagram {insta_status}")
    print(sep)
    print(f"  Log -> logs/publish_content.log\n")

    logger.info(f"GCP: {gcp_status} | YT: {yt_status} | Insta: {insta_status}")


# ================================================================== #
#  CLI
# ================================================================== #

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Upload content to GCP, YouTube, and Instagram."
    )
    p.add_argument("--type",      required=True, choices=["reel", "image"],
                   help="Content type: reel (video) or image")
    p.add_argument("--file",      required=True,
                   help="Local path to the media file")
    p.add_argument("--title",     default="",
                   help="YouTube video title (required for reels)")
    p.add_argument("--caption",   default="",
                   help="Caption / description for all platforms")
    p.add_argument("--tags",      default="AI,Shorts,Reels",
                   help="Comma-separated tags for YouTube")
    p.add_argument("--thumbnail", default=None,
                   help="Local path to thumbnail image (reel only)")
    p.add_argument("--skip-gcp",   action="store_true",
                   help="Skip GCP upload")
    p.add_argument("--skip-yt",    action="store_true",
                   help="Skip YouTube upload")
    p.add_argument("--skip-insta", action="store_true",
                   help="Skip Instagram upload")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
