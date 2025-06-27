Quick and dirty Discord bot that reads Google Sheets data and renders images for posting into a Discord channel. Made for use with a 'Shopping List' for my settlement on BitCraft.

.env usage
'DISCORD_TOKEN' # self explanitory
'CHANNEL_ID' # Channel ID that you want the bot to post in
'SHEET_ID' # Google Sheets ID found in URL
'RANGE' # Range of sheet you want the bot to watch
'MESSAGE_ID_FILE' # Used to track last sent message. Bot will delete old post and send new messages to avoid channel spam.
