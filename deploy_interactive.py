"""
deploy_interactive.py - نشر تفاعلي
"""
import subprocess
import sys
import os
import time

deploy_dir = r"C:\Users\Administrator\.openclaw\workspace\projects\iraq-website-business\generated_sites\deploy_temp"
domain = "dca-dental-clinic.surge.sh"

print("=" * 50)
print("نشر الموقع على Surge.sh")
print("=" * 50)

# إنشاء ملف الاعتمادات
creds = """clawadam828@gmail.com
P@ssw0rd@123.com.
"""

# محاولة النشر المباشر (إذا كان مسجل مسبقاً)
print("\nمحاولة النشر...")
result = subprocess.run(
    ["surge", ".", domain],
    cwd=deploy_dir,
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("Error:", result.stderr)

if "Published" in result.stdout or "Success" in result.stdout:
    print(f"\n✅ تم النشر: https://{domain}")
else:
    print("\n⚠️ يحتاج تسجيل دخول...")
    print("\nقم بتشغيل هذا الأمر يدوياً:")
    print(f"  cd {deploy_dir}")
    print(f"  surge . {domain}")
    print("\nأدخل:")
    print(f"  Email: clawadam828@gmail.com")
    print(f"  Password: P@ssw0rd@123.com.")
