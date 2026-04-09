# ==========================================================
# نظام "بهجة برو V26" - التحديث التراكمي (نسخة م. أيمن الحميري)
# الميزات: كشف ختامي، إدارة المدير، صفحة تواصل، استعادة بيانات
# ==========================================================

import http.server, socketserver, sqlite3, urllib.parse, os, cgi, shutil, random, string
from datetime import datetime

# --- 1. الإعدادات ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_PATH, "bahjat_v26_pro.db")
BK_DIR = os.path.join(BASE_PATH, "backups_v26")
if not os.path.exists(BK_DIR): os.makedirs(BK_DIR)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, store_name TEXT, user_real_name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, fullname TEXT, mobile TEXT, address TEXT, vat_number TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS currencies (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, c_name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, customer_id INTEGER, val_amount REAL, val_currency TEXT, val_type TEXT, val_notes TEXT, entry_date TEXT)")
    conn.commit(); conn.close()

init_db()
SESSIONS = {}

# --- 2. التصميم الفاخر المحدث ---
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

class BahjatProV26(http.server.SimpleHTTPRequestHandler):
    
    def get_uid(self):
        ck = self.headers.get('Cookie')
        if ck and "sid=" in ck:
            sid = ck.split("sid=")[1].split(";")[0]
            return SESSIONS.get(sid)
        return None

    def do_GET(self):
        uid = self.get_uid(); parsed = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(parsed.query)
        path = parsed.path
        
        # التوجيه الذكي
        if uid and path in ['/login', '/register']: self.redirect('/'); return
        if path == '/login': self.ui_login(); return
        if path == '/register': self.ui_register(); return
        if path == '/contact': self.page_contact(uid); return
        if not uid: self.redirect('/login'); return

        # المسارات والتبويبات
        if path == '/': self.page_customers(uid)
        elif path == '/new_tx': self.page_new_tx(uid)
        elif path == '/reports': self.page_reports(uid)
        elif path == '/settings': self.page_settings(uid)
        elif path == '/admin': self.page_admin(uid)
        elif path == '/statement': self.page_statement(uid, q.get('id',[''])[0])
        elif path == '/edit_cust': self.page_edit_cust(uid, q.get('id',[''])[0])
        elif path == '/del_cust':
            c = sqlite3.connect(DB_NAME); c.execute("DELETE FROM customers WHERE id=? AND owner_id=?", (q.get('id',[''])[0], uid)); c.commit(); self.redirect('/')
        elif path == '/do_backup': self.action_backup(); self.redirect('/settings')
        elif path == '/restore': self.action_restore(q.get('f',[''])[0]); self.redirect('/settings')
        elif path == '/logout':
            self.send_response(303); self.send_header('Set-Cookie', 'sid=; Max-Age=0; Path=/'); self.send_header('Location', '/login'); self.end_headers()

    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        uid = self.get_uid()

        if self.path == '/do_reg':
            un, e, p, s = form.getvalue('un'), form.getvalue('e'), form.getvalue('p'), form.getvalue('s')
            cur.execute("INSERT INTO users (email, password, store_name, user_real_name) VALUES (?,?,?,?)", (e, p, s, un))
            nid = cur.lastrowid
            [cur.execute("INSERT INTO currencies (owner_id, c_name) VALUES (?,?)", (nid, c)) for c in ['ريال سعودي','ريال يمني','دولار']]
            conn.commit()
            sid = "".join(random.choices(string.ascii_letters + string.digits, k=30)); SESSIONS[sid] = nid
            self.send_response(303); self.send_header('Set-Cookie', f'sid={sid}; Path=/; HttpOnly'); self.send_header('Location', '/'); self.end_headers()
            return

        elif self.path == '/do_login':
            u = conn.execute("SELECT id FROM users WHERE email=? AND password=?", (form.getvalue('e'), form.getvalue('p'))).fetchone()
            if u:
                sid = "".join(random.choices(string.ascii_letters + string.digits, k=30)); SESSIONS[sid] = u[0]
                self.send_response(303); self.send_header('Set-Cookie', f'sid={sid}; Path=/; HttpOnly'); self.send_header('Location', '/'); self.end_headers()
            else: self.redirect('/login?err=1')
            return

        if uid:
            if self.path == '/add_cust':
                cur.execute("INSERT INTO customers (owner_id, fullname, mobile, address, vat_number) VALUES (?,?,?,?,?)", (uid, form.getvalue('n'), form.getvalue('m'), form.getvalue('a'), form.getvalue('v')))
            elif self.path == '/update_cust':
                cur.execute("UPDATE customers SET fullname=?, mobile=?, address=?, vat_number=? WHERE id=? AND owner_id=?", (form.getvalue('n'), form.getvalue('m'), form.getvalue('a'), form.getvalue('v'), form.getvalue('id'), uid))
            elif self.path == '/save_tx':
                cur.execute("INSERT INTO ledger (owner_id, customer_id, val_amount, val_currency, val_type, val_notes, entry_date) VALUES (?,?,?,?,?,?,?)", (uid, form.getvalue('cid'), float(form.getvalue('amt')), form.getvalue('curr'), form.getvalue('type'), form.getvalue('note'), datetime.now().strftime("%Y-%m-%d %H:%M")))
            elif self.path == '/update_profile':
                cur.execute("UPDATE users SET email=?, store_name=?, user_real_name=? WHERE id=?", (form.getvalue('e'), form.getvalue('s'), form.getvalue('un'), uid))
                if form.getvalue('p'): cur.execute("UPDATE users SET password=? WHERE id=?", (form.getvalue('p'), uid))
            conn.commit(); self.redirect('/')
        conn.close()

    def render(self, t, c, uid=None, active=""):
        store = "بهجة برو V26"
        if uid:
            conn = sqlite3.connect(DB_NAME); res = conn.execute("SELECT store_name FROM users WHERE id=?", (uid,)).fetchone()
            if res: store = res[0]
        nav = ""
        if uid:
            links = [('/', '👥 العملاء'), ('/new_tx', '📥 إضافة حركة'), ('/reports', '📊 التقارير'), ('/admin', '👑 المدير'), ('/settings', '⚙️ الإعدادات'), ('/contact', '📞 تواصل')]
            nav = "<div class='nav no-print'>" + "".join([f'<a href="{p}" class="{"active" if active==p else ""}">{n}</a>' for p, n in links]) + "<a href='/logout' style='color:var(--red)'>🚪 خروج</a></div>"
        h = f"<html><head><meta charset='UTF-8'><title>{t}</title>{CSS}</head><body dir='rtl'><div class='header'><h2>{store}</h2></div>{nav}<div class='card'>{c}</div></body></html>"
        self.send_response(200); self.send_header('Content-type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write(h.encode())

    # --- التبويبات والميزات ---
    def page_customers(self, uid):
        conn = sqlite3.connect(DB_NAME)
        f = f"""<h4>👤 إضافة عميل جديد</h4><form action='/add_cust' method='POST'><div class='grid'>
        <input name='n' placeholder='الاسم الكامل' required><input name='m' placeholder='رقم الجوال'>
        <input name='a' placeholder='العنوان'><input name='v' placeholder='الرقم الضريبي'></div><button class='btn btn-p'>حفظ البيانات</button></form><hr>"""
        search = "<input type='text' id='sInp' onkeyup='searchTable()' placeholder='🔍 ابحث بالاسم أو الرقم...' class='search-box'>"
        res = conn.execute("SELECT id, fullname, mobile FROM customers WHERE owner_id=? ORDER BY id DESC", (uid,)).fetchall()
        rows = ""
        for r in res:
            bals = conn.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) FROM ledger WHERE customer_id=? GROUP BY val_currency", (r[0],)).fetchall()
            b_txt = " ".join([f"<span class='{'bal-pos' if b[1]>=0 else 'bal-neg'}'>{b[0]}: {b[1]:,.2f}</span>" for b in bals]) or "0.00"
            rows += f"<tr><td><a href='/statement?id={r[0]}'><b>{r[1]}</b></a></td><td>{r[2] or '-'}</td><td>{b_txt}</td><td><a href='/edit_cust?id={r[0]}' class='btn' style='background:#f1f5f9; color:var(--p)'>تعديل</a></td></tr>"
        self.render("العملاء", f + search + "<table id='cTab'><thead><tr><th>الاسم</th><th>الجوال</th><th>الأرصدة</th><th>التحكم</th></tr></thead>" + rows + "</table>", uid, "/")

    def page_statement(self, uid, cid):
        conn = sqlite3.connect(DB_NAME); name = conn.execute("SELECT fullname FROM customers WHERE id=?", (cid,)).fetchone()[0]
        txs = conn.execute("SELECT entry_date, val_type, val_amount, val_currency, val_notes FROM ledger WHERE customer_id=? ORDER BY id ASC", (cid,)).fetchall()
        rows = "".join([f"<tr><td>{t[0]}</td><td class='{'bal-pos' if 'له' in t[1] else 'bal-neg'}'>{t[1]}</td><td>{t[2]:,.2f}</td><td>{t[3]}</td><td>{t[4]}</td></tr>" for t in txs])
        
        # ميزة إجمالي الرصيد الختامي (V26)
        sums = conn.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) FROM ledger WHERE customer_id=? GROUP BY val_currency", (cid,)).fetchall()
        total_rows = "".join([f"<tr class='footer-total'><td colspan='2'>صافي الرصيد الختامي ({s[0]})</td><td colspan='3' class='{'bal-pos' if s[1]>=0 else 'bal-neg'}'>{s[1]:,.2f}</td></tr>" for s in sums])
        
        self.render("كشف حساب", f"<h3>📜 كشف حساب: {name}</h3><button onclick='window.print()' class='btn no-print' style='background:#444; color:white;'>🖨️ طباعة</button><table><thead><tr><th>التاريخ</th><th>النوع</th><th>المبلغ</th><th>العملة</th><th>البيان</th></tr></thead>{rows}{total_rows}</table>", uid)

    def page_admin(self, uid):
        conn = sqlite3.connect(DB_NAME)
        u_count = conn.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        c_count = conn.execute("SELECT COUNT(id) FROM customers").fetchone()[0]
        l_count = conn.execute("SELECT COUNT(id) FROM ledger").fetchone()[0]
        content = f"""<h3>👑 لوحة تحكم المدير الرئيسي</h3>
        <div class='grid'>
            <div class='stat-bar' style='background:white; padding:20px; border-radius:10px; border:1px solid #ddd;'><h5>عدد المستخدمين</h5><h2>{u_count}</h2></div>
            <div class='stat-bar' style='background:white; padding:20px; border-radius:10px; border:1px solid #ddd;'><h5>إجمالي العملاء</h5><h2>{c_count}</h2></div>
            <div class='stat-bar' style='background:white; padding:20px; border-radius:10px; border:1px solid #ddd;'><h5>إجمالي العمليات</h5><h2>{l_count}</h2></div>
        </div><br><h4>إدارة النظام: م. أيمن الحميري</h4>"""
        self.render("إدارة المدير", content, uid, "/admin")

    def page_contact(self, uid):
        content = f"""
        <div style='text-align:center; padding:40px;'>
            <h2 style='color:var(--p);'>📞 تواصل مع المطور</h2>
            <img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' width='100' style='border-radius:50%; margin-bottom:20px;'>
            <h3>م. أيمن الحميري</h3>
            <p style='color:#64748b;'>مستشار استراتيجي ومطور برمجيات</p>
            <hr style='width:50%; border:1px solid #eee;'>
            <div style='margin-top:20px;'>
                <a href='https://wa.me/966556868717' class='btn btn-wa' target='_blank'>💬 تواصل عبر الواتساب (0556868717)</a><br><br>
                <a href='mailto:kebriay2030@gmail.com' class='btn' style='background:#f1f5f9; color:var(--p); width:100%; border:1px solid #ddd;'>📧 kebriay2030@gmail.com</a>
            </div>
            <p style='margin-top:30px; font-size:12px; color:#999;'>نظام بهجة برو - جميع الحقوق محفوظة لـ م. أيمن</p>
        </div>"""
        self.render("تواصل", content, uid, "/contact")

    def page_settings(self, uid):
        conn = sqlite3.connect(DB_NAME); u = conn.execute("SELECT email, store_name, user_real_name FROM users WHERE id=?", (uid,)).fetchone()
        bks = "".join([f"<tr><td>{f}</td><td><a href='/restore?f={f}' class='btn' style='background:var(--green); color:white; font-size:11px;'>استعادة</a></td></tr>" for f in os.listdir(BK_DIR)])
        c = f"""<h4>⚙️ إعدادات الحساب</h4><form action='/update_profile' method='POST'><div class='grid'><input name='un' value='{u[2]}'><input name='e' value='{u[0]}'><input name='s' value='{u[1]}'><input name='p' type='password' placeholder='تغيير كلمة السر'></div><button class='btn btn-p'>تحديث الملف</button></form><hr>
        <h4>💾 النسخ الاحتياطي والاستعادة</h4><a href='/do_backup' class='btn btn-p' style='background:#444;'>إنشاء نسخة احتياطية جديدة</a><table><thead><tr><th>تاريخ النسخة</th><th>الإجراء</th></tr></thead>{bks}</table>"""
        self.render("الإعدادات", c, uid, "/settings")

    def page_new_tx(self, uid):
        conn = sqlite3.connect(DB_NAME); cs = conn.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
        currs = conn.execute("SELECT c_name FROM currencies WHERE owner_id=?", (uid,)).fetchall()
        c_opts = "".join([f"<option value='{r[0]}'>{r[1]}</option>" for r in cs])
        cr_opts = "".join([f"<option>{r[0]}</option>" for r in currs])
        c = f"<h3>📥 تسجيل حركة مالية</h3><form action='/save_tx' method='POST'><select name='cid' required><option value=''>-- اختر العميل --</option>{c_opts}</select><div class='grid'><div><input name='amt' type='number' step='any' placeholder='المبلغ' required></div><div><select name='curr'>{cr_opts}</select></div></div><select name='type'><option>له (إيداع)</option><option>عليه (سحب)</option></select><textarea name='note' placeholder='البيان (مثلاً: سداد فاتورة رقم...)' rows='3'></textarea><button class='btn btn-p'>حفظ العملية</button></form>"
        self.render("حركة", c, uid, "/new_tx")

    def page_reports(self, uid):
        conn = sqlite3.connect(DB_NAME); cs = conn.execute("SELECT id, fullname FROM customers WHERE owner_id=?", (uid,)).fetchall()
        rows = ""
        for r in cs:
            bals = conn.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) FROM ledger WHERE customer_id=? GROUP BY val_currency", (r[0],)).fetchall()
            b_txt = " | ".join([f"<span class='{'bal-pos' if b[1]>=0 else 'bal-neg'}'>{b[0]}: {b[1]:,.2f}</span>" for b in bals]) or "0.00"
            rows += f"<tr><td>{r[1]}</td><td>{b_txt}</td><td><a href='/statement?id={r[0]}' class='btn' style='background:var(--p); color:white; font-size:11px;'>تفصيلي</a></td></tr>"
        self.render("التقارير", "<h3>📊 ميزان المراجعة</h3><table><thead><tr><th>العميل</th><th>الرصيد التراكمي</th><th>الإجراء</th></tr></thead>" + rows + "</table>", uid, "/reports")

    def ui_login(self): self.render("دخول", "<h3>🔐 تسجيل الدخول</h3><form action='/do_login' method='POST'><input name='e' placeholder='البريد' required><input name='p' type='password' placeholder='كلمة السر' required><button class='btn btn-p'>دخول</button></form><p align='center'><a href='/register'>إنشاء حساب جديد</a></p>")
    def ui_register(self): self.render("تسجيل", "<h3>📝 مستخدم جديد</h3><form action='/do_reg' method='POST'><input name='un' placeholder='الاسم الكامل' required><input name='e' placeholder='البريد' required><input name='p' placeholder='كلمة السر' required><input name='s' placeholder='اسم المحل' required><button class='btn btn-p'>تأكيد وبدء</button></form>")
    def redirect(self, p): self.send_response(303); self.send_header('Location', p); self.end_headers()
    def action_backup(self): shutil.copy2(DB_NAME, os.path.join(BK_DIR, f"bk_{datetime.now().strftime('%Y%m%d_%H%M')}.db"))
    def action_restore(self, f): shutil.copy2(os.path.join(BK_DIR, f), DB_NAME)

if __name__ == "__main__":
    PORT = 5000
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), BahjatProV26) as httpd:
        print(f"✅ م. أيمن: نسخة النخبة V26 برو جاهزة الآن على المنفذ {PORT}"); httpd.serve_forever()
