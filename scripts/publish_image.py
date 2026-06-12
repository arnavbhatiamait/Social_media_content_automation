import argparse
import sys
import os
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logs_setup.logger import Logger
from gcp_upload.gcp_bucket_upload import GCPBucketUpload
from insta_configuration.insta_setup import InstaSetup

logger = Logger(name="PublishImage", log_file="logs/publish_image.log").get_logger()

def upload_image_pipeline(file_path: str, caption: str, skip_gcp: bool, skip_insta: bool):
    """
    Uploads an image to GCP (to get a signed URL) and then to Instagram.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    logger.info(f"--- Starting Image Upload Pipeline ---")
    logger.info(f"File: {file_path}")
    logger.info(f"Caption: {caption}")

    signed_url = None

    # Step 1: Upload to GCP Storage
    if not skip_gcp:
        try:
            logger.info("[GCP] Uploading image to bucket...")
            print("[GCP] Uploading image to bucket...")
            gcp = GCPBucketUpload()
            blob_name = f"images/{os.path.basename(file_path)}"
            
            gcp_result = gcp.upload_file(local_file_path=file_path, destination_blob_name=blob_name, make_public=False)
            logger.info(f"[GCP] Upload successful: {gcp_result['gs_url']}")
            print(f"[GCP] ✓ Upload successful: {gcp_result['gs_url']}")

            if not skip_insta:
                signed_url = gcp.get_signed_url(blob_name, expiration_time=3600)
                logger.info("[GCP] Generated signed URL for Instagram.")
                
        except Exception as e:
            logger.error(f"[GCP] Upload failed: {e}")
            print(f"[GCP] ✗ Upload failed: {e}")
            return
    else:
        logger.info("[GCP] Skipped.")
        print("[GCP] Skipped.")

    # Step 2: Upload to Instagram
    if not skip_insta:
        if not signed_url:
            logger.error("[INSTA] Missing signed URL. You must upload to GCP first (--skip-gcp=False) to provide a valid URL to Instagram.")
            print("[INSTA] ✗ Failed: Missing signed URL from GCP.")
            return

        try:
            logger.info("[INSTA] Publishing image to Instagram...")
            print("[INSTA] Publishing image to Instagram...")
            insta = InstaSetup()
            insta_result = insta.publish_image(image_url=signed_url, caption=caption)
            logger.info(f"[INSTA] Image published successfully: {insta_result}")
            print(f"[INSTA] ✓ Image published successfully! Post ID: {insta_result.get('id')}")
        except Exception as e:
            logger.error(f"[INSTA] Publish failed: {e}")
            print(f"[INSTA] ✗ Publish failed: {e}")
            return
    else:
        logger.info("[INSTA] Skipped.")
        print("[INSTA] Skipped.")
        
    logger.info("--- Image Upload Pipeline Finished ---")
    print("\nDone! Log saved to logs/publish_image.log")

def parse_args():
    parser = argparse.ArgumentParser(description="Upload an image to GCP and publish it to Instagram.")
    parser.add_argument("--file", required=True, help="Local path to the image file.")
    parser.add_argument("--caption", default="", help="Caption for the Instagram post.")
    parser.add_argument("--skip-gcp", action="store_true", help="Skip Google Cloud Storage upload.")
    parser.add_argument("--skip-insta", action="store_true", help="Skip Instagram publish.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    upload_image_pipeline(args.file, args.caption, args.skip_gcp, args.skip_insta)
