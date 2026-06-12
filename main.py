import os
import sys
import argparse
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logs_setup.logger import Logger

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

logger = Logger(name="MainOrchestrator", log_file="logs/main_pipeline.log").get_logger()

def main():
    parser = argparse.ArgumentParser(description="Automated Content Posts Orchestrator")
    parser.add_argument("--type", choices=["image", "video","both"], default="both", 
                        help="Pipeline type to execute: 'image' or 'video' (defaults to 'both')")
    parser.add_argument("--prompt", help="Prompt or deity name to generate the asset")
    parser.add_argument("--image", help="Existing image file path or URL (for image pipeline)")
    parser.add_argument("--video", help="Existing video file path (for video pipeline)")
    parser.add_argument("--caption", help="Caption or description for social media posts")
    parser.add_argument("--title", help="Title for YouTube upload (video pipeline only)")
    parser.add_argument("--tags", help="Comma-separated tags for YouTube (video pipeline only)")
    parser.add_argument("--no-storage", action="store_true", help="Disable Google Cloud Storage uploading")
    parser.add_argument("--no-db", action="store_true", help="Disable database logging and operations")
    parser.add_argument("--generator", default="flux", choices=["flux", "imagen"], help="Image generator model to use")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info(f"Main Orchestrator Started — Type: {args.type.upper()}")
    logger.info("=" * 60)
    
    if args.type=="both":
        from Piepline.imagePipeline import ImageUploadPipeline
        logger.info("Initializing Image Upload Pipeline...")
        pipeline = ImageUploadPipeline(
            Storage=not args.no_storage,
            Database=not args.no_db,
            generator_type=args.generator
        )
        success = pipeline.run(
            prompt=args.prompt,
            image_path=args.image,
            caption=args.caption
        )
        from Piepline.VideoPipeline import VideoUploadPipeline
        logger.info("Initializing Video Upload Pipeline...")
        tags_list = [t.strip() for t in args.tags.split(",")] if args.tags else None
        pipeline = VideoUploadPipeline(
            Storage=not args.no_storage,
            Database=not args.no_db
        )
        success = pipeline.run(
            prompt=args.prompt,
            video_path=args.video,
            title=args.title,
            caption=args.caption,
            tags=tags_list
        )



    elif args.type == "image":
        from Piepline.imagePipeline import ImageUploadPipeline
        logger.info("Initializing Image Upload Pipeline...")
        pipeline = ImageUploadPipeline(
            Storage=not args.no_storage,
            Database=not args.no_db,
            generator_type=args.generator
        )
        success = pipeline.run(
            prompt=args.prompt,
            image_path=args.image,
            caption=args.caption
        )
    else:
        from Piepline.VideoPipeline import VideoUploadPipeline
        logger.info("Initializing Video Upload Pipeline...")
        tags_list = [t.strip() for t in args.tags.split(",")] if args.tags else None
        pipeline = VideoUploadPipeline(
            Storage=not args.no_storage,
            Database=not args.no_db
        )
        success = pipeline.run(
            prompt=args.prompt,
            video_path=args.video,
            title=args.title,
            caption=args.caption,
            tags=tags_list
        )

    if success:
        logger.info(f"Pipeline executed successfully for type: {args.type}")
        print(f"\n{args.type.capitalize()} pipeline execution completed successfully!")
    else:
        logger.error(f"Pipeline execution failed for type: {args.type}")
        print(f"\n{args.type.capitalize()} pipeline execution failed or nothing to process.")

if __name__ == "__main__":
    main()
