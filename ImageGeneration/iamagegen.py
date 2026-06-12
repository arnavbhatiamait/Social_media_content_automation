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
LOCATION = os.getenv("LOCATION")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)
os.makedirs("images", exist_ok=True)

class ImageGen:
    def __init__(self):
        self.model = ImageGenerationModel.from_pretrained(
    "imagen-4.0-generate-001"
    )
        logger.info(f"Model used {self.model}")


    def generate_single_image(self,prompt:str):
        logger.info(f"Generating image for prompt: {prompt}")
        images = self.model.generate_images(
            prompt=prompt,
            number_of_images=1,
            # image_size="1K",
            aspect_ratio="1:1",
            safety_filter_level="block_some"
        )   
        logger.info(f"Generated  images for prompt: {prompt}, images: {images}")
        for i,image in enumerate(images):
            try:
                logger.info(f"Saving image {i} for prompt: {prompt}, image: {image}")
                image.save(
                    f"images/generated_image_{i}.png",
                    include_generation_parameters=False
                )
            except Exception as e:
                logger.error(f"Error occurred while saving image {i} for prompt: {prompt}, image: {image}, error: {e}")
            
        return [f"images/generated_image_{i}.png" for i in range(1,2)]
    
    def generate_multiple_images(self,prompt:str,number_of_images:int):
        images = self.model.generate_images(
            prompt=prompt,
            number_of_images=number_of_images,
            # image_size="1K",
            aspect_ratio="1:1",
            safety_filter_level="block_some"
        )   
        for i,image in enumerate(images,1):
            image.save(
                f"images/generated_images_{i}.png",
                include_generation_parameters=False
            )
        return [f"images/generated_images_{i}.png" for i in range(1,number_of_images+1)]
    
    async def generate_image_async(self,prompt:str,number_of_images:int):
        images = await self.model.agenerate_images(
            prompt=prompt,
            number_of_images=number_of_images,
            # image_size="1K",
            aspect_ratio="1:1",
            safety_filter_level="block_some"
        )   
        for i,image in enumerate(images,1):
            image.save(
                f"images/generated_image_async_{i}.png",
                include_generation_parameters=False
            )
    
        return [f"images/generated_image_async_{i}.png" for i in range(1,number_of_images+1)]
    


    async def generate_image_async_stream(
        self,
        prompt: str,
        number_of_images: int
    ):
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
            file_path = output_dir / f"generated_image_{idx}.png"

            image.save(
                str(file_path),
                include_generation_parameters=False,
            )

            generated_files.append(str(file_path))
            idx += 1

        return generated_files

if __name__ == "__main__":
    image_gen = ImageGen()
    image_gen.generate_single_image(prompt="A photo of a cat")