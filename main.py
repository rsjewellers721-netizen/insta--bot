import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.environ.get("TELEGRAM_TOKEN", "8679386904:AAESp3oAzU3pu_v0nucVfzUwx61ulzRd_mg")
DOWNLOAD_PATH = "downloads/"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Instagram link bhej, main video download kar dunga!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = None
    try:
        msg = await update.message.reply_text("⏳ Downloading...")
        url = update.message.text
        if "instagram.com" not in url:
            await msg.edit_text("❌ Bas Instagram link bhej!")
            return
        
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}video.%(ext)s',
            'format': 'best',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Video')
        
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, caption=f"🎥 {title[:50]}", supports_streaming=True)
        
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        if msg:
            await msg.edit_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
