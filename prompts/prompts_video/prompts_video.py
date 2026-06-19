import random
import json

ENVIRONMENTS = [
    "Mount Kailash",
    "Himalayan Cave",
    "Sacred River",
    "Cosmic Realm",
    "Celestial Palace",
    "Ancient Temple",
    "Golden Kingdom",
    "Lotus Garden",
    "Mystical Forest",
    "Divine Battlefield",
    "Sacred Desert",
    "Monsoon Landscape",
    "Floating Islands",
    "Star-filled Universe",
    "Ocean of Consciousness",
    "Spiritual Dimension",
    "Cloud Kingdom",
    "Ancient Indian City",
    "Mountain Monastery",
    "Jungle Shrine",
    "Sacred Waterfall",
    "Glowing Crystal Valley",
    "Moonlit Lake",
    "Heavenly Courtyard",
    "Celestial Throne Room",
    "Divine Library",
    "Floating Temple",
    "Ethereal Sky Realm",
    "Sacred Volcano",
    "Hidden Valley",
]

TIMES = [
    "Golden Sunrise",
    "Early Morning Mist",
    "Noon Light",
    "Golden Hour",
    "Sunset",
    "Twilight",
    "Blue Hour",
    "Full Moon Night",
    "Starry Night",
    "Cosmic Dawn",
    "Solar Eclipse",
    "Lunar Eclipse",
]

WEATHER = [
    "Clear Sky",
    "Monsoon Rain",
    "Thunderstorm",
    "Light Snow",
    "Heavy Snow",
    "Sacred Mist",
    "Divine Fog",
    "Golden Clouds",
    "Celestial Rain",
    "Cosmic Storm",
    "Floating Petals",
    "Sacred Ash Particles",
    "Glowing Dust",
    "Fireflies",
    "Aurora",
]

CAMERA_ANGLES = [
    "Extreme Close Up",
    "Close Up Portrait",
    "Chest Up",
    "Waist Up",
    "Full Body",
    "Hero Shot",
    "Low Angle",
    "Ultra Low Angle",
    "Top Down",
    "Bird's Eye View",
    "Wide Cinematic",
    "Over The Shoulder",
    "Dynamic Action Camera",
    "Drone Shot",
    "Epic Landscape Shot",
]

POSES = [
    "Meditating",
    "Walking",
    "Flying",
    "Blessing devotees",
    "Playing flute",
    "Holding weapon",
    "Sitting on throne",
    "Dancing",
    "Standing on mountain",
    "Looking at horizon",
    "Surrounded by celestial beings",
    "Riding divine vehicle",
    "Teaching disciples",
    "Performing divine act",
]

LIGHTING = [
    "Volumetric God Rays",
    "Cinematic Rim Light",
    "Golden Glow",
    "Moonlight",
    "Firelight",
    "Temple Lamp Light",
    "Celestial Light",
    "Cosmic Energy Glow",
    "Ethereal Lighting",
    "HDR Illumination",
    "Divine Halo",
    "Backlighting",
    "Dramatic Shadows",
]

COLOR_PALETTES = [
    "Gold and Crimson",
    "Blue and Silver",
    "Emerald and Gold",
    "Violet and Cyan",
    "Orange and Gold",
    "White and Sapphire",
    "Ruby and Gold",
    "Monochrome Divine",
    "Cosmic Rainbow",
    "Royal Purple and Gold",
]

ART_STYLES = [
    "Hyper Realistic Photography",
    "Cinematic Movie Frame",
    "Unreal Engine Render",
    "Fine Art Masterpiece",
    "Epic Fantasy Illustration",
    "Divine Concept Art",
    "Photorealistic Digital Painting",
    "Mythological Blockbuster Poster",
    "IMAX Cinematic Frame",
    "Ultra Detailed Sacred Art",
]

BACKGROUND_DETAILS = [
    "Lotus flowers",
    "Sacred rivers",
    "Mountains",
    "Waterfalls",
    "Ancient pillars",
    "Golden temples",
    "Celestial birds",
    "Floating islands",
    "Cosmic nebula",
    "Stars",
    "Planets",
    "Sacred fire",
    "Clouds",
    "Monks",
    "Devotees",
    "Divine animals",
    "Ancient architecture",
    "Temple bells",
    "Sacred lamps",
    "Golden particles",
    "Spiritual energy waves",
    "Crystal formations",
    "Heavenly gates",
    "Celestial stairs",
    "Constellations",
]
HINDU_DEITIES = {
    "Lord Shiva": {
        "titles": ["Mahadev", "Neelkanth", "Bholenath", "Shankara", "Rudra"],
        "appearance": [
            "blue-grey skin",
            "ash-covered body",
            "long matted hair",
            "third eye",
            "crescent moon",
            "flowing Ganga from hair",
        ],
        "symbols": [
            "Trishul",
            "Damaru",
            "Rudraksha malas",
            "snake around neck",
            "tiger skin garment",
        ],
        "personality": ["calm", "meditative", "powerful", "cosmic", "transcendent"],
        "vehicle": "Nandi",
        "domain": "destruction and transformation",
    },
    "Lord Krishna": {
        "titles": ["Govinda", "Gopala", "Madhava", "Keshava"],
        "appearance": [
            "divine blue complexion",
            "beautiful youthful face",
            "radiant smile",
        ],
        "symbols": [
            "flute",
            "peacock feather crown",
            "yellow silk dhoti",
            "lotus garland",
        ],
        "personality": ["playful", "compassionate", "charismatic", "divine"],
        "vehicle": None,
        "domain": "love, devotion and wisdom",
    },
    "Lord Rama": {
        "titles": ["Maryada Purushottam", "Raghava"],
        "appearance": ["royal blue complexion", "warrior prince", "noble expression"],
        "symbols": ["Kodanda bow", "arrow", "royal crown"],
        "personality": ["righteous", "disciplined", "honorable"],
        "vehicle": None,
        "domain": "dharma and righteousness",
    },
    "Lord Hanuman": {
        "titles": ["Bajrangbali", "Pavan Putra", "Mahaveer"],
        "appearance": [
            "powerful muscular divine form",
            "monkey-faced deity",
            "radiant orange aura",
        ],
        "symbols": ["golden mace", "mountain", "Rama's ring"],
        "personality": ["devoted", "fearless", "loyal", "strong"],
        "vehicle": None,
        "domain": "strength and devotion",
    },
    "Lord Ganesha": {
        "titles": ["Ganapati", "Vinayaka", "Vighnaharta"],
        "appearance": ["elephant head", "large ears", "gentle eyes"],
        "symbols": ["modak", "lotus", "axe", "blessing hand"],
        "personality": ["wise", "benevolent", "joyful"],
        "vehicle": "Mouse",
        "domain": "wisdom and prosperity",
    },
    "Goddess Lakshmi": {
        "titles": ["Mahalakshmi", "Shri"],
        "appearance": ["radiant golden glow", "beautiful red saree", "divine elegance"],
        "symbols": ["lotus flower", "gold coins", "elephants"],
        "personality": ["graceful", "prosperous", "compassionate"],
        "vehicle": "Owl",
        "domain": "wealth and prosperity",
    },
    "Goddess Saraswati": {
        "titles": ["Vagdevi", "Sharada"],
        "appearance": ["pure white attire", "serene expression"],
        "symbols": ["Veena", "swan", "sacred scriptures"],
        "personality": ["wise", "calm", "intellectual"],
        "vehicle": "Swan",
        "domain": "knowledge and arts",
    },
    "Goddess Durga": {
        "titles": ["Mahishasura Mardini", "Jagadamba"],
        "appearance": ["multiple arms", "radiant warrior goddess", "red garments"],
        "symbols": ["trident", "sword", "chakra", "lion"],
        "personality": ["protective", "powerful", "fearless"],
        "vehicle": "Lion",
        "domain": "protection and divine power",
    },
    "Goddess Kali": {
        "titles": ["Mahakali"],
        "appearance": ["dark complexion", "wild flowing hair", "fierce expression"],
        "symbols": ["sword", "garland", "divine fire"],
        "personality": ["fierce", "transformative", "protective"],
        "vehicle": None,
        "domain": "time and destruction of evil",
    },
    "Lord Vishnu": {
        "titles": ["Narayana", "Hari"],
        "appearance": ["blue complexion", "royal divine appearance"],
        "symbols": ["Shankha", "Chakra", "Gada", "Padma"],
        "personality": ["preserving", "compassionate", "wise"],
        "vehicle": "Garuda",
        "domain": "preservation of the universe",
    },
}


def random_scene():
    god_name = random.choice(list(HINDU_DEITIES.keys()))
    deity = HINDU_DEITIES[god_name]

    return {
        "god": god_name,
        "titles": deity.get("titles", []),
        "appearance": deity.get("appearance", []),
        "symbols": deity.get("symbols", []),
        "personality": deity.get("personality", []),
        "vehicle": deity.get("vehicle"),
        "domain": deity.get("domain"),
        "environments": random.sample(ENVIRONMENTS, random.randint(1, 3)),
        "time_of_day": random.choice(TIMES),
        "weather": random.choice(WEATHER),
        "camera_angle": random.choice(CAMERA_ANGLES),
        "pose": random.choice(POSES),
        "lighting": random.sample(LIGHTING, random.randint(2, 4)),
        "color_palette": random.choice(COLOR_PALETTES),
        "art_style": random.choice(ART_STYLES),
        "background_details": random.sample(
            BACKGROUND_DETAILS,
            random.randint(5, 15)
        ),
        "seed": random.randint(1, 999999999),
    }
print(random_scene())
def get_prompt():
    rand_json = random_scene()
    

    PROMPT="""
    You are an elite Hindu Mythology Documentary Creator, Cinematic Story Director, AI Prompt Engineer, and Short-Form Content Writer.

    Your task is to generate a complete viral-ready short video package about a Hindu deity.

    You will receive the following JSON as input:

    {json_input}


    ==================================================
    OBJECTIVE
    =========

    Create a highly engaging 45-90 second cinematic video package that can be used to generate:

    1. AI Images
    2. AI Narration (TTS)
    3. Instagram Reels
    4. YouTube Shorts
    5. TikTok Videos

    The final output must tell a compelling visual story about the deity while remaining respectful to Hindu traditions and mythology.

    ==================================================
    CRITICAL RULES
    ==============

    * Return ONLY valid JSON.
    * No markdown.
    * No explanations.
    * No text before JSON.
    * No text after JSON.
    * Output must be machine-readable.
    * All fields are required.
    * Do not invent contradictory deity features.
    * Preserve the deity appearance throughout all scenes.
    * Preserve symbols throughout all scenes.
    * Preserve visual identity throughout all scenes.
    * Preserve color palette throughout all scenes.
    * Preserve lighting style throughout all scenes.
    * Preserve art style throughout all scenes.
    * Ensure visual continuity between scenes.
    * Every image prompt must feel like part of the same movie.

    ==================================================
    DEITY USAGE RULES
    =================

    The deity is:

    {god}

    Titles:

    {titles}

    Appearance:

    {appearance}

    Symbols:

    {symbols}

    Personality:

    {personality}

    Vehicle:

    {vehicle}

    Divine Domain:

    {domain}

    Every narration segment and image prompt must incorporate these characteristics naturally.

    ==================================================
    VISUAL STYLE RULES
    ==================

    Use:

    Environment:
    {environments}

    Time:
    {time_of_day}

    Weather:
    {weather}

    Camera Style:
    {camera_angle}

    Pose:
    {pose}

    Lighting:
    {lighting}

    Color Palette:
    {color_palette}

    Art Style:
    {art_style}

    Background Elements:
    {background_details}

    The above visual parameters must be woven naturally into every image prompt.

    ==================================================
    SCENE STRUCTURE
    ===============

    Generate exactly 5 scenes.

    Scene 1:
    Divine introduction.

    Scene 2:
    Reveal powers and personality.

    Scene 3:
    Show domain and cosmic influence.

    Scene 4:
    Show legendary mythological act or symbolic divine moment.

    Scene 5:
    Epic cinematic finale and blessing to humanity.

    Each scene should progressively increase in visual grandeur.

    ==================================================
    IMAGE PROMPT REQUIREMENTS
    =========================

    Generate exactly 5 image prompts.

    Each prompt must be 150-300 words.

    Each prompt must contain:

    * deity name
    * divine title
    * deity appearance
    * symbols
    * personality traits
    * environment
    * weather
    * lighting
    * color palette
    * background details
    * camera angle
    * cinematic framing
    * lens description
    * depth of field
    * atmosphere
    * sacred elements
    * mythological grandeur
    * ultra realism
    * masterpiece quality

    Every prompt should end with:

    "ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere"

    Do not use bullet points.

    Generate complete descriptive paragraphs.

    ==================================================
    NARRATION REQUIREMENTS
    ======================

    Generate exactly 5 narration segments.

    Each segment should:

    * Match the corresponding scene.
    * Flow naturally into the next segment.
    * Sound like a Netflix mythological documentary.
    * Be emotionally powerful.
    * Be spiritually uplifting.
    * Be historically respectful.
    * Avoid repetition.
    * MUST BE IN HINDI (written in Devanagari script). The narration text (the 'text' field under 'audio_segments') must be written in beautiful, fluent, and dramatic Hindi.

    Total narration length:
    45-90 seconds.

    ==================================================
    DESCRIPTION REQUIREMENTS
    ========================

    Generate:

    1. A powerful title in Hindi (using Devanagari script).
    2. A viral social media description in Hindi (using Devanagari script).
    3. SEO keywords.
    4. Relevant hashtags.

    * The 'title' and 'description' fields MUST be written in Hindi (using Devanagari script) or a mix of Hindi and English.
    * The 'image_prompts' MUST be written in English because image generators only understand English.


    ==================================================
    OUTPUT JSON SCHEMA
    ==================

    {
    "title": "",
    "deity": "",
    "description": "",
    "seo_keywords": [],
    "hashtags": [],
    "duration_seconds": 60,

    "audio_segments": [
    {
    "scene": 1,
    "title": "",
    "text": "",
    "start_time_seconds": 0,
    "end_time_seconds": 12,
    "duration_seconds": 12
    },
    {
    "scene": 2,
    "title": "",
    "text": "",
    "start_time_seconds": 12,
    "end_time_seconds": 24,
    "duration_seconds": 12
    },
    {
    "scene": 3,
    "title": "",
    "text": "",
    "start_time_seconds": 24,
    "end_time_seconds": 36,
    "duration_seconds": 12
    },
    {
    "scene": 4,
    "title": "",
    "text": "",
    "start_time_seconds": 36,
    "end_time_seconds": 48,
    "duration_seconds": 12
    },
    {
    "scene": 5,
    "title": "",
    "text": "",
    "start_time_seconds": 48,
    "end_time_seconds": 60,
    "duration_seconds": 12
    }
    ],

    "image_prompts": [
    {
    "scene": 1,
    "prompt": ""
    },
    {
    "scene": 2,
    "prompt": ""
    },
    {
    "scene": 3,
    "prompt": ""
    },
    {
    "scene": 4,
    "prompt": ""
    },
    {
    "scene": 5,
    "prompt": ""
    }
    ]
    }

    Return only the JSON object and nothing else.
    """
    
    PROMPT = PROMPT.replace("{json_input}", json.dumps(rand_json, indent=4))
    PROMPT = PROMPT.replace("{god}", str(rand_json.get('god', '')))
    PROMPT = PROMPT.replace("{titles}", str(rand_json.get('titles', [])))
    PROMPT = PROMPT.replace("{appearance}", str(rand_json.get('appearance', [])))
    PROMPT = PROMPT.replace("{symbols}", str(rand_json.get('symbols', [])))
    PROMPT = PROMPT.replace("{personality}", str(rand_json.get('personality', [])))
    PROMPT = PROMPT.replace("{vehicle}", str(rand_json.get('vehicle', '')))
    PROMPT = PROMPT.replace("{domain}", str(rand_json.get('domain', '')))
    
    PROMPT = PROMPT.replace("{environments}", str(rand_json.get('environments', [])))
    PROMPT = PROMPT.replace("{time_of_day}", str(rand_json.get('time_of_day', '')))
    PROMPT = PROMPT.replace("{weather}", str(rand_json.get('weather', '')))
    PROMPT = PROMPT.replace("{camera_angle}", str(rand_json.get('camera_angle', '')))
    PROMPT = PROMPT.replace("{pose}", str(rand_json.get('pose', '')))
    PROMPT = PROMPT.replace("{lighting}", str(rand_json.get('lighting', [])))
    PROMPT = PROMPT.replace("{color_palette}", str(rand_json.get('color_palette', '')))
    PROMPT = PROMPT.replace("{art_style}", str(rand_json.get('art_style', '')))
    PROMPT = PROMPT.replace("{background_details}", str(rand_json.get('background_details', [])))
    
    return PROMPT

print(get_prompt())

def generate_god_scene_prompt():
    return {
        "system_prompt": get_prompt(),
        "human_prompt": """Please generate a json with the following structure and I am attaching an example with this 
         
        
        json structure:
        {
    "title": "महादेव: ब्रह्मांडीय परिवर्तन के शाश्वत स्रोत",
    "deity": "Lord Shiva",
    "description": "माउंट कैलाश की रहस्यमयी ऊंचाइयों में कदम रखें और भगवान शिव की अनंत महिमा का दर्शन करें, जिन्हें ब्रह्मांड में महादेव के रूप में जाना जाता है। इस सिनेमाई वृत्तचित्र यात्रा में सर्वोच्च योगी के प्राचीन प्रतीकों, अलौकिक लोकों और कालातीत ज्ञान की खोज करें। #Mahadev #LordShiva #HinduMythology #SpiritualJourney #CosmicEnergy #ShivaTandava #DivinePower",
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
            "title": "मौन अवतरण",
            "text": "माउंट कैलाश की जमी हुई, अनंत चोटियों के बीच, एक प्राचीन स्थिरता पृथ्वी को जकड़े हुए है। यहाँ, पवित्र धुंध में लिपटे हुए, सर्वोच्च चेतना प्रकट होती है: महादेव, परिवर्तन के महान स्वामी।",
            "start_time_seconds": 0,
            "end_time_seconds": 12,
            "duration_seconds": 12
        },
        {
            "scene": 2,
            "title": "योगी का प्रभामंडल",
            "text": "उनकी नीली-धूसर त्वचा पवित्र भस्म से ढकी है, जो अस्तित्व की नश्वरता का एक स्पष्ट प्रमाण है। एक शांत, ध्यानमग्न ध्यान के साथ जो बदलते आयामों को स्थिर करता है, उनका तीसरा नेत्र बंद रहता है, जो ब्रह्मांडीय ऊर्जा के अनंत कुएं को रोके हुए है।",
            "start_time_seconds": 12,
            "end_time_seconds": 24,
            "duration_seconds": 12
        },
        {
            "scene": 3,
            "title": "ब्रह्मांडीय संतुलन के स्वामी",
            "text": "उनके मस्तक पर चांदी का अर्धचंद्र विराजमान है, जो स्वयं समय के प्रवाह को नियंत्रित करता है। जैसे ही गंगा की पवित्र धारा उनकी जटाओं से बहती है, राजसी बैल नंदी अपने स्वामी के शाश्वत, पारलौकिक क्षेत्र की रखवाली करता है।",
            "start_time_seconds": 24,
            "end_time_seconds": 36,
            "duration_seconds": 12
        },
        {
            "scene": 4,
            "title": "धर्म का शस्त्र",
            "text": "अचानक, अंतरिक्ष में एक गहरा बदलाव गूंजता है। अपने हाथों में, वे पवित्र त्रिशूल उठाते हैं, वह ब्रह्मांडीय त्रिशूल जो भ्रम को चकनाचूर कर देता है, जबकि एक रहस्यमयी सांप उनके गले के चारों ओर धीरे-धीरे घूमता है, जो मृत्यु पर पूर्ण विजय का प्रतीक है।",
            "start_time_seconds": 36,
            "end_time_seconds": 48,
            "duration_seconds": 12
        },
        {
            "scene": 5,
            "title": "परम कृपा",
            "text": "जैसे ही स्वर्ग खुलता है, एक शानदार दिव्य प्रभामंडल पर्वत की चोटी को आलोकित करता है। अनंत करुणा के साथ, भोलेनाथ अपना हाथ एक शाश्वत आशीर्वाद में बढ़ाते हैं, भौतिक संसार में शांति और परिवर्तन की लहरें भेजते हैं।",
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


        
    }