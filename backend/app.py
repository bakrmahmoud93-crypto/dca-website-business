"""
Flask Backend - داشبورد مستضاف
"""

from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app, supports_credentials=True)

# قاعدة البيانات - استخدم /tmp في البيئات السحابية
import tempfile
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
try:
    test_file = os.path.join(DATA_DIR, '.write_test')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
except:
    DATA_DIR = tempfile.gettempdir()
    print(f"Using temp directory: {DATA_DIR}")
DATABASE = os.path.join(DATA_DIR, 'database.db')

# مصادقة بسيطة
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
    
    default_permissions = [
        ('auto_send', 0),
        ('auto_deploy', 1),
        ('auto_followup', 0),
        ('night_mode', 0)
    ]
    
    for key, enabled in default_permissions:
        cursor.execute('INSERT OR IGNORE INTO permissions (key, enabled) VALUES (?, ?)', (key, enabled))
    
    conn.commit()
    conn.close()

# ============= ROUTES =============

@app.route('/')
@requires_auth
def dashboard():
    return render_template('index.html')

# ============= API (بدون مصادقة للتسهيل) =============

@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    status = request.args.get('status')
    conn = get_db()
    cursor = conn.cursor()
    
    if status:
        cursor.execute('SELECT * FROM businesses WHERE status = ? ORDER BY created_at DESC', (status,))
    else:
        cursor.execute('SELECT * FROM businesses ORDER BY created_at DESC')
    
    businesses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'businesses': businesses})

@app.route('/api/businesses', methods=['POST'])
def add_business():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO businesses (name, phone, category, address, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('phone'), data.get('category', 'other'), data.get('address', ''), data.get('description', '')))
    
    business_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': business_id})

@app.route('/api/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM businesses WHERE id = ?', (business_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({'success': True, 'business': dict(row)})
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.route('/api/businesses/<int:business_id>/status', methods=['PUT'])
def update_status(business_id):
    data = request.json
    new_status = data.get('status')
    price = data.get('price')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if new_status == 'sent':
        cursor.execute('''
            UPDATE businesses SET status = ?, sent_at = ?, website_url = ?
            WHERE id = ?
        ''', (new_status, datetime.now().isoformat(), data.get('website_url'), business_id))
    elif new_status == 'sold':
        cursor.execute('''
            UPDATE businesses SET status = ?, sold_at = ?, price = ?
            WHERE id = ?
        ''', (new_status, datetime.now().isoformat(), price, business_id))
    else:
        cursor.execute('UPDATE businesses SET status = ? WHERE id = ?', (new_status, business_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/businesses/<int:business_id>', methods=['DELETE'])
def delete_business(business_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM businesses WHERE id = ?', (business_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE status = "prospect"')
    prospects = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE status = "sent"')
    sent = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE status = "sold"')
    sold = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(price) FROM businesses WHERE status = "sold"')
    revenue = cursor.fetchone()[0] or 0
    
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

@app.route('/api/permissions', methods=['GET'])
def get_permissions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM permissions')
    rows = cursor.fetchall()
    conn.close()
    
    permissions = {row['key']: bool(row['enabled']) for row in rows}
    return jsonify({'success': True, 'permissions': permissions})

@app.route('/api/permissions/<key>', methods=['PUT'])
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

# ============= MAIN =============

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("DCA Dashboard Server")
    print("=" * 50)
    print("\nUsername: dca")
    print("Password: dca2026@iraq")
    print("\nDashboard: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
