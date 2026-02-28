"""
WordPress Site Generator - يولد مواقع ووردبريس احترافية
"""

import requests
import json
from typing import dict, Optional
import os

class WordPressGenerator:
    """
    توليد مواقع ووردبريس عبر REST API
    
    المتطلبات:
    - موقع ووردبريس مثبت
    - Application Password للـ API
    - قالب احترافي (مثل Astra, OceanWP)
    """
    
    def __init__(self, wp_url: str, username: str, app_password: str):
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.session = requests.Session()
        self.session.auth = (username, app_password)
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def create_page(self, title: str, content: str, status: str = 'publish') -> dict:
        """إنشاء صفحة جديدة"""
        endpoint = f"{self.wp_url}/wp-json/wp/v2/pages"
        
        data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        response = self.session.post(endpoint, json=data)
        
        if response.status_code == 201:
            return {'success': True, 'page': response.json()}
        
        return {'success': False, 'error': response.text}
    
    def create_post(self, title: str, content: str, categories: list = None, status: str = 'publish') -> dict:
        """إنشاء مقال جديد"""
        endpoint = f"{self.wp_url}/wp-json/wp/v2/posts"
        
        data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        if categories:
            data['categories'] = categories
        
        response = self.session.post(endpoint, json=data)
        
        if response.status_code == 201:
            return {'success': True, 'post': response.json()}
        
        return {'success': False, 'error': response.text}
    
    def upload_media(self, file_path: str, title: str = None) -> dict:
        """رفع صورة"""
        endpoint = f"{self.wp_url}/wp-json/wp/v2/media"
        
        headers = {
            'Content-Disposition': f'attachment; filename={os.path.basename(file_path)}',
            'Content-Type': 'image/jpeg'  # أو نوع الصورة المناسب
        }
        
        with open(file_path, 'rb') as f:
            response = self.session.post(
                endpoint,
                headers=headers,
                data=f.read()
            )
        
        if response.status_code == 201:
            return {'success': True, 'media': response.json()}
        
        return {'success': False, 'error': response.text}
    
    def set_site_title(self, title: str) -> dict:
        """تغيير عنوان الموقع"""
        endpoint = f"{self.wp_url}/wp-json/wp/v2/settings"
        
        response = self.session.post(endpoint, json={'title': title})
        
        if response.status_code == 200:
            return {'success': True}
        
        return {'success': False, 'error': response.text}
    
    def generate_business_site(self, business_data: dict) -> dict:
        """
        توليد موقع كامل لعمل
        
        Args:
            business_data: {
                'name': 'اسم العمل',
                'category': 'clinic/restaurant/salon/shop',
                'phone': '+964...',
                'address': 'العنوان',
                'description': 'الوصف',
                'services': ['خدمة 1', 'خدمة 2']
            }
        """
        results = {'pages': [], 'errors': []}
        
        # 1. تغيير عنوان الموقع
        title_result = self.set_site_title(business_data['name'])
        if not title_result['success']:
            results['errors'].append(f"خطأ في تغيير العنوان: {title_result.get('error')}")
        
        # 2. إنشاء الصفحة الرئيسية
        home_content = self._generate_home_content(business_data)
        home_result = self.create_page(business_data['name'], home_content)
        
        if home_result['success']:
            results['pages'].append({'title': 'الرئيسية', 'url': home_result['page']['link']})
        else:
            results['errors'].append(f"خطأ في الصفحة الرئيسية: {home_result.get('error')}")
        
        # 3. إنشاء صفحة "من نحن"
        about_content = self._generate_about_content(business_data)
        about_result = self.create_page('من نحن', about_content)
        
        if about_result['success']:
            results['pages'].append({'title': 'من نحن', 'url': about_result['page']['link']})
        
        # 4. إنشاء صفحة الخدمات
        services_content = self._generate_services_content(business_data)
        services_result = self.create_page('خدماتنا', services_content)
        
        if services_result['success']:
            results['pages'].append({'title': 'خدماتنا', 'url': services_result['page']['link']})
        
        # 5. إنشاء صفحة اتصل بنا
        contact_content = self._generate_contact_content(business_data)
        contact_result = self.create_page('اتصل بنا', contact_content)
        
        if contact_result['success']:
            results['pages'].append({'title': 'اتصل بنا', 'url': contact_result['page']['link']})
        
        results['success'] = len(results['pages']) > 0
        return results
    
    def _generate_home_content(self, data: dict) -> str:
        """توليد محتوى الصفحة الرئيسية"""
        return f"""
<!-- wp:html -->
<style>
.hero {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 80px 20px;
    text-align: center;
    border-radius: 20px;
    margin-bottom: 40px;
}}
.hero h1 {{ font-size: 3em; margin-bottom: 20px; }}
.hero p {{ font-size: 1.3em; opacity: 0.9; }}
.btn {{
    display: inline-block;
    background: white;
    color: #764ba2;
    padding: 15px 40px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: bold;
    margin-top: 30px;
    transition: transform 0.3s;
}}
.btn:hover {{ transform: scale(1.1); }}
.services {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 40px 0; }}
.service {{ text-align: center; padding: 30px; background: #f8f9fa; border-radius: 15px; }}
.service-icon {{ font-size: 48px; margin-bottom: 15px; }}
@media (max-width: 768px) {{ .services {{ grid-template-columns: 1fr; }} }}
</style>
<!-- /wp:html -->

<!-- wp:html -->
<div class="hero">
    <h1>{data['name']}</h1>
    <p>{data.get('tagline', 'خدمات متميزة لعملائنا الكرام')}</p>
    <a href="tel:{data['phone']}" class="btn">📞 اتصل بنا الآن</a>
</div>
<!-- /wp:html -->

<!-- wp:paragraph -->
<p style="text-align: center; font-size: 1.2em;">{data.get('description', 'مرحباً بكم في موقعنا')}</p>
<!-- /wp:paragraph -->

<!-- wp:html -->
<div class="services">
    <div class="service">
        <div class="service-icon">✅</div>
        <h3>جودة عالية</h3>
        <p>نلتزم بأعلى معايير الجودة</p>
    </div>
    <div class="service">
        <div class="service-icon">⚡</div>
        <h3>خدمة سريعة</h3>
        <p>نحترم وقتكم الثمين</p>
    </div>
    <div class="service">
        <div class="service-icon">🤝</div>
        <h3>ثقة ومصداقية</h3>
        <p>سنوات من الخبرة والتميز</p>
    </div>
</div>
<!-- /wp:html -->
"""
    
    def _generate_about_content(self, data: dict) -> str:
        """توليد محتوى صفحة من نحن"""
        return f"""
<!-- wp:heading -->
<h2>من نحن</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{data['name']} - نحن فريق متخصص نقدم لكم أفضل الخدمات بجودة عالية وأسعار منافسة.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>خبرتنا الطويلة في مجال {data.get('category', 'الخدمات')} تضمن لكم الحصول على أفضل النتائج.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h3>لماذا تختاروننا؟</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
    <li>خبرة احترافية</li>
    <li>أسعار تنافسية</li>
    <li>خدمة عملاء متميزة</li>
    <li>ضمان الجودة</li>
</ul>
<!-- /wp:list -->
"""
    
    def _generate_services_content(self, data: dict) -> str:
        """توليد محتوى صفحة الخدمات"""
        services_html = "<!-- wp:heading --><h2>خدماتنا</h2><!-- /wp:heading -->"
        
        services = data.get('services', ['خدمة 1', 'خدمة 2', 'خدمة 3'])
        for i, service in enumerate(services, 1):
            services_html += f"""
<!-- wp:paragraph -->
<p><strong>{i}. {service}</strong></p>
<!-- /wp:paragraph -->
"""
        
        return services_html
    
    def _generate_contact_content(self, data: dict) -> str:
        """توليد محتوى صفحة اتصل بنا"""
        return f"""
<!-- wp:html -->
<style>
.contact-box {{
    background: #f8f9fa;
    padding: 30px;
    border-radius: 15px;
    margin: 20px 0;
}}
.contact-item {{
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    background: white;
    border-radius: 10px;
    margin-bottom: 10px;
}}
.contact-icon {{ font-size: 24px; }}
</style>

<div class="contact-box">
    <h2>تواصلوا معنا</h2>
    
    <div class="contact-item">
        <span class="contact-icon">📍</span>
        <div>
            <strong>العنوان:</strong><br>
            {data.get('address', 'بغداد، العراق')}
        </div>
    </div>
    
    <div class="contact-item">
        <span class="contact-icon">📞</span>
        <div>
            <strong>الهاتف:</strong><br>
            <a href="tel:{data['phone']}">{data['phone']}</a>
        </div>
    </div>
    
    <div class="contact-item">
        <span class="contact-icon">🕐</span>
        <div>
            <strong>أوقات العمل:</strong><br>
            السبت - الخميس: 9 ص - 9 م
        </div>
    </div>
</div>
<!-- /wp:html -->
"""


# ============= بديل: WP CLI =============

class WordPressCLIGenerator:
    """
    توليد مواقع ووردبريس عبر WP CLI
    
    المتطلبات:
    - WP CLI مثبت
    - وصول SSH للسيرفر
    """
    
    def __init__(self, wp_path: str):
        self.wp_path = wp_path
    
    def create_site(self, business_data: dict) -> dict:
        """إنشاء موقع جديد"""
        import subprocess
        
        # أوامر WP CLI
        commands = [
            f'cd {self.wp_path}',
            f'wp option update blogname "{business_data["name"]}"',
            f'wp post create --post_type=page --post_title="الرئيسية" --post_status=publish',
            f'wp post create --post_type=page --post_title="من نحن" --post_status=publish',
            f'wp post create --post_type=page --post_title="خدماتنا" --post_status=publish',
            f'wp post create --post_type=page --post_title="اتصل بنا" --post_status=publish',
        ]
        
        for cmd in commands:
            subprocess.run(cmd, shell=True)
        
        return {'success': True}


# ============= Mock Generator للاختبار =============

class MockWordPressGenerator:
    """مولد وهمي للاختبار بدون ووردبريس"""
    
    def generate_business_site(self, business_data: dict) -> dict:
        """توليد موقع وهمي"""
        return {
            'success': True,
            'site_url': f"https://demo-site-{business_data['name'].replace(' ', '-')}.com",
            'pages': [
                {'title': 'الرئيسية', 'url': '/home'},
                {'title': 'من نحن', 'url': '/about'},
                {'title': 'خدماتنا', 'url': '/services'},
                {'title': 'اتصل بنا', 'url': '/contact'},
            ]
        }


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # اختبار
    print("اختبار WordPress Generator\n")
    
    # استخدام Mock للاختبار
    generator = MockWordPressGenerator()
    
    result = generator.generate_business_site({
        'name': 'عيادة الأسنان المتميزة',
        'category': 'clinic',
        'phone': '+9647701234567',
        'address': 'بغداد، المنصور',
        'description': 'عيادة أسنان متخصصة بأحدث التقنيات'
    })
    
    print(f"نتيجة: {result}")
