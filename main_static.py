import os
import sys
import argparse
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logs_setup.logger import Logger
from Piepline.staticPostPipeline import StaticPostPipeline

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

logger = Logger(name="MainStaticOrchestrator", log_file="logs/main_static_pipeline.log").get_logger()

def main():
    parser = argparse.ArgumentParser(description="Automated Static Posts Orchestrator")
    parser.add_argument("--topic", help="Override automatic topic selection with a specific topic")
    parser.add_argument("--post-type", choices=["breaking_news", "technical_deep_dive", "thought_leadership"],
                        help="Override automatic post type choice")
    parser.add_argument("--carousel", action="store_true", help="Generate multiple card images and post as a carousel")
    parser.add_argument("--no-publish", action="store_true", help="Dry run: skip social media publishing")
    parser.add_argument("--no-storage", action="store_true", help="Disable GCS storage upload")
    parser.add_argument("--no-db", action="store_true", help="Disable database logging and rotation checks")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Static Post Orchestrator Started")
    logger.info(f"Carousel Mode: {args.carousel} | Dry Run: {args.no_publish}")
    logger.info("=" * 60)

    try:
        pipeline = StaticPostPipeline(
            use_storage=not args.no_storage,
            use_database=not args.no_db
        )
        
        success = pipeline.run(
            topic=args.topic,
            post_type=args.post_type,
            carousel=args.carousel,
            publish=not args.no_publish
        )

        if success:
            logger.info("Pipeline execution completed successfully.")
            print("\nStatic post pipeline execution completed successfully!")
        else:
            logger.error("Pipeline execution finished with errors.")
            print("\nStatic post pipeline execution finished with errors.")

    except Exception as e:
        logger.exception(f"Unhandled exception in orchestrator: {e}")
        print(f"\nPipeline crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
