from PIL import Image, ImageDraw, ImageFont
import textwrap

W, H = 1080, 1080

img = Image.new("RGB", (W, H), "#0F172A")
draw = ImageDraw.Draw(img)

title_font = ImageFont.truetype("arial.ttf", 90)
body_font = ImageFont.truetype("arial.ttf", 50)

title = "AI AUTOMATION"
body = """
Save 20+ hours every week with AI Agents.

• Content Generation
• Lead Qualification
• Customer Support
• Meeting Scheduling

Start automating today.
"""

# Title
draw.text((80, 120), title, fill="#38BDF8", font=title_font)

# Divider
draw.line((80, 260, 1000, 260), fill="#38BDF8", width=4)

# Body
wrapped = "\n".join(textwrap.wrap(body, width=28))
draw.multiline_text(
    (80, 330),
    wrapped,
    fill="white",
    font=body_font,
    spacing=15
)

# Branding
draw.text(
    (80, 950),
    "@arnavbhatiamait",
    fill="#94A3B8",
    font=body_font
)

img.save("linkedin_post.png")