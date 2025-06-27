# CapyCraft Bot

Quick and dirty Discord bot that reads Google Sheets data and renders images for posting into a Discord channel.  
Originally made to manage a "Shopping List" for my settlement in BitCraft.

## 🔧 .env Usage

Set the following environment variables in a `.env` file:

- `DISCORD_TOKEN` — your bot's token (self-explanatory)
- `CHANNEL_ID` — the ID of the Discord channel you want the bot to post in
- `SHEET_ID` — the Google Sheets ID (found in the URL)
- `RANGE` — the range of the sheet you want the bot to monitor
- `MESSAGE_ID_FILE` — file used to track the last sent message; the bot deletes old posts to avoid channel spam
