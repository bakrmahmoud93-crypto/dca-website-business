"""
Iraq Business Scraper - يستخرج الشركات العراقية بدون موقع إلكتروني
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from dataclasses import dataclass
from typing import List, Optional
import os

@dataclass
class Business:
    """بيانات الشركة أو المحل"""
    name: str
    category: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    has_website: bool = False
    source: str = ""
    city: str = "بغداد"
    
    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "has_website": self.has_website,
            "source": self.source,
            "city": self.city
        }

class IraqBusinessScraper:
    """مستخرج الشركات العراقية"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.businesses: List[Business] = []
        
    def scrape_earabicmarket(self, category: str = "") -> List[Business]:
        """استخراج من دليل earabicmarket"""
        businesses = []
        base_url = "http://iraq.earabicmarket.com/"
        
        try:
            response = self.session.get(base_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن روابط الفئات
            categories = soup.find_all('a', href=True)
            for cat_link in categories:
                href = cat_link.get('href', '')
                if '/category/' in href or '/companies/' in href:
                    # استخراج الشركات من كل فئة
                    cat_url = base_url.rstrip('/') + href if href.startswith('/') else href
                    try:
                        cat_response = self.session.get(cat_url, timeout=30)
                        cat_soup = BeautifulSoup(cat_response.text, 'html.parser')
                        
                        # استخراج بيانات الشركات
                        listings = cat_soup.find_all('div', class_=re.compile('(company|business|listing|item)', re.I))
                        for listing in listings:
                            name_elem = listing.find(['h2', 'h3', 'h4', 'a'], class_=re.compile('(name|title)', re.I))
                            name = name_elem.get_text(strip=True) if name_elem else listing.find('a').get_text(strip=True) if listing.find('a') else ""
                            
                            if not name:
                                continue
                                
                            # البحث عن الموقع
                            website = None
                            links = listing.find_all('a', href=True)
                            for link in links:
                                href = link.get('href', '')
                                if href.startswith('http') and 'earabicmarket' not in href:
                                    website = href
                                    break
                            
                            # استخراج العنوان والهاتف
                            address_elem = listing.find(['p', 'span', 'div'], class_=re.compile('(address|location)', re.I))
                            address = address_elem.get_text(strip=True) if address_elem else ""
                            
                            phone_elem = listing.find(['p', 'span', 'a'], string=re.compile(r'(\+?964|0\d{2})'))
                            phone = phone_elem.get_text(strip=True) if phone_elem else ""
                            
                            business = Business(
                                name=name,
                                category=category or "عام",
                                address=address,
                                phone=phone if phone else None,
                                website=website,
                                has_website=bool(website),
                                source="earabicmarket"
                            )
                            businesses.append(business)
                            
                    except Exception as e:
                        print(f"خطأ في فئة {cat_url}: {e}")
                        continue
                        
        except Exception as e:
            print(f"خطأ في الاتصال بـ earabicmarket: {e}")
            
        return businesses
    
    def scrape_google_maps_manual(self, search_query: str, city: str = "بغداد") -> List[Business]:
        """
        استخراج من Google Maps - الطريقة اليدوية
        ملاحظة: للحصول على نتائج أفضل استخدم Outscraper أو Apify
        """
        businesses = []
        
        # هذه طريقة مبسطة - للإنتاج استخدم API أو خدمة خارجية
        search_url = f"https://www.google.com/maps/search/{search_query}+in+{city}+Iraq"
        
        print(f"للاستخراج الكامل من Google Maps، استخدم:")
        print(f"1. Outscraper: https://outscraper.com/google-maps-scraper/")
        print(f"2. Apify: https://apify.com/compass/google-maps-scraper")
        print(f"3. Scrap.io: https://scrap.io/")
        
        return businesses
    
    def filter_no_website(self, businesses: List[Business]) -> List[Business]:
        """فلترة الشركات بدون موقع"""
        return [b for b in businesses if not b.has_website]
    
    def save_to_json(self, businesses: List[Business], filename: str = "businesses.json"):
        """حفظ البيانات في ملف JSON"""
        data = [b.to_dict() for b in businesses]
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"تم حفظ {len(businesses)} شركة في {filepath}")
        
    def save_to_csv(self, businesses: List[Business], filename: str = "businesses.csv"):
        """حفظ البيانات في ملف CSV"""
        import csv
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'category', 'address', 'phone', 'email', 'website', 'has_website', 'source', 'city'])
            writer.writeheader()
            for b in businesses:
                writer.writerow(b.to_dict())
        
        print(f"تم حفظ {len(businesses)} شركة في {filepath}")
    
    def run(self):
        """تشغيل السكرابر"""
        print("=" * 50)
        print("🚀 بدء استخراج الشركات العراقية...")
        print("=" * 50)
        
        # استخراج من earabicmarket
        print("\n📍 استخراج من دليل العراق التجاري...")
        businesses = self.scrape_earabicmarket()
        
        # فلترة بدون موقع
        no_website = self.filter_no_website(businesses)
        
        print(f"\n📊 النتائج:")
        print(f"   - إجمالي الشركات: {len(businesses)}")
        print(f"   - بدون موقع: {len(no_website)}")
        
        # حفظ البيانات
        if businesses:
            self.save_to_json(businesses)
            self.save_to_csv(businesses)
        
        return no_website

if __name__ == "__main__":
    scraper = IraqBusinessScraper()
    results = scraper.run()
    
    print(f"\n✅ تم العثور على {len(results)} شركة بدون موقع!")
    print("📄 البيانات محفوظة في businesses.json و businesses.csv")
