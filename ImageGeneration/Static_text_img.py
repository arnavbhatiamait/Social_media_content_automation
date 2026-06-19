import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys
# Ensure the project root is in sys.path for local package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
from logs_setup.logger import Logger

logger=Logger(name="static Image Logger",log_file="logs/static_image_logger.log").get_logger()


class SocialMediaPostGenerator:

    THEMES = [
        {"bg":"#0F172A","title":"#38BDF8","text":"#FFFFFF"},
        {"bg":"#1E1B4B","title":"#A78BFA","text":"#FFFFFF"},
        {"bg":"#052E16","title":"#4ADE80","text":"#FFFFFF"},
        {"bg":"#7F1D1D","title":"#F87171","text":"#FFFFFF"},
        {"bg":"#18181B","title":"#FACC15","text":"#FFFFFF"},
        {"bg":"#111827","title":"#60A5FA","text":"#F9FAFB"},
        {"bg":"#172554","title":"#93C5FD","text":"#FFFFFF"},
        {"bg":"#14532D","title":"#86EFAC","text":"#FFFFFF"},
        {"bg":"#4A044E","title":"#E879F9","text":"#FFFFFF"},
        {"bg":"#581C87","title":"#C084FC","text":"#FFFFFF"},
        {"bg":"#7C2D12","title":"#FB923C","text":"#FFFFFF"},
        {"bg":"#0C4A6E","title":"#67E8F9","text":"#FFFFFF"},
        {"bg":"#3F3F46","title":"#F4F4F5","text":"#FFFFFF"},
        {"bg":"#1F2937","title":"#FBBF24","text":"#FFFFFF"},
        {"bg":"#365314","title":"#BEF264","text":"#FFFFFF"},
        {"bg":"#4C0519","title":"#FB7185","text":"#FFFFFF"},
        {"bg":"#431407","title":"#FDBA74","text":"#FFFFFF"},
        {"bg":"#082F49","title":"#7DD3FC","text":"#FFFFFF"},
        {"bg":"#2E1065","title":"#DDD6FE","text":"#FFFFFF"},
        {"bg":"#134E4A","title":"#99F6E4","text":"#FFFFFF"},
    ]

    GRADIENTS = [
        ("#0F172A", "#1E293B"),
        ("#7C3AED", "#2563EB"),
        ("#DC2626", "#F97316"),
        ("#16A34A", "#06B6D4"),
        ("#9333EA", "#EC4899"),
        ("#0EA5E9", "#14B8A6"),
        ("#F59E0B", "#EF4444"),
        ("#4F46E5", "#7C3AED"),
        ("#059669", "#0EA5E9"),
        ("#111827", "#374151"),
    ]

    LAYOUTS = [
        "center",
        "left",
        "quote"
    ]

    FONTS = [
        "fonts/Poppins-Regular.ttf",
        "fonts/Poppins-Bold.ttf",
        # "fonts/Montserrat-Regular.ttf",
        # "fonts/Montserrat-Bold.ttf",
        # "fonts/Roboto-Regular.ttf",
        # "fonts/Roboto-Bold.ttf",
        # "fonts/OpenSans-Regular.ttf",
        # "fonts/OpenSans-Bold.ttf",
        "fonts/Lato-Regular.ttf",
        "fonts/Lato-Bold.ttf",
        # "fonts/Inter-Regular.ttf",
        # "fonts/Inter-Bold.ttf",
        # "fonts/Oswald-Regular.ttf",
        # "fonts/PlayfairDisplay-Regular.ttf",
        # "fonts/Raleway-Regular.ttf",
        # "fonts/Nunito-Regular.ttf",
        # "fonts/Merriweather-Regular.ttf",
        "fonts/BebasNeue-Regular.ttf",
        "fonts/Anton-Regular.ttf",
        # "fonts/SourceSansPro-Regular.ttf",
    ]

    def __init__(
        self,
        width=1080,
        height=1080,
        branding="@arnavbhatia"
    ):
        self.width = width
        self.height = height
        self.branding = branding
        logger.debug(f"Initialized SocialMediaPostGenerator with width={width}, height={height}, branding='{branding}'")

    def _hex_to_rgb(self, color):
        color = color.lstrip("#")
        logger.debug(f"Converting hex color '{color}' to RGB")
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    def _random_theme(self):
        theme = random.choice(self.THEMES)
        logger.debug(f"Selecting random theme ,theme name: {theme}")
        return theme

    def _random_layout(self):
        layout = random.choice(self.LAYOUTS)
        logger.debug(f"Selecting random layout ,layout name: {layout}")
        return layout

    def _random_font(self, size):

        available_fonts = [
            f for f in self.FONTS if Path(f).exists()
        ]

        if available_fonts:
            try:
                font = ImageFont.truetype(
                    random.choice(available_fonts),
                    size
                )
                logger.debug(f"Selected random font: {font}")
                return font
            except Exception as e:
                logger.error(f"Error occurred while loading font: {e}")
                pass

        return ImageFont.load_default()

    def _gradient_background(self):

        start_hex, end_hex = random.choice(
            self.GRADIENTS
        )

        start = self._hex_to_rgb(start_hex)
        end = self._hex_to_rgb(end_hex)

        img = Image.new(
            "RGB",
            (self.width, self.height)
        )

        draw = ImageDraw.Draw(img)
        logger.debug(f"Creating gradient background from {start_hex} to {end_hex}")

        for y in range(self.height):

            ratio = y / self.height

            r = int(
                start[0] * (1 - ratio)
                + end[0] * ratio
            )
            g = int(
                start[1] * (1 - ratio)
                + end[1] * ratio
            )
            b = int(
                start[2] * (1 - ratio)
                + end[2] * ratio
            )
            logger.debug(f"Drawing line at y={y} with color RGB({r}, {g}, {b})")
            draw.line(
                [(0, y), (self.width, y)],
                fill=(r, g, b)
            )

        return img

    def _solid_background(self, color):
        logger.debug(f"Creating solid background with color {color}")
        return Image.new(
            "RGB",
            (self.width, self.height),
            color
        )

    def create_post(
        self,
        title,
        body,
        output_file="post.png",
        use_gradient=True
    ):

        theme = self._random_theme()
        logger.debug(f"Selected theme for post: {theme}")
        if use_gradient:
            img = self._gradient_background()
        else:
            img = self._solid_background(
                theme["bg"]
            )

        draw = ImageDraw.Draw(img)

        title_font = self._random_font(90)
        body_font = self._random_font(50)
        branding_font = self._random_font(35)

        layout = self._random_layout()
        logger.debug(f"Using layout: {layout}")

        wrapped_body = "\n".join(
            textwrap.wrap(body, width=30)
        )

        if layout == "left":

            draw.text(
                (80, 100),
                title.upper(),
                font=title_font,
                fill=theme["title"]
            )

            draw.line(
                (80, 240, 1000, 240),
                fill=theme["title"],
                width=4
            )

            draw.multiline_text(
                (80, 300),
                wrapped_body,
                font=body_font,
                fill=theme["text"],
                spacing=15
            )
            logger.debug(f"Drawn text for 'left' layout with title '{title}' and body '{body}'")
        elif layout == "center":

            bbox = draw.textbbox(
                (0, 0),
                title,
                font=title_font
            )

            title_width = bbox[2] - bbox[0]

            draw.text(
                (
                    (self.width - title_width) / 2,
                    120
                ),
                title.upper(),
                font=title_font,
                fill=theme["title"]
            )

            draw.multiline_text(
                (150, 350),
                wrapped_body,
                font=body_font,
                fill=theme["text"],
                spacing=20,
                align="center"
            )
            logger.debug(f"Drawn text for 'center' layout with title '{title}' and body '{body}'")
        else:

            draw.text(
                (100, 250),
                '"',
                font=self._random_font(200),
                fill=theme["title"]
            )

            draw.multiline_text(
                (180, 250),
                wrapped_body,
                font=body_font,
                fill=theme["text"],
                spacing=20
            )

        draw.text(
            (80, self.height - 80),
            self.branding,
            font=branding_font,
            fill=theme["text"]
        )
        logger.debug(f"Drawn branding text '{self.branding}' at the bottom of the post")
        img.save(output_file)

        logger.debug(f"Saved: {output_file}")
        logger.debug(f"Theme: {theme}")
        logger.debug(f"Layout: {layout}")


if __name__ == "__main__":

    generator = SocialMediaPostGenerator()

    generator.create_post(
        title="AI Automation",
        body="""
AI Agents are transforming businesses.

• Automate repetitive tasks
• Generate content automatically
• Handle customer support
• Improve productivity

Start building with AI today.
        """,
        output_file="ai_automation_post.png",
        use_gradient=True
    )