import io
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_profile_card(username: str, level: int, current_xp: int, next_lvl_xp: int) -> io.BytesIO:
    # Target dimensions for the card
    width, height = 600, 200

    # 1. Load the background image using your absolute path trick
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 2. Step up out of 'classes' into 'src', then go into 'assets'
    # This results in: /home/ubuntu/baratheon-bot/src/assets/profile_bg.png
    BG_PATH = "src/assets/images/profile-bg.png"
    FONT_PATH = "src/assets/fonts/Ancient Medium.ttf"

    try:
        # Open the image and resize it to fit our dimensions perfectly
        background = Image.open(str(BG_PATH)).convert("RGB")
        image = background.resize((width, height), Image.Resampling.LANCZOS)
    except IOError:
        # Fallback to solid color if the image file is missing
        print(f"Could not find background image at {BG_PATH}, using fallback.")
        image = Image.new("RGB", (width, height), (24, 25, 28))

    # 2. Attach our drawing tool to the loaded image
    draw = ImageDraw.Draw(image)

    # 3. Load Fonts
    try:
        font_title = ImageFont.truetype(str(FONT_PATH), 32)
        font_sub = ImageFont.truetype(str(FONT_PATH), 24)
    except IOError:
        font_title = font_sub = ImageFont.load_default()

    # 4. Draw Text (White text usually pops best on custom backgrounds)
    draw.text((40, 40), username, fill=(217, 195, 56), font=font_title)
    draw.text((40, 80), f"Level {level}", fill=(181, 163, 51), font=font_sub)
    draw.text((430, 80), f"{current_xp} / {next_lvl_xp} XP", fill=(255, 255, 255), font=font_sub)

    # 5. Progress Bar Math
    bar_x1, bar_y1 = 40, 120
    bar_x2, bar_y2 = 560, 145
    bar_width = bar_x2 - bar_x1

    xp_ratio = min(current_xp / next_lvl_xp, 1.0) if next_lvl_xp > 0 else 0
    fill_width = int(bar_width * xp_ratio)

    # 6. Draw Progress Bar
    # Tip: Darken the background bar slightly so it's visible over busy images
    draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=12, fill=(20, 20, 20, 180))

    if fill_width > 0:
        draw.rounded_rectangle([bar_x1, bar_y1, bar_x1 + fill_width, bar_y2], radius=12, fill=(217, 195, 56))

    # 7. Save to memory
    image_binary = io.BytesIO()
    image.save(image_binary, "PNG")
    image_binary.seek(0)

    return image_binary
