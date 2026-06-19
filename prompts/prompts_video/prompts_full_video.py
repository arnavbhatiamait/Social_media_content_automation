import random
import json

# Import resources from the existing prompts file to maintain visual/deity consistency
from prompts.prompts_video.prompts_video import (
    HINDU_DEITIES,
    ENVIRONMENTS,
    TIMES,
    WEATHER,
    CAMERA_ANGLES,
    POSES,
    LIGHTING,
    COLOR_PALETTES,
    ART_STYLES,
    BACKGROUND_DETAILS,
    random_scene
)

def get_full_video_prompt(deity_input_json: dict = None) -> str:
    """
    Returns the system prompt instructing the LLM to output a 10-scene, 
    full-length video configuration in JSON format.
    """
    if deity_input_json is None:
        deity_input_json = random_scene()

    PROMPT = """
    You are an elite Hindu Mythology Documentary Creator, Cinematic Story Director, AI Prompt Engineer, and Long-Form Content Writer.

    Your task is to generate a complete viral-ready long-form documentary video package about a Hindu deity.

    You will receive the following JSON as input describing the target deity and stylistic variables:

    {json_input}

    ==================================================
    OBJECTIVE
    =========

    Create a highly engaging 100-180 second cinematic video package that can be used to generate:

    1. AI Images (10 total)
    2. AI Narration (TTS, 10 segments total)
    3. YouTube Documentary / Facebook Video
    4. Long-form Instagram Video / IG TV

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
    * Preserve the deity appearance throughout all scenes to maintain visual continuity.
    * Preserve symbols throughout all scenes.
    * Preserve visual identity throughout all scenes.
    * Preserve color palette throughout all scenes.
    * Preserve lighting style throughout all scenes.
    * Preserve art style throughout all scenes.
    * Ensure visual continuity between scenes. Every image prompt must feel like part of the same cinematic movie.

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
    Environment: {environments}
    Time: {time_of_day}
    Weather: {weather}
    Camera Style: {camera_angle}
    Pose: {pose}
    Lighting: {lighting}
    Color Palette: {color_palette}
    Art Style: {art_style}
    Background Elements: {background_details}

    The above visual parameters must be woven naturally into every image prompt.

    ==================================================
    SCENE STRUCTURE
    ===============

    Generate exactly 10 scenes.

    Scene 1: Divine introduction. Establish the deity's cosmic origins.
    Scene 2: Transition into the sacred realm. Establish the visual atmosphere.
    Scene 3: Reveal powers, weapons, and divine personality traits.
    Scene 4: Deepen the cosmic influence and connection to the universe.
    Scene 5: Portray the sacred wisdom, teachings, or meditative calm.
    Scene 6: Introduce a legendary conflict, mythological act, or cosmic task.
    Scene 7: Resolve the conflict with supreme mythological power and grandeur.
    Scene 8: Show the universe/nature acknowledging the divine presence.
    Scene 9: Epic cinematic crescendo (e.g. cosmic dance, intense blessing, ultimate form).
    Scene 10: Beautiful finale, ultimate blessing to devotees, and message of peace to humanity.

    Each scene should progressively increase in visual grandeur.

    ==================================================
    IMAGE PROMPT REQUIREMENTS
    =========================

    Generate exactly 10 image prompts (one for each scene).
    Each prompt must be 150-300 words.
    Each prompt must contain:
    * deity name and divine title
    * deity appearance and specific symbols (wielded or in scene)
    * personality traits
    * environment and weather
    * lighting and color palette
    * background details
    * camera angle and cinematic framing
    * lens description and depth of field
    * atmosphere (sacred elements, mythological grandeur)
    * ultra realism, masterpiece quality

    Every prompt should end with:
    "ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere"

    Do not use bullet points. Generate complete descriptive paragraphs.

    ==================================================
    NARRATION REQUIREMENTS
    ======================

    Generate exactly 10 narration segments.
    Each segment should:
    * Match the corresponding scene and image.
    * Flow naturally into the next segment.
    * Sound like a Netflix mythological documentary.
    * Be emotionally powerful, spiritually uplifting, and historically respectful.
    * Avoid repetition.
    * MUST BE IN HINDI (written in Devanagari script). The narration text (the 'text' field under 'audio_segments') must be written in beautiful, fluent, and dramatic Hindi.

    Total narration length: 100-180 seconds. (Each scene should be ~12 seconds of speech).

    ==================================================
    DESCRIPTION REQUIREMENTS
    ========================

    Generate:
    1. A powerful title in Hindi (using Devanagari script).
    2. A viral social media description suitable for YouTube/Facebook in Hindi (using Devanagari script).
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
      "duration_seconds": 120,

      "audio_segments": [
        {
          "scene": 1,
          "title": "Title 1",
          "text": "Narration text...",
          "start_time_seconds": 0,
          "end_time_seconds": 12,
          "duration_seconds": 12
        },
        ...
        {
          "scene": 10,
          "title": "Title 10",
          "text": "Narration text...",
          "start_time_seconds": 108,
          "end_time_seconds": 120,
          "duration_seconds": 12
        }
      ],

      "image_prompts": [
        {
          "scene": 1,
          "prompt": "Detailed image prompt..."
        },
        ...
        {
          "scene": 10,
          "prompt": "Detailed image prompt..."
        }
      ]
    }

    Return only the JSON object and nothing else.
    """

    PROMPT = PROMPT.replace("{json_input}", json.dumps(deity_input_json, indent=4))
    PROMPT = PROMPT.replace("{god}", str(deity_input_json.get('god', '')))
    PROMPT = PROMPT.replace("{titles}", str(deity_input_json.get('titles', [])))
    PROMPT = PROMPT.replace("{appearance}", str(deity_input_json.get('appearance', [])))
    PROMPT = PROMPT.replace("{symbols}", str(deity_input_json.get('symbols', [])))
    PROMPT = PROMPT.replace("{personality}", str(deity_input_json.get('personality', [])))
    PROMPT = PROMPT.replace("{vehicle}", str(deity_input_json.get('vehicle', '')))
    PROMPT = PROMPT.replace("{domain}", str(deity_input_json.get('domain', '')))
    
    PROMPT = PROMPT.replace("{environments}", str(deity_input_json.get('environments', [])))
    PROMPT = PROMPT.replace("{time_of_day}", str(deity_input_json.get('time_of_day', '')))
    PROMPT = PROMPT.replace("{weather}", str(deity_input_json.get('weather', '')))
    PROMPT = PROMPT.replace("{camera_angle}", str(deity_input_json.get('camera_angle', '')))
    PROMPT = PROMPT.replace("{pose}", str(deity_input_json.get('pose', '')))
    PROMPT = PROMPT.replace("{lighting}", str(deity_input_json.get('lighting', [])))
    PROMPT = PROMPT.replace("{color_palette}", str(deity_input_json.get('color_palette', '')))
    PROMPT = PROMPT.replace("{art_style}", str(deity_input_json.get('art_style', '')))
    PROMPT = PROMPT.replace("{background_details}", str(deity_input_json.get('background_details', [])))
    
    return PROMPT

def generate_god_scene_full_prompt():
    """
    Builds the complete dictionary of system prompt and human instruction
    for generating the 10-scene documentary JSON package.
    """
    return {
        "system_prompt": get_full_video_prompt(),
        "human_prompt": """Please generate a json with the following structure and I am attaching an example with this 
         
        json structure:
        {
          "title": "महादेव: ब्रह्मांडीय चेतना के दस आयाम",
          "deity": "Lord Shiva",
          "description": "माउंट कैलाश की रहस्यमयी ऊंचाइयों में कदम रखें और भगवान शिव की अनंत महिमा का दर्शन करें, जिन्हें ब्रह्मांड में महादेव के रूप में जाना जाता है। इस पूर्ण-लंबाई वाली सिनेमाई वृत्तचित्र यात्रा में सर्वोच्च योगी के प्राचीन प्रतीकों, अलौकिक लोकों और कालातीत ज्ञान की खोज करें। #Mahadev #LordShiva #HinduMythology #SpiritualJourney #CosmicEnergy #ShivaTandava #DivinePower",
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
          "duration_seconds": 120,
          "audio_segments": [
              {
                  "scene": 1,
                  "title": "अनंत उत्पत्ति",
                  "text": "समय और अंतरिक्ष के निर्माण से पहले, केवल एक अनंत शून्य था। इसी ब्रह्मांडीय मौन से सर्वोच्च चेतना, भगवान शिव का उदय हुआ, जो माउंट कैलाश की पवित्र ऊंचाइयों पर प्रकट हुए।",
                  "start_time_seconds": 0,
                  "end_time_seconds": 12,
                  "duration_seconds": 12
              },
              {
                  "scene": 2,
                  "title": "जमा हुआ गर्भगृह",
                  "text": "घनी बर्फ और पवित्र धुंध से घिरे कैलाश के बर्फीले पहाड़ शांत खड़े हैं। यहाँ, गोधूलि बेला की रोशनी में, शिव अपने शांत और अछूते गर्भगृह में निवास करते हैं।",
                  "start_time_seconds": 12,
                  "end_time_seconds": 24,
                  "duration_seconds": 12
              },
              {
                  "scene": 3,
                  "title": "योगी का स्वरूप",
                  "text": "उनकी नीली-धूसर त्वचा पवित्र भस्म से ढकी है, जो सभी सांसारिक चीजों की नश्वरता को दर्शाती है। जटाओं और मस्तक को सुशोभित करते चांदी के अर्धचंद्र के साथ, वे एक शांत शक्ति का संचार करते हैं।",
                  "start_time_seconds": 24,
                  "end_time_seconds": 36,
                  "duration_seconds": 12
              },
              {
                  "scene": 4,
                  "title": "पावन नदी",
                  "text": "उनकी जटाओं से बहती हुई गंगा की पवित्र धारा पृथ्वी पर अवतरित होती है। पवित्रता की यह नदी मानवता के अज्ञान को धो देती है, जिससे आध्यात्मिक जागृति आती है।",
                  "start_time_seconds": 36,
                  "end_time_seconds": 48,
                  "duration_seconds": 12
              },
              {
                  "scene": 5,
                  "title": "मौन ध्यान",
                  "text": "गहन, अडिग ध्यान में लीन, सर्वोच्च योगी सभी बाहरी रचनाओं से विरक्त हैं। पूर्ण स्थिरता की इस अवस्था में, वे जीवन और मृत्यु की शक्तियों को संतुलित करते हैं।",
                  "start_time_seconds": 48,
                  "end_time_seconds": 60,
                  "duration_seconds": 12
              },
              {
                  "scene": 6,
                  "title": "बढ़ता संघर्ष",
                  "text": "फिर भी, जब ब्रह्मांडीय व्यवस्था को अंधकारमय शक्तियों से खतरा होता है, तो शांत योगी का स्वरूप बदल जाता है। जब महान रुद्र हस्तक्षेप करने और दिव्य संतुलन बहाल करने की तैयारी करते हैं, तो पृथ्वी और स्वर्ग कांप उठते हैं।",
                  "start_time_seconds": 60,
                  "end_time_seconds": 72,
                  "duration_seconds": 12
              },
              {
                  "scene": 7,
                  "title": "विनाश का त्रिशूल",
                  "text": "अचानक एक तीव्र गति के साथ, शिव अपना पराक्रमी त्रिशूल उठाते हैं। स्वर्ण त्रिशूल दिव्य ऊर्जा के साथ चमकता है, भ्रम को भेदते हुए पूरी सृष्टि के अहंकार को नष्ट कर देता है।",
                  "start_time_seconds": 72,
                  "end_time_seconds": 84,
                  "duration_seconds": 12
              },
              {
                  "scene": 8,
                  "title": "डम-डम डमरू की ताल",
                  "text": "वे पवित्र डमरू बजाते हैं। इसकी ब्रह्मांडीय तरंगें आकाशगंगाओं में गूंजती हैं, ॐ की आदिम ध्वनि का निर्माण करती हैं, और स्वयं वास्तविकता के ताने-बाने को पुनर्गठित करती हैं।",
                  "start_time_seconds": 84,
                  "end_time_seconds": 96,
                  "duration_seconds": 12
              },
              {
                  "scene": 9,
                  "title": "तांडव नृत्य",
                  "text": "सूर्य ग्रहण के दिव्य प्रकाश में, शिव तांडव करते हैं, जो ब्रह्मांडीय विनाश और पुनर्जन्म का नृत्य है। प्रत्येक कदम नए युग की शुरुआत का मार्ग प्रशस्त करने के लिए पुरानी दुनिया को ध्वस्त कर देता है।",
                  "start_time_seconds": 96,
                  "end_time_seconds": 108,
                  "duration_seconds": 12
              },
              {
                  "scene": 10,
                  "title": "दिव्य अनुग्रह",
                  "text": "जैसे ही तूफान थमता है, महादेव के चारों ओर एक गर्म सुनहरा प्रभामंडल छा जाता है। परम सुरक्षा के भाव में अपना हाथ बढ़ाते हुए, भोलेनाथ ब्रह्मांड पर अपनी कृपा और शाश्वत शांति की वर्षा करते हैं।",
                  "start_time_seconds": 108,
                  "end_time_seconds": 120,
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
                  "prompt": "An ultra-realistic, cinematic movie frame of Lord Shiva, portraying the serene Kailash sanctuary in early morning mist. The setting is surrounded by mountains and frozen waterfalls, with temple bells in the background. A wide landscape shot captures the vast, divine scale of the snowy kingdom. Ethereal lighting creates dramatic shadows. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 3,
                  "prompt": "A chest up cinematic portrait of Lord Shiva, displaying his long matted locks, the crescent moon glowing softly in his hair, and the sacred cobra snake wrapped around his neck. The lighting is cinematic temple lamp light casting a golden rim light. The color palette features warm golds and deep blues. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 4,
                  "prompt": "A cinematic over the shoulder shot showing the holy River Ganga cascading in glowing golden streams from Shiva's matted hair. Ethereal light highlights the sacred water droplets. The background details ancient rocks and floating lotus flowers. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 5,
                  "prompt": "A full body shot of Lord Shiva meditating on a tiger skin garment in a hidden cave temple. The scene is illuminated by temple lamps and a soft cosmic energy glow. The pose is classic padmasana, showing deep, meditative peace. Deep, rich shadows fill the cave. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 6,
                  "prompt": "A dramatic low angle shot of Lord Shiva standing on the edge of a mountain cliff as a celestial storm approaches. Swirling dark clouds and lightning bolts crackle in the sky, reflecting a fierce, powerful expression on the deity's face. Volumetric god rays highlight the dramatic composition. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 7,
                  "prompt": "A dynamic action camera shot of Lord Shiva wielding his golden Trishul (trident) which emits waves of electric blue celestial energy. The background shows ancient architectures collapsing into dust, representing the destruction of illusion. Gold and crimson color palette. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 8,
                  "prompt": "A cinematic medium close up of Lord Shiva holding the Damaru drum, its vibrations creating concentric golden sound waves in the air. Volumetric rays of temple lamp light pierce through sacred ash particles in the air. Ethereal, mystical atmosphere. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 9,
                  "prompt": "An epic cinematic frame of Lord Shiva performing the cosmic Tandava dance, surrounded by a halo of divine fire. The camera angle is an ultra-wide bird's eye view. The color palette features intense reds, golds, and violets. The background is a starry universe with nebulae. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              },
              {
                  "scene": 10,
                  "prompt": "The final scene showing Lord Shiva in a peaceful standing pose, extending his hand in a blessing to devotees. A bright golden aura radiates from him under a cosmic dawn. Floating petals and glowing fireflies fill the air. Warm, compassionate colors. Ultra detailed, masterpiece, award winning photography, volumetric lighting, cinematic composition, ultra realistic textures, mythological epic, 8k, HDR, IMAX quality, divine atmosphere."
              }
          ]
        }

        Please generate a detailed prompt and description based on the above system prompt. Ensure the output is a properly formatted JSON that can be easily parsed.
        """
    }
