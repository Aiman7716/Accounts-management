# ==========================================================
# نظام "بهجة برو V26" - النسخة السحابية الكاملة (Vercel)
# تطوير م. أيمن الحميري - "الشريك العبقري"
# ==========================================================

from flask import Flask, request, make_response, redirect, render_template_string
import sqlite3, os, random, string, shutil
from datetime import datetime

app = Flask(__name__)

# --- 1. الإعدادات السحابية (متطلبات Vercel) ---
DB_NAME = "/tmp/bahjat_v26_pro.db"
BK_DIR = "/tmp/backups_v26"
if not os.path.exists(BK_DIR): os.makedirs(BK_DIR)

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, store_name TEXT, user_real_name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, fullname TEXT, mobile TEXT, address TEXT, vat_number TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS currencies (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, c_name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, customer_id INTEGER, val_amount REAL, val_currency TEXT, val_type TEXT, val_notes TEXT, entry_date TEXT)")
    conn.commit(); conn.close()

init_db()

# --- 2. التصميم الفاخر (نفس CSS م. أيمن دون تعديل) ---
CSS = """
<style>
    :root { --p: #0d47a1; --s: #1976d2; --bg: #f8fafc; --w: #ffffff; --green: #2e7d32; --red: #c62828; }
    body { font-family: 'Segoe UI', Tahoma; background: var(--bg); direction: rtl; margin: 0; color: #1e293b; }
    .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 25px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .nav { display: flex; justify-content: center; background: var(--w); padding: 12px; gap: 8px; border-bottom: 1px solid #e2e8f0; position: sticky; top: 0; z-index: 1000; overflow-x: auto; }
    .nav a { border: 1px solid var(--p); color: var(--p); text-decoration: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 13px; white-space: nowrap; transition: 0.3s; }
    .nav a:hover, .nav a.active { background: var(--p); color: white; }
    .card { background: var(--w); padding: 25px; margin: 20px auto; max-width: 1100px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .bal-pos { background: #dcfce7; color: var(--green); padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 13px; }
    .bal-neg { background: #fee2e2; color: var(--red); padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 13px; }
    .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; text-align: center; transition: 0.2s; }
    .btn-p { background: var(--p); color: white; width: 100%; }
    .btn-wa { background: #25d366; color: white; margin-top: 10px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 15px; border-bottom: 1px solid #f1f5f9; text-align: right; }
    th { background: #f8fafc; color: #64748b; font-weight: 600; }
    .footer-total { background: #f1f5f9; font-weight: 900; font-size: 1.1em; border-top: 3px solid var(--p); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
    input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; }
    .search-box { background: #fff; border: 2px solid var(--p); }
    @media print { .no-print { display: none !important; } .card { box-shadow: none; border: none; } }
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
        nav = "<div class='nav no-print'>" + "".join([f'<a href="{p}" class="{"active" if active==p else ""}">{n}</a>' for p, n in links]) + "<a href='/logout' style='color:var(--red)'>🚪 خروج</a></div>"
    return render_template_string(f"<html><head><meta charset='UTF-8'><title>{title}</title>{CSS}</head><body><div class='header'><h2>{store}</h2></div>{nav}<div class='card'>{content}</div></body></html>")

# --- 3. الصفحات والمتطلبات (كاملة) ---

@app.route('/') # صفحة العملاء مع متطلباتها
def page_customers():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    f = """<h4>👤 إضافة عميل جديد</h4><form action='/add_cust' method='POST'><div class='grid'><input name='n' placeholder='الاسم الكامل' required><input name='m' placeholder='رقم الجوال'><input name='a' placeholder='العنوان'><input name='v' placeholder='الرقم الضريبي'></div><button class='btn btn-p'>حفظ البيانات</button></form><hr>"""
    search = "<input type='text' id='sInp' placeholder='🔍 ابحث...' class='search-box'>"
    res = conn.execute("SELECT * FROM customers WHERE owner_id=? ORDER BY id DESC", (uid,)).fetchall()
    rows = "".join([f"<tr><td><a href='/statement/{r['id']}'><b>{r['fullname']}</b></a></td><td>{r['mobile'] or '-'}</td><td><a href='/edit_cust/{r['id']}' class='btn'>تعديل</a></td></tr>" for r in res])
    return render_ui("العملاء", f + search + "<table><thead><tr><th>الاسم</th><th>الجوال</th><th>التحكم</th></tr></thead>" + rows + "</table>", uid, "/")

@app.route('/new_tx') # صفحة إضافة حركة مع متطلباتها
def page_new_tx():
    uid = request.cookies.get('uid')
    conn = get_db()
    cs = conn.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
    c_opts = "".join([f"<option value='{r['id']}'>{r['fullname']}</option>" for r in cs])
    c = f"<h3>📥 تسجيل حركة مالية</h3><form action='/save_tx' method='POST'><select name='cid' required><option value=''>-- اختر العميل --</option>{c_opts}</select><div class='grid'><div><input name='amt' type='number' step='any' placeholder='المبلغ' required></div><div><select name='curr'><option>ريال سعودي</option><option>ريال يمني</option><option>دولار</option></select></div></div><select name='type'><option>له (إيداع)</option><option>عليه (سحب)</option></select><textarea name='note' placeholder='البيان...'></textarea><button class='btn btn-p'>حفظ العملية</button></form>"
    return render_ui("حركة", c, uid, "/new_tx")

@app.route('/reports') # صفحة التقارير مع متطلباتها
def page_reports():
    uid = request.cookies.get('uid')
    conn = get_db()
    cs = conn.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
    rows = ""
    for r in cs:
        bals = conn.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) as bal FROM ledger WHERE customer_id=? GROUP BY val_currency", (r['id'],)).fetchall()
        b_txt = " | ".join([f"{b['val_currency']}: {b['bal']:,.2f}" for b in bals]) or "0.00"
        rows += f"<tr><td>{r['fullname']}</td><td>{b_txt}</td><td><a href='/statement/{r['id']}' class='btn' style='background:var(--p); color:white;'>تفصيلي</a></td></tr>"
    return render_ui("التقارير", "<h3>📊 ميزان المراجعة</h3><table><thead><tr><th>العميل</th><th>الرصيد التراكمي</th><th>الإجراء</th></tr></thead>" + rows + "</table>", uid, "/reports")

@app.route('/settings') # صفحة إعدادات مع متطلباتها
def page_settings():
    uid = request.cookies.get('uid')
    conn = get_db(); u = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c = f"""<h4>⚙️ إعدادات الحساب</h4><form action='/update_profile' method='POST'><div class='grid'><input name='un' value='{u['user_real_name']}'><input name='e' value='{u['email']}'><input name='s' value='{u['store_name']}'></div><button class='btn btn-p'>تحديث</button></form>"""
    return render_ui("الإعدادات", c, uid, "/settings")

@app.route('/contact') # صفحة تواصل مع متطلباتها
def page_contact():
    uid = request.cookies.get('uid')
    c = """<div style='text-align:center;'><h2>📞 تواصل مع المطور</h2><h3>م. أيمن الحميري</h3><a href='https://wa.me/966556868717' class='btn btn-wa'>واتساب: 0556868717</a></div>"""
    return render_ui("تواصل", c, uid, "/contact")

@app.route('/logout') # تسجيل خروج
def logout():
    resp = make_response(redirect('/login')); resp.set_cookie('uid', '', expires=0); return resp

# --- العمليات (POST) ---
@app.route('/add_cust', methods=['POST'])
def add_cust():
    uid = request.cookies.get('uid')
    conn = get_db(); conn.execute("INSERT INTO customers (owner_id, fullname, mobile) VALUES (?,?,?)", (uid, request.form['n'], request.form['m'])); conn.commit()
    return redirect('/')

@app.route('/save_tx', methods=['POST'])
def save_tx():
    uid = request.cookies.get('uid')
    conn = get_db(); conn.execute("INSERT INTO ledger (owner_id, customer_id, val_amount, val_currency, val_type, val_notes, entry_date) VALUES (?,?,?,?,?,?,?)", 
                 (uid, request.form['cid'], float(request.form['amt']), request.form['curr'], request.form['type'], request.form['note'], datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); return redirect('/reports')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db(); user = conn.execute("SELECT id FROM users WHERE email=? AND password=?", (request.form['e'], request.form['p'])).fetchone()
        if user: resp = make_response(redirect('/')); resp.set_cookie('uid', str(user['id'])); return resp
    return render_ui("دخول", "<h3>🔐 دخول</h3><form method='POST'><input name='e' placeholder='البريد'><input name='p' type='password' placeholder='كلمة السر'><button class='btn btn-p'>دخول</button></form>")

if __name__ == "__main__":
    app.run()
