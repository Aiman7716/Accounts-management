from flask import Flask, request, make_response, redirect, render_template_string
import sqlite3, os
from datetime import datetime

app = Flask(__name__)

# --- 1. إعداد قاعدة بيانات سريعة (تعمل في ذاكرة السيرفر لضمان الاستجابة) ---
# ملاحظة: هذه الطريقة تضمن عمل الموقع فوراً على Vercel/Render
DB_CONN = sqlite3.connect(":memory:", check_same_thread=False)
DB_CONN.row_factory = sqlite3.Row

def init_db():
    cur = DB_CONN.cursor()
    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, password TEXT, store_name TEXT, user_real_name TEXT)")
    cur.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, owner_id INTEGER, fullname TEXT, mobile TEXT)")
    cur.execute("CREATE TABLE ledger (id INTEGER PRIMARY KEY, owner_id INTEGER, customer_id INTEGER, val_amount REAL, val_currency TEXT, val_type TEXT, val_notes TEXT, entry_date TEXT)")
    # مستخدم جاهز للدخول فوراً
    cur.execute("INSERT INTO users (id, email, password, store_name, user_real_name) VALUES (1, 'admin@bahjat.com', '123456', 'متجر النخبة', 'م. أيمن الحميري')")
    DB_CONN.commit()

init_db()

# --- 2. التصميم الفاخر (نفس بصمة م. أيمن) ---
CSS = """
<style>
    :root { --p: #0d47a1; --s: #1976d2; --bg: #f8fafc; --w: #ffffff; }
    body { font-family: 'Segoe UI', Tahoma; background: var(--bg); direction: rtl; margin: 0; text-align: right; }
    .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 20px; text-align: center; }
    .nav { display: flex; justify-content: center; background: var(--w); padding: 10px; gap: 10px; border-bottom: 2px solid var(--p); overflow-x: auto; }
    .nav a { text-decoration: none; color: var(--p); font-weight: bold; padding: 8px 15px; border-radius: 20px; border: 1px solid var(--p); font-size: 13px; }
    .nav a.active { background: var(--p); color: white; }
    .card { background: var(--w); padding: 25px; margin: 20px auto; max-width: 800px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    .btn { padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; display: block; text-align: center; text-decoration: none; }
    .btn-p { background: var(--p); color: white; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 12px; border-bottom: 1px solid #eee; }
    input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
</style>
"""

def render_ui(title, content, uid=None, active=""):
    nav = ""
    if uid:
        links = [('/', '👥 العملاء'), ('/new_tx', '📥 حركة'), ('/reports', '📊 تقارير'), ('/settings', '⚙️ إعدادات'), ('/contact', '📞 تواصل')]
        nav = "<div class='nav'>" + "".join([f'<a href="{p}" class="{"active" if active==p else ""}">{n}</a>' for p, n in links]) + "<a href='/logout' style='color:red'>🚪 خروج</a></div>"
    return render_template_string(f"<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title>{CSS}</head><body><div class='header'><h2>بهجة برو V26</h2></div>{nav}<div class='card'>{content}</div></body></html>")

# --- 3. المسارات والصفحات (كاملة كما طلبت) ---

@app.route('/')
def page_customers():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    cur = DB_CONN.cursor()
    res = cur.execute("SELECT * FROM customers WHERE owner_id=?", (uid,)).fetchall()
    f = """<h3>👥 إدارة العملاء</h3><form action='/add_cust' method='POST'><input name='n' placeholder='اسم العميل الجديد' required><button class='btn btn-p'>➕ إضافة عميل</button></form><hr>"""
    rows = "".join([f"<tr><td><b>{r['fullname']}</b></td><td><a href='/new_tx?cid={r['id']}' style='color:var(--s)'>تسجيل حركة</a></td></tr>" for r in res])
    return render_ui("العملاء", f + "<table><thead><tr><th>الاسم</th><th>التحكم</th></tr></thead>" + rows + "</table>", uid, "/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cur = DB_CONN.cursor()
        user = cur.execute("SELECT id FROM users WHERE email=? AND password=?", (request.form['e'], request.form['p'])).fetchone()
        if user:
            resp = make_response(redirect('/'))
            resp.set_cookie('uid', str(user['id']))
            return resp
        return render_ui("خطأ", "❌ بيانات غير صحيحة. <a href='/login'>حاول مرة أخرى</a>")
    return render_ui("دخول", "<h3>🔐 تسجيل الدخول</h3><p style='color:gray; font-size:12px;'>الحساب التجريبي: admin@bahjat.com | كلمة السر: 123456</p><form method='POST'><input name='e' placeholder='البريد'><input name='p' type='password' placeholder='كلمة السر'><button class='btn btn-p'>دخول</button></form><br><center><a href='/register'>إنشاء حساب جديد</a></center>")

@app.route('/new_tx', methods=['GET', 'POST'])
def page_new_tx():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    if request.method == 'POST':
        cur = DB_CONN.cursor()
        cur.execute("INSERT INTO ledger (owner_id, customer_id, val_amount, val_currency, val_type, val_notes, entry_date) VALUES (?,?,?,?,?,?,?)", 
                    (uid, request.form['cid'], request.form['amt'], request.form['curr'], request.form['type'], request.form['note'], datetime.now().strftime("%Y-%m-%d %H:%M")))
        DB_CONN.commit()
        return redirect('/reports')
    
    cur = DB_CONN.cursor()
    cs = cur.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
    opts = "".join([f"<option value='{r['id']}'>{r['fullname']}</option>" for r in cs])
    return render_ui("إضافة حركة", f"<h3>📥 تسجيل حركة مالية</h3><form method='POST'><select name='cid' required><option value=''>-- اختر العميل --</option>{opts}</select><input name='amt' type='number' step='any' placeholder='المبلغ' required><select name='curr'><option>ريال سعودي</option><option>ريال يمني</option><option>دولار</option></select><select name='type'><option>له (إيداع)</option><option>عليه (سحب)</option></select><textarea name='note' placeholder='البيان (اختياري)'></textarea><button class='btn btn-p'>حفظ الحركة</button></form>", uid, "/new_tx")

@app.route('/reports')
def page_reports():
    uid = request.cookies.get('uid')
    if not uid: return redirect('/login')
    cur = DB_CONN.cursor()
    # كود ميزان المراجعة التراكمي
    data = cur.execute("""SELECT c.fullname, 
                        SUM(CASE WHEN l.val_type LIKE 'له%' THEN l.val_amount ELSE -l.val_amount END) as bal 
                        FROM customers c LEFT JOIN ledger l ON c.id = l.customer_id 
                        WHERE c.owner_id=? GROUP BY c.id""", (uid,)).fetchall()
    rows = "".join([f"<tr><td>{r['fullname']}</td><td style='color:{'green' if (r['bal'] or 0)>=0 else 'red'}'>{r['bal'] or 0:,.2f}</td></tr>" for r in data])
    return render_ui("التقارير", f"<h3>📊 ميزان المراجعة</h3><table><thead><tr><th>العميل</th><th>الرصيد التراكمي</th></tr></thead>{rows}</table>", uid, "/reports")

@app.route('/register', methods=['GET', 'POST'])
def page_register():
    if request.method == 'POST':
        cur = DB_CONN.cursor()
        cur.execute("INSERT INTO users (email, password, store_name, user_real_name) VALUES (?,?,?,?)", 
                    (request.form['e'], request.form['p'], request.form['s'], request.form['un']))
        DB_CONN.commit()
        return redirect('/login')
    return render_ui("تسجيل", "<h3>📝 مستخدم جديد</h3><form method='POST'><input name='un' placeholder='الاسم الكامل'><input name='e' placeholder='البريد'><input name='p' placeholder='كلمة السر'><input name='s' placeholder='اسم المتجر'><button class='btn btn-p'>تأكيد التسجيل</button></form>")

@app.route('/settings')
def page_settings():
    uid = request.cookies.get('uid')
    return render_ui("الإعدادات", "<h4>⚙️ الإعدادات</h4><p>نسخة م. أيمن الحميري V26 برو جاهزة ومستقرة.</p>", uid, "/settings")

@app.route('/contact')
def page_contact():
    uid = request.cookies.get('uid')
    return render_ui("تواصل", "<h4>📞 تواصل مع المطور</h4><h3>م. أيمن الحميري</h3><p>واتساب: 0556868717</p><p>إيميل: kebriay2030@gmail.com</p>", uid, "/contact")

@app.route('/add_cust', methods=['POST'])
def add_cust():
    uid = request.cookies.get('uid')
    cur = DB_CONN.cursor()
    cur.execute("INSERT INTO customers (owner_id, fullname) VALUES (?,?)", (uid, request.form['n']))
    DB_CONN.commit()
    return redirect('/')

@app.route('/logout')
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('uid', '', expires=0)
    return resp

if __name__ == "__main__":
    app.run()
