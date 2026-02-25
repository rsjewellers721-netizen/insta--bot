import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import openai
import re

# ========== YAHAN APNI VALUES DAAL ==========
TELEGRAM_TOKEN = "8679386904:AAESp3oAzU3pu_v0nucVfzUwx61ulzRd_mg"  # TERA TOKEN
OPENAI_API_KEY = ""  # OPENAI KEY nahi hai to khali chhod de
# =============================================

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

DOWNLOAD_PATH = "downloads/"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 **Instagram Video Downloader**\n\n"
        "Mujhe Instagram ka link bhejo, main:\n"
        "1️⃣ Video download karunga\n"
        "2️⃣ Caption likh kar dunga\n"
        "3️⃣ Video bhej dunga\n\n"
        "Tu YouTube pe upload kar lena!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = None
    try:
        msg = await update.message.reply_text("⏳ Process shuru...")
        url = update.message.text
        
        if "instagram.com" not in url:
            await msg.edit_text("❌ Bas Instagram link bhej!")
            return
        
        await msg.edit_text("📥 Video download ho raha...")
        
        # Download video
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}video.%(ext)s',
            'format': 'best',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Instagram Video')
            filename = ydl.prepare_filename(info)
        
        # Caption
        caption = info.get('description', '') or video_title
        if OPENAI_API_KEY:
            try:
                await msg.edit_text("🤖 AI caption bana raha...")
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Rewrite this caption with emojis and hashtags."},
                        {"role": "user", "content": f"Caption: {caption}"}
                    ],
                    max_tokens=100
                )
                caption = response.choices[0].message.content
            except:
                caption = caption + "\n\n#viral #reels"
        else:
            caption = caption + "\n\n#viral #reels"
        
        await msg.edit_text("📤 Video bhej raha...")
        
        # Send video
        with open(filename, 'rb') as f:
            await update.message.reply_video(
                video=f,
                caption=f"🎥 {video_title[:50]}\n\n{caption[:200]}...",
                supports_streaming=True
            )
        
        # Clean up
        os.remove(filename)
        await msg.delete()
        
    except Exception as e:
        if msg:
            await msg.edit_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot chal raha hai...")
    app.run_polling()

if __name__ == '__main__':
    main()
