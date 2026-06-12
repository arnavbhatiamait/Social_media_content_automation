import time
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser

try:
    from logs_setup.logger import Logger
except ImportError as e:
    from sys import path
    from pathlib import Path

    path.append(str(Path(__file__).parent.parent))
    from logs_setup.logger import Logger

    print(f"Error importing Logger: {e}")
import typing
from typing_extensions import Optional
import os
from dotenv import load_dotenv

load_dotenv()
# api_key_groq = os.getenv("GROQ_API_KEY2")
# print(f"Using GROQ_API_KEY2: {api_key_groq is not None}")
api_key_gemini = os.getenv("GOOGLE_API_KEY")
print(f"Using GOOGLE_API_KEY: {api_key_gemini is not None}")


class LLMModel:
    # def __init__(self,model_name="llama3.2:latest", temperature=0.7,provider="ollama",system_prompt="You are a helpful assistant."):
    def __init__(
        self,
        model_name="gemini-2.5-flash",
        temperature=0.7,
        provider="gemini",
        system_prompt="You are a helpful assistant.",
    ):
        self.model_name = model_name
        self.model_provider = provider
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.logger = Logger(
            name="llm_model", log_file="logs/llm_model.log"
        ).get_logger()
        self.logger.info(
            f"Initializing LLMModel | provider={provider} | model={model_name} | temperature={temperature},system_prompt={system_prompt}"
        )
        self.llm = self.get_llm()
        self.human_prompt_post = "Please generate a JSON with keys 'prompt' and 'description' for an image generation model based on the above system prompt. The 'prompt' should be a concise description suitable for input to an image generation model, while the 'description' should provide a more detailed explanation of the scene, including elements, composition, and artistic style. Ensure the JSON is properly formatted and parsable."
        self.human_prompt_reel = """Please generate a json with the following structure and I am attaching an example with this 
         
        
        json structure:
        {
    "title": "Mahadev: The Eternal Source of Cosmic Transformation",
    "deity": "Lord Shiva",
    "description": "Step into the mystical heights of Mount Kailash and behold the infinite majesty of Lord Shiva, known across the cosmos as Mahadev. Witness the calm before the cosmic storm as the ultimate protector and transformer balances the universe through profound meditation and divine power. Discover the ancient symbols, ethereal realms, and timeless wisdom of the supreme yogi in this cinematic documentary journey. #Mahadev #LordShiva #HinduMythology #SpiritualJourney #CosmicEnergy #ShivaTandava #DivinePower",
    "seo_keywords": [
        "Lord Shiva",
        "Mahadev",
        "Mount Kailash",
        "Hindu Mythology Documentary",
        "Shiva Cosmic Transformation",
        "Trishul and Damaru",
        "Spiritual Meditation",
        "Vedic Traditions"
    ],
    "hashtags": [
        "Mahadev",
        "LordShiva",
        "HinduMythology",
        "CosmicEnergy",
        "SpiritualJourney",
        "HarHarMahadev"
    ],
    "duration_seconds": 60,
    "audio_segments": [
        {
            "scene": 1,
            "title": "The Silent Descent",
            "text": "Deep within the frozen, timeless peaks of Mount Kailash, an ancient stillness grips the earth. Here, wrapped in sacred mist, manifests the supreme consciousness: Mahadev, the great lord of transformation.",
            "start_time_seconds": 0,
            "end_time_seconds": 12,
            "duration_seconds": 12
        },
        {
            "scene": 2,
            "title": "The Yogi's Aura",
            "text": "His blue-grey skin is coated in sacred ash, a stark testament to the transient nature of existence. With a calm, meditative focus that stabilizes the shifting dimensions, his piercing third eye remains closed, holding back an infinite well of cosmic energy.",
            "start_time_seconds": 12,
            "end_time_seconds": 24,
            "duration_seconds": 12
        },
        {
            "scene": 3,
            "title": "Lord of the Cosmic Balance",
            "text": "Upon his head rests the silver crescent moon, anchoring the flow of time itself. As the holy waters of the River Ganga cascade from his matted locks, the majestic bull Nandi watches over his master's eternal, transcendent domain.",
            "start_time_seconds": 24,
            "end_time_seconds": 36,
            "duration_seconds": 12
        },
        {
            "scene": 4,
            "title": "The Weapon of Righteousness",
            "text": "Suddenly, a profound shift reverberates through space. In his hands, he raises the sacred Trishul, the cosmic trident that shatters illusion, while a mystical snake moves gently around his neck, symbolizing absolute mastery over death.",
            "start_time_seconds": 36,
            "end_time_seconds": 48,
            "duration_seconds": 12
        },
        {
            "scene": 5,
            "title": "The Ultimate Grace",
            "text": "As the heavens part, a magnificent divine halo illuminates the mountaintop. With infinite compassion, Bholenath extends his hand in an eternal blessing, sending waves of peace and transformation across the material world.",
            "start_time_seconds": 48,
            "end_time_seconds": 60,
            "duration_seconds": 12
        }
    ],
    "image_prompts": [
        {
            "scene": 1,
            "prompt": "An epic, photorealistic digital painting capturing Lord Shiva, reverently known as Mahadev, manifesting his divine presence on the snowy peaks of Mount Kailash. The atmosphere is saturated with a thick, swirling sacred mist under the breathtaking hues of a golden sunrise. The deity stands in a powerful, commanding stance, framed from an ultra low angle heroic shot. His iconic blue-grey skin and ash-covered body contrast brilliantly against a vivid gold and crimson color palette. Swirling golden clouds and ancient pillars materialize faintly in the background. Masterful volumetric god rays stream through the fog, casting cinematic rim light and rich, dramatic shadows across the mountain peaks. Rendered with an anamorphic cinematic depth of field and hyper-realistic micro-textures showcasing the fine grains of snow and stone. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
        },
        {
            "scene": 2,
            "prompt": "An ultra-realistic, cinematic movie frame of Lord Shiva, known as Bholenath, portraying his deeply calm and meditative personality. Captured in a waist up portrait frame using a high-end anamorphic lens, the deity's face shows an expression of supreme, transcendent focus. His long matted hair flows gently in the wind, adorned with the glowing silver crescent moon. A soft cosmic energy glow illuminates his third eye and the tiger skin garment draped over his muscular form. The background reveals intricate details of mountain ranges, floating islands, and temple bells obscured by a heavy divine fog. The color palette shifts to a striking balance of gold and crimson with deep obsidian shadows. Sharp, volumetric god rays pierce the haze, highlighting the micro-textures of the ash on his divine skin. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
        },
        {
            "scene": 3,
            "prompt": "A majestic, fine art masterpiece depicting Lord Shiva, known across the cosmos as Neelkanth, showcasing his vast spiritual domain. The deity is positioned in a serene full body pose, sitting on a rocky ledge overlooking a cascading sacred waterfall that morphs into a vibrant sacred river. From his long matted hair, the river Ganga flows outward into the environment. His divine vehicle, the massive white bull Nandi, rests loyally by his side. The camera angle is a wide cinematic view, establishing an immense scale between the deity and the sweeping Himalayan cave system. The setting is bathed in the dramatic highlights of a solar eclipse, casting a rare, eerie golden glow combined with deep, rich shadows. Spiritual energy waves and floating lotus flowers accentuate the mystical landscape. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
        },
        {
            "scene": 4,
            "prompt": "An explosive, dynamic action camera shot of Lord Shiva, known as Rudra, performing a legendary mythological act of power. The deity stands in an intense, powerful stance, wielding the sacred Trishul which crackles with raw, celestial energy, while his other hand commands the Damaru drum. A massive cobra snake is wrapped securely around his neck, its scales catching the sharp backlighting. The environment is an awe-inspiring, chaotic storm of monsoon rain and celestial rain, with heavy thunderclouds lit from within by cosmic energy. The composition utilizes a dramatic low angle perspective, emphasizing the deity's immense scale. The color palette explodes with saturated gold and crimson tones against dark, stormy blues. Intricate background details include shattered floating rocks, ancient architecture, and swirling golden particles captured with sharp depth of field. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
        },
        {
            "scene": 5,
            "prompt": "The epic cinematic finale, a photorealistic digital painting of Lord Shiva, affectionately known as Shankara, granting a transcendent blessing to humanity. The deity is captured in a magnificent, standing blessing devotees stance, his right hand extended forward emitting a radiant divine halo of pure golden light. The camera composition is a masterfully balanced full body shot with an expansive, wide angle lens. The entire atmosphere is filled with glowing dust, fireflies, and floating petals under the ethereal light of a cosmic dawn. The rich background displays a celestial throne room melting into a star-filled universe with vibrant constellations, nebulae, and sacred lamps. The color palette reaches its peak grandeur with shimmering gold, crimson, and deep cosmic violet hues. Hyper-realistic textures detail the fine threads of his rudraksha malas and the stone patterns of Mount Kailash. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
        }
    ]
}

make sure to generate a detailed prompt and description based on the above system prompt. The 'prompt' should be concise and actionable for an image generation model, while the 'description' should provide a rich, detailed explanation of the scene, including elements, composition, and artistic style. Ensure the output is a properly formatted JSON that can be easily parsed.
           """

    def _get_combined_system_prompt(
        self, system_prompt: Optional[str] = None, is_greeting: bool = False
    ) -> str:
        sys_p = system_prompt if system_prompt is not None else self.system_prompt
        if is_greeting:
            return sys_p
        return f"{sys_p}"

    def get_llm(self):
        self.logger.info(f"Loading LLM backend for provider '{self.model_provider}'")
        if self.model_provider.lower() == "ollama":
            # pyrefly: ignore [missing-import]
            from langchain_ollama import ChatOllama

            self.logger.info(
                f"using model = {self.model_name} provider={self.model_provider}"
            )
            return ChatOllama(model=self.model_name, temperature=self.temperature)
        elif self.model_provider.lower() == "openai":
            from langchain_openai import ChatOpenAI

            self.logger.info(
                f"using model = {self.model_name} provider={self.model_provider}"
            )
            return ChatOpenAI(model=self.model_name, temperature=self.temperature)
        elif self.model_provider.lower() == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI

            self.logger.info(
                f"using model = {self.model_name} provider={self.model_provider}"
            )
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=api_key_gemini,
            )
        elif self.model_provider.lower() == "groq":
            from langchain_groq import ChatGroq

            self.logger.info(
                f"using model = {self.model_name} provider={self.model_provider}"
            )
            return ChatGroq(
                model=self.model_name,
                temperature=self.temperature,
                api_key=api_key_groq,
            )
        else:
            self.logger.error(f"Unknown provider: '{self.model_provider}'")
            raise ValueError("Provider not found")

    def _messages_from_history(self, history):
        messages = []
        for user_msg, assistant_msg in history:
            messages.append(HumanMessage(content=user_msg))
            messages.append(AIMessage(content=assistant_msg))
        return messages

    def get_response_sync(self, prompt: str, history: list, system_prompt: str = None):
        self.logger.info(
            f"[sync] Invoking LLM | prompt_length={len(prompt)} | history_turns={len(history)}"
        )
        start_time = time.perf_counter()

        is_greeting = (
            "opening greeting" in prompt.lower()
            or "starting a new outbound" in prompt.lower()
        )
        messages = [
            SystemMessage(
                content=self._get_combined_system_prompt(
                    system_prompt, is_greeting=is_greeting
                )
            )
        ] + self._messages_from_history(history)
        messages.append(HumanMessage(content=prompt))
        response = self.llm.invoke(messages)
        latency = time.perf_counter() - start_time
        self.logger.info(f"[sync] LLM response received | latency={latency:.3f}s")
        return {"response": response.content, "latency": latency}

    def get_response_stream(
        self, prompt: str, history: list, system_prompt: str = None
    ):
        self.logger.info(
            f"[stream] Invoking LLM | prompt_length={len(prompt)} | history_turns={len(history)}"
        )
        start_time = time.perf_counter()

        is_greeting = (
            "opening greeting" in prompt.lower()
            or "starting a new outbound" in prompt.lower()
        )
        messages = [
            SystemMessage(
                content=self._get_combined_system_prompt(
                    system_prompt, is_greeting=is_greeting
                )
            )
        ] + self._messages_from_history(history)
        messages.append(HumanMessage(content=prompt))
        initial_latency = time.perf_counter() - start_time
        self.logger.info(f"[stream] Initial latency: {initial_latency:.3f}s")
        for chunk in self.llm.stream(messages):
            yield chunk.content

    async def get_response_async(
        self, prompt: str, history: list, system_prompt: str = None
    ):
        self.logger.info(
            f"[async] Invoking LLM | prompt_length={len(prompt)} | history_turns={len(history)}"
        )
        start_time = time.perf_counter()

        is_greeting = (
            "opening greeting" in prompt.lower()
            or "starting a new outbound" in prompt.lower()
        )
        messages = [
            SystemMessage(
                content=self._get_combined_system_prompt(
                    system_prompt, is_greeting=is_greeting
                )
            )
        ] + self._messages_from_history(history)
        messages.append(HumanMessage(content=prompt))
        initial_latency = time.perf_counter() - start_time
        self.logger.info(f"[async] Initial latency: {initial_latency:.3f}s")
        response = await self.llm.ainvoke(messages)
        total_latency = time.perf_counter() - start_time
        self.logger.info(
            f"[async] LLM response received | total_latency={total_latency:.3f}s"
        )
        return {"response": response.content, "latency": total_latency}

    async def get_response_stream_async(
        self, prompt: str, history: list, system_prompt: str = None
    ):
        self.logger.info(
            f"[async_stream] Invoking LLM | prompt_length={len(prompt)} | history_turns={len(history)}"
        )
        start_time = time.perf_counter()
        is_greeting = (
            "opening greeting" in prompt.lower()
            or "starting a new outbound" in prompt.lower()
        )
        messages = [
            SystemMessage(
                content=self._get_combined_system_prompt(
                    system_prompt, is_greeting=is_greeting
                )
            )
        ] + self._messages_from_history(history)
        messages.append(HumanMessage(content=prompt))
        initial_latency = time.perf_counter() - start_time
        self.logger.info(f"[async_stream] Initial latency: {initial_latency:.3f}s")
        async for chunk in self.llm.astream(messages):
            yield chunk.content

    def response_llm(self, system_prompt: str, post: bool = True):
        if post:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=self.human_prompt_post),
            ]
        else:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=self.human_prompt_reel),
            ]
        output_parser = JsonOutputParser()
        chain = self.llm | output_parser
        print(f"Invoking LLM with system prompt: {system_prompt}")
        print(type(messages), messages)
        response = chain.invoke(messages)
        return response


if __name__ == "__main__":
    from prompts.prompts_posts.god_prompt import generate_god_scene_prompt
    from prompts.prompts_video.prompts_video import get_prompt

    model = LLMModel(system_prompt="You are a helpful assistant.")
    # system_prompt = generate_god_scene_prompt()
    system_prompt = get_prompt()
    print(f"System Prompt: {type(system_prompt)} | {system_prompt}")
    response = model.response_llm(system_prompt=system_prompt, post=False)
    print(response)
