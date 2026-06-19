import os
import sys
import uuid
import random
import json
from pathlib import Path
from datetime import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logs_setup.logger import Logger
from insta_configuration.insta_setup import InstaSetup
from schemas_n_db.database import DatabaseOperations
from ImageGeneration.Static_text_img import SocialMediaPostGenerator
from LLM.tools import compile_research
from LLM.llm_post_data import LLMModel

logger = Logger(name="StaticPostPipeline", log_file="logs/static_post_pipeline.log").get_logger()

AI_TOPICS = [
    "Artificial Intelligence",
    "Machine Learning",
    "Large Language Models",
    "Generative AI",
    "AI Agents",
    "Robotics",
    "Computer Vision",
    "MLOps",
    "Open Source AI",
    "AI Infrastructure",
    "AI Safety"
]

POST_TYPES = ["breaking_news", "technical_deep_dive", "thought_leadership"]

class StaticPostPipeline:
    def __init__(self, use_storage: bool = True, use_database: bool = True):
        logger.info(f"Initializing StaticPostPipeline (Storage: {use_storage}, Database: {use_database})")
        self.use_storage = use_storage
        self.use_database = use_database

        self.insta = InstaSetup()

        # Initialize Facebook
        try:
            from Facebook_upload.facebook_config import FacebookPublisher
            fb_page_id = os.getenv("FB_PAGE_ID")
            fb_access_token = os.getenv("FB_ACCESS_TOKEN")
            if fb_page_id and fb_access_token:
                self.facebook = FacebookPublisher(page_id=fb_page_id, access_token=fb_access_token)
            else:
                logger.warning("Facebook credentials not found. facebook=None.")
                self.facebook = None
        except Exception as e:
            logger.error(f"Failed to initialize FacebookPublisher: {e}")
            self.facebook = None

        # Initialize LinkedIn
        try:
            from linkedin.linkedin_setup import LinkedInPublisher
            li_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
            li_org = os.getenv("LINKEDIN_ORGANIZATIONAL_ID")
            if li_token and li_org:
                self.linkedin = LinkedInPublisher(access_token=li_token, organization_id=li_org)
            else:
                logger.warning("LinkedIn credentials not found. linkedin=None.")
                self.linkedin = None
        except Exception as e:
            logger.error(f"Failed to initialize LinkedInPublisher: {e}")
            self.linkedin = None

        # Initialize Database operations
        try:
            self.db = DatabaseOperations()
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseOperations: {e}. Running with database=False.")
            self.use_database = False
            self.db = None

        # Initialize GCS uploader (lazy or direct)
        self.gcp = None
        if self.use_storage:
            try:
                from gcp_upload.gcp_bucket_upload import GCPBucketUpload
                self.gcp = GCPBucketUpload()
            except Exception as e:
                logger.error(f"Failed to initialize GCPBucketUpload: {e}. Running with Storage=False.")
                self.use_storage = False

    def select_topic_and_type(self, override_topic: str = None, override_type: str = None):
        """
        Selects a topic and post category using database-backed rotation.
        """
        # Topic selection
        if override_topic:
            topic = override_topic
        elif self.use_database and self.db:
            try:
                recent_topics = self.db.get_recent_static_topics(limit=5)
                # Filter out recently posted topics to ensure rotation
                available = [t for t in AI_TOPICS if t not in recent_topics]
                if not available:
                    logger.info("All topics have been posted recently. Resetting pool.")
                    available = AI_TOPICS
                topic = random.choice(available)
            except Exception as e:
                logger.error(f"Error querying recent topics: {e}. Choosing random topic.")
                topic = random.choice(AI_TOPICS)
        else:
            topic = random.choice(AI_TOPICS)

        # Type selection
        if override_type:
            post_type = override_type
        else:
            post_type = random.choice(POST_TYPES)

        logger.info(f"Selected Topic: '{topic}' | Post Type: '{post_type}'")
        return topic, post_type

    def create_single_card(self, data: dict, generator: SocialMediaPostGenerator, run_id: str) -> str:
        """
        Generates a single summary post card.
        """
        os.makedirs("images", exist_ok=True)
        out_file = f"images/static_{run_id}.png"
        
        title = data.get("post_title", "AI Update")
        
        # Combine hook, summary, and primary takeaways
        takeaways_str = "\n".join(f"• {t}" for t in data.get("key_takeaways", [])[:3])
        body_text = f"{data.get('hook', '')}\n\n{data.get('summary', '')}\n\nKey Highlights:\n{takeaways_str}"
        
        generator.create_post(title=title, body=body_text, output_file=out_file, use_gradient=True)
        return out_file

    def create_carousel_cards(self, data: dict, generator: SocialMediaPostGenerator, run_id: str) -> list:
        """
        Generates a list of card images for a carousel post.
        """
        os.makedirs("images", exist_ok=True)
        image_files = []
        
        title = data.get("post_title", "AI Update")
        
        # Slide 1: Hook and Summary
        slide1_path = f"images/static_{run_id}_card1.png"
        slide1_body = f"{data.get('hook', '')}\n\n{data.get('summary', '')}"
        generator.create_post(title=title, body=slide1_body, output_file=slide1_path, use_gradient=True)
        image_files.append(slide1_path)

        # Slide 2: Technical Breakdown
        breakdown_list = data.get("technical_breakdown", [])
        if breakdown_list:
            slide2_path = f"images/static_{run_id}_card2.png"
            slide2_body = "Technical Breakdown:\n\n" + "\n\n".join(f"• {t}" for t in breakdown_list[:4])
            generator.create_post(title="Technical Details", body=slide2_body, output_file=slide2_path, use_gradient=True)
            image_files.append(slide2_path)

        # Slide 3: Industry Impact
        impact_list = data.get("industry_impact", [])
        if impact_list:
            slide3_path = f"images/static_{run_id}_card3.png"
            slide3_body = "Industry & Business Impact:\n\n" + "\n\n".join(f"• {t}" for t in impact_list[:4])
            generator.create_post(title="Industry Impact", body=slide3_body, output_file=slide3_path, use_gradient=True)
            image_files.append(slide3_path)

        # Slide 4: Key Takeaways & Question
        takeaway_list = data.get("key_takeaways", [])
        slide4_path = f"images/static_{run_id}_card4.png"
        slide4_body = "Key Takeaways:\n\n" + "\n".join(f"• {t}" for t in takeaway_list[:3])
        if data.get("engagement_question"):
            slide4_body += f"\n\nQuestion:\n{data.get('engagement_question')}"
        generator.create_post(title="Key Takeaways", body=slide4_body, output_file=slide4_path, use_gradient=True)
        image_files.append(slide4_path)

        return image_files

    def upload_images_to_gcs(self, image_paths: list) -> list:
        """
        Uploads a list of local images to GCS and returns their signed URLs.
        """
        gcp_urls = []
        if not self.use_storage or not self.gcp:
            logger.info("Storage is disabled or unavailable. Skipping GCP upload.")
            return gcp_urls

        for path in image_paths:
            try:
                blob_name = f"static_posts/{os.path.basename(path)}"
                logger.info(f"Uploading local file {path} to GCP as {blob_name}")
                self.gcp.upload_file(local_file_path=path, destination_blob_name=blob_name, make_public=False)
                # Generate signed URL
                signed_url = self.gcp.get_signed_url(blob_name=blob_name, expiration_time=86400 * 3) # 3 days expiration
                gcp_urls.append(signed_url)
            except Exception as e:
                logger.error(f"GCP upload failed for {path}: {e}")
                
        return gcp_urls

    def run(self, topic: str = None, post_type: str = None, carousel: bool = False, publish: bool = True) -> bool:
        logger.info("=== Running Static News Posting Pipeline ===")
        run_id = uuid.uuid4().hex[:8]

        # 1. Topic and Type rotation
        selected_topic, selected_type = self.select_topic_and_type(topic, post_type)

        # 2. Research Compiler
        logger.info(f"Searching and compiling news for '{selected_topic}'...")
        research_context = compile_research(selected_topic)

        # 3. LLM Content Generation
        logger.info("Invoking LLM to analyze news and write content...")
        try:
            model = LLMModel(provider="gemini", model_name="gemini-2.5-flash")
            post_data = model.generate_ai_news_post(selected_topic, selected_type, research_context)
            logger.debug(f"LLM Response data: {json.dumps(post_data)}")
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return False

        # 4. Generate PIL Images
        logger.info(f"Generating image cards (Carousel Mode: {carousel})...")
        try:
            generator = SocialMediaPostGenerator(branding="@arnavbhatia")
            if carousel:
                image_files = self.create_carousel_cards(post_data, generator, run_id)
            else:
                image_files = [self.create_single_card(post_data, generator, run_id)]
            logger.info(f"Successfully generated image cards: {image_files}")
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return False

        # 5. GCP Upload
        gcp_urls = self.upload_images_to_gcs(image_files)

        # Caption text for posting
        caption = post_data.get("linkedin_post", "")
        if not caption:
            # Fallback
            caption = f"{post_data.get('post_title')}\n\n{post_data.get('hook')}\n\n{post_data.get('summary')}"
            
        linkedin_success = False
        insta_success = False
        fb_success = False

        if publish:
            # 6. Post to LinkedIn
            if self.linkedin:
                logger.info("Publishing to LinkedIn...")
                try:
                    if len(image_files) > 1:
                        li_res = self.linkedin.create_multi_image_post(caption, image_files)
                    else:
                        li_res = self.linkedin.create_image_post(caption, image_files[0])
                    if li_res:
                        logger.info("Successfully posted to LinkedIn")
                        linkedin_success = True
                except Exception as e:
                    logger.error(f"LinkedIn posting failed: {e}")
            else:
                logger.warning("LinkedIn publisher not initialized. Skipping.")

            # 7. Post to Instagram (requires signed URLs)
            if self.insta and gcp_urls:
                logger.info("Publishing to Instagram...")
                try:
                    if len(gcp_urls) > 1:
                        insta_res = self.insta.publish_carousel(gcp_urls, caption)
                    else:
                        insta_res = self.insta.publish_image(gcp_urls[0], caption)
                    if insta_res and "id" in insta_res:
                        logger.info(f"Successfully posted to Instagram. ID: {insta_res['id']}")
                        insta_success = True
                except Exception as e:
                    logger.error(f"Instagram posting failed: {e}")
            else:
                logger.warning("Instagram publisher or signed URLs unavailable. Skipping.")

            # 8. Post to Facebook (uses local paths)
            if self.facebook:
                logger.info("Publishing to Facebook...")
                try:
                    if len(image_files) > 1:
                        fb_res = self.facebook.post_carousel(image_files, caption)
                    else:
                        fb_res = self.facebook.post_image(image_files[0], caption)
                    if fb_res and "id" in fb_res:
                        logger.info(f"Successfully posted to Facebook. ID: {fb_res['id']}")
                        fb_success = True
                except Exception as e:
                    logger.error(f"Facebook posting failed: {e}")
            else:
                logger.warning("Facebook publisher not initialized. Skipping.")

        # 9. Database Logging
        if self.use_database and self.db:
            logger.info("Logging run history to the database...")
            try:
                self.db.save_static_post_history(
                    topic=selected_topic,
                    post_type=selected_type,
                    post_title=post_data.get("post_title", "AI Update"),
                    hook=post_data.get("hook", ""),
                    summary=post_data.get("summary", ""),
                    technical_breakdown=post_data.get("technical_breakdown", []),
                    industry_impact=post_data.get("industry_impact", []),
                    key_takeaways=post_data.get("key_takeaways", []),
                    engagement_question=post_data.get("engagement_question", ""),
                    hashtags=post_data.get("hashtags", []),
                    linkedin_post=caption,
                    local_images=image_files,
                    gcp_urls=gcp_urls,
                    linkedin_posted=linkedin_success,
                    insta_posted=insta_success,
                    fb_posted=fb_success
                )
            except Exception as e:
                logger.error(f"Failed to log history to DB: {e}")

        logger.info(f"Pipeline finished. Success checklist: LinkedIn={linkedin_success}, Instagram={insta_success}, Facebook={fb_success}")
        return True

if __name__ == "__main__":
    # Test execution
    pipeline = StaticPostPipeline(use_storage=True, use_database=True)
    pipeline.run(carousel=True, publish=False)
