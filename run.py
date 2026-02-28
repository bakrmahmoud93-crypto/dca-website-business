"""
run.py - تشغيل النظام الكامل
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from website_generator import WebsiteGenerator
from whatsapp_sender import WhatsAppSender
import webbrowser
import os

def main():
    print("=" * 60)
    print("   IRAQ WEBSITE BUSINESS - نظام بيع المواقع")
    print("=" * 60)
    print()
    
    # 1. توليد الموقع
    print("[1/3] توليد الموقع التجريبي...")
    generator = WebsiteGenerator()
    website_path = generator.generate_for_bakr()
    print(f"      -> {website_path}")
    print()
    
    # 2. تجهيز رسالة واتساب
    print("[2/3] تجهيز رسالة واتساب...")
    sender = WhatsAppSender()
    
    # في الإنتاج: نرفع الموقع على subdomain
    # للتجربة: نفتح الملف محلياً
    website_url = f"file:///{website_path.replace(os.sep, '/')}"
    
    result = sender.send_website(
        phone="+9647701234567",  # رقم البكر
        business_name="عيادة الأسنان المتميزة",
        website_url=website_url,
        price=150
    )
    
    print("      -> تم تجهيز الرسالة!")
    print()
    
    # 3. فتح الموقع + واتساب
    print("[3/3] فتح الموقع وواتساب...")
    
    # فتح الموقع في المتصفح
    webbrowser.open(website_url)
    
    # فتح واتساب ويب
    webbrowser.open(result['whatsapp_link'])
    
    print("      -> تم فتح المتصفح!")
    print()
    
    print("=" * 60)
    print("   تم بنجاح!")
    print("=" * 60)
    print()
    print("الموقع مفتوح في المتصفح")
    print("واتساب ويب مفتوح مع الرسالة الجاهزة")
    print()
    print("الرسالة:")
    print("-" * 60)
    print(result['message'])
    print("-" * 60)

if __name__ == "__main__":
    main()
