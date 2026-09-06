import os
import io
import sqlite3
import smtplib
import random
import time
import base64
import requests 
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# ReportLab & QR Generation Imports
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Load environment variables
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'static'),
    template_folder=os.path.join(BASE_DIR, 'templates')
)
app.secret_key = os.getenv("SECRET_KEY", "evora_super_secret_session_key_2026")
app.config.update(
    SESSION_COOKIE_NAME='evora_session',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=86400 * 7
)
CORS(app)

DB_FILE = os.path.join(BASE_DIR, "evora.db")
ADMIN_EMAILS = ["admin@evora.com", "owner@evora.com", "ayaanpathan1617@gmail.com"]

# SMTP Settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "ayaanpathan1617@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

# Razorpay Settings
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "placeholder_secret")

try:
    import razorpay
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
except Exception:
    razorpay_client = None


# ==========================================================================
# DATABASE INITIALIZATION
# ==========================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. OTP Codes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            is_verified INTEGER DEFAULT 0
        )
    ''')

    # 3. Bookings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            booking_type TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            booking_ref TEXT,
            payment_id TEXT DEFAULT 'N/A',
            status TEXT DEFAULT 'CONFIRMED',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Safe Auto-Patch columns
    cursor.execute("PRAGMA table_info(bookings)")
    cols = [col[1] for col in cursor.fetchall()]
    if 'payment_id' not in cols:
        cursor.execute("ALTER TABLE bookings ADD COLUMN payment_id TEXT DEFAULT 'N/A'")
    if 'status' not in cols:
        cursor.execute("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'CONFIRMED'")

    # 4. Login Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            fullname TEXT NOT NULL,
            login_time TEXT NOT NULL,
            ip_address TEXT DEFAULT '127.0.0.1',
            status TEXT DEFAULT 'SUCCESS'
        )
    ''')

    # 5. Event Tier Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            tier_key TEXT NOT NULL,
            tier_name TEXT NOT NULL,
            total_capacity INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            UNIQUE(event_id, tier_key)
        )
    ''')

    # Seed default inventory for events 1 through 8
    default_capacities = [
        ('regular', 'Regular Pass', 100),
        ('silver', 'Silver Zone', 60),
        ('gold', 'Gold Deck', 30),
        ('premium', 'Premium Lounge', 20),
        ('balcony', 'Balcony View', 15),
        ('frontrow', 'Front Row VIP', 8)
    ]
    for ev_id in range(1, 9):
        for t_key, t_name, cap in default_capacities:
            cursor.execute('''
                INSERT OR IGNORE INTO event_inventory (event_id, tier_key, tier_name, total_capacity, available_seats)
                VALUES (?, ?, ?, ?, ?)
            ''', (ev_id, t_key, t_name, cap, cap))

    # Master Admin Account
    cursor.execute("SELECT id FROM users WHERE email = 'admin@evora.com'")
    if not cursor.fetchone():
        hashed = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (fullname, email, phone, password, role) VALUES (?, ?, ?, ?, ?)",
            ("Evora Owner", "admin@evora.com", "+919876543210", hashed, "admin")
        )

    conn.commit()
    conn.close()

init_db()


# ==========================================================================
# TRANSACTIONAL EMAIL TEMPLATES & SENDER (SSL PORT 465)
# ==========================================================================
def get_otp_email_template(fullname, otp_code):
    return f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; padding: 40px 20px; color: #0f172a;">
        <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="font-size: 26px; font-weight: 800; color: #7c3aed; margin: 0;">evora</h1>
                <p style="font-size: 13px; color: #64748b; margin-top: 4px;">Live Concerts, Venues & Event Operations</p>
            </div>
            <h2 style="font-size: 18px; font-weight: 700; color: #0f172a;">Verify Your Email Address</h2>
            <p style="font-size: 14px; color: #475569; line-height: 1.6;">Hello <strong>{fullname}</strong>,</p>
            <p style="font-size: 14px; color: #475569; line-height: 1.6;">Use the following 6-digit One-Time Password (OTP) to complete your account registration:</p>
            <div style="text-align: center; margin: 28px 0;">
                <span style="display: inline-block; background: #ede9fe; color: #7c3aed; font-size: 32px; font-weight: 800; letter-spacing: 8px; padding: 14px 32px; border-radius: 12px; border: 1px dashed #7c3aed;">
                    {otp_code}
                </span>
            </div>
            <p style="font-size: 12px; color: #94a3b8; text-align: center;">Valid for <strong>5 minutes</strong>. If you did not request this, please ignore this email.</p>
        </div>
    </div>
    """

def get_welcome_email_html(user_name):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; }}
            .header {{ background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); padding: 30px 20px; text-align: center; }}
            .header h1 {{ margin: 0; color: #ffffff; font-size: 28px; letter-spacing: 1px; }}
            .content {{ padding: 30px; line-height: 1.6; color: #cbd5e1; }}
            .content h2 {{ color: #ffffff; margin-top: 0; }}
            .btn-container {{ text-align: center; margin: 30px 0; }}
            .btn {{ background: #6366f1; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; }}
            .footer {{ background-color: #0f172a; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>EVORA LIVE</h1>
            </div>
            <div class="content">
                <h2>Welcome to Evora, {user_name}! 🎉</h2>
                <p>Your account has been successfully verified and activated.</p>
                <p>You're all set to discover live concerts, book exclusive passes, manage event logistics, and access your automated QR tickets anywhere.</p>
                <div class="btn-container">
                    <a href="https://evora-0m5i.onrender.com/login" class="btn">Explore Events Now</a>
                </div>
                <p>If you have any questions or need support, reply directly to this email.</p>
            </div>
            <div class="footer">
                &copy; 2026 Evora Platform. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

def get_venue_approval_email_template(fullname, venue_name, booking_date, shift_type, total_price, booking_ref):
    return f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; padding: 40px 15px; color: #0f172a; line-height: 1.6;">
        <div style="max-width: 580px; margin: 0 auto; background: #ffffff; border-radius: 20px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.04);">
            <div style="background: linear-gradient(135deg, #059669, #10b981); padding: 32px 28px; text-align: center; color: #ffffff;">
                <h1 style="font-size: 28px; font-weight: 800; margin: 0; letter-spacing: -0.5px;">evora</h1>
                <p style="font-size: 13px; opacity: 0.9; margin: 4px 0 0 0; text-transform: uppercase; letter-spacing: 1px;">Official Venue Allocation Desk</p>
            </div>
            <div style="padding: 32px 28px;">
                <div style="display: inline-block; background: #ecfdf5; color: #059669; font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 20px; margin-bottom: 14px; border: 1px solid #a7f3d0;">
                    ✓ REQUEST APPROVED & VENUE ALLOCATED
                </div>
                <h2 style="font-size: 22px; font-weight: 700; color: #0f172a; margin: 0 0 10px 0;">Great news, {fullname}! 🎉</h2>
                <p style="font-size: 14px; color: #475569; margin: 0 0 20px 0;">
                    Your booking request for <strong>{venue_name}</strong> has been officially approved and allocated by the Evora Operations Team.
                </p>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; margin-bottom: 24px;">
                    <h3 style="font-size: 13px; font-weight: 700; color: #0f172a; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                        🏛️ Allocation Summary
                    </h3>
                    <table style="width: 100%; font-size: 13px; color: #334155; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 6px 0; color: #64748b;">Venue:</td>
                            <td style="padding: 6px 0; font-weight: 700; color: #0f172a;">{venue_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b;">Reserved Date:</td>
                            <td style="padding: 6px 0; font-weight: 600;">{booking_date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b;">Shift / Timing:</td>
                            <td style="padding: 6px 0; font-weight: 600;">{shift_type}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #64748b;">Booking Ref ID:</td>
                            <td style="padding: 6px 0; font-weight: 600; color: #7c3aed;">{booking_ref}</td>
                        </tr>
                        <tr style="border-top: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0 0 0; font-weight: 700; color: #0f172a;">Total Payable:</td>
                            <td style="padding: 10px 0 0 0; font-weight: 800; font-size: 16px; color: #059669;">₹ {total_price:,.2f}</td>
                        </tr>
                    </table>
                </div>
                <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 16px; margin-bottom: 24px;">
                    <strong style="color: #1e40af; font-size: 13px; display: block; margin-bottom: 4px;">
                        ⚠️ Next Step: Complete Payment to Lock Your Dates
                    </strong>
                    <p style="font-size: 12px; color: #1e3a8a; margin: 0;">
                        Your payment gateway is now unlocked. Please complete the transaction on your dashboard to lock the venue slot and generate your verified tax invoice.
                    </p>
                </div>
                <div style="text-align: center; margin: 28px 0;">
                    <a href="http://127.0.0.1:5000/dashboard" style="display: inline-block; background: linear-gradient(135deg, #059669, #10b981); color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; padding: 14px 32px; border-radius: 10px; box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3);">
                        Open Dashboard & Pay ₹{total_price:,.2f} →
                    </a>
                </div>
                <div style="border-top: 1px solid #e2e8f0; padding-top: 18px; margin-top: 20px; font-size: 12px; color: #64748b;">
                    Need changes to timings or catering setup? Call your assigned coordinator directly at <strong>+91 7219899114</strong>.
                </div>
            </div>
            <div style="background: #f1f5f9; padding: 16px 28px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0;">
                © 2026 Evora Live Event Operations Pvt Ltd. All rights reserved.
            </div>
        </div>
    </div>
    """
def send_email_direct(to_email, subject, html_content):
    """Sends email via Brevo REST API over HTTPS (Port 443 - works on Render)"""
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")

    if not api_key or not sender_email:
        print("❌ [BREVO ERROR] Missing BREVO_API_KEY or SENDER_EMAIL.")
        return False, "Email configuration missing."

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": "Evora Live", "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201, 202]:
            print(f"✅ [EMAIL SENT] Successfully delivered to {to_email}")
            return True, "Success"
        else:
            print(f"❌ [BREVO API ERROR] {response.status_code}: {response.text}")
            return False, f"Brevo API error: {response.status_code}"
    except Exception as e:
        print(f"❌ [NETWORK ERROR] {e}")
        return False, str(e)


# ==========================================================================
# AUTH GUARDS & DECORATORS
# ==========================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_email'):
            return jsonify({"status": "auth_required", "message": "Please login to proceed with booking."}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            if request.path.startswith('/api/'):
                return jsonify({"status": "auth_required", "message": "Admin authentication required."}), 403
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================================================
# PAGE ROUTES
# ==========================================================================
@app.route('/')
def home(): return render_template('index.html')

@app.route('/events')
def events(): return render_template('concerts_hub.html')

@app.route('/event-detail')
def event_detail(): return render_template('concert_detail.html')

@app.route('/venues')
def venues(): return render_template('venues.html')

@app.route('/manpower')
def manpower(): return render_template('manpower.html')

@app.route('/planner')
def event_planner(): return render_template('planner.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

@app.route('/signup')
def signup_page(): return render_template('signup.html')

@app.route('/login')
def login_page(): return render_template('login.html')

@app.route('/admin')
@admin_required
def admin_page(): return render_template('admin.html')


# ==========================================================================
# AUTHENTICATION & OTP APIS
# ==========================================================================
@app.route('/api/auth/send-otp', methods=['POST'])
def send_registration_otp():
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        fullname = (data.get('fullname') or '').strip()

        if not email or not fullname:
            return jsonify({"status": "error", "message": "Name and email are required."}), 400

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": "error", "message": "An account with this email already exists. Please login."}), 409

        otp_code = str(random.randint(100000, 999999))
        expires_at = int(time.time()) + 300

        cursor.execute("DELETE FROM otp_codes WHERE email = ?", (email,))
        cursor.execute("INSERT INTO otp_codes (email, otp, expires_at) VALUES (?, ?, ?)", (email, otp_code, expires_at))
        conn.commit()
        conn.close()

        print("\n" + "="*45)
        print(f"🔑 [OTP GENERATED] Email: {email} | Code: {otp_code}")
        print("="*45)

        success, message = send_email_direct(
            email, 
            f"Your Evora Verification Code: {otp_code}", 
            get_otp_email_template(fullname, otp_code)
        )

        if not success:
            return jsonify({
                "status": "error", 
                "message": f"Email dispatch failed: {message}"
            }), 500

        return jsonify({
            "status": "success", 
            "message": f"Verification code dispatched to {email}."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/auth/verify-and-register', methods=['POST'])
def verify_and_register():
    try:
        data = request.get_json(silent=True) or {}
        fullname = data.get('fullname', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        otp_input = data.get('otp', '').strip()

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = int(time.time())

        cursor.execute("SELECT otp, expires_at FROM otp_codes WHERE email = ? ORDER BY id DESC LIMIT 1", (email,))
        rec = cursor.fetchone()
        if not rec or now > rec[1] or otp_input != rec[0]:
            conn.close()
            return jsonify({"status": "error", "message": "Invalid or expired OTP code."}), 400

        hashed = generate_password_hash(password)
        role = 'admin' if email in ADMIN_EMAILS else 'customer'
        cursor.execute("INSERT INTO users (fullname, email, phone, password, role) VALUES (?, ?, ?, ?, ?)", (fullname, email, phone, hashed, role))
        cursor.execute("DELETE FROM otp_codes WHERE email = ?", (email,))
        conn.commit()
        conn.close()

        session['user_email'] = email
        session['user_name'] = fullname
        session['user_role'] = role
        session['is_admin'] = (role == 'admin')

        # DISPATCH WELCOME ONBOARDING EMAIL
        send_email_direct(
            email,
            f"Welcome to Evora, {fullname}! 🎉",
            get_welcome_email_template(fullname, email)
        )

        return jsonify({"status": "success", "fullname": fullname, "email": email, "is_admin": session['is_admin']}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form if request.form else request.get_json(silent=True) or {}
        email = (data.get('user_email') or data.get('email', '')).strip().lower()
        password = data.get('user_password') or data.get('password')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT fullname, password, role FROM users WHERE email = ?", (email,))
        user_record = cursor.fetchone()
        conn.close()

        if not user_record:
            return jsonify({"status": "error", "message": "User not found."}), 404

        db_name, db_hash, db_role = user_record
        is_valid = check_password_hash(db_hash, password) if db_hash.startswith(('pbkdf2:', 'scrypt:')) else (password == db_hash)

        if is_valid:
            session['user_email'] = email
            session['user_name'] = db_name
            session['user_role'] = db_role
            session['is_admin'] = (db_role == 'admin' or email in ADMIN_EMAILS)

            # Record login log
            login_time_str = datetime.now().strftime("%d %b %Y, %I:%M:%S %p IST")
            log_conn = sqlite3.connect(DB_FILE)
            log_cur = log_conn.cursor()
            log_cur.execute("INSERT INTO login_logs (user_email, fullname, login_time, ip_address, status) VALUES (?, ?, ?, ?, ?)",
                            (email, db_name, login_time_str, request.remote_addr or '127.0.0.1', 'SUCCESS'))
            log_conn.commit()
            log_conn.close()

            return jsonify({"status": "success", "fullname": db_name, "email": email, "is_admin": session['is_admin']}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid password."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    resp = make_response(redirect(url_for('login_page')))
    resp.set_cookie('evora_session', '', expires=0, path='/')
    return resp


@app.route('/api/auth/session', methods=['GET'])
def get_auth_session():
    if session.get('user_email'):
        return jsonify({
            "is_logged_in": True,
            "email": session.get('user_email'),
            "fullname": session.get('user_name'),
            "is_admin": session.get('is_admin', False)
        }), 200
    return jsonify({"is_logged_in": False}), 200


# ==========================================================================
# REAL-TIME INVENTORY APIS
# ==========================================================================
@app.route('/api/inventory/<int:event_id>', methods=['GET'])
def get_event_inventory(event_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tier_key, tier_name, total_capacity, available_seats
        FROM event_inventory
        WHERE event_id = ?
    ''', (event_id,))
    rows = cursor.fetchall()
    conn.close()

    inventory = {}
    for r in rows:
        inventory[r[0]] = {
            "tier_name": r[1],
            "total": r[2],
            "available": r[3],
            "is_sold_out": (r[3] <= 0)
        }

    return jsonify({"status": "success", "event_id": event_id, "inventory": inventory}), 200


# ==========================================================================
# LIVE QR PAYMENT BRIDGE APIS
# ==========================================================================
LIVE_PAYMENT_SESSIONS = {}

@app.route('/api/payment/create-qr-session', methods=['POST'])
@login_required
def create_qr_payment_session():
    try:
        data = request.get_json(silent=True) or {}
        amount = float(data.get('total_price', 0))
        if amount <= 0:
            return jsonify({"status": "error", "message": "Invalid payment amount."}), 400

        session_id = f"PAY-EVR-{random.randint(100000, 999999)}"
        LIVE_PAYMENT_SESSIONS[session_id] = {
            "status": "PENDING",
            "amount": amount,
            "booking_data": data,
            "user_email": session.get('user_email'),
            "user_name": session.get('user_name'),
            "created_at": time.time()
        }

        pay_url = f"{request.host_url.rstrip('/')}/pay/{session_id}"

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "pay_url": pay_url,
            "amount": amount
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/pay/<session_id>')
def mobile_pay_screen(session_id):
    """Renders the mobile mock payment gateway on the user's phone"""
    session_info = LIVE_PAYMENT_SESSIONS.get(session_id)
    if not session_info:
        return "<h2 style='font-family:sans-serif; text-align:center; margin-top:50px;'>QR Code Expired or Invalid</h2>", 404
    
    return render_template('mobile_gateway.html', 
                           session_id=session_id, 
                           amount=session_info['amount'], 
                           user_name=session_info.get('user_name', 'Customer'))


@app.route('/api/payment/confirm-mobile-pay/<session_id>', methods=['POST'])
def confirm_mobile_pay(session_id):
    """Called by the user's phone when they click 'Pay'"""
    if session_id not in LIVE_PAYMENT_SESSIONS:
        return jsonify({"status": "error", "message": "Invalid session"}), 404

    LIVE_PAYMENT_SESSIONS[session_id]['status'] = 'PAID'
    LIVE_PAYMENT_SESSIONS[session_id]['paid_at'] = time.time()
    
    return jsonify({"status": "success", "message": "Payment Approved!"}), 200


@app.route('/api/payment/check-status/<session_id>', methods=['GET'])
def check_qr_payment_status(session_id):
    """Polled by the website every 1.5 seconds"""
    session_info = LIVE_PAYMENT_SESSIONS.get(session_id)
    if not session_info:
        return jsonify({"status": "expired"}), 404

    if session_info['status'] == 'PAID':
        return jsonify({
            "status": "PAID",
            "booking_data": session_info['booking_data'],
            "session_id": session_id
        }), 200

    return jsonify({"status": "PENDING"}), 200


# ==========================================================================
# PAYMENT & LIVE ORDER APIS
# ==========================================================================
@app.route('/api/payment/create-order', methods=['POST'])
@login_required
def create_payment_order():
    try:
        data = request.get_json(silent=True) or {}
        amount_rupees = float(data.get('amount', 0))
        if amount_rupees <= 0:
            return jsonify({"status": "error", "message": "Invalid payment amount."}), 400

        amount_paise = int(round(amount_rupees * 100))
        currency = "INR"
        receipt_id = f"rcpt_{random.randint(100000, 999999)}"

        if razorpay_client and "rzp_test_placeholder" not in RAZORPAY_KEY_ID:
            razorpay_order = razorpay_client.order.create({
                "amount": amount_paise,
                "currency": currency,
                "receipt": receipt_id,
                "payment_capture": 1
            })
            order_id = razorpay_order['id']
        else:
            order_id = f"order_mock_{random.randint(100000, 999999)}"

        return jsonify({
            "status": "success",
            "order_id": order_id,
            "amount": amount_paise,
            "currency": currency,
            "key_id": RAZORPAY_KEY_ID,
            "customer_name": session.get('user_name'),
            "customer_email": session.get('user_email')
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/payment/verify-and-book', methods=['POST'])
@login_required
def verify_payment_and_book():
    try:
        data = request.get_json(silent=True) or {}
        user_email = session.get('user_email')
        user_name = session.get('user_name', 'Customer')
        
        booking_type = data.get('booking_type')
        title = data.get('title')
        details = data.get('details')
        booking_date = data.get('booking_date', 'Upcoming')
        total_price = float(data.get('total_price', 0))
        razorpay_payment_id = data.get('razorpay_payment_id', f"PAY-EVR-{random.randint(1000,9999)}")
        individual_items = data.get('individual_items', [])
        existing_booking_id = data.get('existing_booking_id')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        generated_passes = []

        # 1. Update Existing Approved Venue Booking if paying post-approval
        if existing_booking_id:
            cursor.execute('''
                UPDATE bookings 
                SET status = 'CONFIRMED', payment_id = ?
                WHERE id = ? AND user_email = ?
            ''', (razorpay_payment_id, existing_booking_id, user_email))
            ref_id = f"EVR-VEN-{existing_booking_id}"
            generated_passes.append({"ticket_ref": ref_id, "tier_name": title, "price": total_price})

        # 2. Multi-Tier Concert Passes
        elif booking_type == 'passes' and individual_items:
            event_id = int(data.get('event_id', 1))

            tier_request_counts = {}
            for item in individual_items:
                tk = item.get('tier_key', 'regular')
                tier_request_counts[tk] = tier_request_counts.get(tk, 0) + 1

            for tk, req_qty in tier_request_counts.items():
                cursor.execute("SELECT available_seats, tier_name FROM event_inventory WHERE event_id = ? AND tier_key = ?", (event_id, tk))
                inv_row = cursor.fetchone()
                if not inv_row or inv_row[0] < req_qty:
                    t_name = inv_row[1] if inv_row else tk
                    conn.close()
                    return jsonify({
                        "status": "sold_out",
                        "message": f"Sorry! {t_name} has just sold out or does not have enough remaining seats."
                    }), 409

            for tk, req_qty in tier_request_counts.items():
                cursor.execute('''
                    UPDATE event_inventory
                    SET available_seats = available_seats - ?
                    WHERE event_id = ? AND tier_key = ?
                ''', (req_qty, event_id, tk))

            base_order_ref = f"EVR-{random.randint(100000, 999999)}"
            for index, item in enumerate(individual_items, start=1):
                tier_name = item.get('tier_name', 'General Pass')
                tier_price = float(item.get('price', 0))
                ticket_ref = f"{base_order_ref}-T{index}"

                cursor.execute('''
                    INSERT INTO bookings (user_email, booking_type, title, details, booking_date, total_price, booking_ref, payment_id, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_email,
                    'passes',
                    f"{title} — Pass #{index}",
                    f"Tier: {tier_name} • Pass {index} of {len(individual_items)} • Venue: {details}",
                    booking_date,
                    tier_price,
                    ticket_ref,
                    razorpay_payment_id,
                    'CONFIRMED'
                ))
                
                generated_passes.append({
                    "ticket_ref": ticket_ref,
                    "tier_name": tier_name,
                    "price": tier_price
                })
        else:
            ref_id = f"EVR-{random.randint(100000, 999999)}"
            cursor.execute('''
                INSERT INTO bookings (user_email, booking_type, title, details, booking_date, total_price, booking_ref, payment_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_email, booking_type, title, details, booking_date, total_price, ref_id, razorpay_payment_id, 'CONFIRMED'))
            generated_passes.append({"ticket_ref": ref_id, "tier_name": title, "price": total_price})

        conn.commit()
        conn.close()

        # Send Email Confirmation
        tickets_html_list = "".join([
            f"<li style='margin-bottom: 6px;'><strong>Pass #{idx}</strong>: {p['tier_name']} — Ref: <code style='color:#7c3aed;'>{p['ticket_ref']}</code> (₹{p['price']:,.2f})</li>"
            for idx, p in enumerate(generated_passes, start=1)
        ])

        html_email = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; padding: 30px 20px; color: #0f172a;">
            <div style="max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; padding: 28px;">
                <h1 style="color: #7c3aed; margin: 0 0 10px 0;">evora</h1>
                <h2 style="font-size: 18px; margin: 0 0 14px 0;">🎉 Booking Confirmed!</h2>
                <p style="font-size: 13px; color: #64748b;">Hello {user_name}, your booking for <strong>{title}</strong> is confirmed.</p>
                <div style="background: #f8fafc; border-radius: 10px; padding: 14px; margin: 16px 0; border: 1px solid #e2e8f0;">
                    <ul style="padding-left: 18px; font-size: 13px; margin: 0;">
                        {tickets_html_list}
                    </ul>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://127.0.0.1:5000/dashboard" style="background: linear-gradient(135deg, #7c3aed, #db2777); color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-size: 13px; font-weight: 600; display: inline-block;">Open My Dashboard</a>
                </div>
            </div>
        </div>
        """
        send_email_direct(user_email, f"Confirmed: Booking for {title}", html_email)

        return jsonify({
            "status": "success",
            "total_tickets": len(generated_passes),
            "tickets": generated_passes,
            "message": "Booking and transaction verified successfully!"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================================================
# VENUE APPROVAL-FIRST WORKFLOW APIS
# ==========================================================================
@app.route('/api/venues/request-booking', methods=['POST'])
@login_required
def request_venue_booking():
    """Step 1: User submits venue booking request (No upfront payment)"""
    try:
        data = request.get_json(silent=True) or {}
        user_email = session.get('user_email')
        venue_name = data.get('venue_name')
        booking_date = data.get('booking_date')
        shift_type = data.get('shift_type', 'Full Day')
        total_price = float(data.get('total_price', 0))
        guest_count = data.get('guest_count', 'N/A')
        notes = data.get('notes', '')

        if not venue_name or not booking_date:
            return jsonify({"status": "error", "message": "Venue name and date are required."}), 400

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id FROM bookings 
            WHERE booking_type = 'venues' 
              AND title = ? 
              AND booking_date = ? 
              AND status IN ('CONFIRMED', 'APPROVED_AWAITING_PAYMENT')
        ''', (venue_name, booking_date))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": "error", "message": "This venue is already booked/locked for this date."}), 409

        booking_ref = f"REQ-VEN-{random.randint(100000, 999999)}"
        details = f"Shift: {shift_type} • Guests: {guest_count} • Notes: {notes}"

        cursor.execute('''
            INSERT INTO bookings (user_email, booking_type, title, details, booking_date, total_price, booking_ref, payment_id, status)
            VALUES (?, 'venues', ?, ?, ?, ?, ?, 'UNPAID', 'PENDING_APPROVAL')
        ''', (user_email, venue_name, details, booking_date, total_price, booking_ref))

        conn.commit()
        conn.close()

        # Send alert email to admin
        admin_alert_html = f"""
        <div style="font-family:sans-serif; padding:20px; color:#0f172a;">
            <h2 style="color:#7c3aed;">New Venue Booking Request</h2>
            <p>User <strong>{user_email}</strong> has requested to reserve <strong>{venue_name}</strong>.</p>
            <ul>
                <li>Date: {booking_date}</li>
                <li>Shift: {shift_type}</li>
                <li>Estimated Price: ₹{total_price:,.2f}</li>
                <li>Ref: {booking_ref}</li>
            </ul>
            <p>Please log in to your <a href="http://127.0.0.1:5000/admin">Admin Panel</a> to allocate and approve this venue.</p>
        </div>
        """
        send_email_direct(ADMIN_EMAILS[0], f"Venue Request: {venue_name} ({booking_ref})", admin_alert_html)

        return jsonify({
            "status": "success",
            "message": "Venue request submitted! Awaiting Admin Allocation before payment.",
            "booking_ref": booking_ref
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/approve-venue-booking', methods=['POST'])
@admin_required
def admin_approve_venue():
    """Step 2: Admin confirms and allocates the venue, sending payment instruction email to user"""
    try:
        data = request.get_json(silent=True) or {}
        booking_id = data.get('booking_id')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.user_email, b.title, b.details, b.booking_date, b.total_price, b.booking_ref,
                   COALESCE(u.fullname, 'Valued Customer') as fullname
            FROM bookings b
            LEFT JOIN users u ON b.user_email = u.email
            WHERE b.id = ?
        ''', (booking_id,))
        record = cursor.fetchone()

        if not record:
            conn.close()
            return jsonify({"status": "error", "message": "Booking request not found."}), 404

        user_email, venue_name, b_details, b_date, price, b_ref, fullname = record

        shift_type = "Full Day Shift"
        if "Shift:" in b_details:
            shift_type = b_details.split("Shift:")[1].split("•")[0].strip()

        cursor.execute("UPDATE bookings SET status = 'APPROVED_AWAITING_PAYMENT' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        # Send Real-Time Email Notification to User via SSL Port 465
        email_subject = f"Venue Approved: {venue_name} — Complete Your Payment"
        email_body = get_venue_approval_email_template(
            fullname=fullname,
            venue_name=venue_name,
            booking_date=b_date,
            shift_type=shift_type,
            total_price=float(price),
            booking_ref=b_ref
        )
        send_email_direct(user_email, email_subject, email_body)

        return jsonify({
            "status": "success", 
            "message": f"Venue allocated successfully! Approval email sent to {user_email}."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================================================
# PDF E-TICKET & INVOICE GENERATION API
# ==========================================================================
@app.route('/api/download-ticket-pdf/<int:booking_id>', methods=['GET'])
@login_required
def download_ticket_pdf(booking_id):
    user_email = session.get('user_email')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, booking_type, title, details, booking_date, total_price, booking_ref, payment_id, status 
        FROM bookings 
        WHERE id = ? AND user_email = ?
    ''', (booking_id, user_email))
    booking = cursor.fetchone()
    conn.close()

    if not booking:
        return jsonify({"status": "error", "message": "Booking not found or unauthorized."}), 404

    b_id, b_type, b_title, b_details, b_date, b_price, b_ref, b_pay_id, b_status = booking

    qr_data = f"EVORA-VERIFIED|{b_ref}|{b_title}|{user_email}|{b_status}"
    qr_img = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36,
        topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'EvoraHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#7c3aed'),
        spaceAfter=4
    )
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569')
    )

    story = []

    header_data = [
        [
            Paragraph("<b>evora</b><br/><font size=8 color='#64748b'>Official Verified Entry Pass & Tax Invoice</font>", title_style),
            Paragraph(f"<font color='#059669'><b>STATUS: {b_status}</b></font><br/><b>Ref:</b> {b_ref}<br/><b>Date:</b> {b_date}", meta_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 16))

    line_data = [
        ["Item / Tier Description", "Event / Allocation Details", "Amount Paid"],
        [Paragraph(f"<b>{b_title}</b>", meta_style), Paragraph(b_details, meta_style), f"INR {b_price:,.2f}"]
    ]
    t_line = Table(line_data, colWidths=[2.2*inch, 3.5*inch, 1.3*inch])
    t_line.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_line)
    story.append(Spacer(1, 20))

    rl_qr = RLImage(qr_buffer, width=1.5*inch, height=1.5*inch)
    auth_data = [
        [
            rl_qr,
            Paragraph(
                f"<b>Gate Security Instructions:</b><br/>"
                f"Present this official QR code at the event turnstile.<br/>"
                f"Issued To: <b>{user_email}</b><br/>"
                f"Payment Ref ID: <b>{b_pay_id}</b><br/>"
                f"<font size=8 color='#94a3b8'>Evora Live Event Operations Pvt Ltd • GSTIN: 27AABCE1234F1Z5</font>",
                meta_style
            )
        ]
    ]
    t_auth = Table(auth_data, colWidths=[1.8*inch, 5.2*inch])
    t_auth.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#ede9fe')),
        ('PADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(t_auth)

    doc.build(story)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Evora_Ticket_{b_ref}.pdf",
        mimetype='application/pdf'
    )


# ==========================================================================
# CUSTOMER & ADMIN DASHBOARD APIS
# ==========================================================================
@app.route('/api/user-bookings', methods=['GET'])
@login_required
def get_user_bookings():
    user_email = session.get('user_email')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Fetch user's actual registered name
    cursor.execute('SELECT fullname FROM users WHERE email = ?', (user_email,))
    user_row = cursor.fetchone()
    fullname = user_row[0] if user_row else session.get('user_name', 'Customer')
    
    # 2. Fetch user's bookings
    cursor.execute('''
        SELECT id, booking_type, title, details, booking_date, total_price, booking_ref, status 
        FROM bookings 
        WHERE user_email = ? 
        ORDER BY id DESC
    ''', (user_email,))
    rows = cursor.fetchall()
    conn.close()

    bookings = [{
        "id": r[0], "type": r[1], "title": r[2], "details": r[3], 
        "date": r[4], "price": r[5], "ref": r[6], "status": r[7]
    } for r in rows]
    
    return jsonify({
        "status": "success", 
        "user_email": user_email,
        "fullname": fullname,
        "bookings": bookings
    }), 200


@app.route('/api/admin/all-bookings', methods=['GET'])
@admin_required
def admin_get_all_bookings():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.user_email, b.booking_type, b.title, b.details, 
               b.booking_date, b.total_price, b.booking_ref, b.status,
               COALESCE(u.fullname, 'Guest Customer') as customer_name,
               COALESCE(u.phone, 'N/A') as customer_phone
        FROM bookings b
        LEFT JOIN users u ON b.user_email = u.email
        ORDER BY b.id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    bookings = []
    for r in rows:
        bookings.append({
            "id": r[0], "user_email": r[1], "type": r[2], "title": r[3],
            "details": r[4], "date": r[5], "price": float(r[6] or 0),
            "ref": r[7], "status": r[8], "customer_name": r[9], "customer_phone": r[10]
        })

    return jsonify({
        "status": "success",
        "bookings": bookings,
        "stats": {
            "total_bookings": len(bookings),
            "total_revenue": sum(b['price'] for b in bookings),
            "passes_count": sum(1 for b in bookings if b['type'] == 'passes'),
            "manpower_count": sum(1 for b in bookings if b['type'] == 'manpower'),
            "venues_count": sum(1 for b in bookings if b['type'] == 'venues')
        }
    }), 200


# ==========================================================================
# VENUE REAL-TIME AVAILABILITY & CALENDAR LOCK API
# ==========================================================================
@app.route('/api/venue-booked-dates', methods=['GET'])
def get_venue_booked_dates():
    venue_name = request.args.get('venue_name', '').strip()
    if not venue_name:
        return jsonify({"status": "error", "message": "Venue name is required"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT booking_date, details 
        FROM bookings 
        WHERE booking_type = 'venues' 
          AND title = ? 
          AND status IN ('CONFIRMED', 'APPROVED_AWAITING_PAYMENT')
    ''', (venue_name,))
    rows = cursor.fetchall()
    conn.close()

    booked_schedule = {}
    for date_str, details in rows:
        if not date_str:
            continue
        
        details_lower = (details or '').lower()
        if 'full day' in details_lower or 'full' in details_lower:
            shift = 'FULL_DAY'
        elif 'morning' in details_lower:
            shift = 'MORNING'
        elif 'evening' in details_lower:
            shift = 'EVENING'
        else:
            shift = 'FULL_DAY'

        if date_str not in booked_schedule:
            booked_schedule[date_str] = []
        booked_schedule[date_str].append(shift)

    fully_locked_dates = []
    partially_locked_dates = {}

    for date_str, shifts in booked_schedule.items():
        if 'FULL_DAY' in shifts or ('MORNING' in shifts and 'EVENING' in shifts):
            fully_locked_dates.append(date_str)
        else:
            partially_locked_dates[date_str] = shifts[0]

    return jsonify({
        "status": "success",
        "venue_name": venue_name,
        "fully_locked_dates": fully_locked_dates,
        "partially_locked_dates": partially_locked_dates
    }), 200


@app.route('/api/admin/update-booking-status', methods=['POST'])
@admin_required
def admin_update_status():
    try:
        data = request.get_json(silent=True) or {}
        booking_id = data.get('booking_id')
        new_status = data.get('status')
        notes = data.get('allocation_notes', '')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        if notes:
            cursor.execute("SELECT details FROM bookings WHERE id = ?", (booking_id,))
            row = cursor.fetchone()
            cur_details = row[0] if row else ''
            if "Allocated:" not in cur_details:
                cursor.execute("UPDATE bookings SET details = ? WHERE id = ?", (f"{cur_details} • Allocated: {notes}", booking_id))

        cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Updated to '{new_status}' successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users-and-logs', methods=['GET'])
@admin_required
def admin_get_users_and_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, fullname, email, phone, role, created_at FROM users ORDER BY id DESC")
    users = [{"id": u[0], "fullname": u[1], "email": u[2], "phone": u[3], "role": u[4], "created_at": u[5]} for u in cursor.fetchall()]

    cursor.execute("SELECT id, user_email, fullname, login_time, ip_address, status FROM login_logs ORDER BY id DESC LIMIT 50")
    logs = [{"id": l[0], "email": l[1], "fullname": l[2], "time": l[3], "ip": l[4], "status": l[5]} for l in cursor.fetchall()]

    conn.close()
    return jsonify({"status": "success", "users": users, "logs": logs}), 200


# ==========================================================================
# ADMIN TRANSACTION & AUDIT PURGE APIS
# ==========================================================================
@app.route('/api/admin/delete-booking/<int:booking_id>', methods=['DELETE', 'POST'])
@admin_required
def admin_delete_single_booking(booking_id):
    """Admin can delete a single transaction/booking record by ID"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT booking_ref, title FROM bookings WHERE id = ?", (booking_id,))
        record = cursor.fetchone()
        if not record:
            conn.close()
            return jsonify({"status": "error", "message": "Booking not found."}), 404

        cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success", 
            "message": f"Booking {record[0]} ({record[1]}) removed from pipeline."
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/clear-all-bookings', methods=['POST'])
@admin_required
def admin_clear_all_bookings():
    """Admin can wipe all booking records and reset pipeline data"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookings")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='bookings'")
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success", 
            "message": "All bookings and transactions cleared from pipeline."
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/clear-login-logs', methods=['POST'])
@admin_required
def admin_clear_login_logs():
    """Admin can clear all user login activity logs"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM login_logs")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='login_logs'")
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success", 
            "message": "Login audit stream cleared."
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/admin/users/delete', methods=['POST'])
def admin_delete_user():
    # Enforce admin authorization
    if not session.get('is_admin'):
        return jsonify({'status': 'error', 'message': 'Unauthorized. Admin access required.'}), 403

    data = request.get_json(silent=True) or {}
    target_email = data.get('email', '').strip().lower()

    if not target_email:
        return jsonify({'status': 'error', 'message': 'Target email is required.'}), 400

    # Prevent admin from accidentally deleting themselves
    if target_email == session.get('user_email'):
        return jsonify({'status': 'error', 'message': 'You cannot delete your own admin account.'}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (target_email,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            return jsonify({'status': 'error', 'message': 'User not found.'}), 404

        # Delete user credentials and associated OTP session records
        cursor.execute("DELETE FROM users WHERE email = ?", (target_email,))
        cursor.execute("DELETE FROM otp_codes WHERE email = ?", (target_email,))
        conn.commit()
        conn.close()

        print(f"🗑️ [ADMIN ACTION] User account deleted: {target_email}")
        return jsonify({'status': 'success', 'message': f'Account {target_email} successfully removed.'}), 200

    except Exception as e:
        conn.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==========================================================================
# SERVER RUNNER
# ==========================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Ensure static/uploads exists
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/events/host-event', methods=['POST'])
def host_custom_event():
    """Allows users/organizers to upload an image from device and publish an event"""
    try:
        title = request.form.get('title', '').strip()
        cat = request.form.get('cat', 'music').strip()
        venue = request.form.get('venue', '').strip()
        date = request.form.get('date', '').strip()
        price = int(request.form.get('price', 499))
        
        if not title or not venue or not date:
            return jsonify({"status": "error", "message": "All event details are required."}), 400

        # Handle Image Upload from Device
        image_file = request.files.get('poster_image')
        image_url = "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?auto=format&fit=crop&w=600&q=80" # fallback

        if image_file and allowed_file(image_file.filename):
            filename = f"event_{int(time.time())}_{secure_filename(image_file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)
            image_url = f"/static/uploads/{filename}"

        return jsonify({
            "status": "success",
            "message": "Event published successfully!",
            "event": {
                "title": title,
                "cat": cat,
                "venue": venue,
                "date": date,
                "price": price,
                "banner": "HOSTED",
                "img": image_url
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
