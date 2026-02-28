"""
auto_deploy.py - نشر تلقائي على Surge
"""
import pexpect
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EMAIL = "clawadam828@gmail.com"
PASSWORD = "P@ssw0rd@123.com."
DOMAIN = "dca-dental-clinic.surge.sh"
DEPLOY_DIR = r"C:\Users\Administrator\.openclaw\workspace\projects\iraq-website-business\generated_sites\deploy_temp"

def login_and_deploy():
    print("تسجيل الدخول إلى Surge...")
    
    # تشغيل surge login
    child = pexpect.spawn('surge login', encoding='utf-8', timeout=30)
    
    # انتظار طلب الإيميل
    child.expect('email:')
    print("إدخال الإيميل...")
    child.sendline(EMAIL)
    
    # انتظار طلب الباسوورد
    child.expect('password:')
    print("إدخال الباسوورد...")
    child.sendline(PASSWORD)
    
    # انتظار النتيجة
    child.expect(pexpect.EOF)
    print(child.before)
    
    print("\nتم تسجيل الدخول!")
    print("\nجاري نشر الموقع...")
    
    # نشر الموقع
    deploy = pexpect.spawn(f'surge {DEPLOY_DIR} {DOMAIN}', encoding='utf-8', timeout=60)
    deploy.expect(pexpect.EOF)
    print(deploy.before)
    
    print(f"\nتم النشر! الرابط: https://{DOMAIN}")

if __name__ == "__main__":
    try:
        login_and_deploy()
    except Exception as e:
        print(f"خطأ: {e}")
        # محاولة بديلة
        print("\nجاري المحاولة البديلة...")
        os.system(f'cd {DEPLOY_DIR} && surge . {DOMAIN}')
