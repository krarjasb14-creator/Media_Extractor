import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# التوكن الخاص بك
TOKEN = '8772085568:AAHsBkYdUa1rVIQkEJjOEPJCglHFE_hM9nI'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 أهلاً بك في قسم التحميل (Downloader Module)\n\n"
        "أرسل رابط فيديو من تيك توك، يوتيوب، أو إنستغرام وسأقوم بالتحميل فوراً."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("⏳ جاري المعالجة... قد يستغرق الأمر ثواني.")

    # اسم ملف فريد لتجنب تداخل التحميلات
    video_filename = f'dl_{chat_id}.mp4'
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': video_filename,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # استخدام loop.run_in_executor لمنع تعليق البوت أثناء التحميل
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, lambda: ydl.download([url]))
        
        if os.path.exists(video_filename):
            with open(video_filename, 'rb') as video:
                await context.bot.send_video(chat_id=chat_id, video=video, caption="✅ تم التحميل بنجاح!")
            os.remove(video_filename) # حذف الملف لتوفير المساحة
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ في التحميل: {str(e)}")
        if os.path.exists(video_filename):
            os.remove(video_filename)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("📡 Downloader Core is running...")
    app.run_polling()
