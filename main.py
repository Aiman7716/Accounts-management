# ==========================================================
# نظام "بهجة برو V26.1" - التحديث التراكمي (نسخة م. أيمن الحميري)
# الميزات: تسجيل مستخدم جديد، كشف ختامي، إدارة المدير، صفحة تواصل
# ==========================================================

from flask import Flask, request, make_response, redirect, render_template_string
import sqlite3, os, random, string
from datetime import datetime

app = Flask(__name__)

# --- 1. الإعدادات السحابية ---
DB_NAME = "/tmp/bahjat_v26_pro.db"
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, store_name TEXT, user_real_name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, fullname TEXT, mobile TEXT, address TEXT, vat_number TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, customer_id INTEGER, val_amount REAL, val_currency TEXT, val_type TEXT, val_notes TEXT, entry_date TEXT)")
    conn.commit(); conn.close()

init_db()

# --- 2. التصميم الفاخر (نسخة م. أيمن) ---
CSS = """
<style>
    :root { --p: #0d47a1; --s: #1976d2; --bg: #f8fafc; --w: #ffffff; --green: #2e7d32; --red: #c62828; }
    body { font-family: 'Segoe UI', Tahoma; background: var(--bg); direction: rtl; margin: 0; color: #1e293b; }
    .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .nav { display: flex; justify-content: center; background: var(--w); padding: 12px; gap: 8px; border-bottom: 1px solid #e2e8f0; position: sticky; top: 0; z-index: 1000; overflow-x: auto; }
    .nav a { border: 1px solid var(--p); color: var(--p); text-decoration: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 13px; white-space: nowrap; transition: 0.3s; }
    .nav a:hover, .nav a.active { background: var(--p); color: white; }
    .card { background: var(--w); padding: 25px; margin: 20px auto; max-width: 1100px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .bal-pos { background: #dcfce7; color: var(--green); padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 13px; }
    .bal-neg { background: #fee2e2; color: var(--red); padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 13px; }
    .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; text-align: center; transition: 0.2s; }
    .btn-p { background: var(--p); color: white; width: 100%; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 15px; border-bottom: 1px solid #f1f5f9; text-align: right; }
    th { background: #f8fafc; color: #64748b; font-weight: 600; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
    input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; }
</style>
"""

def render_ui(title, content, uid=None, active=""):
    store = "بهجة برو V26"
    if uid:
        conn = get_db(); res = conn.execute("SELECT store_name FROM users WHERE id=?", (uid,)).fetchone()
        if res: store = res['store_name']
    nav = ""
    if uid:
        links = [('/', '👥 العملاء'), ('/new_tx', '📥 حركة'), ('/reports', '📊 تقارير'), ('/admin', '👑 المدير'), ('/settings', '⚙️ إعدادات'), ('/contact', '📞 تواصل')]
        nav = "<div class='nav'>" + "".join([f'<a href="{p}" class="{"active" if active==p else ""}">{n}</a>' for p, n in links]) + "<a href='/logout' style='color:var(--red)'>🚪 خروج</a></div>"
    return render_template_string(f"<html><head><meta charset='UTF-8'><title>{title}</title>{CSS}</head><body><div class='header'><h2>{store}</h2></div>{nav}<div class='card'>{content}</div></body></html>")

# --- 3. المسارات الوظيفية ---

@app.route('/')
def index():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    res = conn.execute("SELECT * FROM customers WHERE owner_id=? ORDER BY id DESC", (uid,)).fetchall()
    f = """<h4>👤 إضافة عميل جديد</h4><form action='/add_cust' method='POST'><div class='grid'><input name='n' placeholder='الاسم الكامل' required><input name='m' placeholder='رقم الجوال'></div><button class='btn btn-p'>حفظ</button></form><hr>"""
    rows = "".join([f"<tr><td><a href='/statement/{r['id']}'><b>{r['fullname']}</b></a></td><td>{r['mobile'] or '-'}</td></tr>" for r in res])
    return render_ui("العملاء", f + "<table><thead><tr><th>الاسم</th><th>الجوال</th></tr></thead>" + rows + "</table>", uid, "/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        user = conn.execute("SELECT id FROM users WHERE email=? AND password=?", (request.form['e'], request.form['p'])).fetchone()
        if user:
            resp = make_response(redirect('/'))
            resp.set_cookie('uid', str(user['id']))
            return resp
        return render_ui("خطأ", "<h3>❌ خطأ في الدخول</h3><a href='/login'>حاول ثانية</a>")
    return render_ui("دخول", "<h3>🔐 تسجيل الدخول</h3><form method='POST'><input name='e' placeholder='البريد' required><input name='p' type='password' placeholder='كلمة السر' required><button class='btn btn-p'>دخول</button></form><p align='center'><a href='/register'>إنشاء حساب جديد (مستخدم جديد)</a></p>")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (email, password, store_name, user_real_name) VALUES (?,?,?,?)", (request.form['e'], request.form['p'], request.form['s'], request.form['un']))
            conn.commit()
            return redirect('/login')
        except: return render_ui("خطأ", "<h3>❌ البريد مسجل مسبقاً</h3><a href='/register'>حاول ثانية</a>")
    return render_ui("تسجيل", "<h3>📝 مستخدم جديد</h3><form method='POST'><input name='un' placeholder='الاسم الكامل' required><input name='e' placeholder='البريد' required><input name='p' placeholder='كلمة السر' required><input name='s' placeholder='اسم المحل' required><button class='btn btn-p'>تأكيد التسجيل</button></form>")

@app.route('/new_tx')
def new_tx():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    cs = conn.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
    opts = "".join([f"<option value='{r['id']}'>{r['fullname']}</option>" for r in cs])
    c = f"<h3>📥 تسجيل حركة</h3><form action='/save_tx' method='POST'><select name='cid' required><option value=''>-- اختر العميل --</option>{opts}</select><input name='amt' type='number' step='any' placeholder='المبلغ' required><select name='curr'><option>ريال سعودي</option><option>ريال يمني</option><option>دولار</option></select><select name='type'><option>له (إيداع)</option><option>عليه (سحب)</option></select><textarea name='note' placeholder='البيان'></textarea><button class='btn btn-p'>حفظ</button></form>"
    return render_ui("حركة", c, uid, "/new_tx")

@app.route('/save_tx', methods=['POST'])
def save_tx():
    uid = request.cookies.get('uid')
    conn = get_db()
    conn.execute("INSERT INTO ledger (owner_id, customer_id, val_amount, val_currency, val_type, val_notes, entry_date) VALUES (?,?,?,?,?,?,?)", 
                 (uid, request.form['cid'], float(request.form['amt']), request.form['curr'], request.form['type'], request.form['note'], datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    return redirect('/reports')

@app.route('/reports')
def reports():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    cs = conn.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
    rows = ""
    for r in cs:
        bals = conn.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) as bal FROM ledger WHERE customer_id=? GROUP BY val_currency", (r['id'],)).fetchall()
        b_txt = " | ".join([f"{b['val_currency']}: {b['bal']:,.2f}" for b in bals]) or "0.00"
        rows += f"<tr><td>{r['fullname']}</td><td>{b_txt}</td></tr>"
    return render_ui("التقارير", "<h3>📊 ميزان المراجعة</h3><table><thead><tr><th>العميل</th><th>الرصيد التراكمي</th></tr></thead>" + rows + "</table>", uid, "/reports")

@app.route('/logout')
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('uid', '', expires=0)
    return resp

@app.route('/contact')
def contact():
    uid = request.cookies.get('uid')
    return render_ui("تواصل", "<h3>📞 م. أيمن الحميري</h3><p>واتساب: 0556868717</p>", uid, "/contact")

@app.route('/add_cust', methods=['POST'])
def add_cust():
    uid = request.cookies.get('uid')
    conn = get_db()
    conn.execute("INSERT INTO customers (owner_id, fullname, mobile) VALUES (?,?,?)", (uid, request.form['n'], request.form['m']))
    conn.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run()
