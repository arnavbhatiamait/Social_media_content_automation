from pathlib import Path
from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
try:
    from logs_setup.logger import Logger
except ImportError as e:
    from sys import path
    path.append(str(Path(__file__).parent.parent))
    from logs_setup.logger import Logger
    print(f"Error importing logger: {e}")

logger = Logger(name="ImageGen",log_file="logs/iamgegen.log").get_logger()
import os  
from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION") or os.getenv("GCP_LOCATION") or "us-central1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)
os.makedirs("images", exist_ok=True)

class ImageGen:
    def __init__(self):
        self.model = ImageGenerationModel.from_pretrained(
    # "imagen-4.0-fast-generate-001"
    "imagen-4.0-generate-001"
    )
        logger.info(f"Model used {self.model}")


    def generate_single_image(self, prompt: str, output_path: str = None):
        logger.info(f"Generating image for prompt: {prompt}")
        images = self.model.generate_images(
            prompt=prompt,
            number_of_images=1,
            # image_size="1K",
            aspect_ratio="1:1",
            safety_filter_level="block_some"
        )   
        logger.info(f"Generated  images for prompt: {prompt}, images: {images}")
        saved_paths = []
        for i, image in enumerate(images):
            try:
                path_to_save = output_path if output_path else f"images/generated_image_{i}.png"
                logger.info(f"Saving image {i} for prompt: {prompt} to: {path_to_save}")
                image.save(
                    path_to_save,
                    include_generation_parameters=False
                )
                saved_paths.append(path_to_save)
            except Exception as e:
                logger.error(f"Error occurred while saving image {i} for prompt: {prompt}, error: {e}")
            
        return saved_paths
    
    def generate_multiple_images(self,prompt:str,number_of_images:int):
        logger.info(f"Generating {number_of_images} images for prompt: {prompt}")
        images = self.model.generate_images(
            prompt=prompt,
            number_of_images=number_of_images,
            # image_size="1K",
            aspect_ratio="1:1",
            safety_filter_level="block_some"
        )   
        for i,image in enumerate(images,1):
            logger.info(f"Saving image {i} for prompt: {prompt}, image: {image}")
            try:
                image.save(
                    f"images/generated_images_{i}.png",
                    include_generation_parameters=False
                )
            except Exception as e:
                logger.error(f"Error occurred while saving image {i} for prompt: {prompt}, image: {image}, error: {e}")
        return [f"images/generated_images_{i}.png" for i in range(1,number_of_images+1)]
    
    async def generate_image_async(self,prompt:str,number_of_images:int):
        logger.info(f"Generating {number_of_images} async images for prompt: {prompt}")
        images = await self.model.agenerate_images(
            prompt=prompt,
            number_of_images=number_of_images,
            # image_size="1K",
            aspect_ratio="1:1",
            safety_filter_level="block_some"
        )   
        for i,image in enumerate(images,1):
            logger.info(f"Saving async image {i} for prompt: {prompt}, image: {image}")
            try:
                image.save(
                    f"images/generated_image_async_{i}.png",
                    include_generation_parameters=False
                )
            except Exception as e:
                logger.error(f"Error occurred while saving async image {i} for prompt: {prompt}, image: {image}, error: {e}")

        return [f"images/generated_image_async_{i}.png" for i in range(1,number_of_images+1)]
    


    async def generate_image_async_stream(
        self,
        prompt: str,
        number_of_images: int
    ):
        logger.info(f"Generating {number_of_images} async stream images for prompt: {prompt}")
        output_dir = Path("images")
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []
        idx = 0

        async for image in self.model.agenerate_images_stream(
            
            prompt=prompt,
            number_of_images=number_of_images,
            # image_size="1K",
            aspect_ratio="1:1",
            safety_filter_level="block_some",
        ):
            logger.info(f"Received streamed image {idx} for prompt: {prompt}, image: {image}")
            file_path = output_dir / f"generated_image_{idx}.png"

            image.save(
                str(file_path),
                include_generation_parameters=False,
            )

            generated_files.append(str(file_path))
            idx += 1
            logger.info(f"Saved streamed image {idx} for prompt: {prompt}, file_path: {file_path}")
        return generated_files

if __name__ == "__main__":
    image_gen = ImageGen()
    image_gen.generate_single_image(prompt="A photo of a cat")