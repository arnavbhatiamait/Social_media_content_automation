import os
import sys
import json
import uuid
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from insta_configuration.insta_setup import InstaSetup
from logs_setup.logger import Logger
from gcp_upload.gcp_bucket_upload import GCPBucketUpload
from schemas_n_db.database import DatabaseOperations

logger = Logger(name="ImageUploadPipeline", log_file="logs/image_upload_pipeline.log").get_logger()

class ImageUploadPipeline:
    def __init__(self, Storage: bool = True, Database: bool = True, generator_type: str = "flux"):
        """
        Initialize the ImageUploadPipeline with toggleable storage and database components.
        """
        self.use_storage = Storage
        self.use_database = Database
        self.generator_type = generator_type.lower()
        self.generator = None

        logger.info(f"Initializing ImageUploadPipeline (Storage: {Storage}, Database: {Database}, Generator: {self.generator_type})")

        self.insta = InstaSetup()

        # Conditionally initialize GCP bucket storage
        if self.use_storage:
            try:
                self.storage = GCPBucketUpload()
            except Exception as e:
                logger.error(f"Could not initialize GCPBucketUpload: {e}. Running with Storage=False.")
                self.use_storage = False
                self.storage = None
        else:
            self.storage = None

        # Conditionally initialize Database Operations
        if self.use_database:
            try:
                self.db = DatabaseOperations()
            except Exception as e:
                logger.error(f"Could not initialize DatabaseOperations: {e}. Running with Database=False.")
                self.use_database = False
                self.db = None
        else:
            self.db = None

    def get_god_prompt_for_deity(self, deity_name: str = None) -> str:
        """
        Generates the god scene system prompt, optionally overriding the deity choice.
        """
        import random
        from prompts.prompts_posts.god_prompt import HINDU_DEITIES, generate_god_scene_prompt
        
        if not deity_name:
            return generate_god_scene_prompt()

        matched_god = None
        for g in HINDU_DEITIES:
            if deity_name.lower() in g.lower():
                matched_god = g
                break
        
        if not matched_god:
            # If no deity matched, treat deity_name as a custom prompt and return it directly
            return deity_name

        god_name = matched_god
        
        # Monkeypatch random.choice temporarily to force selecting the matched deity
        old_choice = random.choice
        try:
            random.choice = lambda x: god_name if isinstance(x, list) and len(x) > 0 and x[0] in HINDU_DEITIES else old_choice(x)
            system_prompt = generate_god_scene_prompt()
        finally:
            random.choice = old_choice
            
        return system_prompt

    def create_image(self, prompt: str, output_path: str = None) -> str:
        """
        Generate an image from a prompt using Flux, with fallbacks to SDXL and Vertex Imagen.
        """
        logger.info(f"Generating image for prompt: '{prompt}'")
        os.makedirs("images", exist_ok=True)

        if not output_path:
            output_path = f"images/gen_{uuid.uuid4().hex[:8]}.png"

        # Try Flux
        try:
            logger.info("Attempting image generation using Flux...")
            from ImageGeneration.flux import FluxImageGen
            generator = FluxImageGen()
            response = generator.client.text_to_image(
                prompt,
                model=generator.model,
                width=1024,
                height=1024
            )
            response.save(output_path)
            logger.info(f"Saved generated Flux image to: {output_path}")
            return output_path
        except Exception as flux_err:
            logger.error(f"Flux image generation failed: {flux_err}. Trying Free SDXL fallback...")

        # Fallback 1: Free Stable Diffusion XL
        try:
            logger.info("Attempting image generation using Free SDXL...")
            from huggingface_hub import InferenceClient
            client = InferenceClient(
                provider="hf-inference",
                api_key=os.getenv("HF_TOKEN")
            )
            sd_model = "stabilityai/stable-diffusion-xl-base-1.0"
            
            image = client.text_to_image(
                prompt,
                model=sd_model,
                width=1024,
                height=1024
            )
            image.save(output_path)
            logger.info(f"Saved generated SDXL image to: {output_path}")
            return output_path
        except Exception as sdxl_err:
            logger.error(f"SDXL fallback also failed: {sdxl_err}. Trying Vertex AI Imagen fallback...")

        # Fallback 2: Vertex AI Imagen (iamagegen.py)
        try:
            logger.info("Attempting image generation using Vertex AI Imagen (iamagegen.py)...")
            from ImageGeneration.iamagegen import ImageGen
            fallback = ImageGen()
            saved = fallback.generate_single_image(prompt=prompt, output_path=output_path)
            if saved and os.path.exists(output_path):
                logger.info(f"Saved generated Imagen image to: {output_path}")
                return output_path
            else:
                raise RuntimeError("No image returned/saved by Vertex AI model via iamagegen.py.")
        except Exception as imagen_err:
            logger.error(f"All image generation fallbacks failed: {imagen_err}")
            raise RuntimeError(f"All image generation attempts failed: {imagen_err}") from flux_err

    def upload_image_storage(self, image_path: str) -> dict:
        """
        Uploads a local image file to GCP storage and returns the metadata and signed URL.
        """
        if not self.use_storage or not self.storage:
            logger.warning("Storage option is disabled. Skipping GCP upload.")
            return {}

        logger.info(f"Uploading image to storage: {image_path}")
        try:
            blob_name = f"images/{os.path.basename(image_path)}"
            gcp_result = self.storage.upload_file(
                local_file_path=image_path,
                destination_blob_name=blob_name,
                make_public=False
            )
            signed_url = self.storage.get_signed_url(blob_name, expiration_time=3600)
            return {
                "gs_url": gcp_result.get("gs_url"),
                "filename": gcp_result.get("filename"),
                "signed_url": signed_url
            }
        except Exception as e:
            logger.error(f"Failed to upload image to GCP Storage: {e}")
            return {}

    def upload_image_insta(self, image_url: str, caption: str) -> bool:
        """
        Publishes a public URL image directly to Instagram.
        """
        if not image_url:
            logger.error("No valid image URL provided for Instagram.")
            return False

        logger.info("Publishing image post to Instagram...")
        try:
            result = self.insta.publish_image(image_url=image_url, caption=caption)
            post_id = result.get('id') if result else None
            if post_id:
                logger.info(f"Instagram publish success. Post ID: {post_id}")
                return True
            else:
                logger.error(f"Instagram publish failed: {result}")
                return False
        except Exception as e:
            logger.error(f"Instagram publishing failed: {e}")
            return False

    def save_metadata(self, db_id: int | None, image_path: str, gcp_url: str | None, 
                      gcp_filename: str | None, signed_url: str | None, 
                      caption: str, prompt: str, insta_posted: bool):
        """
        Persists run metadata to the database, updating both queues and execution history logs.
        """
        try:
            if db_id is not None:
                self.db.mark_image_generated(db_id)
                if insta_posted:
                    self.db.mark_image_insta_posted(db_id)

            session = self.db._get_session()
            if session:
                try:
                    from schemas_n_db.schema import Images_God
                    model_name = getattr(self.generator or self, 'generator_type', 'unknown')
                    if hasattr(self, 'generator') and self.generator:
                        model_name = getattr(self.generator, 'model', model_name)

                    img_record = Images_God(
                        url=image_path,
                        gcp_bucket_url=gcp_url or "",
                        gcp_filename=gcp_filename or "",
                        prompt_used=prompt,
                        model_used=str(model_name),
                        insta_url=signed_url or "",
                        yt_url="",
                        alt_text=caption[:255] if caption else "",
                        description=caption or "",
                        yt_posted=False,
                        insta_posted=insta_posted,
                        posted=insta_posted
                    )
                    session.add(img_record)
                    session.commit()
                    logger.info("Saved image metadata to Images_God database table.")
                except Exception as db_err:
                    session.rollback()
                    logger.error(f"Failed to record metadata entry in Images_God: {db_err}")
                finally:
                    session.close()
        except Exception as e:
            logger.error(f"Database updates failed: {e}")

    def run_pipeline_for_single_image(self, image_path: str, caption: str, prompt: str = "", db_id: int = None) -> bool:
        """
        Runs the full sequence: uploads local files, publishes to Instagram, and logs to DB.
        """
        logger.info(f"Running sub-pipeline for: {image_path}")
        is_local = not (image_path.startswith("http://") or image_path.startswith("https://"))
        
        gcp_url, gcp_filename, signed_url = None, None, None

        if is_local:
            upload_info = self.upload_image_storage(image_path)
            if upload_info:
                gcp_url = upload_info.get("gs_url")
                gcp_filename = upload_info.get("filename")
                signed_url = upload_info.get("signed_url")
            else:
                logger.warning(f"Could not upload local file '{image_path}' to storage. Instagram requires a public URL.")
                return False
        else:
            signed_url = image_path

        insta_posted = self.upload_image_insta(signed_url, caption)

        if self.use_database and self.db:
            self.save_metadata(db_id, image_path, gcp_url, gcp_filename, signed_url, caption, prompt, insta_posted)

        return insta_posted

    def generate_and_process_llm(self, deity_name: str = None, caption_override: str = None, db_id: int = None) -> bool:
        """
        Queries the LLM using generate_god_scene_prompt (post=True), generates the image,
        uploads it to storage, publishes to Instagram, and registers database values.
        """
        logger.info(f"Querying LLM to generate prompt and caption for deity: {deity_name or 'Random'}")
        try:
            from LLM.model import LLMModel
            
            system_prompt = self.get_god_prompt_for_deity(deity_name)
            model = LLMModel(system_prompt="You are a helpful assistant.", provider="gemini")
            
            logger.info("Invoking LLM response for post (post=True)...")
            response = model.response_llm(system_prompt=system_prompt, post=True)
            
            if isinstance(response, str):
                response_data = json.loads(response)
            else:
                response_data = response

            generated_prompt = response_data.get("prompt")
            generated_caption = caption_override if caption_override else response_data.get("description")
            
            if not generated_prompt:
                logger.error("LLM did not return a valid prompt.")
                return False

            logger.info(f"LLM Generated Prompt: {generated_prompt}")
            logger.info(f"LLM Generated Caption: {generated_caption}")

            # Generate the image using the detailed generated prompt
            generated_file = self.create_image(generated_prompt)
            if not generated_file:
                return False

            # Publish the generated image and save metadata
            return self.run_pipeline_for_single_image(
                image_path=generated_file,
                caption=generated_caption,
                prompt=deity_name or generated_prompt,
                db_id=db_id
            )
        except Exception as e:
            logger.error(f"Failed to generate and process image via LLM: {e}")
            return False

    def process_database_queue(self) -> bool:
        """
        Processes all pending image prompts in the database images_on_demand table.
        """
        if not self.use_database or not self.db:
            logger.warning("Database option is disabled. Cannot process queue.")
            return False

        pending = self.db.get_pending_images()
        if not pending:
            logger.info("No pending images in queue.")
            return True

        logger.info(f"Processing {len(pending)} pending image(s) from database.")
        success_count = 0

        for row in pending:
            try:
                # We use the row.prompt as the guide deity for LLM prompt generation
                if self.generate_and_process_llm(deity_name=row.prompt, db_id=row.id):
                    success_count += 1
            except Exception as e:
                logger.error(f"Error processing row ID {row.id} from queue: {e}")

        return success_count == len(pending)

    def run(self, prompt: str = None, image_path: str = None, caption: str = None) -> bool:
        """
        Master orchestrator to execute the image generation and publishing pipeline.
        """
        logger.info("=== Starting Image Pipeline Execution ===")

        # Case 1: Existing image file path or URL
        if image_path:
            final_caption = caption if caption else "Check this out! #ai #image"
            return self.run_pipeline_for_single_image(image_path, final_caption, prompt or "")

        # Case 2: Database Queue Processing (if no specific prompt is passed and DB is enabled)
        if not prompt and self.use_database:
            pending = self.db.get_pending_images()
            if pending:
                return self.process_database_queue()
            else:
                logger.info("Database queue is empty. Falling back to a random LLM generation...")

        # Case 3: Prompt-based or random LLM Generation
        return self.generate_and_process_llm(deity_name=prompt, caption_override=caption)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Image Upload Pipeline CLI")
    parser.add_argument("--prompt", help="Prompt to generate an image")
    parser.add_argument("--image", help="Local path or URL of an existing image")
    parser.add_argument("--caption", help="Caption for Instagram")
    parser.add_argument("--no-storage", action="store_true", help="Disable GCP storage upload")
    parser.add_argument("--no-db", action="store_true", help="Disable database logging")
    parser.add_argument("--generator", default="flux", choices=["flux", "imagen"], help="Image generator to use")
    
    args = parser.parse_args()
    
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
    
    if success:
        print("\nImage pipeline execution completed successfully!")
    else:
        print("\nImage pipeline execution failed or nothing to process.")