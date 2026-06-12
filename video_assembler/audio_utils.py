from mutagen import File
import subprocess
from logs_setup.logger import Logger

logger = Logger(name="AudioUtils", log_file="logs/video_assembler.log").get_logger()

class AudioManager:
    @staticmethod
    def get_audio_duration(path: str) -> float:
        try:
            audio = File(path)
            if audio is None:
                raise ValueError(f"Could not read audio file: {path}")
            return audio.info.length
        except Exception as e:
            logger.error(f"Failed to get duration for {path}: {e}")
            raise

    @staticmethod
    def mix_background_music(narration_path: str, bgm_path: str, output_path: str, bgm_volume: float = 0.15):
        logger.info(f"Mixing narration {narration_path} with BGM {bgm_path} into {output_path}")
        cmd = [
            "ffmpeg",
            "-y",
            "-i", narration_path,
            "-i", bgm_path,
            "-filter_complex",
            f"[1:a]volume={bgm_volume}[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Background music mixed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed while mixing background music: {e}")
            raise
