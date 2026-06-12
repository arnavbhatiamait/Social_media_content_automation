import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from LLM.model import LLMModel
from ImageGeneration.flux import FluxImageGen
from tts.gtts import GoogleTTS
from video_assembler.video_pipeline import VideoPipeline
from prompts.prompts_video.prompts_video import get_prompt
from logs_setup.logger import Logger

logger = Logger(name="MainPipeline", log_file="logs/main_pipeline.log").get_logger()

def _generate_images_sync(prompts, output_dir):
    flux_gen = FluxImageGen()
    logger.info(f"Generating {len(prompts)} images...")
    paths = flux_gen.generate_images_reels(prompts)
    
    os.makedirs(output_dir, exist_ok=True)
    renamed_paths = []
    for idx, path in enumerate(paths):
        scene_num = idx + 1
        new_path = os.path.join(output_dir, f"scene_{scene_num}.png")
        if os.path.exists(path):
            os.replace(path, new_path)
            renamed_paths.append(new_path)
        else:
            logger.error(f"Image not found at {path}")
    return renamed_paths

def _generate_audio_sync(texts, output_dir):
    tts = GoogleTTS()
    logger.info(f"Generating {len(texts)} audio clips...")
    os.makedirs(output_dir, exist_ok=True)
    
    # batch_process generates "output_001.wav" etc.
    paths = tts.batch_process(texts, output_dir=output_dir)
    
    renamed_paths = []
    for idx, path in enumerate(paths):
        scene_num = idx + 1
        new_path = os.path.join(output_dir, f"scene_{scene_num}.wav")
        if os.path.exists(path):
            os.replace(path, new_path)
            renamed_paths.append(new_path)
        else:
            logger.error(f"Audio not found at {path}")
    return renamed_paths

async def generate_assets_parallel(prompts, texts, images_dir, audio_dir):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        logger.info("Starting parallel image and audio generation...")
        img_task = loop.run_in_executor(pool, _generate_images_sync, prompts, images_dir)
        audio_task = loop.run_in_executor(pool, _generate_audio_sync, texts, audio_dir)
        
        await asyncio.gather(img_task, audio_task)
        logger.info("Parallel asset generation complete.")

def main():
    logger.info("--- Starting End-to-End Pipeline ---")
    
    # Step 1: LLM Generation
    system_prompt = get_prompt()
    model = LLMModel(system_prompt="You are a helpful assistant.", provider="gemini")
    logger.info("Requesting JSON from LLM...")
    response_str = model.response_llm(system_prompt=system_prompt, post=False)
    
    try:
        # LLM returns dict if it was parsed by JsonOutputParser
        if isinstance(response_str, str):
            data = json.loads(response_str)
        else:
            data = response_str
        logger.info(f"LLM JSON successfully parsed. Extracted {len(scenes)} scenes and {len(image_prompts)} image prompts.")
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return

    # Extract scenes
    scenes = data.get("audio_segments", [])
    if not scenes:
        logger.error("No audio_segments found in JSON.")
        return

    # In your provided JSON structure, there's `image_prompts` separate from `audio_segments`.
    # Let's match them by scene index.
    image_prompts = data.get("image_prompts", [])
    
    texts = [scene.get("text", "") for scene in scenes]
    prompts = [item.get("prompt", "") for item in image_prompts]

    # Handle missing prompts by repeating the first or using a default
    if len(prompts) < len(texts):
        logger.warning("Fewer image prompts than audio segments. Using default prompt.")
        while len(prompts) < len(texts):
            prompts.append(prompts[-1] if prompts else "A beautiful cinematic scene.")

    images_dir = os.path.abspath("output/images")
    audio_dir = os.path.abspath("output/audio")
    
    # Step 2: Parallel Generation
    logger.info("=== STEP 2: PARALLEL ASSET GENERATION ===")
    asyncio.run(generate_assets_parallel(prompts, texts, images_dir, audio_dir))
    
    # Optional: ensure data conforms to VideoPipeline expectations
    # VideoPipeline looks for "scenes" key with text
    data["scenes"] = scenes

    # Step 3: Video Assembly
    logger.info("=== STEP 3: VIDEO ASSEMBLY PIPELINE ===")
    pipeline = VideoPipeline(output_dir=os.path.abspath("output"))
    try:
        final_video = pipeline.run_pipeline(
            data=data,
            images_dir=images_dir,
            audio_dir=audio_dir,
            bgm_path=None # Optional: you can add a path here if you have bgm
        )
        logger.info(f"Pipeline complete! Video saved to {final_video}")
    except Exception as e:
        logger.error(f"Video pipeline failed: {e}")

if __name__ == "__main__":
    main()
