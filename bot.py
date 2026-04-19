import logging
import os
import re
import asyncio
import time
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, Application
from dotenv import load_dotenv

# تعطيل رسائل السجلات الخاصة بمكتبة الاتصال httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
# Import downloaders
from downloaders import (
    download_youtube_video,
    download_twitter_video,
    download_facebook_video,
    download_tiktok_video,
    is_tiktok_url,
    check_file_size,
    cleanup_file,
    MAX_FILE_SIZE_MB
)

from downloaders.instagram import get_post_media, InstagramMedia

# Load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN:
    TOKEN = TOKEN.strip()
WATERMARK_ENABLED = os.getenv("WATERMARK_ENABLED", "False").lower() == "true"
WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "@your_channel_name")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Performance guardrail: limit concurrent downloads to avoid hanging under load
try:
    MAX_CONCURRENT_DOWNLOADS = max(1, int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "2")))
except Exception:
    MAX_CONCURRENT_DOWNLOADS = 2

DOWNLOAD_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


def build_buttons(media_list: list[InstagramMedia]) -> InlineKeyboardMarkup:
    """Builds an inline keyboard with one button per media item."""
    keyboard: list[list[InlineKeyboardButton]] = []
    keyboard.append([InlineKeyboardButton("All", callback_data="igsel:all")])
    for i in range(len(media_list)):
        keyboard.append([InlineKeyboardButton(f"Image {i + 1}", callback_data=f"igsel:{i}")])
    return InlineKeyboardMarkup(keyboard)


async def _send_instagram_media(chat_message, media: InstagramMedia):
    """Send a single Instagram media item using direct URL."""
    if media.kind == "video":
        await chat_message.reply_video(video=media.url, write_timeout=300, read_timeout=300)
    else:
        await chat_message.reply_photo(photo=media.url, write_timeout=300, read_timeout=300)


async def handle_selection(callback_query, context: ContextTypes.DEFAULT_TYPE):
    """Handles a user selecting a specific carousel item via inline buttons."""
    await callback_query.answer()

    data = callback_query.data or ""
    if not data.startswith("igsel:"):
        return

    selection = data.split(":", 1)[1]

    media_list = context.user_data.get("ig_media_list")
    if not media_list:
        await callback_query.message.reply_text("❌ انتهت صلاحية الاختيار. أرسل الرابط مرة أخرى.\n❌ Selection expired. Please send the link again.")
        return

    try:
        if selection == "all":
            await callback_query.message.reply_text("⬆️ Sending all media...")
            for media in media_list:
                await _send_instagram_media(callback_query.message, media)
        else:
            try:
                index = int(selection)
            except Exception:
                await callback_query.message.reply_text("❌ اختيار غير صالح | Invalid selection")
                return

            if not (0 <= index < len(media_list)):
                await callback_query.message.reply_text("❌ رقم غير صالح | Invalid index")
                return

            await _send_instagram_media(callback_query.message, media_list[index])

        # Remove buttons after successful selection to avoid confusion
        try:
            await callback_query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
    finally:
        # Clear selection state
        context.user_data.pop("ig_media_list", None)


async def instagram_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """PTB handler wrapper for Instagram selection callbacks."""
    if not update.callback_query:
        return
    await handle_selection(update.callback_query, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message."""
    user_name = update.effective_user.first_name
    
    # Create inline keyboard buttons
    keyboard = [
        [
            InlineKeyboardButton("❓ المساعدة | Help", callback_data='help'),
            InlineKeyboardButton("ℹ️ عن المطور | About", callback_data='about')
        ],
        [
            InlineKeyboardButton("▶️ YouTube", callback_data='platform_youtube'),
            InlineKeyboardButton("📷 Instagram", callback_data='platform_instagram')
        ],
        [
            InlineKeyboardButton("🐦 Twitter/X", callback_data='platform_twitter'),
            InlineKeyboardButton("👥 Facebook", callback_data='platform_facebook')
        ],
        [
            InlineKeyboardButton("🎬 TikTok", callback_data='platform_tiktok')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 **مرحباً {user_name}!**\n"
        f"**Welcome {user_name}!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🤖 **أنا بوت تحميل الميديا الاحترافي**\n"
        "🤖 **I'm a Professional Media Downloader Bot**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌐 **المنصات المدعومة | Supported Platforms:**\n\n"
        "▶️ **YouTube** - فيديوهات بجودة عالية\n"
        "📷 **Instagram** - منشورات، ريلز، وقصص\n"
        "🐦 **Twitter/X** - فيديوهات وصور\n"
        "👥 **Facebook** - فيديوهات ومقاطع\n"
        "🎬 **TikTok** - فيديوهات ومقاطع\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 **كيفية الاستخدام | How to Use:**\n"
        "1️⃣ أرسل لي رابط من أي منصة مدعومة\n"
        "2️⃣ سأقوم بتحميل المحتوى لك\n"
        "3️⃣ استمتع بالمحتوى! ✅\n\n"
        f"⚠️ **الحد الأقصى للملف:** {MAX_FILE_SIZE_MB}MB\n"
        f"⚠️ **Max file size:** {MAX_FILE_SIZE_MB}MB\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 **استخدم الأزرار أدناه للتنقل**\n"
        "💡 **Use the buttons below to navigate**\n\n"
        "⚡ **جاهز للبدء! أرسل رابطك الآن!**\n"
        "⚡ **Ready to go! Send your link now!**",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends help information."""
    await update.message.reply_text(
        "❓ **مركز المساعدة | Help Center**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 **كيفية استخدام البوت | How to Use:**\n\n"
        "1️⃣ انسخ رابط الفيديو أو المنشور\n"
        "   Copy the video or post link\n\n"
        "2️⃣ أرسله لي مباشرة في الدردشة\n"
        "   Send it directly in the chat\n\n"
        "3️⃣ انتظر قليلاً حتى أقوم بالتحميل\n"
        "   Wait a moment while I download\n\n"
        "4️⃣ استلم الملف جاهزاً! ✅\n"
        "   Receive your file ready! ✅\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌐 **المنصات المدعومة | Supported Platforms:**\n\n"
        "▶️ **YouTube**\n"
        "   • فيديوهات بجودة عالية\n"
        "   • High quality videos\n\n"
        "🎵 **YouTube Music**\n"
        "   • تحميل الأغاني كـ MP3\n"
        "   • Download songs as MP3\n"
        "   • مع جميع البيانات والمعلومات\n"
        "   • With full metadata\n\n"
        "📷 **Instagram**\n"
        "   • منشورات، ريلز، قصص\n"
        "   • Posts, Reels, Stories\n\n"
        "🐦 **Twitter/X**\n"
        "   • فيديوهات وصور\n"
        "   • Videos and images\n\n"
        "👥 **Facebook**\n"
        "   • فيديوهات ومقاطع\n"
        "   • Videos and clips\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚙️ **معلومات تقنية | Technical Info:**\n\n"
        f"📦 الحد الأقصى للملف: **{MAX_FILE_SIZE_MB}MB**\n"
        f"📦 Max file size: **{MAX_FILE_SIZE_MB}MB**\n\n"
        "⏱️ وقت التحميل يعتمد على حجم الملف\n"
        "⏱️ Download time depends on file size\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📌 **الأوامر المتاحة | Available Commands:**\n\n"
        "/start - بدء البوت | Start the bot\n"
        "/help - عرض المساعدة | Show help\n"
        "/about - معلومات عن المطور | About developer\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💬 **هل تحتاج مساعدة؟**\n"
        "**Need help?**\n"
        "فقط أرسل رابطك وسأقوم بالباقي! ⚡\n"
        "Just send your link and I'll do the rest! ⚡",
        parse_mode='Markdown'
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends information about the developer."""
    await update.message.reply_text(
        "ℹ️ **About Developer**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "👤 **Developer:** Mahmoud Sabry Elkhwass\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💼 **Specialization:**\n\n"
        "• Python Developer\n"
        "• Telegram Bot Developer\n"
        "• Web Scraping & Automation\n"
        "• Media Processing\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌐 **Website:**\n"
        "https://linktree2026.vercel.app/\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📖 **About This Bot:**\n\n"
        "This bot was developed to facilitate downloading content from various social media platforms quickly and securely.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "⭐ **Features:**\n\n"
        "✅ Fast and reliable downloads\n"
        "✅ Multiple platform support\n"
        "✅ User-friendly interface\n"
        "✅ Continuous updates\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📅 **Version:** 1.0.0\n"
        "📅 **Last Update:** November 2025\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 **Note:**\n"
        "This bot is completely free and open to everyone!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🙏 **Thank you for using the bot!**\n\n"
        "💬 For support and suggestions, use /help",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        # Show help information
        keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية | Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "❓ **مركز المساعدة | Help Center**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **كيفية استخدام البوت | How to Use:**\n\n"
            "1️⃣ انسخ رابط الفيديو أو المنشور\n"
            "   Copy the video or post link\n\n"
            "2️⃣ أرسله لي مباشرة في الدردشة\n"
            "   Send it directly in the chat\n\n"
            "3️⃣ انتظر قليلاً حتى أقوم بالتحميل\n"
            "   Wait a moment while I download\n\n"
            "4️⃣ استلم الملف جاهزاً! ✅\n"
            "   Receive your file ready! ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📦 الحد الأقصى للملف: **{MAX_FILE_SIZE_MB}MB**\n"
            f"📦 Max file size: **{MAX_FILE_SIZE_MB}MB**\n\n"
            "💬 فقط أرسل رابطك وسأقوم بالباقي! ⚡\n"
            "💬 Just send your link and I'll do the rest! ⚡",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'about':
        # Show about information
        keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية | Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "ℹ️ **About Developer**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 **Developer:** Mahmoud Sabry Elkhwass\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💼 **Specialization:**\n\n"
            "• Python Developer\n"
            "• Telegram Bot Developer\n"
            "• Web Scraping & Automation\n"
            "• Media Processing\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🌐 **Website:**\n"
            "https://linktree2026.vercel.app/\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📅 **Version:** 1.0.0\n"
            "📅 **Last Update:** November 2025\n\n"
            "🙏 **Thank you for using the bot!**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'platform_youtube':
        keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية | Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "▶️ **YouTube Downloader**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **كيفية الاستخدام:**\n"
            "1️⃣ افتح فيديو YouTube\n"
            "2️⃣ انسخ الرابط\n"
            "3️⃣ أرسله لي هنا\n\n"
            "✅ **مثال:**\n"
            "`https://www.youtube.com/watch?v=...`\n"
            "`https://youtu.be/...`\n\n"
            "⚡ سأقوم بتحميله بأعلى جودة متاحة!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'platform_instagram':
        keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية | Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "📷 **Instagram Downloader**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **كيفية الاستخدام:**\n"
            "1️⃣ افتح منشور أو ريل Instagram\n"
            "2️⃣ انسخ الرابط\n"
            "3️⃣ أرسله لي هنا\n\n"
            "✅ **مثال:**\n"
            "`https://www.instagram.com/p/...`\n"
            "`https://www.instagram.com/reel/...`\n\n"
            "⚡ سأقوم بتحميل جميع الصور والفيديوهات!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'platform_twitter':
        keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية | Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "🐦 **Twitter/X Downloader**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **كيفية الاستخدام:**\n"
            "1️⃣ افتح تغريدة تحتوي على فيديو\n"
            "2️⃣ انسخ الرابط\n"
            "3️⃣ أرسله لي هنا\n\n"
            "✅ **مثال:**\n"
            "`https://twitter.com/.../status/...`\n"
            "`https://x.com/.../status/...`\n\n"
            "⚡ سأقوم بتحميل الفيديو بأفضل جودة!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'platform_facebook':
        keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية | Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "👥 **Facebook Downloader**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **كيفية الاستخدام:**\n"
            "1️⃣ افتح فيديو Facebook\n"
            "2️⃣ انسخ الرابط\n"
            "3️⃣ أرسله لي هنا\n\n"
            "✅ **مثال:**\n"
            "`https://www.facebook.com/watch/...`\n"
            "`https://fb.watch/...`\n\n"
            "⚡ سأقوم بتحميل الفيديو فوراً!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    elif query.data == 'platform_tiktok':
        keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية | Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "🎬 **TikTok Downloader**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **كيفية الاستخدام:**\n"
            "1️⃣ افتح فيديو TikTok\n"
            "2️⃣ انسخ الرابط\n"
            "3️⃣ أرسله لي هنا\n\n"
            "✅ **أمثلة على الروابط:**\n"
            "`https://www.tiktok.com/@username/video/123456789`\n"
            "`https://vm.tiktok.com/...`\n"
            "`https://vt.tiktok.com/...`\n\n"
            "⚡ سأقوم بتحميل الفيديو بدون علامات مائية!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'main_menu':
        # Return to main menu
        user_name = query.from_user.first_name
        keyboard = [
            [
                InlineKeyboardButton("❓ المساعدة | Help", callback_data='help'),
                InlineKeyboardButton("ℹ️ عن المطور | About", callback_data='about')
            ],
            [
                InlineKeyboardButton("▶️ YouTube", callback_data='platform_youtube'),
                InlineKeyboardButton("📷 Instagram", callback_data='platform_instagram')
            ],
            [
                InlineKeyboardButton("🐦 Twitter/X", callback_data='platform_twitter'),
                InlineKeyboardButton("👥 Facebook", callback_data='platform_facebook')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"🏠 **القائمة الرئيسية | Main Menu**\n\n"
            f"مرحباً {user_name}! اختر ما تريد:\n"
            f"Welcome {user_name}! Choose what you want:\n\n"
            "⚡ **جاهز للبدء!**\n"
            "⚡ **Ready to go!**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and routes to appropriate downloader."""
    url = (update.message.text or "").strip()
    url_lc = url.lower()
    
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text(
            "❌ أرسل رابط صحيح يبدأ بـ http:// أو https://\n"
            "❌ Please send a valid URL starting with http:// or https://"
        )
        return

    # Block unsupported TikTok photo posts early
    if "tiktok.com" in url_lc and "/photo/" in url_lc:
        await update.message.reply_text(
            "❌ النوع ده (TikTok photo) مش مدعوم حاليًا.\n"
            "❌ TikTok photo posts are not supported right now."
        )
        return

    status_msg = await update.message.reply_text("⏳ جاري معالجة الرابط... | Processing your link...")
    
    # Progress callback setup
    loop = asyncio.get_running_loop()
    last_update_time = 0

    def progress_callback(downloaded, total):
        nonlocal last_update_time
        current_time = time.time()
        
        # Update every 2 seconds or if completed
        if current_time - last_update_time < 2 and downloaded < total:
            return
            
        last_update_time = current_time
        if total > 0:
            percentage = (downloaded / total) * 100
            bar_length = 15
            filled_length = int(bar_length * downloaded // total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            text = f"⬇️ جاري التحميل... | Downloading...\n[{bar}] {percentage:.1f}%"
        else:
            text = "⬇️ جاري التحميل... | Downloading..."

        try:
            asyncio.run_coroutine_threadsafe(
                status_msg.edit_text(text),
                loop
            )
        except Exception:
            pass # Ignore errors if message is not modified or network issues

    try:
        # If the bot is under load, user gets a friendly queue message
        if DOWNLOAD_SEMAPHORE.locked():
            try:
                await status_msg.edit_text("⏳ في انتظار دورك... | Waiting in queue...")
            except Exception:
                pass

        async with DOWNLOAD_SEMAPHORE:
            files_to_send = []

            # Route based on URL domain
            if "youtube.com" in url_lc or "youtu.be" in url_lc:
                await status_msg.edit_text("⬇️ جاري التحميل من YouTube... | Downloading from YouTube...")
                file_path = await asyncio.to_thread(download_youtube_video, url, "downloads", progress_callback)
                files_to_send.append(file_path)

            elif "instagram.com" in url_lc:
                await status_msg.edit_text("🔎 جاري جلب بيانات المنشور من Instagram... | Fetching Instagram post info...")
                media_list = await asyncio.to_thread(get_post_media, url)

                if not media_list:
                    raise Exception("Empty media list")

                # Carousel: show buttons; Non-carousel: send immediately.
                if len(media_list) == 1:
                    await status_msg.delete()
                    await _send_instagram_media(update.message, media_list[0])
                    return

                context.user_data["ig_media_list"] = media_list
                await status_msg.delete()
                await update.message.reply_text(
                    "Choose an image number:",
                    reply_markup=build_buttons(media_list),
                )
                return

            elif "twitter.com" in url_lc or "x.com" in url_lc:
                await status_msg.edit_text("⬇️ جاري التحميل من Twitter/X... | Downloading from Twitter/X...")
                file_path = await asyncio.to_thread(download_twitter_video, url, "downloads", progress_callback)
                files_to_send.append(file_path)

            elif "facebook.com" in url_lc or "fb.watch" in url_lc:
                await status_msg.edit_text("⬇️ جاري التحميل من Facebook... | Downloading from Facebook...")
                file_path = await asyncio.to_thread(download_facebook_video, url, "downloads", progress_callback)
                files_to_send.append(file_path)

            elif is_tiktok_url(url_lc):
                await status_msg.edit_text("⬇️ جاري التحميل من TikTok... | Downloading from TikTok...")
                file_path = await asyncio.to_thread(download_tiktok_video, url, "downloads", progress_callback)
                files_to_send.append(file_path)

            else:
                await status_msg.edit_text(
                    "❌ رابط غير مدعوم. أدعم YouTube, Instagram, Twitter, Facebook, و TikTok.\n"
                    "❌ Unsupported URL. I support YouTube, Instagram, Twitter, Facebook, and TikTok."
                )
                return

            # Send files
            await status_msg.edit_text("⬆️ جاري رفع الملف... | Uploading media...")

            for file_path in files_to_send:
                original_path = file_path
                final_path = original_path

                if WATERMARK_ENABLED:
                    try:
                        from watermark import apply_watermark
                        await status_msg.edit_text("🖼️ Adding watermark...")
                        watermarked_path = await apply_watermark(original_path, WATERMARK_TEXT)
                        if watermarked_path and os.path.exists(watermarked_path):
                            final_path = watermarked_path
                        else:
                            logger.warning(f"Watermarking failed for {original_path}. Sending original file.")
                    except ImportError:
                        logger.warning("Watermark module not available. Install moviepy to enable watermarks.")
                    except Exception as e:
                        logger.warning(f"Watermarking failed: {e}. Sending original file.")

                is_valid, size = check_file_size(final_path)
                if is_valid:
                    try:
                        if final_path.endswith(('.jpg', '.jpeg', '.png')):
                            with open(final_path, 'rb') as f:
                                await update.message.reply_photo(photo=f, write_timeout=300, read_timeout=300)
                        elif final_path.endswith(('.mp4', '.mkv', '.avi')):
                            with open(final_path, 'rb') as f:
                                await update.message.reply_video(video=f, write_timeout=300, read_timeout=300)
                        elif final_path.endswith(('.mp3', '.m4a', '.wav', '.flac')):
                            with open(final_path, 'rb') as f:
                                await update.message.reply_audio(audio=f, write_timeout=300, read_timeout=300)
                        else:
                            with open(final_path, 'rb') as f:
                                await update.message.reply_document(document=f, write_timeout=300, read_timeout=300)
                    except Exception as e:
                        logger.error(f"Error sending file {final_path}: {e}")
                        await update.message.reply_text(f"❌ Failed to upload {os.path.basename(final_path)}.")
                else:
                    await update.message.reply_text(
                        f"⚠️ File is too large: {os.path.basename(final_path)} ({size:.2f}MB > {MAX_FILE_SIZE_MB}MB)."
                    )

                # Cleanup
                cleanup_file(original_path)
                if original_path != final_path:
                    cleanup_file(final_path)

            await status_msg.delete()

    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        await status_msg.edit_text(f"❌ حدث خطأ | An error occurred: {str(e)}")

async def post_init(application: Application):
    """Sets the bot's menu commands."""
    try:
        await application.bot.set_my_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help"),
            BotCommand("about", "About the developer"),
        ])
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")

async def main():
    """Main function to run the bot."""
    if not TOKEN:
        print("Error: BOT_TOKEN not found. Please set it in .env file.")
        exit(1)

    # Build application with proper configuration for v22+
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CallbackQueryHandler(instagram_selection_callback, pattern=r"^igsel:"))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    # Initialize and run with allowed_updates to prevent conflicts and drop pending updates
    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )
    
    # Keep the bot running
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("An error occurred. Check error_log.txt")
        raise

