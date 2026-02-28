# DCA Website Business 🛡️

نظام بيع المواقع للشركات العراقية

## 🚀 التشغيل المحلي

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل السيرفر
python -m backend.app
```

ثم افتح: http://localhost:5000

## 📦 البنية

```
├── backend/
│   ├── app.py              ← Flask API
│   ├── scraper_scheduler.py ← سكرابر يومي
│   └── database.db
├── frontend/
│   └── index.html          ← Dashboard
├── wordpress_generator/
│   └── generate.py         ← WP sites
└── requirements.txt
```

## 🔧 API Endpoints

- `GET /api/businesses` - جلب الزبائن
- `POST /api/businesses` - إضافة زبون
- `GET /api/stats` - الإحصائيات
- `PUT /api/permissions/:key` - تحكم بالصلاحيات

## 🌐 النشر على Render

1. ارفع على GitHub
2. اربط Render بالـ repo
3. Deploy تلقائي!

---

Made with ❤️ by DCA
