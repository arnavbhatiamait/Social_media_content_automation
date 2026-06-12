import os
import json
import shutil
import subprocess
from logs_setup.logger import Logger
from video_assembler.audio_utils import AudioManager
from video_assembler.scene_creator import SceneCreator
from video_assembler.subtitle_generator import SubtitleGenerator

logger = Logger(name="VideoPipeline", log_file="logs/video_assembler.log").get_logger()

class VideoPipeline:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.tmp_dir = os.path.join(output_dir, "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)

    def concatenate_scenes(self, video_files: list, output_path: str):
        logger.info("Concatenating scenes...")
        list_file = os.path.join(self.tmp_dir, "video_list.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for vf in video_files:
                # ffmpeg requires forward slashes or escaped backslashes and absolute path works best
                safe_path = os.path.abspath(vf).replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Concatenated scenes into {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed while concatenating scenes: {e}")
            raise

    def add_intro_title(self, video_path: str, title: str, output_path: str):
        logger.info(f"Adding intro title '{title}' to {video_path}")
        # Drawtext filter needs escaped single quotes and colons
        safe_title = title.replace("'", "\\'").replace(":", "\\:")
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", f"drawtext=text='{safe_title}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,3)'",
            "-c:a", "copy",
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Intro title added.")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed to add intro title: {e}")
            raise

    def generate_thumbnail(self, image_path: str, output_path: str):
        logger.info(f"Generating thumbnail from {image_path}")
        shutil.copy2(image_path, output_path)

    def run_pipeline(self, data: dict, images_dir: str, audio_dir: str, bgm_path: str = None) -> str:
        logger.info("================================================")
        logger.info("Starting Video Assembly Pipeline...")
        logger.info(f"Output directory set to: {self.output_dir}")
        logger.info("================================================")
        scene_files = []
        scenes = data.get("scenes", [])
        
        for idx, scene in enumerate(scenes):
            scene_num = idx + 1
            logger.info(f"--- Processing Scene {scene_num}/{len(scenes)} ---")
            image_path = os.path.join(images_dir, f"scene_{scene_num}.png")
            audio_path = os.path.join(audio_dir, f"scene_{scene_num}.wav")
            
            if not os.path.exists(image_path) or not os.path.exists(audio_path):
                logger.error(f"Missing image or audio for scene {scene_num}")
                continue

            duration = AudioManager.get_audio_duration(audio_path)
            
            # Paths
            tmp_video = os.path.join(self.tmp_dir, f"scene_{scene_num}_animated.mp4")
            tmp_narrated = os.path.join(self.tmp_dir, f"scene_{scene_num}_narrated.mp4")
            srt_path = os.path.join(self.tmp_dir, f"scene_{scene_num}.srt")
            tmp_subbed = os.path.join(self.tmp_dir, f"scene_{scene_num}_subbed.mp4")

            # Pipeline steps for each scene
            logger.info(f"[Scene {scene_num}] Step A: Converting image to video...")
            SceneCreator.image_to_video(image_path, duration, tmp_video)
            
            logger.info(f"[Scene {scene_num}] Step B: Attaching audio...")
            SceneCreator.attach_audio(tmp_video, audio_path, tmp_narrated)
            
            # Only burn subtitles if enabled via environment variable
            add_subtitles = os.getenv("ADD_SUBTITLES", "True").lower() in ("true", "1", "yes")
            if add_subtitles:
                SubtitleGenerator.create_srt(scene.get("text", ""), duration, srt_path)
                SubtitleGenerator.burn_subtitles(tmp_narrated, srt_path, tmp_subbed)
                scene_files.append(tmp_subbed)
            else:
                logger.info(f"Skipping subtitles for scene {scene_num}")
                scene_files.append(tmp_narrated)

        if not scene_files:
            raise ValueError("No scenes were successfully generated.")

        logger.info("--- All scenes processed. Starting Concatenation ---")
        concatenated_video = os.path.join(self.tmp_dir, "concatenated.mp4")
        self.concatenate_scenes(scene_files, concatenated_video)

        final_video = os.path.join(self.output_dir, "final_video.mp4")

        # Add background music if provided
        if bgm_path and os.path.exists(bgm_path):
            with_bgm = os.path.join(self.tmp_dir, "with_bgm.mp4")
            AudioManager.mix_background_music(concatenated_video, bgm_path, with_bgm)
            base_video = with_bgm
        else:
            base_video = concatenated_video

        # Add intro title
        title = data.get("title", "Generated Video")
        self.add_intro_title(base_video, title, final_video)

        # Generate thumbnail
        if scenes:
            thumb_source = os.path.join(images_dir, f"scene_{len(scenes)}.png") # Usually scene 5
            if os.path.exists(thumb_source):
                self.generate_thumbnail(thumb_source, os.path.join(self.output_dir, "thumbnail.png"))

        # Save metadata
        metadata = {
            "title": title,
            "description": data.get("description", ""),
            "hashtags": data.get("hashtags", [])
        }
        with open(os.path.join(self.output_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        logger.info(f"Pipeline finished! Final video at {final_video}")
        return final_video
