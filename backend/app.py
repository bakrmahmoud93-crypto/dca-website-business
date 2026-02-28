"""
Flask Backend - داشبورد مستضاف
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import sqlite3
import os
import sys

# Debug: print to stderr so it shows in logs
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Working directory: {os.getcwd()}", file=sys.stderr)

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app, supports_credentials=True)

# قاعدة البيانات
import tempfile
DATA_DIR = tempfile.gettempdir()
DATABASE = os.path.join(DATA_DIR, 'dca_database.db')
print(f"Database path: {DATABASE}", file=sys.stderr)

# مصادحة
AUTH_USERNAME = "dca"
AUTH_PASSWORD = "dca2026@iraq"

def check_auth(username, password):
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

def requires_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response(
                '🔒 تسجيل الدخول مطلوب',
                401,
                {'WWW-Authenticate': 'Basic realm="DCA Dashboard"'}
            )
        return f(*args, **kwargs)
    return decorated

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("Initializing database...", file=sys.stderr)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            category TEXT DEFAULT 'other',
            address TEXT,
            description TEXT,
            status TEXT DEFAULT 'prospect',
            website_url TEXT,
            local_path TEXT,
            price INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_at TIMESTAMP,
            sold_at TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            key TEXT PRIMARY KEY,
            enabled INTEGER DEFAULT 0
        )
    ''')
    
    # بيانات تجريبية
    cursor.execute('SELECT COUNT(*) FROM businesses')
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('عيادة الأسنان المتميزة', '+9647701234567', 'clinic', 'بغداد، المنصور', 'عيادة أسنان متخصصة'),
            ('مطعم البيت العراقي', '+9647709876543', 'restaurant', 'بغداد، الكرادة', 'مطعم عراقي تقليدي'),
            ('صالون الأناقة', '+9647705551234', 'salon', 'بغداد، الجادرية', 'صالون حلاقة رجالي'),
        ]
        for data in sample_data:
            cursor.execute('INSERT INTO businesses (name, phone, category, address, description) VALUES (?, ?, ?, ?, ?)', data)
    
    # صلاحيات افتراضية
    default_permissions = [
        ('auto_send', 0),
        ('auto_deploy', 1),
        ('auto_followup', 0),
        ('night_mode', 0)
    ]
    for key, value in default_permissions:
        cursor.execute('INSERT OR IGNORE INTO permissions (key, enabled) VALUES (?, ?)', (key, value))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!", file=sys.stderr)

# Initialize on import
init_db()

@app.route('/')
@requires_auth
def index():
    return app.send_static_file('index.html')

@app.route('/api/stats')
@requires_auth
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE status = "prospect"')
    prospects = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE status = "sent"')
    sent = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE status = "sold"')
    sold = cursor.fetchone()[0]
    
    cursor.execute('SELECT COALESCE(SUM(price), 0) FROM businesses WHERE status = "sold"')
    revenue = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'prospects': prospects,
            'sent': sent,
            'sold': sold,
            'revenue': revenue
        }
    })

@app.route('/api/businesses')
@requires_auth
def get_businesses():
    status = request.args.get('status', 'prospect')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM businesses WHERE status = ? ORDER BY created_at DESC', (status,))
    rows = cursor.fetchall()
    conn.close()
    
    businesses = []
    for row in rows:
        businesses.append({
            'id': row['id'],
            'name': row['name'],
            'phone': row['phone'],
            'category': row['category'],
            'address': row['address'],
            'description': row['description'],
            'status': row['status'],
            'website_url': row['website_url'],
            'price': row['price']
        })
    
    return jsonify({'success': True, 'businesses': businesses})

@app.route('/api/businesses', methods=['POST'])
@requires_auth
def add_business():
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO businesses (name, phone, category, address, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('phone'),
        data.get('category', 'other'),
        data.get('address'),
        data.get('description')
    ))
    
    conn.commit()
    business_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'id': business_id})

@app.route('/api/businesses/<int:business_id>/status', methods=['PUT'])
@requires_auth
def update_status(business_id):
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE businesses SET status = ?, price = ?, sent_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (data.get('status'), data.get('price'), business_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/permissions')
@requires_auth
def get_permissions():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT key, enabled FROM permissions')
    rows = cursor.fetchall()
    conn.close()
    
    permissions = {row['key']: bool(row['enabled']) for row in rows}
    return jsonify({'success': True, 'permissions': permissions})

@app.route('/api/permissions/<key>', methods=['PUT'])
@requires_auth
def toggle_permission(key):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT enabled FROM permissions WHERE key = ?', (key,))
    row = cursor.fetchone()
    
    if row:
        new_value = 0 if row['enabled'] else 1
        cursor.execute('UPDATE permissions SET enabled = ? WHERE key = ?', (new_value, key))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'enabled': bool(new_value)})
    
    conn.close()
    return jsonify({'success': False, 'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
