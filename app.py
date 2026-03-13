#!/usr/bin/env python3
"""
Email Validation API - MVP
Validate email addresses in real-time
"""

import os
import re
import json
import uuid
import hashlib
import socket
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'email-validation-secret-2026')
CORS(app)

DATABASE = 'email_validation.db'

# Common disposable email domains
DISPOSABLE_DOMAINS = {
    '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
    'tempmail.com', 'throwaway.email', 'fakeinbox.com',
    'dispostable.com', 'mailnesia.com', 'temp-mail.org',
    'getairmail.com', 'mohmal.com', 'yopmail.com',
    'sharklasers.com', 'guerrillamailblock.com', 'pokemail.net',
    'spam4.me', 'grr.la', 'guerrillamail.de', 'maildrop.cc'
}

# Database setup
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            key_hash TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            usage_limit INTEGER DEFAULT 1000
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS validations (
            id TEXT PRIMARY KEY,
            api_key_id TEXT,
            email TEXT,
            valid INTEGER,
            reason TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper functions
def generate_api_key():
    return f"ev_live_{uuid.uuid4().hex[:20]}"

def hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()

def verify_api_key(key):
    conn = get_db()
    key_hash = hash_key(key)
    api_key = conn.execute(
        'SELECT * FROM api_keys WHERE key_hash = ?', (key_hash,)
    ).fetchone()
    
    if not api_key:
        conn.close()
        return None
    
    if api_key['usage_count'] >= api_key['usage_limit']:
        conn.close()
        return {'error': 'Usage limit exceeded'}
    
    conn.execute(
        'UPDATE api_keys SET last_used = ?, usage_count = usage_count + 1 WHERE id = ?',
        (datetime.utcnow().isoformat(), api_key['id'])
    )
    conn.commit()
    conn.close()
    
    return dict(api_key)

def validate_syntax(email):
    """Check if email format is valid"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_domain(email):
    """Extract domain from email"""
    try:
        return email.split('@')[1].lower()
    except:
        return None

def check_mx_records(domain):
    """Check if domain has MX records"""
    if not DNS_AVAILABLE:
        return None  # Can't check without dnspython
    
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except:
        return False

def is_disposable(domain):
    """Check if domain is a known disposable email provider"""
    return domain.lower() in DISPOSABLE_DOMAINS

def validate_email(email, check_smtp=False):
    """Full email validation"""
    result = {
        'email': email,
        'valid': True,
        'reason': None,
        'checks': {
            'syntax': False,
            'domain_exists': None,
            'has_mx_records': None,
            'is_disposable': False,
            'smtp_check': None
        },
        'suggestion': None
    }
    
    # Syntax check
    result['checks']['syntax'] = validate_syntax(email)
    if not result['checks']['syntax']:
        result['valid'] = False
        result['reason'] = 'invalid_syntax'
        return result
    
    # Get domain
    domain = get_domain(email)
    if not domain:
        result['valid'] = False
        result['reason'] = 'invalid_domain_format'
        return result
    
    # Disposable check
    result['checks']['is_disposable'] = is_disposable(domain)
    if result['checks']['is_disposable']:
        result['valid'] = False
        result['reason'] = 'disposable_email'
        return result
    
    # MX record check
    if DNS_AVAILABLE:
        result['checks']['has_mx_records'] = check_mx_records(domain)
        if not result['checks']['has_mx_records']:
            result['valid'] = False
            result['reason'] = 'domain_has_no_mx_records'
            return result
        result['checks']['domain_exists'] = True
    else:
        result['checks']['has_mx_records'] = None
        result['checks']['domain_exists'] = None
    
    # SMTP check (optional, skipped by default)
    if check_smtp:
        # Would need to implement SMTP verification
        result['checks']['smtp_check'] = None
    
    return result

# Routes
@app.route('/')
def index():
    return jsonify({
        'name': 'Email Validation API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/validate': 'Validate single email',
            'POST /api/validate/bulk': 'Validate multiple emails',
            'POST /api/keys': 'Create API key',
            'GET /api/keys/:id': 'Get key stats'
        }
    })

@app.route('/api/keys', methods=['POST'])
def create_api_key():
    """Create a new API key"""
    api_key = generate_api_key()
    key_hash = hash_key(api_key)
    key_id = uuid.uuid4().hex[:12]
    
    conn = get_db()
    conn.execute(
        'INSERT INTO api_keys (id, key_hash, created_at) VALUES (?, ?, ?)',
        (key_id, key_hash, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'api_key': api_key,
        'id': key_id,
        'created_at': datetime.utcnow().isoformat(),
        'usage_limit': 1000,
        'warning': 'Store this key securely. It cannot be retrieved again.'
    }), 201

@app.route('/api/validate', methods=['POST'])
def validate_single():
    """Validate a single email address"""
    # Optional API key check
    api_key = request.headers.get('X-API-Key')
    if api_key:
        verified = verify_api_key(api_key)
        if verified and 'error' in verified:
            return jsonify(verified), 429
    
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Email required'}), 400
    
    email = data['email'].strip().lower()
    check_smtp = data.get('check_smtp', False)
    
    result = validate_email(email, check_smtp)
    
    return jsonify(result)

@app.route('/api/validate/bulk', methods=['POST'])
def validate_bulk():
    """Validate multiple email addresses"""
    api_key = request.headers.get('X-API-Key')
    if api_key:
        verified = verify_api_key(api_key)
        if verified and 'error' in verified:
            return jsonify(verified), 429
    
    data = request.get_json()
    if not data or 'emails' not in data:
        return jsonify({'error': 'Emails array required'}), 400
    
    emails = data['emails']
    if not isinstance(emails, list):
        return jsonify({'error': 'Emails must be an array'}), 400
    
    if len(emails) > 100:
        return jsonify({'error': 'Maximum 100 emails per request'}), 400
    
    results = [validate_email(email.strip().lower()) for email in emails]
    
    summary = {
        'total': len(results),
        'valid': sum(1 for r in results if r['valid']),
        'invalid': sum(1 for r in results if not r['valid']),
        'disposable': sum(1 for r in results if r['checks']['is_disposable'])
    }
    
    return jsonify({
        'results': results,
        'summary': summary
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'dns_available': DNS_AVAILABLE,
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print('📧 Email Validation API starting on port 5561...')
    print(f'   DNS resolution: {"✅ Available" if DNS_AVAILABLE else "❌ Install dnspython"}')
    app.run(host='0.0.0.0', port=5561, debug=True)