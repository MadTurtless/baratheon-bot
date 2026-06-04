import io
from PIL import Image, ImageDraw, ImageFont

async def create_leaderboard_card(ctx, users: list) -> io.BytesIO:
    width, height = 800, 600

    bg_path = "src/assets/images/profile-bg.png"
    font_path = "src/assets/fonts/Arial-Unicode-MS.ttf"

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

    for i in range(len(users)):
        u = users[i]
        y_offset = i * 110
        x_offset = 0

        if i > 4:
            x_offset = 400
            y_offset = (i - 5) * 110

        guild = ctx.guild
        user = guild.get_member(u[0])
        username = user.display_name
        level = u[2]
        xp = u[3]

        draw.text((40 + x_offset, 40 + y_offset), f"{i + 1}. {username}", fill=(217, 195, 56), font=font_title)
        if i != 9:
            draw.text((76 + x_offset, 75 + y_offset), f"Level {level}", fill=(181, 163, 51), font=font_sub)
            draw.text((76 + x_offset, 100 + y_offset), f"{xp} XP", fill=(217, 195, 56), font=font_sub)
        else:
            draw.text((93 + x_offset, 75 + y_offset), f"Level {level}", fill=(181, 163, 51), font=font_sub)
            draw.text((93 + x_offset, 100 + y_offset), f"{xp} XP", fill=(217, 195, 56), font=font_sub)


    image_binary = io.BytesIO()
    image.save(image_binary, "PNG")
    image_binary.seek(0)

    return image_binary
