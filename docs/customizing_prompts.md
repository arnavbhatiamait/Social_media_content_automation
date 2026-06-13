# ✍️ Customizing Prompts & Queue Guide

This guide describes how the automation queue works, how dynamic prompts are generated, and how you can customize the deity attributes and visual art themes.

---

## 📋 File-Based Prompt Queue (`video_prompts.txt`)

The project supports running queue-based automated runs (ideal for schedule/cron triggers). This is managed via the **`video_prompts.txt`** file in the project root:

```plaintext
# [PROCESSED] Lord Shiva
Lord Krishna
Lord Hanuman
Lord Ganesha
Goddess Lakshmi
```

### Queue Logic
1.  On execution (without CLI `--prompt` parameters), the pipeline reads `video_prompts.txt`.
2.  It parses the file line-by-line, skipping empty lines and lines starting with `#`.
3.  It selects the **first unprocessed line** (e.g., `Lord Krishna`).
4.  It marks that line as processed: `# [PROCESSED] Lord Krishna`.
5.  It writes the updated queue file back to disk.
6.  The chosen string is sent into the generation pipeline.

---

## 🔮 Dynamic Prompt Generator

When the pipeline receives a prompt name (either from CLI or the queue file), it checks if it matches any of the registered deities.

### 1. Deity Match
If the prompt matches a key in the `HINDU_DEITIES` dictionary:
*   The script extracts all attributes: **Titles**, **Appearance**, **Symbols**, **Personality**, **Vehicle**, and **Divine Domain**.
*   It randomly samples values from the design databases: **Environments**, **Times**, **Weather**, **Camera Angles**, **Poses**, **Lighting**, **Color Palettes**, **Art Styles**, and **Background Details**.
*   It compiles these attributes into a structured instruction set for the LLM.

### 2. Custom Text Prompt
If the prompt does **not** match any registered deity, the script treats the input as a custom prompt. It bypasses the randomizer and sends the raw custom prompt directly to the LLM.

---

## 🛠️ How to Customize Deities & Visuals

You can customize the characteristics of existing deities or add brand new ones by modifying the Python source files:
*   **Video Prompts Database**: `prompts/prompts_video/prompts_video.py`
*   **Image Posts Database**: `prompts/prompts_posts/god_prompt.py`

### 1. Adding or Editing a Deity
Open the target file and edit the `HINDU_DEITIES` dictionary. For example, to add *Lord Vishnu*:

```python
HINDU_DEITIES = {
    # Existing deities...
    "Lord Vishnu": {
        "titles": ["Narayana", "Hari"],
        "appearance": ["blue complexion", "royal divine appearance"],
        "symbols": ["Shankha", "Chakra", "Gada", "Padma"],
        "personality": ["preserving", "compassionate", "wise"],
        "vehicle": "Garuda",
        "domain": "preservation of the universe",
    },
}
```

### 2. Changing Visual Styles & Themes
If you want to shift the visual direction of generated images (e.g., from classical Indian fine art to cyberpunk, digital art, or pencil sketch styles), edit the randomizer lists:

```python
ART_STYLES = [
    "Cyberpunk Digital Render",       # Added custom style
    "Watercolor Painting",            # Added custom style
    "Hyper Realistic Photography",
    "Cinematic Movie Frame",
    # ...
]

ENVIRONMENTS = [
    "Neon City Skyline",              # Custom environment
    "Mount Kailash",
    # ...
]
```

---

## 🧠 LLM Prompts & Schemas

The LLM is instructed to return a strictly structured JSON response.

### Video Generation Schema (`prompts_video.py`)
Generates 5 distinct, sequential scenes detailing a cinematic narrative journey:

```json
{
  "title": "Mahadev: The Eternal Source of Cosmic Transformation",
  "deity": "Lord Shiva",
  "description": "...",
  "seo_keywords": ["Lord Shiva", "Mahadev", ...],
  "hashtags": ["Mahadev", "LordShiva", ...],
  "duration_seconds": 60,
  "audio_segments": [
    {
      "scene": 1,
      "title": "The Silent Descent",
      "text": "Deep within the frozen, timeless peaks of Mount Kailash...",
      "start_time_seconds": 0,
      "end_time_seconds": 12,
      "duration_seconds": 12
    }
    // Scene 2, 3, 4, 5...
  ],
  "image_prompts": [
    {
      "scene": 1,
      "prompt": "An epic, photorealistic digital painting capturing Lord Shiva..."
    }
    // Prompts for Scene 2, 3, 4, 5...
  ]
}
```

### Image Post Schema (`god_prompt.py`)
Generates single-image posts:

```json
{
  "prompt": "Detailed descriptive prompt containing subject, lighting, and composition details...",
  "description": "Short caption for Instagram with hashtags (max 10 words)..."
}
```
