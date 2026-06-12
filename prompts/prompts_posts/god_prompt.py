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

def generate_god_scene_prompt():
    scene = random_scene()

    prompt = (
    f"A breathtaking, highly detailed {scene['art_style']} masterpiece depicting the divine presence of {scene['god']}, "
    f"known as {', '.join(scene['titles'])}. "
    
    f"The deity is portrayed with {', '.join(scene['appearance'])}, "
    f"radiating a {', '.join(scene['personality'])} aura. "
    f"In their hands, they wield sacred {', '.join(scene['symbols'])}, "
    f"symbolizing their immense cosmic power. "
    
    f"The environment is awe-inspiring: {', '.join(scene['environments'])} "
    f"bathed in the ethereal light of {scene['time_of_day']}, "
    f"complemented by {scene['weather']} atmospheric conditions. "
    
    f"The composition uses a {scene['camera_angle']} perspective, capturing the deity in a {scene['pose']} stance. "
    
    f"Dramatic lighting, featuring {', '.join(scene['lighting'])}, "
    f"casts deep shadows and brilliant highlights, "
    f"enhancing the visual impact with a striking {scene['color_palette']} color palette. "
    
    f"The intricate background reveals {', '.join(scene['background_details'])}, "
    f"adding extreme depth and lore to the scene. "
    
    f"Rendered in ultra-high resolution (8k, unreal engine 5, octane render style) "
    f"with volumetric lighting, cinematic depth of field, and hyper-realistic textures. "
    f"Use seed {scene['seed']} for reproducibility."

    f"A dramatic {scene['art_style']} portrayal of {scene['god']}, "
    f"featuring {', '.join(scene['symbols'])} "
    f"in a {scene['weather']} {scene['time_of_day']} setting."
    
    f"I want the output in the json format that should have the outptut in the following format: "
    f"{{ 'prompt': prompt, 'description': description }}"  
    )
    prompt_2=(
    f"A breathtaking, highly detailed {scene['art_style']} masterpiece capturing the transcendent presence of {scene['god']}, "
    f"reverently known as {', '.join(scene['titles'])}. The deity manifests physically with {', '.join(scene['appearance'])}, "
    f"radiating a profoundly {', '.join(scene['personality'])} aura that dominates the frame. In their hands, they command "
    f"the sacred {', '.join(scene['symbols'])}, localized conduits of their immense cosmic power. "
    f"The surrounding environment is awe-inspiring: an expansive domain of {', '.join(scene['environments'])} "
    f"bathed in the ethereal, otherworldly light of {scene['time_of_day']}, layered with dense {scene['weather']} atmospheric conditions. "
    f"The composition leverages a dramatic {scene['camera_angle']} perspective, dynamic framing, and isolates the deity in a "
    f"strikingly {scene['pose']} stance. Masterful, cinematic lighting featuring {', '.join(scene['lighting'])} sculpts the form with "
    f"deep, deliberate shadows and brilliant, piercing highlights, all unified by a vivid {scene['color_palette']} color palette. "
    f"Deep within the composition, the intricate background reveals rich lore through {', '.join(scene['background_details'])}, "
    f"adding immense narrative depth. Rendered in ultra-high resolution (8k, unreal engine 5, octane render style) with precise "
    f"volumetric lighting, an anamorphic cinematic depth of field, and hyper-realistic micro-textures. Use seed {scene['seed']} for structural reproducibility. "
    f"Summary: A dramatic {scene['art_style']} vision of {scene['god']} commanding {', '.join(scene['symbols'])} amidst a {scene['weather']} {scene['time_of_day']} backdrop. "
    f"Output requested strictly in JSON format matching the schema: {{'prompt': ' this will be used for generating a image so please generate a detailed prompt and make sure it is descriptive and actionable. I should provide a clear and specific description of the scene, including the main subject, setting, and artistic elements.', 'description': 'It will be used for instagram so use max 10 words and use relevant hashtags for better seo reach'}}"
    )

    return prompt_2
print(generate_god_scene_prompt())