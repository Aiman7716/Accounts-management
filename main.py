# ==========================================================
# نظام "إدارة الحسابات" - النسخة السحابية
# تطوير وتصميم : م. أيمن الحميري
# النسخة: التحديث التراكمي الشامل (V10) - أمان وتعدد مستخدمين
# ==========================================================

import http.server
import socketserver
import sqlite3
import urllib.parse
import os
import cgi
import shutil
import hashlib
import smtplib
import random
import string
from email.mime.text import MIMEText
from datetime import datetime

# ----------------------------------------------------------
# 1. إعدادات البيئة وقاعدة البيانات (تحديث V10)
# ----------------------------------------------------------
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(BASE_PATH, "bahjat_pro_v10.db")
BACKUP_FOLDER = os.path.join(BASE_PATH, "system_backups")

# إعدادات بريد النظام (يُستخدم لإرسال كود الاستعادة للمستخدمين)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SYSTEM_MAIL = "your_email@gmail.com"  # ضع بريدك هنا
SYSTEM_PASS = "your_app_password"     # ضع كلمة مرور التطبيق هنا

def setup_database_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    
    # جدول المستخدمين (جديد V10)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        email TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL,
        store_name TEXT,
        reset_code TEXT
    )""")
    
    # تحديث جدول العملاء ليدعم owner_id (تعديل تراكمي)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        owner_id INTEGER,
        fullname TEXT NOT NULL, 
        mobile TEXT,
        work_address TEXT,
        vat_number TEXT,
        general_notes TEXT
    )""")
    
    # تحديث جدول العملات ليكون خاصاً بكل مستخدم
    cur.execute("CREATE TABLE IF NOT EXISTS currencies (c_name TEXT, owner_id INTEGER)")
    
    # تحديث جدول الحركات ليدعم owner_id
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        owner_id INTEGER,
        customer_id INTEGER, 
        val_amount REAL NOT NULL, 
        val_currency TEXT NOT NULL, 
        val_type TEXT NOT NULL, 
        val_notes TEXT, 
        entry_date TEXT
    )""")
    
    cur.execute("CREATE TABLE IF NOT EXISTS store_info (property TEXT PRIMARY KEY, value TEXT, owner_id INTEGER)")
    
    conn.commit()
    conn.close()
    if not os.path.exists(BACKUP_FOLDER): os.makedirs(BACKUP_FOLDER)

setup_database_tables()

# ----------------------------------------------------------
# 2. وظائف الأمان والجلسات (جديد V10)
# ----------------------------------------------------------
ACTIVE_SESSIONS = {} # {session_id: user_id}

def hash_pw(password): return hashlib.sha256(password.encode()).hexdigest()

def send_reset_mail(target_email, code):
    try:
        msg = MIMEText(f"كود استعادة كلمة المرور الخاص بك هو: {code}", 'plain', 'utf-8')
        msg['Subject'] = "استعادة كلمة المرور - نظام أيمن الحميري"
        msg['From'] = SYSTEM_MAIL
        msg['To'] = target_email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SYSTEM_MAIL, SYSTEM_PASS)
            server.send_message(msg)
        return True
    except: return False

# ----------------------------------------------------------
# 3. الواجهة والـ CSS (نفس كود V9 مع إضافات بسيطة)
# ----------------------------------------------------------
CSS_STYLES = """
<style>
    :root { --primary-blue: #0d47a1; --accent-blue: #1976d2; --bg-light: #f0f2f5; --white: #ffffff; --danger: #d32f2f; --success: #388e3c; }
    * { box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg-light); margin: 0; direction: rtl; }
    .header-bar { background: var(--primary-blue); color: white; padding: 25px; text-align: center; }
    .nav-menu { display: flex; justify-content: center; background: white; padding: 15px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.1); gap: 10px; }
    .nav-menu a { text-decoration: none; color: var(--primary-blue); padding: 12px 20px; border: 2px solid #ddd; border-radius: 8px; font-weight: bold; }
    .nav-menu a.active { background: var(--primary-blue); color: white; }
    .main-wrapper { max-width: 1200px; margin: 30px auto; padding: 0 15px; }
    .content-card { background: var(--white); padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 30px; }
    .input-field { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; }
    .btn-action { padding: 12px 25px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; text-align: center; }
    .btn-save { background: var(--primary-blue); color: white; width: 100%; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 15px; border-bottom: 1px solid #eee; text-align: right; }
    .badge { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
    .bg-pos { background: #e8f5e9; color: #2e7d32; }
    .bg-neg { background: #ffebee; color: #c62828; }
    .auth-box { max-width: 400px; margin: 80px auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
</style>
"""

# ----------------------------------------------------------
# 4. الدوال المساعدة (تحديث V10 لدعم تصفية المستخدم)
# ----------------------------------------------------------
def get_db(): return sqlite3.connect(DATABASE_NAME)

def get_all_balances(customer_id, user_id):
    c = get_db(); cur = c.cursor()
    cur.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) FROM ledger WHERE customer_id = ? AND owner_id = ? GROUP BY val_currency", (customer_id, user_id))
    data = cur.fetchall(); c.close()
    return data

def build_layout(title, content, user_id, active_path="", is_printable=False):
    c = get_db(); cur = c.cursor()
    cur.execute("SELECT value FROM store_info WHERE property='name' AND owner_id=?", (user_id,))
    s_name = cur.fetchone(); s_name = s_name[0] if s_name else "نظام المحاسبة"
    cur.execute("SELECT value FROM store_info WHERE property='loc' AND owner_id=?", (user_id,))
    s_loc = cur.fetchone(); s_loc = s_loc[0] if s_loc else ""
    c.close()
    
    links = [('/', 'العملاء'), ('/page_new_entry', 'حركة جديدة'), ('/page_exchange', 'المصارفة الذكية'), ('/page_reports', 'مركز التقارير'), ('/page_system', 'إعدادات النظام')]
    nav_html = "".join([f'<a href="{p}" class="{"active" if active_path == p else ""}">{n}</a>' for p, n in links])
    nav_html += '<a href="/do_logout" style="color:red;">تسجيل خروج</a>'
    p_btn = f'<button onclick="window.print()" class="btn-action no-print" style="background:#555; color:white; margin-bottom:15px;">🖨️ طباعة</button>' if is_printable else ''
    return f"<!DOCTYPE html><html lang='ar'><head><meta charset='UTF-8'><title>{title}</title>{CSS_STYLES}</head><body><div class='header-bar no-print'><h1>{s_name}</h1><p>{s_loc}</p></div><div class='nav-menu no-print'>{nav_html}</div><div class='main-wrapper'>{p_btn}{content}</div></body></html>"

# ----------------------------------------------------------
# 5. معالج السيرفر المطور (V10)
# ----------------------------------------------------------
class AymanHandler(http.server.SimpleHTTPRequestHandler):
    
    def get_current_user(self):
        cookie = self.headers.get('Cookie')
        if cookie and "session_id=" in cookie:
            sid = cookie.split("session_id=")[1].split(";")[0]
            return ACTIVE_SESSIONS.get(sid)
        return None

    def do_GET(self):
        uid = self.get_current_user()
        parsed = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(parsed.query)

        # صفحات عامة
        if parsed.path == '/login': self.show_auth_page("دخول"); return
        if parsed.path == '/register': self.show_auth_page("تسجيل"); return
        if parsed.path == '/forgot': self.show_auth_page("نسيت"); return
        if parsed.path == '/do_logout':
            cookie = self.headers.get('Cookie')
            if cookie: 
                sid = cookie.split("session_id=")[1].split(";")[0]
                if sid in ACTIVE_SESSIONS: del ACTIVE_SESSIONS[sid]
            self.redirect("/login"); return

        if not uid: self.redirect("/login"); return

        # --- هنا تبدأ دوال V9 الأصلية مع إضافة UID للتصفية ---
        self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
        
        c = get_db(); cur = c.cursor()
        
        if parsed.path == '/':
            rows = cur.execute("SELECT id, fullname, mobile FROM customers WHERE owner_id=? ORDER BY id DESC", (uid,)).fetchall()
            t_rows = "".join([f"<tr><td><b><a href='/report_customer_statement?id={r[0]}'>{r[1]}</a></b></td><td>{r[2] or '-'}</td><td>{''.join([f'<span class=\"badge {'bg-pos' if b[1]>=0 else 'bg-neg'}\">{b[0]}: {b[1]:,.2f}</span>' for b in get_all_balances(r[0], uid)])}</td><td class='no-print'><a href='/ui_edit_customer?id={r[0]}' class='btn-action btn-edit' style='background:#e3f2fd; color:#1565c0;'>تعديل</a></td></tr>" for r in rows])
            content = f"<div class='content-card no-print'><h3>إضافة عميل</h3><form action='/do_save_customer' method='POST'><div class='grid-container'><input name='fullname' placeholder='الاسم' class='input-field' required><input name='mobile' placeholder='الجوال' class='input-field'><input name='work_address' placeholder='العنوان' class='input-field'><input name='vat_number' placeholder='الرقم الضريبي' class='input-field'></div><button class='btn-action btn-save'>حفظ</button></form></div><div class='content-card'><table><thead><tr><th>الاسم</th><th>الجوال</th><th>الأرصدة</th><th class='no-print'>التحكم</th></tr></thead>{t_rows}</table></div>"
            self.wfile.write(build_layout("العملاء", content, uid, "/").encode())

        elif parsed.path == '/page_new_entry':
            ps = cur.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
            currs = [r[0] for r in cur.execute("SELECT c_name FROM currencies WHERE owner_id=?", (uid,)).fetchall()]
            p_o = "".join([f"<option value='{p[0]}'>{p[1]}</option>" for p in ps]); c_o = "".join([f"<option>{cr}</option>" for cr in currs])
            content = f"<div class='content-card'><h3>تسجيل حركة</h3><form action='/do_save_tx' method='POST'><select name='cid' class='input-field'>{p_o}</select><div class='grid-container'><input name='amt' type='number' step='any' class='input-field' placeholder='المبلغ'><select name='curr' class='input-field'>{c_o}</select><select name='type' class='input-field'><option>له (إيداع)</option><option>عليه (سحب)</option></select></div><textarea name='notes' class='input-field' placeholder='البيان'></textarea><button class='btn-action btn-save'>تأكيد</button></form></div>"
            self.wfile.write(build_layout("حركة جديدة", content, uid, "/page_new_entry").encode())
        
        # ... (بقية الـ GET من كود V9 تُضاف هنا بنفس المنطق)
        c.close()

    def show_auth_page(self, mode, error=""):
        self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
        title = "دخول النظام" if mode == "دخول" else ("حساب جديد" if mode == "تسجيل" else "استعادة الحساب")
        action = "/do_login" if mode == "دخول" else ("/do_register" if mode == "تسجيل" else "/do_request_reset")
        
        content = f"<div class='auth-box'><h2>{title}</h2><p style='color:red;'>{error}</p><form action='{action}' method='POST'>"
        content += "<input name='email' type='email' placeholder='البريد الإلكتروني' class='input-field' required>"
        if mode != "نسيت":
            content += "<input name='password' type='password' placeholder='كلمة المرور' class='input-field' required>"
        if mode == "تسجيل":
            content += "<input name='store' placeholder='اسم المحل/المؤسسة' class='input-field' required>"
        
        content += f"<button class='btn-action btn-save'>{title}</button></form>"
        content += f"<div style='margin-top:15px; text-align:center;'>"
        if mode == "دخول": content += "<a href='/register'>إنشاء حساب</a> | <a href='/forgot'>نسيت كلمة المرور؟</a>"
        else: content += "<a href='/login'>العودة للدخول</a>"
        content += "</div></div>"
        self.wfile.write((CSS_STYLES + content).encode())

    def do_POST(self):
        f = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
        uid = self.get_current_user()
        
        # عمليات الدخول والتسجيل
        if self.path == '/do_register':
            email = f.getvalue('email'); pw = hash_pw(f.getvalue('password')); store = f.getvalue('store')
            c = get_db(); cur = c.cursor()
            try:
                cur.execute("INSERT INTO users (email, password, store_name) VALUES (?,?,?)", (email, pw, store))
                new_id = cur.lastrowid
                cur.execute("INSERT INTO store_info VALUES ('name', ?, ?)", (store, new_id))
                for cury in ['ريال سعودي', 'ريال يمني', 'دولار']: cur.execute("INSERT INTO currencies VALUES (?,?)", (cury, new_id))
                c.commit(); self.redirect("/login")
            except: self.show_auth_page("تسجيل", "البريد مسجل مسبقاً")
            finally: c.close()
            return

        elif self.path == '/do_login':
            email = f.getvalue('email'); pw = hash_pw(f.getvalue('password'))
            c = get_db(); row = c.execute("SELECT id FROM users WHERE email=? AND password=?", (email, pw)).fetchone(); c.close()
            if row:
                sid = "".join(random.choices(string.ascii_letters + string.digits, k=32))
                ACTIVE_SESSIONS[sid] = row[0]
                self.send_response(303); self.send_header('Set-Cookie', f'session_id={sid}; HttpOnly; Path=/'); self.send_header('Location', '/'); self.end_headers()
            else: self.show_auth_page("دخول", "بيانات خاطئة")
            return

        elif self.path == '/do_request_reset':
            email = f.getvalue('email')
            c = get_db(); row = c.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if row:
                code = "".join(random.choices(string.digits, k=6))
                c.execute("UPDATE users SET reset_code=? WHERE id=?", (code, row[0])); c.commit()
                send_reset_mail(email, code)
                self.show_auth_page("دخول", "تم إرسال الكود لبريدك")
            else: self.show_auth_page("نسيت", "البريد غير موجود")
            c.close(); return

        # عمليات البيانات (تتطلب UID)
        if not uid: self.redirect("/login"); return
        
        c = get_db(); cur = c.cursor()
        if self.path == '/do_save_customer':
            cur.execute("INSERT INTO customers (owner_id, fullname, mobile, work_address, vat_number) VALUES (?,?,?,?,?)", (uid, f.getvalue('fullname'), f.getvalue('mobile'), f.getvalue('work_address'), f.getvalue('vat_number')))
        elif self.path == '/do_save_tx':
            cur.execute("INSERT INTO ledger (owner_id, customer_id, val_amount, val_currency, val_type, val_notes, entry_date) VALUES (?,?,?,?,?,?,?)", (uid, f.getvalue('cid'), float(f.getvalue('amt')), f.getvalue('curr'), f.getvalue('type'), f.getvalue('notes'), datetime.now().strftime("%Y-%m-%d %H:%M")))
        
        c.commit(); c.close(); self.redirect("/")

    def redirect(self, p): self.send_response(303); self.send_header('Location', p); self.end_headers()

if __name__ == '__main__':
    PORT = 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), AymanHandler) as httpd:
        print(f"نظام أيمن الحميري V10 يعمل على {PORT}")
        httpd.serve_forever()
