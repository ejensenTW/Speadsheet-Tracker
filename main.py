from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw, ImageFont
import io
import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
SHEET_ID = os.getenv('SHEET_ID')
RANGE = os.getenv('RANGE')
MESSAGE_ID_FILE = os.getenv('MESSAGE_ID_FILE', 'message_id.txt')

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Setup Discord client
intents = discord.Intents.default()
client_bot = discord.Client(intents=intents)

def render_table_image(headers, rows):
    # Remove 'Notes' column
    if "Notes" in headers:
        note_index = headers.index("Notes")
        headers = [h for i, h in enumerate(headers) if i != note_index]
        rows = [[cell for i, cell in enumerate(row) if i != note_index] for row in rows]

    font = ImageFont.load_default()
    bold_font = ImageFont.load_default()
    line_height = 24
    padding = 10
    num_display_rows = 6

    # Pad rows if less than 6
    while len(rows) < num_display_rows:
        rows.append(["" for _ in headers])

    all_values = [headers] + rows
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*all_values)]
    col_widths = [max(w * 10, 80) for w in col_widths]

    img_width = sum(col_widths) + padding * 2
    img_height = (num_display_rows + 1) * line_height + padding * 2

    image = Image.new("RGB", (img_width, img_height), color="white")
    draw = ImageDraw.Draw(image)

    # Draw header row
    x = padding
    y = padding
    header_bg = (230, 230, 250)
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        draw.rectangle([x, y, x + width, y + line_height], fill=header_bg)
        draw.text((x + 5, y + 4), str(header), font=bold_font, fill="black")
        x += width

    y += line_height
    for row in rows:
        x = padding
        for i, (cell, width) in enumerate(zip(row, col_widths)):
            cell_str = str(cell)
            if headers[i].lower() == "need status":
                color_map = {
                    "Stocked": (144, 238, 144),
                    "Low": (255, 255, 153),
                    "Out of Stock": (255, 160, 122)
                }
                bg_color = color_map.get(cell_str, "white")
                draw.rectangle([x, y, x + width, y + line_height], fill=bg_color, outline="lightgray")
            else:
                draw.rectangle([x, y, x + width, y + line_height], outline="lightgray")
            draw.text((x + 5, y + 4), cell_str, font=font, fill="black")
            x += width
        y += line_height

    return image

async def update_sheet_message():
    await client_bot.wait_until_ready()
    channel = client_bot.get_channel(CHANNEL_ID)

    while not client_bot.is_closed():
        values = sheet.get_all_values()
        headers = values[0]
        rows = values[1:]

        # Remove empty rows entirely
        rows = [row for row in rows if any(cell.strip() for cell in row)]

        # Clear previous messages if needed
        try:
            with open(MESSAGE_ID_FILE, 'r') as f:
                ids = f.read().splitlines()
                for msg_id in ids:
                    try:
                        old_msg = await channel.fetch_message(int(msg_id))
                        await old_msg.delete()
                    except:
                        pass
        except FileNotFoundError:
            pass

        message_ids = []
        for i in range(0, len(rows), 6):
            chunk = rows[i:i+6]
            img = render_table_image(headers, chunk)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            file = discord.File(buffer, filename=f"sheet_part_{i//6 + 1}.png")
            msg = await channel.send(file=file)
            message_ids.append(str(msg.id))

        with open(MESSAGE_ID_FILE, 'w') as f:
            f.write("\n".join(message_ids))

        await asyncio.sleep(60)  # Wait a minute

@client_bot.event
async def on_ready():
    print(f'Bot logged in as {client_bot.user}')
    client_bot.loop.create_task(update_sheet_message())

client_bot.run(DISCORD_TOKEN)
