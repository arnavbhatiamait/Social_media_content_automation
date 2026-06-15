import argparse
import sys
import os
import time
import io

# Force UTF-8 on Windows so Unicode symbols don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logs_setup.logger import Logger
from gcp_upload.gcp_bucket_upload import GCPBucketUpload
from insta_configuration.insta_setup import InstaSetup

logger = Logger(name="PublishCarousel", log_file="logs/publish_carousel.log").get_logger()

def upload_carousel_pipeline(files: list, caption: str, skip_gcp: bool, skip_insta: bool):
    """
    Uploads multiple images to GCP (to get signed URLs) and then publishes them as a Carousel on Instagram.
    """
    if not files:
        logger.error("No files provided for carousel upload.")
        print("Error: No files provided.")
        sys.exit(1)

    logger.info("--- Starting Carousel Upload Pipeline ---")
    logger.info(f"Files to process: {files}")
    logger.info(f"Caption: {caption}")

    signed_urls = []

    # Step 1: Upload files to GCP Storage (if not skipped)
    if not skip_gcp:
        try:
            logger.info("[GCP] Starting batch upload to bucket...")
            print("[GCP] Uploading images to bucket...")
            gcp = GCPBucketUpload()
            
            # Prepare temporary directory for cropped images
            tmp_carousel_dir = os.path.join(PROJECT_ROOT, "output", "tmp", "carousel_crop")
            os.makedirs(tmp_carousel_dir, exist_ok=True)
            
            for index, file_path in enumerate(files):
                if file_path.startswith("http://") or file_path.startswith("https://"):
                    logger.info(f"[GCP] File {index+1} is already a URL: {file_path}")
                    print(f"[GCP] OK File {index+1} is already a URL: {file_path}")
                    signed_urls.append(file_path)
                    continue

                if not os.path.exists(file_path):
                    logger.error(f"File not found: {file_path}")
                    print(f"Error: File not found: {file_path}")
                    sys.exit(1)

                from PIL import Image
                upload_path = file_path
                with Image.open(file_path) as img:
                    width, height = img.size
                    if width != height:
                        logger.info(f"[GCP] File {index+1} is not square ({width}x{height}). Center-cropping to 1:1 square...")
                        print(f"[GCP] Cropping [{index+1}/{len(files)}]: {os.path.basename(file_path)} to 1:1...")
                        min_dim = min(width, height)
                        left = (width - min_dim) // 2
                        top = (height - min_dim) // 2
                        right = left + min_dim
                        bottom = top + min_dim
                        cropped_img = img.crop((left, top, right, bottom))
                        cropped_path = os.path.join(tmp_carousel_dir, f"crop_{index}_{os.path.basename(file_path)}")
                        cropped_img.save(cropped_path)
                        upload_path = cropped_path

                blob_name = f"images/carousel_{int(time.time())}_{os.path.basename(file_path)}"
                logger.info(f"[GCP] Uploading {upload_path} as {blob_name}...")
                print(f"[GCP] Uploading [{index+1}/{len(files)}]: {os.path.basename(file_path)}...")
                
                gcp_result = gcp.upload_file(local_file_path=upload_path, destination_blob_name=blob_name, make_public=False)
                logger.info(f"[GCP] Upload successful for file {index+1}: {gcp_result['gs_url']}")
                
                signed_url = gcp.get_signed_url(blob_name, expiration_time=3600)
                signed_urls.append(signed_url)
                logger.info(f"[GCP] Generated signed URL for file {index+1}.")
            
            print(f"[GCP] OK All uploads finished. Total URLs: {len(signed_urls)}")
        except Exception as e:
            logger.error(f"[GCP] Upload pipeline failed: {e}")
            print(f"[GCP] ERROR Upload pipeline failed: {e}")
            return
    else:
        logger.info("[GCP] Skipped. Using files as direct URLs.")
        print("[GCP] Skipped. Treating input files directly as URLs.")
        signed_urls = files

    # Step 2: Upload Carousel to Instagram
    if not skip_insta:
        if len(signed_urls) < 2:
            logger.error(f"[INSTA] Instagram carousel requires at least 2 items. Only have {len(signed_urls)} URLs.")
            print(f"[INSTA] ERROR: Instagram carousel requires at least 2 items. Found {len(signed_urls)}.")
            return

        try:
            logger.info("[INSTA] Publishing carousel to Instagram...")
            print("[INSTA] Creating and publishing carousel container (this might take a few moments)...")
            insta = InstaSetup()
            insta_result = insta.publish_carousel(images=signed_urls, caption=caption)
            logger.info(f"[INSTA] Carousel published successfully: {insta_result}")
            print(f"[INSTA] OK Carousel published successfully! Post ID: {insta_result.get('id')}")
        except Exception as e:
            logger.error(f"[INSTA] Publish failed: {e}")
            print(f"[INSTA] ERROR Publish failed: {e}")
            return
    else:
        logger.info("[INSTA] Skipped.")
        print("[INSTA] Skipped.")
        
    logger.info("--- Carousel Upload Pipeline Finished ---")
    print("\nDone! Log saved to logs/publish_carousel.log")

def parse_args():
    parser = argparse.ArgumentParser(description="Upload multiple images to GCP and publish them as an Instagram carousel.")
    parser.add_argument("--files", nargs="+", required=True, help="List of local image files or public image URLs (at least 2).")
    parser.add_argument("--caption", default="", help="Caption for the Instagram carousel post.")
    parser.add_argument("--skip-gcp", action="store_true", help="Skip Google Cloud Storage upload (treat input files directly as public image URLs).")
    parser.add_argument("--skip-insta", action="store_true", help="Skip Instagram publish.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    upload_carousel_pipeline(args.files, args.caption, args.skip_gcp, args.skip_insta)
