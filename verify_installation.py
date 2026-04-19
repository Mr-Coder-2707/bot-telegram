#!/usr/bin/env python3
"""
Music Feature Installation Verification Script
تحقق من تثبيت ميزة تحميل الأغاني
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def check_python():
    """Check Python version"""
    print("🐍 فحص Python | Checking Python...")
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        print(f"  ✅ Python {version} - موافق | Compatible")
        return True
    else:
        print(f"  ❌ Python {version} - مطلوب 3.8+ | Requires 3.8+")
        return False

def check_ffmpeg():
    """Check FFmpeg installation"""
    print("🎬 فحص FFmpeg | Checking FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            # Get first line with version
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ FFmpeg مثبت | Installed: {version_line[:50]}")
            return True
        else:
            print("  ❌ FFmpeg موجود لكن لا يعمل | Found but not working")
            return False
    except FileNotFoundError:
        print("  ❌ FFmpeg غير مثبت | Not installed")
        print("     الرجاء تثبيت FFmpeg: choco install ffmpeg")
        return False
    except Exception as e:
        print(f"  ⚠️  خطأ في الفحص | Error: {e}")
        return False

def check_packages():
    """Check Python packages"""
    print("📦 فحص الحزم | Checking packages...")
    
    required_packages = {
        'telegram': 'python-telegram-bot',
        'yt_dlp': 'yt-dlp',
        'aiofiles': 'aiofiles',
        'dotenv': 'python-dotenv',
    }
    
    all_installed = True
    for module, package_name in required_packages.items():
        try:
            __import__(module)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - غير مثبت | Not installed")
            all_installed = False
    
    return all_installed


def check_env_vars():
    """Check required environment variables for running the bot."""
    print("\n🔐 فحص المتغيرات | Checking environment variables...")

    bot_token = (os.getenv('BOT_TOKEN') or '').strip()
    cookies_txt = (os.getenv('COOKIES_TXT') or '').strip()

    ok = True
    if bot_token:
        print("  ✅ BOT_TOKEN")
    else:
        print("  ❌ BOT_TOKEN - مطلوب لتشغيل البوت | Required to run the bot")
        ok = False

    if cookies_txt:
        print("  ✅ COOKIES_TXT (اختياري) | Optional")
    else:
        print("  ⚠️  COOKIES_TXT (اختياري) | Optional")

    return ok

def check_files():
    """Check if all required files exist"""
    print("📁 فحص الملفات | Checking files...")
    
    required_files = [
        'bot.py',
        'downloaders/music.py',
        'downloaders/__init__.py',
        'requirements.txt',
    ]

    optional_files = [
        '.env',
    ]
    
    documentation_files = [
        'START_HERE.md',
        'QUICK_START.md',
        'MUSIC_SETUP.md',
        'MUSIC_FEATURE.md',
        'COMPLETE_GUIDE.md',
        'UPDATE_SUMMARY.md',
    ]
    
    print("\n  المشروع الأساسي | Project Files:")
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"    ✅ {file} ({size:,} bytes)")
        else:
            print(f"    ❌ {file} - مفقود | Missing")
            all_exist = False

    print("\n  ملفات اختيارية | Optional Files:")
    for file in optional_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"    ✅ {file} ({size:,} bytes)")
        else:
            print(f"    ⚠️  {file} - اختياري | Optional")
    
    print("\n  الملفات الموثقية | Documentation Files:")
    for file in documentation_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"    ✅ {file} ({size:,} bytes)")
        else:
            print(f"    ⚠️  {file} - اختياري | Optional")
    
    return all_exist

def check_imports():
    """Check if music module imports work"""
    print("🎵 فحص وحدة الموسيقى | Checking music module...")
    
    try:
        from downloaders import (
            download_music,
            extract_metadata,
            format_metadata_message,
            create_metadata_file,
        )
        print("  ✅ جميع الدوال معرّفة | All functions imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ خطأ في الاستيراد | Import error: {e}")
        return False

def print_summary(results):
    """Print summary of checks"""
    print_header("📋 ملخص الفحص | Verification Summary")
    
    checks = [
        ("🐍 Python", results['python']),
        ("🎬 FFmpeg", results['ffmpeg']),
        ("📦 Packages", results['packages']),
        ("🔐 Env Vars", results['env']),
        ("📁 Files", results['files']),
        ("🎵 Music Module", results['imports']),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ موافق | OK" if result else "❌ غير موافق | Not OK"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("  🎉 جميع الفحوصات نجحت! | All checks passed!")
        print("  ✨ أنت جاهز للبدء! | Ready to start!")
        print("\n  الخطوات التالية | Next steps:")
        print("  1. اقرأ START_HERE.md")
        print("  2. اتبع QUICK_START.md")
        print("  3. شغّل: python bot.py")
    else:
        print("  ⚠️  بعض الفحوصات فشلت | Some checks failed")
        print("  📖 اقرأ MUSIC_SETUP.md للمساعدة | Read MUSIC_SETUP.md for help")
    print("="*60 + "\n")
    
    return all_passed

def main():
    """Main verification function"""
    print_header("🔍 فحص تثبيت ميزة الأغاني | Music Feature Installation Check")
    
    results = {
        'python': check_python(),
        'ffmpeg': check_ffmpeg(),
        'packages': check_packages(),
        'env': check_env_vars(),
        'files': check_files(),
        'imports': check_imports(),
    }
    
    all_passed = print_summary(results)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
