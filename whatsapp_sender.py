"""
WhatsApp Sender - يرسل المواقع عبر واتساب
"""

import webbrowser
import urllib.parse
import pyperclip
from typing import Optional
import os

class WhatsAppSender:
    """مرسل رسائل واتساب"""
    
    def __init__(self):
        self.message_templates = {
            'initial': """مرحباً! 👋

أنا حسام من DCA للحلول الرقمية.

سررت بإعداد موقع ويب مجاني لمحل {business_name} كهدية ترحيبية! 🎁

الموقع جاهز ويمكنكم معاينته هنا:
{website_url}

الموقع يتضمن:
✅ تصميم عصري ومتجاوب
✅ معلومات التواصل
✅ وصف الخدمات

إذا أعجبكم الموقع، يمكنكم الحصول عليه بـ ${price} فقط!
يشمل: الدومين، الاستضافة، والتعديلات لمدة شهر.

هل تودون معاينة الموقع؟ 🌐""",

            'follow_up': """مرحباً! 👋

كنت أرسلت لكم رابط موقع {business_name}.

هل تمكنتم من معاينته؟ 

الموقع جاهز وينتظر موافقتكم لتفعيله! 🚀

يمكنكم الرد على هذا الرسالة أو الاتصال على:
+964 XXX XXX XXXX""",

            'discount': """🔥 عرض خاص!

{business_name} - خصم 30%!

السعر الأصلي: ${original_price}
السعر الآن: ${discounted_price}

العرض ساري لمدة 48 ساعة فقط! ⏰

للحجز، ردوا بكلمة "أوافق" ✅"""
        }
    
    def format_phone(self, phone: str) -> str:
        """تنسيق رقم الهاتف للواتساب"""
        # إزالة المسافات والشرطات
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # إضافة كود العراق إذا لم يكن موجوداً
        if phone.startswith('0'):
            phone = '+964' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+' + phone
        
        return phone
    
    def generate_whatsapp_link(self, phone: str, message: str) -> str:
        """توليد رابط واتساب"""
        formatted_phone = self.format_phone(phone)
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{formatted_phone.replace('+', '')}?text={encoded_message}"
    
    def send_via_browser(self, phone: str, message: str) -> bool:
        """إرسال عبر فتح المتصفح"""
        try:
            link = self.generate_whatsapp_link(phone, message)
            webbrowser.open(link)
            return True
        except Exception as e:
            print(f"خطأ: {e}")
            return False
    
    def copy_to_clipboard(self, message: str) -> bool:
        """نسخ الرسالة للحافظة"""
        try:
            pyperclip.copy(message)
            return True
        except:
            return False
    
    def create_message(self, template_name: str, **kwargs) -> str:
        """إنشاء رسالة من قالب"""
        template = self.message_templates.get(template_name, self.message_templates['initial'])
        return template.format(**kwargs)
    
    def send_website(self, phone: str, business_name: str, website_url: str, price: int = 150) -> dict:
        """إرسال موقع لعميل"""
        
        # إنشاء الرسالة
        message = self.create_message(
            'initial',
            business_name=business_name,
            website_url=website_url,
            price=price
        )
        
        # توليد الرابط
        whatsapp_link = self.generate_whatsapp_link(phone, message)
        
        # نسخ للحافظة
        self.copy_to_clipboard(message)
        
        return {
            'success': True,
            'whatsapp_link': whatsapp_link,
            'message': message,
            'phone': phone
        }


def send_to_bakr(website_path: str, phone: str = "+9647701234567"):
    """إرسال موقع للبكر كاختبار"""
    sender = WhatsAppSender()
    
    # تحويل المسار لرابط محلي
    # في الإنتاج: نرفع الموقع على subdomain
    website_url = f"file:///{website_path.replace(os.sep, '/')}"
    
    result = sender.send_website(
        phone=phone,
        business_name="عيادة الأسنان المتميزة",
        website_url=website_url,
        price=150
    )
    
    print("=" * 50)
    print("📱 رسالة واتساب جاهزة!")
    print("=" * 50)
    print(f"الهاتف: {result['phone']}")
    print(f"الرابط: {result['whatsapp_link']}")
    print("-" * 50)
    print("الرسالة:")
    print(result['message'])
    print("-" * 50)
    print("✅ تم نسخ الرسالة للحافظة!")
    print("🔗 افتح الرابط للإرسال عبر واتساب")
    
    # فتح واتساب ويب
    webbrowser.open(result['whatsapp_link'])
    
    return result


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # اختبار - إرسال للبكر
    
    if len(sys.argv) > 1:
        website_path = sys.argv[1]
        phone = sys.argv[2] if len(sys.argv) > 2 else "+9647701234567"
        send_to_bakr(website_path, phone)
    else:
        print("الاستخدام: python whatsapp_sender.py <website_path> [phone]")
