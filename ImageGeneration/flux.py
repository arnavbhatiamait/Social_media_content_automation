import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
os.makedirs("images", exist_ok=True)
os.makedirs("reels_images", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
try:
    from logs_setup.logger import Logger
except Exception as e:
    from pathlib import Path
    from sys import path
    path.append(str(Path(__file__).parent.parent))
    from logs_setup.logger import Logger
    print(f"Error importing logger 2: {e}")

logger = Logger(name="FluxImageGen",log_file="logs/flux_image_gen.log").get_logger()
class FluxImageGen:
    def __init__(self):
        self.client = InferenceClient(
            provider="auto",
            api_key=os.getenv("HF_TOKEN")
        )
        self.model= "black-forest-labs/FLUX.1-schnell"
        logger.info(f"Initialized InferenceClient with provider auto {self.model}")
    def generate_image_normal(self,prompt:str):
        logger.info(f"Generating image for prompt: {prompt}")
        response = self.client.text_to_image(
            prompt,
            model=self.model,
             width=1024,
            height=1024
        )
        logger.info(f"Received response for prompt: {prompt}, response: {response}")
        image = response
        image.save(f"images/generated_image_{timestamp}.png")
        logger.info(f"Saved image for prompt: {prompt} at images/generated_image_{timestamp}.png")
        return image
    def generate_image_reels(self,prompt:str):
        logger.info(f"Generating reels image for prompt: {prompt}")
        response = self.client.text_to_image(
            prompt,
            model=self.model,
             width=1080,
            height=1920
        )
        logger.info(f"Received response for prompt: {prompt}, response: {response}")
        image = response
        image.save(f"reels_images/generated_image_reels_{timestamp}.png")
        logger.info(f"Saved reels image for prompt: {prompt} at reels_images/generated_image_reels_{timestamp}.png")
        return image
    def generate_images_reels(self,prompts:list[str]):
        logger.info(f"Generating reels images for prompts: {prompts}")
        for idx,prompt in enumerate(prompts):
            logger.info(f"Generating reels image {idx} for prompt: {prompt}")
            response = self.client.text_to_image(
                prompt,
                model=self.model,
                width=1080,
                height=1920
            )
            logger.info(f"Received response for prompt: {prompt}, response: {response}")
            image = response
            image.save(f"reels_images/generated_image_reels_{idx}.png")
            logger.info(f"Saved reels image {idx} for prompt: {prompt} at reels_images/generated_image_reels_{idx}.png")
        return [f"reels_images/generated_image_reels_{idx}.png" for idx in range(len(prompts))]

if __name__ == "__main__":
    flux_gen = FluxImageGen()
    # flux_gen.generate_image_normal("A serene landscape with mountains and a river, in the style of a digital painting")
    flux_gen.generate_images_reels(["A futuristic cityscape at night, with neon lights and flying cars, in the style of cyberpunk art","A close-up portrait of a person with vibrant, colorful makeup and intricate patterns, in the style of surrealism"])