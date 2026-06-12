import subprocess
from logs_setup.logger import Logger

logger = Logger(name="SceneCreator", log_file="logs/video_assembler.log").get_logger()

class SceneCreator:
    @staticmethod
    def image_to_video(image_path: str, duration: float, output_path: str):
        logger.info(f"Converting image {image_path} to animated video ({duration}s)")
        cmd = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-vf", "zoompan=z='min(zoom+0.0008,1.15)':d=125:s=1080x1920",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Animated video saved to {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed while converting image to video: {e}")
            raise

    @staticmethod
    def attach_audio(video_path: str, audio_path: str, output_path: str):
        logger.info(f"Attaching audio {audio_path} to video {video_path}")
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-shortest",
            "-c:v", "copy",
            "-c:a", "aac",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Audio attached successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed while attaching audio: {e}")
            raise
