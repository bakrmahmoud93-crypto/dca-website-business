"""
deploy.py - رفع المواقع على دومين مجاني (Netlify/Vercel)
"""

import os
import subprocess
import json
import requests
from datetime import datetime

class WebsiteDeployer:
    """نشر المواقع على خدمات مجانية"""
    
    def __init__(self):
        self.sites_dir = os.path.join(os.path.dirname(__file__), 'generated_sites')
        self.deployments_file = os.path.join(os.path.dirname(__file__), 'deployments.json')
        self.load_deployments()
    
    def load_deployments(self):
        """تحميل سجل النشر"""
        if os.path.exists(self.deployments_file):
            with open(self.deployments_file, 'r', encoding='utf-8') as f:
                self.deployments = json.load(f)
        else:
            self.deployments = {"sites": []}
    
    def save_deployments(self):
        """حفظ سجل النشر"""
        with open(self.deployments_file, 'w', encoding='utf-8') as f:
            json.dump(self.deployments, f, ensure_ascii=False, indent=2)
    
    def deploy_to_netlify(self, html_path: str, business_name: str) -> dict:
        """
        نشر على Netlify Drop (مجاني)
        يتطلب: npm install -g netlify-cli
        """
        try:
            # إنشاء مجلد للنشر
            deploy_dir = os.path.join(self.sites_dir, '_deploy_temp')
            os.makedirs(deploy_dir, exist_ok=True)
            
            # نسخ الملف كـ index.html
            deploy_file = os.path.join(deploy_dir, 'index.html')
            
            # قراءة وتعديل HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            with open(deploy_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # النشر باستخدام netlify deploy
            result = subprocess.run(
                ['netlify', 'deploy', '--prod', '--dir', deploy_dir],
                capture_output=True,
                text=True,
                cwd=deploy_dir
            )
            
            # استخراج الرابط من المخرجات
            if result.returncode == 0:
                # البحث عن رابط URL في المخرجات
                lines = result.stdout.split('\n')
                site_url = None
                for line in lines:
                    if 'https://' in line and 'netlify' in line:
                        # استخراج الرابط
                        import re
                        urls = re.findall(r'https://[^\s]+\.netlify\.app', line)
                        if urls:
                            site_url = urls[0]
                            break
                
                if site_url:
                    deployment = {
                        'business_name': business_name,
                        'local_path': html_path,
                        'live_url': site_url,
                        'deployed_at': datetime.now().isoformat(),
                        'platform': 'netlify'
                    }
                    self.deployments['sites'].append(deployment)
                    self.save_deployments()
                    
                    return {'success': True, 'url': site_url, 'deployment': deployment}
            
            return {'success': False, 'error': result.stderr}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def deploy_to_surge(self, html_path: str, business_name: str) -> dict:
        """
        نشر على Surge.sh (مجاني وسريع)
        يتطلب: npm install -g surge
        """
        try:
            # إنشاء اسم نطاق فريد
            safe_name = "".join(c for c in business_name if c.isalnum()).lower()
            domain = f"{safe_name}-{datetime.now().strftime('%Y%m%d%H%M')}.surge.sh"
            
            # إنشاء مجلد للنشر
            deploy_dir = os.path.join(self.sites_dir, '_deploy_temp')
            os.makedirs(deploy_dir, exist_ok=True)
            
            # نسخ الملف
            deploy_file = os.path.join(deploy_dir, 'index.html')
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            with open(deploy_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # النشر
            result = subprocess.run(
                ['surge', deploy_dir, domain],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                site_url = f"https://{domain}"
                deployment = {
                    'business_name': business_name,
                    'local_path': html_path,
                    'live_url': site_url,
                    'deployed_at': datetime.now().isoformat(),
                    'platform': 'surge'
                }
                self.deployments['sites'].append(deployment)
                self.save_deployments()
                
                return {'success': True, 'url': site_url, 'deployment': deployment}
            
            return {'success': False, 'error': result.stderr}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def deploy_to_github_pages(self, html_path: str, business_name: str) -> dict:
        """
        نشر على GitHub Pages (مجاني)
        يتطلب: git config
        """
        # يتطلب إعداد repo مسبق
        return {'success': False, 'error': 'GitHub Pages يتطلب إعداد repo مسبق'}
    
    def get_simple_hosting(self, html_content: str, business_name: str) -> dict:
        """
        استخدام خدمة استضافة بسيطة
        صفحات ثابتة على خدمة مجانية
        """
        # يمكن استخدام:
        # - Tiiny.host
        # - Static.app
        # - Render.com
        
        return {
            'success': False,
            'error': 'استخدم deploy_to_surge أو deploy_to_netlify',
            'alternatives': [
                'tiiny.host',
                'static.app',
                'render.com'
            ]
        }
    
    def deploy(self, html_path: str, business_name: str, method: str = 'surge') -> dict:
        """نشر الموقع"""
        if method == 'surge':
            return self.deploy_to_surge(html_path, business_name)
        elif method == 'netlify':
            return self.deploy_to_netlify(html_path, business_name)
        else:
            return {'success': False, 'error': f'طريقة غير معروفة: {method}'}


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    deployer = WebsiteDeployer()
    
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
        business_name = sys.argv[2] if len(sys.argv) > 2 else "business"
        
        print(f"جاري نشر {business_name}...")
        result = deployer.deploy(html_path, business_name, 'surge')
        
        if result['success']:
            print(f"تم النشر بنجاح!")
            print(f"الرابط: {result['url']}")
        else:
            print(f"فشل النشر: {result['error']}")
    else:
        print("الاستخدام: python deploy.py <html_path> <business_name>")
