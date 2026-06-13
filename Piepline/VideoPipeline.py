import os
import sys
import json
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logs_setup.logger import Logger
from gcp_upload.gcp_bucket_upload import GCPBucketUpload
from insta_configuration.insta_setup import InstaSetup
from yt_uploader.Youtube import YoutubeUploader
from schemas_n_db.database import DatabaseOperations
from video_assembler.video_pipeline import VideoPipeline

logger = Logger(name="VideoUploadPipeline", log_file="logs/video_upload_pipeline.log").get_logger()

class VideoUploadPipeline:
    def __init__(self, Storage: bool = True, Database: bool = True):
        """
        Initialize the VideoUploadPipeline wrapper with toggleable storage and database components.
        """
        self.use_storage = Storage
        self.use_database = Database

        logger.info(f"Initializing VideoUploadPipeline (Storage: {Storage}, Database: {Database})")

        self.insta = InstaSetup()
        
        # Instantiate YoutubeUploader
        try:
            self.youtube = YoutubeUploader()
        except Exception as e:
            logger.error(f"Could not initialize YoutubeUploader: {e}")
            self.youtube = None

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

    def get_video_prompt_for_deity(self, deity_name: str) -> str:
        """
        Builds the system prompt for a specific deity name dynamically.
        """
        import random
        from prompts.prompts_video.prompts_video import HINDU_DEITIES, get_prompt
        
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
            system_prompt = get_prompt()
        finally:
            random.choice = old_choice
            
        return system_prompt

    def get_prompt_from_file(self) -> str | None:
        """
        Reads the first unprocessed prompt from video_prompts.txt in the project root,
        marks it as processed, and returns it.
        """
        file_path = os.path.join(PROJECT_ROOT, "video_prompts.txt")
        if not os.path.exists(file_path):
            logger.info(f"No prompts file found at {file_path}")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            chosen_prompt = None
            chosen_index = -1

            for idx, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    chosen_prompt = stripped
                    chosen_index = idx
                    break

            if chosen_prompt:
                # Mark as processed in the file
                lines[chosen_index] = f"# [PROCESSED] {chosen_prompt}\n"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                logger.info(f"Read and marked prompt '{chosen_prompt}' as processed in {file_path}")
                return chosen_prompt
            else:
                logger.info(f"No unprocessed prompts left in {file_path}")
                return None
        except Exception as e:
            logger.error(f"Error reading prompts file: {e}")
            return None

    async def generate_assets_parallel(self, prompts, texts, images_dir, audio_dir):
        """
        Invokes image and audio generators in parallel using a thread executor.
        """
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            logger.info("Starting parallel image and audio generation...")
            img_task = loop.run_in_executor(pool, self._generate_images_sync, prompts, images_dir)
            audio_task = loop.run_in_executor(pool, self._generate_audio_sync, texts, audio_dir)
            
            await asyncio.gather(img_task, audio_task)
            logger.info("Parallel asset generation complete.")

    def _generate_images_sync(self, prompts, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        renamed_paths = []
        use_flux = True
        original_error = None

        try:
            from ImageGeneration.flux import FluxImageGen
            flux_gen = FluxImageGen()
            logger.info(f"Generating {len(prompts)} images using Flux...")
            paths = flux_gen.generate_images_reels(prompts)
            
            for idx, path in enumerate(paths):
                scene_num = idx + 1
                new_path = os.path.join(output_dir, f"scene_{scene_num}.png")
                if os.path.exists(path):
                    if os.path.exists(new_path):
                        os.remove(new_path)
                    os.replace(path, new_path)
                    renamed_paths.append(new_path)
                else:
                    logger.error(f"Image not found at {path}")
            return renamed_paths
        except Exception as e:
            logger.error(f"Flux image generation failed: {e}. Falling back to Free Stable Diffusion XL...")
            original_error = e
            use_flux = False

        if not use_flux:
            use_sdxl = True
            try:
                from huggingface_hub import InferenceClient
                client = InferenceClient(
                    provider="hf-inference",
                    api_key=os.getenv("HF_TOKEN")
                )
                sd_model = "stabilityai/stable-diffusion-xl-base-1.0"
                logger.info(f"Generating {len(prompts)} fallback images using free SDXL model...")
                
                for idx, prompt in enumerate(prompts):
                    scene_num = idx + 1
                    new_path = os.path.join(output_dir, f"scene_{scene_num}.png")
                    
                    image = client.text_to_image(
                        prompt,
                        model=sd_model,
                        width=1024,
                        height=1024
                    )
                    
                    if os.path.exists(new_path):
                        os.remove(new_path)
                    image.save(new_path)
                    renamed_paths.append(new_path)
                    logger.info(f"Saved fallback SDXL image for scene {scene_num} to: {new_path}")
                    
                    if idx < len(prompts) - 1:
                        sleep_time = float(os.getenv("IMAGE_GEN_SLEEP", "5.0"))
                        logger.info(f"Sleeping for {sleep_time} seconds to avoid SDXL rate limits...")
                        time.sleep(sleep_time)
                return renamed_paths
            except Exception as sde:
                logger.error(f"SDXL fallback also failed: {sde}. Falling back to Vertex AI Imagen...")
                use_sdxl = False

            if not use_sdxl:
                try:
                    from ImageGeneration.iamagegen import ImageGen
                    imagen = ImageGen()
                    logger.info(f"Generating {len(prompts)} fallback images using Vertex AI Imagen (iamagegen.py)...")
                    for idx, prompt in enumerate(prompts):
                        scene_num = idx + 1
                        new_path = os.path.join(output_dir, f"scene_{scene_num}.png")
                        
                        saved = imagen.generate_single_image(prompt=prompt, output_path=new_path)
                        if saved and os.path.exists(new_path):
                            renamed_paths.append(new_path)
                            logger.info(f"Saved fallback image for scene {scene_num} to: {new_path}")
                        else:
                            raise RuntimeError(f"Vertex AI Imagen (iamagegen.py) failed to generate/save image for scene {scene_num}")
                        
                        if idx < len(prompts) - 1:
                            sleep_time = float(os.getenv("IMAGE_GEN_SLEEP", "12.0"))
                            logger.info(f"Sleeping for {sleep_time} seconds to avoid Vertex AI Imagen rate limits...")
                            time.sleep(sleep_time)
                    return renamed_paths
                except Exception as fe:
                    logger.error(f"Fallback Imagen generation also failed: {fe}")
                    raise RuntimeError(f"All video image generation attempts failed: {fe}") from original_error

    def _generate_audio_sync(self, texts, output_dir):
        from tts.gtts import GoogleTTS
        tts = GoogleTTS()
        logger.info(f"Generating {len(texts)} audio clips...")
        os.makedirs(output_dir, exist_ok=True)
        
        paths = tts.batch_process(texts, output_dir=output_dir)
        
        renamed_paths = []
        for idx, path in enumerate(paths):
            scene_num = idx + 1
            new_path = os.path.join(output_dir, f"scene_{scene_num}.wav")
            if os.path.exists(path):
                if os.path.exists(new_path):
                    os.remove(new_path)
                os.replace(path, new_path)
                renamed_paths.append(new_path)
            else:
                logger.error(f"Audio not found at {path}")
        return renamed_paths

    def create_video(self, prompt: str = None, output_dir: str = "output") -> tuple[str | None, dict]:
        """
        Orchestrates LLM query, parallel image & audio generation, and video assembly.
        """
        logger.info("Starting Video Creation Flow...")
        try:
            # 1. LLM Generation
            from prompts.prompts_video.prompts_video import get_prompt
            from LLM.model import LLMModel
            
            # Use dynamic deity selection if prompt is specified
            if prompt:
                system_prompt = self.get_video_prompt_for_deity(prompt)
            else:
                system_prompt = get_prompt()
                
            model = LLMModel(system_prompt="You are a helpful assistant.", provider="gemini")
            logger.info("Requesting JSON structure from LLM...")
            response_str = model.response_llm(system_prompt=system_prompt, post=False)
            
            if isinstance(response_str, str):
                data = json.loads(response_str)
            else:
                data = response_str
                
            scenes = data.get("audio_segments", [])
            image_prompts = data.get("image_prompts", [])
            
            if not scenes:
                logger.error("No scenes found in LLM response.")
                return None, {}
                
            texts = [scene.get("text", "") for scene in scenes]
            prompts = [item.get("prompt", "") for item in image_prompts]

            # Match lengths
            if len(prompts) < len(texts):
                logger.warning("Fewer image prompts than audio segments. Padding with defaults.")
                while len(prompts) < len(texts):
                    prompts.append(prompts[-1] if prompts else "A beautiful cinematic scene.")

            images_dir = os.path.abspath(os.path.join(output_dir, "images"))
            audio_dir = os.path.abspath(os.path.join(output_dir, "audio"))
            
            # Parallel generation
            asyncio.run(self.generate_assets_parallel(prompts, texts, images_dir, audio_dir))
            
            # Format and run the video assembler pipeline
            data["scenes"] = scenes
            
            # Assemble video
            pipeline = VideoPipeline(output_dir=os.path.abspath(output_dir))
            final_video = pipeline.run_pipeline(
                data=data,
                images_dir=images_dir,
                audio_dir=audio_dir,
                bgm_path=None
            )
            return final_video, data
            
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            return None, {}

    def upload_video_storage(self, video_path: str) -> dict:
        """
        Uploads a local video file to GCP storage and generates a signed URL.
        """
        if not self.use_storage or not self.storage:
            logger.warning("Storage option is disabled. Skipping GCP upload.")
            return {}

        logger.info(f"Uploading video to storage: {video_path}")
        try:
            blob_name = f"videos/{os.path.basename(video_path)}"
            gcp_result = self.storage.upload_file(
                local_file_path=video_path,
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
            logger.error(f"Failed to upload video to GCP Storage: {e}")
            return {}

    def upload_video_youtube(self, video_path: str, title: str, description: str, tags: list[str]) -> str | None:
        """
        Uploads a video to YouTube.
        """
        if not self.youtube:
            logger.warning("YouTube Uploader is not available. Skipping YouTube upload.")
            return None

        logger.info(f"Uploading Short to YouTube: '{title}'")
        try:
            video_id = self.youtube.upload_short(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags
            )
            return video_id
        except Exception as e:
            logger.error(f"Failed to upload video to YouTube: {e}")
            return None

    def upload_video_insta(self, video_url: str, caption: str) -> dict | None:
        """
        Publishes a video to Instagram Reels.
        """
        if not video_url:
            logger.error("No valid video URL provided for Instagram.")
            return None

        logger.info("Publishing Reel to Instagram...")
        try:
            result = self.insta.publish_reel(video_url=video_url, caption=caption)
            logger.info(f"Instagram publish success. Post ID: {result.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Instagram Reel publishing failed: {e}")
            return None

    def save_metadata(self, db_id: int | None, video_path: str, gcp_url: str | None, 
                      gcp_filename: str | None, signed_url: str | None, 
                      yt_video_id: str | None, insta_post_id: str | None,
                      title: str, description: str, prompt: str, 
                      yt_posted: bool, insta_posted: bool):
        """
        Persists run metadata to the database, updating both queues and execution logs.
        """
        try:
            if db_id is not None:
                self.db.mark_video_generated(db_id)
                if yt_posted:
                    self.db.mark_video_yt_posted(db_id)
                if insta_posted:
                    self.db.mark_video_insta_posted(db_id)

            session = self.db._get_session()
            if session:
                try:
                    from schemas_n_db.schema import Video_God
                    
                    video_record = Video_God(
                        url=video_path,
                        gcp_bucket_url=gcp_url or "",
                        gcp_filename=gcp_filename or "",
                        prompt_used=prompt,
                        model_used="gemini-2.5-flash",
                        insta_url=signed_url or "",
                        yt_url=f"https://youtu.be/{yt_video_id}" if yt_video_id else "",
                        alt_text=title[:255] if title else "",
                        description=description or "",
                        yt_posted=yt_posted,
                        insta_posted=insta_posted
                    )
                    session.add(video_record)
                    session.commit()
                    logger.info("Saved video metadata to Video_God database table.")
                except Exception as db_err:
                    session.rollback()
                    logger.error(f"Failed to record metadata entry in Video_God: {db_err}")
                finally:
                    session.close()
        except Exception as e:
            logger.error(f"Database updates failed: {e}")

    def run_pipeline_for_single_video(self, video_path: str, title: str, caption: str, 
                                      tags: list[str], prompt: str = "", db_id: int = None,
                                      seo_keywords: list[str] = None, hashtags: list[str] = None) -> bool:
        """
        Runs the full video uploading sequence: GCP Storage, YouTube upload, Instagram Reels, and DB updates.
        """
        logger.info(f"Running video publishing sub-pipeline for: {video_path}")
        is_local = not (video_path.startswith("http://") or video_path.startswith("https://"))
        
        gcp_url, gcp_filename, signed_url = None, None, None

        if is_local:
            upload_info = self.upload_video_storage(video_path)
            if upload_info:
                gcp_url = upload_info.get("gs_url")
                gcp_filename = upload_info.get("filename")
                signed_url = upload_info.get("signed_url")
            else:
                logger.warning(f"Could not upload local file '{video_path}' to storage. Instagram requires a public URL.")
        else:
            signed_url = video_path

        # Combine title, description, hashtags, and SEO keywords for uploads
        yt_description = caption or ""
        if hashtags:
            formatted_hash = " ".join([h if h.startswith('#') else f"#{h}" for h in hashtags])
            yt_description += f"\n\n{formatted_hash}"
        if seo_keywords:
            yt_description += f"\n\nKeywords: {', '.join(seo_keywords)}"

        yt_tags = list(tags) if tags else []
        if seo_keywords:
            yt_tags.extend(seo_keywords)
        # Clean up tags (no #, strip)
        yt_tags = [t.replace('#', '').strip() for t in yt_tags if t]
        # Deduplicate
        seen = set()
        yt_tags = [x for x in yt_tags if not (x.lower() in seen or seen.add(x.lower()))]

        insta_caption = ""
        if title:
            insta_caption += f"{title}\n\n"
        insta_caption += f"{caption or ''}"
        if hashtags:
            formatted_hash = " ".join([h if h.startswith('#') else f"#{h}" for h in hashtags])
            insta_caption += f"\n\n{formatted_hash}"

        # Publish to YouTube
        yt_posted = False
        yt_video_id = None
        if is_local:
            yt_video_id = self.upload_video_youtube(video_path, title, yt_description, yt_tags)
            if yt_video_id:
                yt_posted = True
        else:
            logger.warning("YouTube upload requires a local video file. Skipping.")

        # Publish to Instagram Reels
        insta_posted = False
        insta_post_id = None
        if signed_url:
            insta_result = self.upload_video_insta(signed_url, insta_caption)
            if insta_result:
                insta_post_id = insta_result.get("id")
                if insta_post_id:
                    insta_posted = True
                else:
                    logger.error(f"Instagram Reel publication failed: {insta_result}")
        else:
            logger.warning("No signed/public URL available. Skipping Instagram publish.")

        if self.use_database and self.db:
            self.save_metadata(
                db_id=db_id,
                video_path=video_path,
                gcp_url=gcp_url,
                gcp_filename=gcp_filename,
                signed_url=signed_url,
                yt_video_id=yt_video_id,
                insta_post_id=insta_post_id,
                title=title,
                description=caption,
                prompt=prompt,
                yt_posted=yt_posted,
                insta_posted=insta_posted
            )

        return yt_posted or insta_posted

    def process_database_queue(self) -> bool:
        """
        Processes all pending video prompts in the database videos_on_demand table.
        """
        if not self.use_database or not self.db:
            logger.warning("Database option is disabled. Cannot process queue.")
            return False

        pending = self.db.get_pending_videos()
        if not pending:
            logger.info("No pending videos in queue.")
            return True

        logger.info(f"Processing {len(pending)} pending video(s) from database.")
        success_count = 0

        for row in pending:
            try:
                video_path, data = self.create_video(row.prompt)
                if video_path and data:
                    title = data.get("title", "Mahadev Documentary")
                    caption = data.get("description", "")
                    tags = data.get("hashtags", ["AI", "Shorts", "Reels"])
                    seo_keywords = data.get("seo_keywords", [])
                    hashtags = data.get("hashtags", [])
                    
                    if self.run_pipeline_for_single_video(
                        video_path=video_path,
                        title=title,
                        caption=caption,
                        tags=tags,
                        prompt=row.prompt,
                        db_id=row.id,
                        seo_keywords=seo_keywords,
                        hashtags=hashtags
                    ):
                        success_count += 1
            except Exception as e:
                logger.error(f"Error processing row ID {row.id} from queue: {e}")

        return success_count == len(pending)

    def run(self, prompt: str = None, video_path: str = None, title: str = None, 
            caption: str = None, tags: list[str] = None) -> bool:
        """
        Master orchestrator to execute the video generation and publishing pipeline.
        """
        logger.info("=== Starting Video Pipeline Execution ===")

        # Case 1: Existing video path
        if video_path:
            final_title = title if title else os.path.basename(video_path)
            final_caption = caption if caption else "Check this out!"
            final_tags = tags if tags else ["AI", "Shorts"]
            return self.run_pipeline_for_single_video(
                video_path=video_path,
                title=final_title,
                caption=final_caption,
                tags=final_tags,
                prompt=prompt or ""
            )

        # If no prompt is passed, try to get one from video_prompts.txt first
        if not prompt:
            file_prompt = self.get_prompt_from_file()
            if file_prompt:
                prompt = file_prompt
                logger.info(f"Using prompt '{prompt}' from video_prompts.txt file")

        # Case 2: Database Queue Processing (if no specific prompt is passed and DB is enabled)
        if not prompt and self.use_database:
            pending = self.db.get_pending_videos()
            if pending:
                return self.process_database_queue()
            else:
                logger.info("Database queue is empty. Falling back to a random LLM video generation...")

        # Case 3: Prompt-based or random LLM Generation
        try:
            generated_path, data = self.create_video(prompt)
            if generated_path and data:
                final_title = title if title else data.get("title", "Generated Video")
                final_caption = caption if caption else data.get("description", "")
                final_tags = tags if tags else data.get("hashtags", ["AI", "Shorts"])
                seo_keywords = data.get("seo_keywords", [])
                hashtags = data.get("hashtags", [])
                return self.run_pipeline_for_single_video(
                    video_path=generated_path,
                    title=final_title,
                    caption=final_caption,
                    tags=final_tags,
                    prompt=prompt or "",
                    seo_keywords=seo_keywords,
                    hashtags=hashtags
                )
        except Exception as e:
            logger.error(f"Failed to generate/process video: {e}")
            return False

        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Video Upload Pipeline CLI")
    parser.add_argument("--prompt", help="Prompt/deity name to generate a video")
    parser.add_argument("--video", help="Local path to an existing video file")
    parser.add_argument("--title", help="YouTube video title")
    parser.add_argument("--caption", help="Caption / Description for social media")
    parser.add_argument("--tags", help="Comma-separated tags for YouTube")
    parser.add_argument("--no-storage", action="store_true", help="Disable GCP storage upload")
    parser.add_argument("--no-db", action="store_true", help="Disable database logging")
    
    args = parser.parse_args()
    
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
        print("\nVideo pipeline execution completed successfully!")
    else:
        print("\nVideo pipeline execution failed or nothing to process.")
