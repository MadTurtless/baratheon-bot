import io
from PIL import Image, ImageDraw, ImageFont


def create_profile_card(username: str, level: int, current_xp: int, next_lvl_xp: int, previous_xp_needed: int) -> io.BytesIO:
    width, height = 600, 200

    bg_path = "src/assets/images/profile-bg.png"
    font_path = "src/assets/fonts/Ancient Medium.ttf"

    try:
        background = Image.open(str(bg_path)).convert("RGB")
        image = background.resize((width, height), Image.Resampling.LANCZOS)
    except IOError:
        print(f"Could not find background image at {bg_path}, using fallback.")
        image = Image.new("RGB", (width, height), (24, 25, 28))

    draw = ImageDraw.Draw(image)

    try:
        font_title = ImageFont.truetype(str(font_path), 32)
        font_sub = ImageFont.truetype(str(font_path), 24)
    except IOError:
        font_title = font_sub = ImageFont.load_default()

    draw.text((40, 40), username, fill=(217, 195, 56), font=font_title)
    draw.text((40, 80), f"Level {level}", fill=(181, 163, 51), font=font_sub)
    draw.text((430, 80), f"{current_xp} / {next_lvl_xp} XP", fill=(255, 255, 255), font=font_sub)

    draw.text((40, 150), f"{previous_xp_needed}", fill=(255, 255, 255), font=font_sub)
    draw.text((560, 150), f"{next_lvl_xp}", fill=(255, 255, 255), font=font_sub, anchor="ra")
    bar_x1, bar_y1 = 40, 120
    bar_x2, bar_y2 = 560, 145
    bar_width = bar_x2 - bar_x1

    xp_ratio = min((current_xp - previous_xp_needed) / (next_lvl_xp - previous_xp_needed), 1.0) if next_lvl_xp > 0 else 0
    fill_width = int(bar_width * xp_ratio)

    draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=12, fill=(20, 20, 20, 180))

    if fill_width > 0:
        draw.rounded_rectangle([bar_x1, bar_y1, bar_x1 + fill_width, bar_y2], radius=12, fill=(217, 195, 56))

    image_binary = io.BytesIO()
    image.save(image_binary, "PNG")
    image_binary.seek(0)

    return image_binary
