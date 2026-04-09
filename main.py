from flask import Flask, request, make_response, redirect, render_template_string
import sqlite3, os
from datetime import datetime

app = Flask(__name__)

# --- 1. إصلاح المسار ليكون متاحاً للكتابة في Vercel ---
DB_NAME = "/tmp/bahjat_v26_pro.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # إنشاء الجداول
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, store_name TEXT, user_real_name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, fullname TEXT, mobile TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, customer_id INTEGER, val_amount REAL, val_currency TEXT, val_type TEXT, val_notes TEXT, entry_date TEXT)")
    
    # --- إضافة مستخدم تلقائي للطوارئ ---
    try:
        cur.execute("INSERT OR IGNORE INTO users (email, password, store_name, user_real_name) VALUES (?,?,?,?)", 
                    ('admin@bahjat.com', '123456', 'متجر النخبة', 'م. أيمن الحميري'))
    except: pass
    
    conn.commit()
    conn.close()

init_db()

# --- 2. التصميم (نفس تصميمك الأصلي 100%) ---
CSS = """
<style>
    :root { --p: #0d47a1; --s: #1976d2; --bg: #f8fafc; --w: #ffffff; --green: #2e7d32; --red: #c62828; }
    body { font-family: 'Segoe UI', Tahoma; background: var(--bg); direction: rtl; margin: 0; }
    .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 20px; text-align: center; }
    .nav { display: flex; justify-content: center; background: var(--w); padding: 10px; gap: 10px; border-bottom: 1px solid #ddd; }
    .nav a { text-decoration: none; color: var(--p); font-weight: bold; padding: 5px 15px; border-radius: 15px; border: 1px solid var(--p); }
    .nav a.active { background: var(--p); color: white; }
    .card { background: var(--w); padding: 20px; margin: 20px auto; max-width: 900px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; }
    .btn-p { background: var(--p); width: 100%; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 12px; border-bottom: 1px solid #eee; text-align: right; }
    input, select, textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; }
</style>
"""

def render_ui(title, content, uid=None, active=""):
    nav = ""
    if uid:
        links = [('/', '👥 العملاء'), ('/new_tx', '📥 حركة'), ('/reports', '📊 تقارير'), ('/settings', '⚙️ إعدادات'), ('/contact', '📞 تواصل')]
        nav = "<div class='nav'>" + "".join([f'<a href="{p}" class="{"active" if active==p else ""}">{n}</a>' for p, n in links]) + "<a href='/logout' style='color:red'>🚪 خروج</a></div>"
    return render_template_string(f"<html><head><meta charset='UTF-8'><title>{title}</title>{CSS}</head><body><div class='header'><h2>بهجة برو V26</h2></div>{nav}<div class='card'>{content}</div></body></html>")

# --- 3. المسارات (Routes) ---

@app.route('/')
def index():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    res = conn.execute("SELECT * FROM customers WHERE owner_id=?", (uid,)).fetchall()
    f = """<h4>👤 إضافة عميل</h4><form action='/add_cust' method='POST'><input name='n' placeholder='اسم العميل' required><button class='btn btn-p'>حفظ</button></form>"""
    rows = "".join([f"<tr><td>{r['fullname']}</td><td><a href='/new_tx?cid={r['id']}'>إضافة حركة</a></td></tr>" for r in res])
    return render_ui("العملاء", f + "<table><thead><tr><th>الاسم</th><th>التحكم</th></tr></thead>" + rows + "</table>", uid, "/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        user = conn.execute("SELECT id FROM users WHERE email=? AND password=?", (request.form['e'], request.form['p'])).fetchone()
        if user:
            resp = make_response(redirect('/'))
            resp.set_cookie('uid', str(user['id']))
            return resp
        return render_ui("خطأ", "<h3>❌ بيانات خاطئة</h3><a href='/login'>عودة</a>")
    
    # رسالة مساعدة في صفحة الدخول
    help_msg = "<div style='background:#fff3cd; padding:10px; border-radius:5px; font-size:12px;'>ملاحظة: يمكنك الدخول بـ admin@bahjat.com وكلمة 123456</div>"
    return render_ui("دخول", f"<h3>🔐 تسجيل الدخول</h3>{help_msg}<form method='POST'><input name='e' placeholder='البريد'><input name='p' type='password' placeholder='كلمة السر'><button class='btn btn-p'>دخول</button></form><br><center><a href='/register'>إنشاء حساب جديد</a></center>")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (email, password, store_name, user_real_name) VALUES (?,?,?,?)", (request.form['e'], request.form['p'], request.form['s'], request.form['un']))
            conn.commit()
            return redirect('/login')
        except: return "البريد موجود مسبقاً"
    return render_ui("تسجيل", "<h3>📝 حساب جديد</h3><form method='POST'><input name='un' placeholder='الاسم'><input name='e' placeholder='البريد'><input name='p' placeholder='كلمة السر'><input name='s' placeholder='المتجر'><button class='btn btn-p'>تسجيل</button></form>")

@app.route('/new_tx', methods=['GET', 'POST'])
def new_tx():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    if request.method == 'POST':
        conn.execute("INSERT INTO ledger (owner_id, customer_id, val_amount, val_currency, val_type, val_notes, entry_date) VALUES (?,?,?,?,?,?,?)", 
                     (uid, request.form['cid'], request.form['amt'], request.form['curr'], request.form['type'], request.form['note'], datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit(); return redirect('/reports')
    
    cs = conn.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
    opts = "".join([f"<option value='{r['id']}'>{r['fullname']}</option>" for r in cs])
    return render_ui("حركة", f"<form method='POST'><select name='cid'>{opts}</select><input name='amt' type='number' placeholder='المبلغ'><select name='curr'><option>ريال سعودي</option></select><select name='type'><option>له</option><option>عليه</option></select><textarea name='note'></textarea><button class='btn btn-p'>حفظ</button></form>", uid, "/new_tx")

@app.route('/reports')
def reports():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    data = conn.execute("SELECT c.fullname, SUM(CASE WHEN l.val_type='له' THEN l.val_amount ELSE -l.val_amount END) as bal FROM customers c LEFT JOIN ledger l ON c.id = l.customer_id WHERE c.owner_id=? GROUP BY c.id", (uid,)).fetchall()
    rows = "".join([f"<tr><td>{r['fullname']}</td><td>{r['bal'] or 0}</td></tr>" for r in data])
    return render_ui("تقارير", f"<table><tr><th>العميل</th><th>الرصيد</th></tr>{rows}</table>", uid, "/reports")

@app.route('/logout')
def logout():
    resp = make_response(redirect('/login')); resp.set_cookie('uid', '', expires=0); return resp

@app.route('/add_cust', methods=['POST'])
def add_cust():
    uid = request.cookies.get('uid')
    conn = get_db(); conn.execute("INSERT INTO customers (owner_id, fullname) VALUES (?,?)", (uid, request.form['n'])); conn.commit()
    return redirect('/')

@app.route('/settings')
def settings(): return render_ui("إعدادات", "قريباً في التحديث القادم", request.cookies.get('uid'), "/settings")

@app.route('/contact')
def contact(): return render_ui("تواصل", "م. أيمن الحميري: 0556868717", request.cookies.get('uid'), "/contact")

if __name__ == "__main__":
    app.run()
