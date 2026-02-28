"""
deploy_final.py - النشر النهائي
"""
import subprocess
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SURGE_PATH = r"D:\npm\surge.cmd"
DEPLOY_DIR = r"C:\Users\Administrator\.openclaw\workspace\projects\iraq-website-business\generated_sites\deploy_temp"
DOMAIN = "dca-dental-clinic.surge.sh"

print("=" * 50)
print("نشر الموقع على Surge.sh")
print("=" * 50)

print("\nمحاولة النشر...")

# تشغيل surge
result = subprocess.run(
    [SURGE_PATH, ".", DOMAIN],
    cwd=DEPLOY_DIR,
    capture_output=True,
    text=True,
    shell=True
)

print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\nReturn code:", result.returncode)
