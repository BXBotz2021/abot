import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import youtube_utils
from config import API_ID, API_HASH, BOT_TOKEN

# Create downloads directory if it doesn't exist
os.makedirs("downloads", exist_ok=True)

# Initialize the Pyrogram client
app = Client(
    "youtube_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 Hello! I'm a YouTube Downloader Bot.\n"
        "Send me a YouTube video link, and I'll download it for you."
    )

# Command handler for /help
@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        "How to use this bot:\n\n"
        "1. Send a YouTube video URL\n"
        "2. Choose video quality\n"
        "3. Wait for the download to complete\n"
        "4. Receive your video!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )

# Handler for YouTube links
@app.on_message(filters.regex(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'))
async def youtube_link_handler(client, message):
    url = message.text
    
    # Provide quality options
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("720p", callback_data=f"dl_{url}_720"),
                InlineKeyboardButton("480p", callback_data=f"dl_{url}_480"),
                InlineKeyboardButton("360p", callback_data=f"dl_{url}_360")
            ]
        ]
    )
    
    await message.reply_text("Please select video quality:", reply_markup=keyboard)

# Callback handler for quality selection
@app.on_callback_query(filters.regex(r'^dl_'))
async def download_callback(client, callback_query):
    # Extract URL and quality from callback data
    _, url, quality = callback_query.data.split("_")
    
    # Send a processing message
    await callback_query.message.edit_text("⏳ Processing your request...")
    
    # Format string based on quality
    if quality == "720":
        format_str = "22"  # 720p
    elif quality == "480":
        format_str = "18"  # 480p
    else:
        format_str = "17"  # 360p
    
    # Download the video
    status_message = await callback_query.message.reply_text("⬇️ Downloading video...")
    file_path = youtube_utils.download_video(url, format_str)
    
    if file_path:
        await status_message.edit_text("✅ Download complete. Now uploading to Telegram...")
        
        # Upload the file to Telegram
        try:
            await client.send_video(
                chat_id=callback_query.message.chat.id,
                video=file_path,
                caption=f"Downloaded from YouTube"
            )
            await status_message.delete()
            await callback_query.message.edit_text("✅ Video uploaded successfully!")
            
            # Clean up - remove the downloaded file
            os.remove(file_path)
        except Exception as e:
            await status_message.edit_text(f"❌ Error uploading video: {str(e)}")
    else:
        await status_message.edit_text("❌ Failed to download the video. Please try again with a different link or quality.")

# Run the bot
if __name__ == "__main__":
    print("Bot starting...")
    app.run()
