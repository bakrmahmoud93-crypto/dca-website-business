"""
Website Generator - يولد مواقع للشركات العراقية
"""

from jinja2 import Template
import os
from datetime import datetime

class WebsiteGenerator:
    """مولد المواقع التلقائي"""
    
    def __init__(self):
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'generated_sites')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # قوالب جاهزة حسب نوع العمل
        self.business_templates = {
            'clinic': {
                'icon': '🏥',
                'tagline': 'رعاية صحية متميزة',
                'services': [
                    {'icon': '🩺', 'title': 'فحوصات شاملة', 'description': 'فحوصات طبية دقيقة'},
                    {'icon': '💊', 'title': 'علاج متخصص', 'description': 'خطط علاج مخصصة'},
                    {'icon': '🔬', 'title': 'تشخيص متطور', 'description': 'أحدث التقنيات'}
                ]
            },
            'restaurant': {
                'icon': '🍽️',
                'tagline': 'نكهات لا تُنسى',
                'services': [
                    {'icon': '🍕', 'title': 'أطباق متنوعة', 'description': 'أشهى المأكولات'},
                    {'icon': '🚗', 'title': 'توصيل سريع', 'description': 'نوصل لباب بيتك'},
                    {'icon': '🎉', 'title': 'مناسبات', 'description': 'حفلات واعياد ميلاد'}
                ]
            },
            'salon': {
                'icon': '💇',
                'tagline': 'جمالك أولويتنا',
                'services': [
                    {'icon': '💇‍♀️', 'title': 'قصات عصرية', 'description': 'أحدث صيحات الموضة'},
                    {'icon': '💅', 'title': 'مانكير وبديكير', 'description': 'عناية كاملة'},
                    {'icon': '💆', 'title': 'علاجات تجميل', 'description': 'خدمات متكاملة'}
                ]
            },
            'shop': {
                'icon': '🏪',
                'tagline': 'كل ما تحتاجه',
                'services': [
                    {'icon': '📦', 'title': 'منتجات متنوعة', 'description': 'أفضل الماركات'},
                    {'icon': '💰', 'title': 'أسعار منافسة', 'description': 'قيمة ممتازة'},
                    {'icon': '🎁', 'title': 'عروض خاصة', 'description': 'خصومات أسبوعية'}
                ]
            },
            'default': {
                'icon': '🏢',
                'tagline': 'خدمات متميزة',
                'services': [
                    {'icon': '✅', 'title': 'جودة عالية', 'description': 'نلتزم بأعلى المعايير'},
                    {'icon': '⚡', 'title': 'خدمة سريعة', 'description': 'نحترم وقتك'},
                    {'icon': '🤝', 'title': 'ثقة ومصداقية', 'description': 'خبرة سنوات'}
                ]
            }
        }
    
    def get_template_type(self, category: str) -> str:
        """تحديد نوع القالب حسب الفئة"""
        category_lower = category.lower()
        
        if any(x in category_lower for x in ['عيادة', 'طب', 'صحة', 'دكتور', 'clinic', 'medical', 'dental']):
            return 'clinic'
        elif any(x in category_lower for x in ['مطعم', 'كافي', 'مأكول', 'restaurant', 'cafe', 'food']):
            return 'restaurant'
        elif any(x in category_lower for x in ['صالون', 'حلاقة', 'جمال', 'salon', 'beauty', 'barber']):
            return 'salon'
        elif any(x in category_lower for x in ['محل', 'متجر', 'سوبرماركت', 'shop', 'store', 'market']):
            return 'shop'
        else:
            return 'default'
    
    def generate_website(self, business_data: dict) -> str:
        """توليد موقع لشركة معينة"""
        
        # تحديد نوع القالب
        template_type = self.get_template_type(business_data.get('category', ''))
        template_config = self.business_templates[template_type]
        
        # تجهيز البيانات
        context = {
            'business_name': business_data.get('name', 'اسم العمل'),
            'business_category': business_data.get('category', 'خدمات'),
            'tagline': template_config['tagline'],
            'icon': template_config['icon'],
            'description': business_data.get('description', f"نحن {business_data.get('name', 'اسم العمل')} نقدم لكم أفضل الخدمات بجودة عالية وأسعار منافسة. زورونا واكتشفوا الفرق!"),
            'address': business_data.get('address', 'بغداد، العراق'),
            'phone': business_data.get('phone', '+964 XXX XXX XXXX'),
            'whatsapp': business_data.get('whatsapp', business_data.get('phone', '')),
            'working_hours': business_data.get('working_hours', 'السبت - الخميس: 9 ص - 9 م'),
            'services': template_config['services']
        }
        
        # قراءة القالب
        template_path = os.path.join(self.templates_dir, 'clinic.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # تطبيق القالب
        template = Template(template_content)
        html_content = template.render(**context)
        
        # حفظ الملف
        safe_name = "".join(c for c in business_data.get('name', 'business') if c.isalnum() or c in ' -_').strip()
        safe_name = safe_name.replace(' ', '-').replace('_', '-')
        filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_for_bakr(self) -> str:
        """توليد موقع تجريبي للبكر"""
        business_data = {
            'name': 'عيادة الأسنان المتميزة',
            'category': 'عيادة أسنان',
            'description': 'نقدم لكم أحدث تقنيات طب الأسنان مع فريق من أمهر الأطباء. خدماتنا تشمل تبييض الأسنان، تركيبات، زراعة، وعلاج الجذور بأسعار مناسبة للجميع.',
            'address': 'المنصور، شارع الأميرات، بناية رقم 15',
            'phone': '+964 770 123 4567',
            'whatsapp': '+9647701234567',
            'working_hours': 'السبت - الخميس: 10 ص - 8 م'
        }
        
        return self.generate_website(business_data)


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    generator = WebsiteGenerator()
    
    # توليد موقع للبكر كاختبار
    path = generator.generate_for_bakr()
    print(f"تم انشاء الموقع: {path}")
