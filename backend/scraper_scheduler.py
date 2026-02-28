"""
Scheduler - تشغيل السكرابر يومياً
"""

import schedule
import time
import threading
from datetime import datetime
import sys
import os

# إضافة المسار
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import IraqBusinessScraper
import sqlite3

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def run_daily_scraper():
    """تشغيل السكرابر اليومي"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] بدء السكرابر اليومي")
    print(f"{'='*50}\n")
    
    # تشغيل السكرابر
    scraper = IraqBusinessScraper()
    businesses = scraper.scrape_earabicmarket()
    
    # فلترة بدون موقع
    no_website = [b for b in businesses if not b.has_website]
    
    # إضافة للقاعدة
    conn = get_db()
    cursor = conn.cursor()
    
    added = 0
    for business in no_website:
        # التحقق من عدم وجوده مسبقاً
        cursor.execute('SELECT id FROM businesses WHERE phone = ? OR name = ?', 
                      (business.phone, business.name))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO businesses (name, phone, category, address, description, status)
                VALUES (?, ?, ?, ?, ?, 'prospect')
            ''', (
                business.name,
                business.phone,
                business.category,
                business.address,
                f"من {business.source}"
            ))
            added += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ تم إضافة {added} زبون جديد")
    print(f"   إجمالي بدون موقع: {len(no_website)}")
    
    # حفظ تقرير
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.now().isoformat()}] Added: {added}, Total found: {len(no_website)}\n")
    
    return added

def schedule_jobs():
    """جدولة المهام"""
    # تشغيل يومي في 9 صباحاً
    schedule.every().day.at("09:00").do(run_daily_scraper)
    
    # تشغيل إضافي في 6 مساءً
    schedule.every().day.at("18:00").do(run_daily_scraper)
    
    print("📅 Scheduler started:")
    print("   - Daily at 09:00")
    print("   - Daily at 18:00")
    print("\nPress Ctrl+C to stop\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # فحص كل دقيقة

def run_in_thread():
    """تشغيل في thread منفصل"""
    thread = threading.Thread(target=schedule_jobs, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 50)
    print("IRAQ WEBSITE BUSINESS - Scheduler")
    print("=" * 50)
    
    # تشغيل مرة الآن
    print("\nتشغيل أولي...")
    run_daily_scraper()
    
    # بدء الجدولة
    schedule_jobs()
