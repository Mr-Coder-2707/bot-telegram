# 📚 دليل استخدام بوت تحميل الميديا

# Media Downloader Bot User Guide

## 🤖 نظرة عامة | Overview

بوت تلجرام متقدم لتحميل المحتوى من منصات التواصل الاجتماعي المختلفة.

An advanced Telegram bot for downloading content from various social media platforms.

---

## 🎯 الأوامر المتاحة | Available Commands

### 1️⃣ `/start` - بدء البوت | Start the Bot

- **الوصف:** يعرض رسالة ترحيبية شاملة مع معلومات عن البوت
- **Description:** Displays a comprehensive welcome message with bot information
- **الاستخدام:** أرسل `/start` في أي وقت

### 2️⃣ `/help` - المساعدة | Help

- **الوصف:** يعرض دليل استخدام مفصل للبوت
- **Description:** Shows a detailed user guide for the bot
- **الاستخدام:** أرسل `/help` للحصول على المساعدة

### 3️⃣ `/about` - معلومات المطور | About Developer

- **الوصف:** يعرض معلومات عن المطور والبوت
- **Description:** Shows information about the developer and bot
- **الاستخدام:** أرسل `/about` لمعرفة المزيد

---

## 🌐 المنصات المدعومة | Supported Platforms

### 🎥 YouTube

- فيديوهات بجودة عالية
- High quality videos
- **مثال:** `https://www.youtube.com/watch?v=...`

### 📸 Instagram

- منشورات، ريلز، وقصص
- Posts, Reels, and Stories
- **مثال:** `https://www.instagram.com/p/...`

### 🐦 Twitter/X

- فيديوهات وصور
- Videos and images
- **مثال:** `https://twitter.com/.../status/...`

### 📘 Facebook

- فيديوهات ومقاطع
- Videos and clips
- **مثال:** `https://www.facebook.com/watch/...`

---

## 📝 كيفية الاستخدام | How to Use

### الطريقة البسيطة | Simple Method:

1. **انسخ الرابط** | Copy the link

   - انسخ رابط الفيديو أو المنشور من أي منصة مدعومة
   - Copy the video or post link from any supported platform

2. **أرسل الرابط** | Send the link

   - الصق الرابط مباشرة في الدردشة مع البوت
   - Paste the link directly in the chat with the bot

3. **انتظر التحميل** | Wait for download

   - سيقوم البوت بتحميل المحتوى تلقائياً
   - The bot will automatically download the content

4. **استلم الملف** | Receive the file
   - سيتم إرسال الملف لك مباشرة
   - The file will be sent to you directly

---

## ⚙️ المعلومات التقنية | Technical Information

### الحد الأقصى لحجم الملف | Maximum File Size

- **2000 MB / 2 GB** (حد تلجرام | Telegram limit)

### أنواع الملفات المدعومة | Supported File Types

- 🎥 فيديو | Video: MP4, MKV, AVI
- 📸 صور | Images: JPG, PNG
- 📄 مستندات | Documents: All types

### شريط التقدم | Progress Bar

- يعرض البوت شريط تقدم أثناء التحميل
- The bot displays a progress bar during download
- **مثال:** `[███████░░░░░░░░] 45.2%`

---

## 🚀 المميزات | Features

### ✅ تحميل سريع | Fast Download

- تحميل سريع وموثوق من جميع المنصات
- Fast and reliable downloads from all platforms

### ✅ واجهة سهلة | Easy Interface

- واجهة بسيطة وسهلة الاستخدام
- Simple and user-friendly interface

### ✅ دعم متعدد اللغات | Multi-language Support

- دعم كامل للغة العربية والإنجليزية
- Full support for Arabic and English

### ✅ تحديثات مستمرة | Continuous Updates

- تحديثات دورية لتحسين الأداء
- Regular updates to improve performance

---

## 👨‍💻 معلومات المطور | Developer Information

**المطور:** محمود | **Developer:** Mahmoud

**التخصص | Specialization:**

- 🔹 Python Developer
- 🔹 Telegram Bot Developer
- 🔹 Web Scraping & Automation
- 🔹 Media Processing

**الإصدار | Version:** 1.0.0  
**آخر تحديث | Last Update:** November 2025

---

## 💡 نصائح وإرشادات | Tips & Guidelines

### ✨ للحصول على أفضل تجربة | For Best Experience:

1. **استخدم روابط مباشرة**
   - Use direct links
2. **تأكد من صحة الرابط**
   - Make sure the link is valid
3. **انتظر حتى اكتمال التحميل**
   - Wait until download completes
4. **لا ترسل روابط متعددة في نفس الوقت**
   - Don't send multiple links at once

---

## ❓ الأسئلة الشائعة | FAQ

### س: ما هو الحد الأقصى لحجم الملف؟

**ج:** 2000 ميجابايت = 2 جيجابايت (حد تلجرام)

### Q: What is the maximum file size?

**A:** 2000 MB = 2 GB (Telegram limit)

---

### س: هل البوت مجاني؟

**ج:** نعم، البوت مجاني تماماً!

### Q: Is the bot free?

**A:** Yes, the bot is completely free!

---

### س: كم من الوقت يستغرق التحميل؟

**ج:** يعتمد على حجم الملف وسرعة الإنترنت

### Q: How long does download take?

**A:** Depends on file size and internet speed

---

---

## 🛠️ حلول المشاكل | Troubleshooting

### 1️⃣ مشكلة جودة الفيديو أو الصوت (ffmpeg)

**المشكلة:** قد تظهر أخطاء تتعلق بـ `ffmpeg` أو يتم تحميل الفيديو بدون صوت.
**الحل:** يجب تثبيت `ffmpeg` على جهازك:

- **Windows:** قم بتحميله من الموقع الرسمي، واستخرجه، وأضف مسار مجلد `bin` إلى `PATH` في نظامك.
- **التأكد:** اكتب `ffmpeg -version` في التيرمينال، إذا ظهرت أرقام الإصدار، فالأمر تم بنجاح.

### 2️⃣ مشكلة الحظر أو "Login Required" (Cookies)

**المشكلة:** إنستغرام أو يوتيوب قد يطلبون تسجيل الدخول أو يظهر خطأ "401 Unauthorized".
**الحل:**

1. استخدم إضافة متصفح مثل (Get cookies.txt LOCALLY).
2. قم باستخراج الكوكيز الخاصة بالموقع المتعثر.
3. احفظ الملف باسم `cookies.txt` في المجلد الرئيسي للبوت.
4. سيقوم البوت تلقائياً باستخدام هذا الملف لتجاوز الحظر.

### 3️⃣ تحديث مكتبات التحميل

**الحل:** تأكد دائماً من تحديث مكتبة `yt-dlp` بالنسخة الأخيرة:

```bash
pip install -U yt-dlp
```

---

## 🙏 شكراً لاستخدامك البوت!

## 🙏 Thank you for using the bot!

**للدعم والاقتراحات | For support and suggestions:**  
استخدم الأوامر المتاحة أو تواصل مع المطور  
Use available commands or contact the developer

---

**📅 تاريخ التحديث | Update Date:** 27 ديسمبر 2025 | December 27, 2025
