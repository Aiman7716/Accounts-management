# ==========================================================
# نظام "بهجة برو V26" - التحديث التراكمي (نسخة م. أيمن الحميري)
# الميزات: كشف ختامي، إدارة المدير، صفحة تواصل، استعادة بيانات
# ==========================================================

from flask import Flask, request, make_response, redirect, render_template_string
import sqlite3, os, random, string, shutil
from datetime import datetime

app = Flask(__name__)

# --- 1. الإعدادات المتوافقة مع Vercel ---
# ملاحظة: المجلد الوحيد المسموح بالكتابة فيه سحابياً هو /tmp
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

# --- 2. التصميم الفاخر المحدث (نفس كود م. أيمن) ---
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
    
    html = f"<html><head><meta charset='UTF-8'><title>{title}</title>{CSS}</head><body><div class='header'><h2>{store}</h2></div>{nav}<div class='card'>{content}</div></body></html>"
    return render_template_string(html)

# --- 3. المسارات الوظيفية (Routes) ---

@app.route('/')
def page_customers():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    f = """<h4>👤 إضافة عميل جديد</h4><form action='/add_cust' method='POST'><div class='grid'><input name='n' placeholder='الاسم الكامل' required><input name='m' placeholder='رقم الجوال'><input name='a' placeholder='العنوان'><input name='v' placeholder='الرقم الضريبي'></div><button class='btn btn-p'>حفظ البيانات</button></form><hr>"""
    search = "<input type='text' id='sInp' placeholder='🔍 ابحث...' class='search-box'>"
    res = conn.execute("SELECT * FROM customers WHERE owner_id=? ORDER BY id DESC", (uid,)).fetchall()
    rows = ""
    for r in res:
        bals = conn.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) as bal FROM ledger WHERE customer_id=? GROUP BY val_currency", (r['id'],)).fetchall()
        b_txt = " ".join([f"<span class='{'bal-pos' if b['bal']>=0 else 'bal-neg'}'>{b['val_currency']}: {b['bal']:,.2f}</span>" for b in bals]) or "0.00"
        rows += f"<tr><td><a href='/statement/{r['id']}'><b>{r['fullname']}</b></a></td><td>{r['mobile'] or '-'}</td><td>{b_txt}</td><td><a href='/edit_cust/{r['id']}' class='btn' style='background:#f1f5f9; color:var(--p)'>تعديل</a></td></tr>"
    return render_ui("العملاء", f + search + "<table><thead><tr><th>الاسم</th><th>الجوال</th><th>الأرصدة</th><th>التحكم</th></tr></thead>" + rows + "</table>", uid, "/")

@app.route('/statement/<int:cid>')
def page_statement(cid):
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    conn = get_db()
    name = conn.execute("SELECT fullname FROM customers WHERE id=?", (cid,)).fetchone()['fullname']
    txs = conn.execute("SELECT * FROM ledger WHERE customer_id=? ORDER BY id ASC", (cid,)).fetchall()
    rows = "".join([f"<tr><td>{t['entry_date']}</td><td class='{'bal-pos' if 'له' in t['val_type'] else 'bal-neg'}'>{t['val_type']}</td><td>{t['val_amount']:,.2f}</td><td>{t['val_currency']}</td><td>{t['val_notes']}</td></tr>" for t in txs])
    sums = conn.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) as bal FROM ledger WHERE customer_id=? GROUP BY val_currency", (cid,)).fetchall()
    total_rows = "".join([f"<tr class='footer-total'><td colspan='2'>صافي الرصيد الختامي ({s['val_currency']})</td><td colspan='3' class='{'bal-pos' if s['bal']>=0 else 'bal-neg'}'>{s['bal']:,.2f}</td></tr>" for s in sums])
    return render_ui("كشف حساب", f"<h3>📜 كشف حساب: {name}</h3><button onclick='window.print()' class='btn no-print' style='background:#444; color:white;'>🖨️ طباعة</button><table><thead><tr><th>التاريخ</th><th>النوع</th><th>المبلغ</th><th>العملة</th><th>البيان</th></tr></thead>{rows}{total_rows}</table>", uid)

@app.route('/admin')
def page_admin():
    uid = request.cookies.get('uid')
    conn = get_db()
    u_c = conn.execute("SELECT COUNT(id) FROM users").fetchone()[0]
    c_c = conn.execute("SELECT COUNT(id) FROM customers").fetchone()[0]
    l_c = conn.execute("SELECT COUNT(id) FROM ledger").fetchone()[0]
    content = f"""<h3>👑 لوحة تحكم المدير الرئيسي</h3><div class='grid'><div class='card'><h5>المستخدمين</h5><h2>{u_c}</h2></div><div class='card'><h5>العملاء</h5><h2>{c_c}</h2></div><div class='card'><h5>العمليات</h5><h2>{l_c}</h2></div></div><br><h4>إدارة النظام: م. أيمن الحميري</h4>"""
    return render_ui("إدارة المدير", content, uid, "/admin")

@app.route('/contact')
def page_contact():
    uid = request.cookies.get('uid')
    content = """<div style='text-align:center; padding:40px;'><h2 style='color:var(--p);'>📞 تواصل مع المطور</h2><h3>م. أيمن الحميري</h3><a href='https://wa.me/966556868717' class='btn btn-wa' target='_blank'>💬 واتساب: 0556868717</a><br><br><p>kebriay2030@gmail.com</p></div>"""
    return render_ui("تواصل", content, uid, "/contact")

# --- دوال العمليات (POST) ---
@app.route('/add_cust', methods=['POST'])
def add_cust():
    uid = request.cookies.get('uid')
    if uid:
        conn = get_db(); conn.execute("INSERT INTO customers (owner_id, fullname, mobile, address, vat_number) VALUES (?,?,?,?,?)", (uid, request.form['n'], request.form['m'], request.form['a'], request.form['v'])); conn.commit()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        user = conn.execute("SELECT id FROM users WHERE email=? AND password=?", (request.form['e'], request.form['p'])).fetchone()
        if user:
            resp = make_response(redirect('/'))
            resp.set_cookie('uid', str(user['id'])); return resp
    return render_ui("دخول", "<h3>🔐 تسجيل الدخول</h3><form method='POST'><input name='e' placeholder='البريد'><input name='p' type='password' placeholder='كلمة السر'><button class='btn btn-p'>دخول</button></form>")

@app.route('/logout')
def logout():
    resp = make_response(redirect('/login')); resp.set_cookie('uid', '', expires=0); return resp

if __name__ == "__main__":
    app.run()
