import pysrt
import subprocess
from logs_setup.logger import Logger

logger = Logger(name="SubtitleGenerator", log_file="logs/video_assembler.log").get_logger()

class SubtitleGenerator:
    @staticmethod
    def create_srt(text: str, duration: float, output_path: str):
        logger.info(f"Generating subtitle for text: '{text[:30]}...' duration: {duration}s")
        try:
            file = pysrt.SubRipFile()
            
            # Create a single subtitle item spanning the entire duration
            item = pysrt.SubRipItem(
                index=1,
                start=pysrt.SubRipTime(0, 0, 0, 0),
                end=pysrt.SubRipTime(seconds=int(duration), milliseconds=int((duration % 1) * 1000)),
                text=text
            )
            file.append(item)
            file.save(output_path, encoding='utf-8')
            logger.info(f"Subtitles saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate subtitle: {e}")
            raise

    @staticmethod
    def burn_subtitles(video_path: str, srt_path: str, output_path: str):
        logger.info(f"Burning subtitles from {srt_path} into {video_path}")
        # FFmpeg on Windows requires special escaping for the subtitles filter path
        # Replace backslashes with forward slashes and escape the drive letter colon
        safe_srt_path = srt_path.replace('\\', '/').replace(':', '\\:')
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", f"subtitles='{safe_srt_path}'",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Subtitles burned successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed while burning subtitles: {e}")
            raise
