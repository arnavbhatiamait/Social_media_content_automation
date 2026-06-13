import os
import time
from pathlib import Path

from google import genai
from google.genai import types


from pathlib import Path
from sys import path
from logs_setup.logger import Logger

logger = Logger(name="VeoVideoGenerator", log_file="logs/veo_video_gen.log").get_logger()

import os 
from dotenv import load_dotenv
load_dotenv()


class VeoVideoGenerator:
    def __init__(self, model_name: str = None, output_dir: str = "output"):
        self.model_name = model_name or os.getenv("VEO_MODEL_NAME", "veo-2.0-generate-001")
        self.output_dir = output_dir

        self.client = genai.Client(
            vertexai=True,
            project=os.getenv("PROJECT_ID"),
            location=os.getenv("GCP_LOCATION"),
        )

        Path(self.output_dir).mkdir(
            parents=True,
            exist_ok=True
        )

    def generate_video(
        self,
        prompt: str,
        output_name: str = "generated_video.mp4"
    ):
        """
        Generate video using Veo
        """

        logger.info(f"Starting video generation with prompt: {prompt}...")

        operation = self.client.models.generate_videos(
            model=self.model_name,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                number_of_videos=1,
                duration_seconds=8,
            ),
        )

        while not operation.done:
            logger.info("Waiting for Veo video generation to complete...")
            time.sleep(20)

            operation = self.client.operations.get(
                operation
            )

        logger.info("Generation complete!")

        generated_video = operation.response.generated_videos[0]

        output_path = os.path.join(
            self.output_dir,
            output_name
        )

        generated_video.video.save(output_path)

        logger.info(f"Saved: {output_path}")

        return output_path
    
