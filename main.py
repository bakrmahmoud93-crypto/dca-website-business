"""
main.py - النظام الرئيسي المتكامل
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import webbrowser
from datetime import datetime
from website_generator import WebsiteGenerator
from deploy import WebsiteDeployer
from whatsapp_sender import WhatsAppSender

class IraqWebsiteBusiness:
    """النظام الرئيسي"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.db_file = os.path.join(self.base_dir, 'database.json')
        self.generator = WebsiteGenerator()
        self.deployer = WebsiteDeployer()
        self.sender = WhatsAppSender()
        
        self.load_database()
    
    def load_database(self):
        """تحميل قاعدة البيانات"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
        else:
            self.db = {
                "schema": "iraq_website_business_v1",
                "businesses": [],
                "settings": {
                    "defaultPrice": 150,
                    "deployMethod": "surge"
                },
                "stats": {
                    "total": 0,
                    "no_website": 0,
                    "contacted": 0,
                    "interested": 0,
                    "sold": 0,
                    "revenue": 0
                }
            }
    
    def save_database(self):
        """حفظ قاعدة البيانات"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)
    
    def add_business(self, name: str, phone: str, category: str = "other", 
                     address: str = "", description: str = "") -> dict:
        """إضافة زبون جديد"""
        business = {
            "id": len(self.db['businesses']) + 1,
            "name": name,
            "phone": phone,
            "category": category,
            "address": address,
            "description": description,
            "status": "prospect",
            "website_url": None,
            "created_at": datetime.now().isoformat()
        }
        
        self.db['businesses'].append(business)
        self.db['stats']['total'] += 1
        self.save_database()
        
        return business
    
    def generate_website(self, business_id: int) -> dict:
        """توليد موقع لزبون"""
        business = next((b for b in self.db['businesses'] if b['id'] == business_id), None)
        
        if not business:
            return {"success": False, "error": "الزبون غير موجود"}
        
        # توليد الموقع
        html_path = self.generator.generate_website(business)
        
        # نشر الموقع
        deploy_result = self.deployer.deploy(html_path, business['name'], 'surge')
        
        if deploy_result['success']:
            # تحديث قاعدة البيانات
            business['website_url'] = deploy_result['url']
            business['local_path'] = html_path
            business['status'] = 'sent'
            self.save_database()
            
            return {
                "success": True,
                "url": deploy_result['url'],
                "business": business
            }
        
        return deploy_result
    
    def send_to_whatsapp(self, business_id: int, price: int = None) -> dict:
        """إرسال الموقع عبر واتساب"""
        business = next((b for b in self.db['businesses'] if b['id'] == business_id), None)
        
        if not business or not business.get('website_url'):
            return {"success": False, "error": "الموقع غير جاهز"}
        
        price = price or self.db['settings']['defaultPrice']
        
        result = self.sender.send_website(
            phone=business['phone'],
            business_name=business['name'],
            website_url=business['website_url'],
            price=price
        )
        
        # فتح واتساب
        webbrowser.open(result['whatsapp_link'])
        
        return result
    
    def process_business(self, business_id: int) -> dict:
        """معالجة كاملة: توليد + نشر + إرسال"""
        print(f"\n{'='*50}")
        print(f"معالجة الزبون #{business_id}")
        print(f"{'='*50}")
        
        # 1. توليد الموقع
        print("\n[1/3] توليد الموقع...")
        gen_result = self.generate_website(business_id)
        
        if not gen_result['success']:
            print(f"خطأ: {gen_result.get('error')}")
            return gen_result
        
        print(f"تم النشر: {gen_result['url']}")
        
        # 2. إرسال واتساب
        print("\n[2/3] فتح واتساب...")
        send_result = self.send_to_whatsapp(business_id)
        
        # 3. فتح الموقع للمعاينة
        print("\n[3/3] فتح الموقع للمعاينة...")
        webbrowser.open(gen_result['url'])
        
        print(f"\n{'='*50}")
        print("تم بنجاح!")
        print(f"{'='*50}")
        
        return {
            "success": True,
            "website_url": gen_result['url'],
            "whatsapp_link": send_result['whatsapp_link']
        }
    
    def get_prospects(self) -> list:
        """الحصول على قائمة الزبائن المحتملين"""
        return [b for b in self.db['businesses'] if b['status'] == 'prospect']
    
    def get_stats(self) -> dict:
        """الحصول على الإحصائيات"""
        return self.db['stats']
    
    def open_dashboard(self):
        """فتح لوحة التحكم"""
        dashboard_path = os.path.join(self.base_dir, 'dashboard', 'index.html')
        webbrowser.open(f'file:///{dashboard_path.replace(os.sep, "/")}')
        print("تم فتح لوحة التحكم!")


def demo():
    """تجربة النظام"""
    system = IraqWebsiteBusiness()
    
    # إضافة زبون تجريبي
    print("\nإضافة زبون تجريبي...")
    business = system.add_business(
        name="عيادة الأسنان المتميزة",
        phone="+9647701234567",
        category="clinic",
        address="بغداد، المنصور",
        description="عيادة أسنان متخصصة"
    )
    
    print(f"تم إضافة: {business['name']} (ID: {business['id']})")
    
    # فتح الداشبورد
    print("\nفتح لوحة التحكم...")
    system.open_dashboard()
    
    print("\nالزبائن المحتملين:")
    for b in system.get_prospects():
        print(f"  - {b['name']} ({b['phone']})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        system = IraqWebsiteBusiness()
        
        if command == 'dashboard':
            system.open_dashboard()
        elif command == 'add':
            # python main.py add "اسم المحل" "+964770..." clinic
            name = sys.argv[2] if len(sys.argv) > 2 else "Test Business"
            phone = sys.argv[3] if len(sys.argv) > 3 else "+9647700000000"
            category = sys.argv[4] if len(sys.argv) > 4 else "other"
            system.add_business(name, phone, category)
            print(f"تم إضافة {name}")
        elif command == 'process':
            # python main.py process 1
            business_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            system.process_business(business_id)
        elif command == 'demo':
            demo()
        else:
            print("الأوامر: dashboard, add, process, demo")
    else:
        demo()
