# ==========================================================
# نظام إدارة "بهجة طيبة للمواد الغذائية"
# تطوير: أيمن
# النسخة السحابية المحدثة للعمل على GitHub & Render
# ==========================================================

import http.server
import socketserver
import sqlite3
import urllib.parse
import os
import cgi
import shutil
from datetime import datetime

# ----------------------------------------------------------
# 1. إعدادات البيئة وقاعدة البيانات (معدلة للسحابة)
# ----------------------------------------------------------
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# تأكد أن قاعدة البيانات في مسار صحيح دائم
DATABASE_NAME = os.path.join(BASE_PATH, "bahjat_pro_v9.db")
BACKUP_FOLDER = os.path.join(BASE_PATH, "system_backups")

def setup_database_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        fullname TEXT UNIQUE NOT NULL, 
        mobile TEXT,
        work_address TEXT,
        vat_number TEXT,
        general_notes TEXT
    )""")
    
    cur.execute("CREATE TABLE IF NOT EXISTS currencies (c_name TEXT PRIMARY KEY)")
    for currency in ['ريال سعودي', 'ريال يمني', 'دولار']:
        cur.execute("INSERT OR IGNORE INTO currencies VALUES (?)", (currency,))
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        customer_id INTEGER, 
        val_amount REAL NOT NULL, 
        val_currency TEXT NOT NULL, 
        val_type TEXT NOT NULL, 
        val_notes TEXT, 
        entry_date TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )""")
    
    cur.execute("CREATE TABLE IF NOT EXISTS store_info (property TEXT PRIMARY KEY, value TEXT)")
    default_info = [
        ('name', 'بهجة طيبة للمواد الغذائية'),
        ('loc', 'القصيم - رياض الخبراء')
    ]
    for key, val in default_info:
        cur.execute("INSERT OR IGNORE INTO store_info VALUES (?, ?)", (key, val))
    
    conn.commit()
    conn.close()
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

setup_database_tables()

# ----------------------------------------------------------
# 2. الواجهة الرسومية (CSS) - كما هي بدون تغيير
# ----------------------------------------------------------
CSS_STYLES = """
<style>
    :root { 
        --primary-blue: #0d47a1; 
        --accent-blue: #1976d2; 
        --bg-light: #f0f2f5; 
        --white: #ffffff; 
        --danger: #d32f2f;
        --success: #388e3c;
    }
    * { box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg-light); margin: 0; direction: rtl; }
    .header-bar { background: var(--primary-blue); color: white; padding: 25px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    .nav-menu { display: flex; justify-content: center; background: white; padding: 15px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.1); gap: 10px; flex-wrap: wrap; }
    .nav-menu a { text-decoration: none; color: var(--primary-blue); padding: 12px 20px; border: 2px solid #ddd; border-radius: 8px; font-weight: bold; }
    .nav-menu a:hover, .nav-menu a.active { background: var(--primary-blue); color: white; }
    .main-wrapper { max-width: 1200px; margin: 30px auto; padding: 0 15px; }
    .content-card { background: var(--white); padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 30px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 15px; border-bottom: 1px solid #eee; text-align: right; }
    th { background: #f8f9fa; }
    .input-field { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; }
    .btn-action { padding: 12px 25px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; text-align: center; }
    .btn-save { background: var(--primary-blue); color: white; width: 100%; }
    .btn-del { background: #ffebee; color: #c62828; padding: 5px 10px; font-size: 12px; }
    .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
    .badge { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
    .bg-pos { background: #e8f5e9; color: #2e7d32; }
    .bg-neg { background: #ffebee; color: #c62828; }
    @media print { .no-print { display: none !important; } }
</style>
"""

# ----------------------------------------------------------
# 3. الدوال المساعدة
# ----------------------------------------------------------
def get_db(): return sqlite3.connect(DATABASE_NAME)

def get_all_balances(customer_id):
    c = get_db(); cur = c.cursor()
    cur.execute("SELECT val_currency, SUM(CASE WHEN val_type LIKE 'له%' THEN val_amount ELSE -val_amount END) FROM ledger WHERE customer_id = ? GROUP BY val_currency", (customer_id,))
    data = cur.fetchall(); c.close()
    return data

def build_layout(title, content, active_path="", is_printable=False):
    c = get_db(); cur = c.cursor(); cur.execute("SELECT property, value FROM store_info"); info = dict(cur.fetchall()); c.close()
    links = [('/', 'العملاء'), ('/page_new_entry', 'حركة جديدة'), ('/page_exchange', 'المصارفة الذكية'), ('/page_reports', 'مركز التقارير'), ('/page_system', 'إعدادات النظام')]
    nav_html = "".join([f'<a href="{p}" class="{"active" if active_path == p else ""}">{n}</a>' for p, n in links])
    p_btn = f'<button onclick="window.print()" class="btn-action no-print" style="background:#555; color:white; margin-bottom:15px;">🖨️ طباعة {title}</button>' if is_printable else ''
    return f"<!DOCTYPE html><html lang='ar'><head><meta charset='UTF-8'><title>{title}</title>{CSS_STYLES}</head><body><div class='header-bar no-print'><h1>{info.get('name')}</h1><p>{info.get('loc')}</p></div><div class='nav-menu no-print'>{nav_html}</div><div class='main-wrapper'>{p_btn}{content}</div></body></html>"

# [بقية الدوال: ui_system_settings, ui_exchange_page, ui_report_center, إلخ... تبقى كما هي تماماً]

# --- ملاحظة: سأختصر العرض هنا لضمان المساحة ولكن الكود عند الرفع يجب أن يحتوي كل الدوال الأصلية التي أرسلتها أنت ---

def ui_system_settings():
    c = get_db(); cur = c.cursor()
    cur.execute("SELECT property, value FROM store_info"); info = dict(cur.fetchall())
    cur.execute("SELECT c_name FROM currencies"); currs = cur.fetchall()
    c.close()
    curr_list = "".join([f"<li>{r[0]} <a href='/do_del_curr?name={r[0]}' class='btn-action btn-del' style='margin-right:10px;'>حذف</a></li>" for r in currs])
    bks = os.listdir(BACKUP_FOLDER) if os.path.exists(BACKUP_FOLDER) else []
    bk_rows = "".join([f"<tr><td>{b}</td><td><a href='/do_restore?file={b}' style='color:green; font-weight:bold;'>استعادة</a></td></tr>" for b in bks])
    content = f"""<div class="grid-container"><div class="content-card"><h3>⚙️ إعدادات المؤسسة</h3><form action="/do_update_store" method="POST"><label>اسم المنشأة:</label><input name="s_name" value="{info.get('name')}" class="input-field"><label>العنوان / الموقع:</label><input name="s_loc" value="{info.get('loc')}" class="input-field"><button class="btn-action btn-save">تحديث البيانات</button></form></div><div class="content-card"><h3>💰 إدارة العملات</h3><form action="/do_add_curr" method="POST" style="display:flex; gap:5px;"><input name="cname" placeholder="اسم عملة جديد" class="input-field" required><button class="btn-action btn-save" style="width:auto;">إضافة</button></form><ul style="margin-top:15px; line-height:2;">{curr_list}</ul></div></div><div class="content-card"><h3>📂 النسخ الاحتياطي والأرشفة</h3><div style="margin-bottom:20px;"><a href="/do_backup" class="btn-action btn-save" style="background:#455a64; text-decoration:none;">إنشاء نسخة احتياطية الآن (Backup)</a></div><table><thead><tr><th>اسم ملف النسخة</th><th>الإجراء</th></tr></thead><tbody>{bk_rows if bk_rows else '<tr><td colspan="2" align="center">لا توجد نسخ محفظوظة</td></tr>'}</tbody></table></div>"""
    return build_layout("إعدادات النظام", content, "/page_system")

def ui_exchange_page(q):
    c = get_db(); ps = c.execute("SELECT id, fullname FROM customers").fetchall(); c.close()
    p_opts = "".join([f"<option value='{p[0]}'>{p[1]}</option>" for p in ps])
    res_html = ""
    if q.get('cid'):
        cid = q['cid'][0]; bals = get_all_balances(cid); total = 0
        r_sar = float(q.get('sar_r', [1])[0]); r_yer = float(q.get('yer_r', [0.006])[0]); r_usd = float(q.get('usd_r', [3.75])[0])
        for b_cur, b_val in bals:
            rate = r_sar if 'سعودي' in b_cur else (r_yer if 'يمني' in b_cur else r_usd)
            total += (b_val * rate)
        res_html = f"<div class='content-card' style='background:#fffde7; border:2px dashed #fbc02d;'><h3>صافي الحساب بالريال السعودي: {total:,.2f}</h3></div>"
    content = f"""<div class="content-card no-print"><h3>🔄 نظام المصارفة الذكي</h3><form action="/page_exchange" method="GET"><label>اختر العميل لتصفية حسابه:</label><select name="cid" class="input-field">{p_opts}</select><div class="grid-container" style="margin-top:15px;"><div><label>سعر الريال السعودي</label><input name="sar_r" value="1" class="input-field" step="any"></div><div><label>سعر الريال اليمني</label><input name="yer_r" value="0.006" class="input-field" step="any"></div><div><label>سعر الدولار</label><input name="usd_r" value="3.75" class="input-field" step="any"></div></div><button class="btn-action btn-save" style="background:#fbc02d; color:#000; margin-top:10px;">احسب التصفية الآن</button></form></div>{res_html}"""
    return build_layout("المصارفة", content, "/page_exchange")

def ui_report_center():
    conn = get_db(); cursor = conn.cursor(); cursor.execute("SELECT id, fullname FROM customers ORDER BY fullname ASC")
    customers = cursor.fetchall(); conn.close()
    options = "".join([f'<option value="{c[0]}">{c[1]}</option>' for c in customers])
    content = f"""<div class='content-card no-print'><h3>📊 مركز التقارير</h3><div class='grid-container'><div style='border:2px solid var(--primary-blue); padding:20px; border-radius:12px; text-align:center;'><h4>تقرير الأرصدة الشامل</h4><a href='/report_all_balances' class='btn-action btn-save'>فتح التقرير</a></div><div style='border:2px solid var(--accent-blue); padding:20px; border-radius:12px; text-align:center;'><h4>كشف حساب تفصيلي</h4><form action='/report_customer_statement' method='GET'><select name='id' class='input-field'>{options}</select><button class='btn-action btn-save' style='background:var(--accent-blue);'>عرض الكشف</button></form></div></div></div>"""
    return build_layout("مركز التقارير", content, "/page_reports")

def ui_report_all_balances():
    c = get_db(); cur = c.cursor(); cur.execute("SELECT id, fullname, mobile FROM customers ORDER BY fullname ASC"); all_cust = cur.fetchall()
    rows = ""
    for cid, name, phone in all_cust:
        bals = get_all_balances(cid)
        b_summary = "".join([f"<div style='color:{'var(--success)' if b[1]>=0 else 'var(--danger)'}; font-weight:bold;'>{b[0]}: {b[1]:,.2f}</div>" for b in bals]) if bals else "0.00"
        rows += f"<tr><td>{name}</td><td>{phone or '-'}</td><td>{b_summary}</td></tr>"
    c.close()
    return build_layout("تقرير الأرصدة الشامل", f"<div class='content-card'><h2>تقرير الأرصدة الشامل</h2><table><thead><tr><th>الاسم</th><th>الجوال</th><th>الأرصدة</th></tr></thead>{rows}</table></div>", is_printable=True)

def ui_report_customer_statement(cid):
    c = get_db(); cur = c.cursor(); cur.execute("SELECT fullname, mobile, vat_number FROM customers WHERE id=?", (cid,)); info = cur.fetchone()
    cur.execute("SELECT entry_date, val_type, val_amount, val_currency, val_notes FROM ledger WHERE customer_id=? ORDER BY id ASC", (cid,)); txs = cur.fetchall()
    bals = get_all_balances(cid); c.close()
    b_html = "".join([f"<div style='background:#f8f9fa; padding:10px; border-radius:8px; text-align:center;'><b>{b[0]}</b><br><span style='color:{'green' if b[1]>=0 else 'red'}'>{b[1]:,.2f}</span></div>" for b in bals])
    rows = "".join([f"<tr><td>{t[0]}</td><td>{t[1]}</td><td>{t[2]:,.2f}</td><td>{t[3]}</td><td>{t[4] or '-'}</td></tr>" for t in txs])
    content = f"<div class='content-card'><h2>كشف حساب: {info[0]}</h2><p>الجوال: {info[1] or '-'} | ضريبي: {info[2] or '-'}</p><hr><table><thead><tr><th>التاريخ</th><th>النوع</th><th>المبلغ</th><th>العملة</th><th>البيان</th></tr></thead>{rows}</table><div class='grid-container' style='margin-top:20px;'>{b_html}</div></div>"
    return build_layout(f"كشف {info[0]}", content, is_printable=True)

# ----------------------------------------------------------
# 6. معالج السيرفر (Server)
# ----------------------------------------------------------
class FinalBahjatHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(parsed.query)
        if parsed.path == '/do_backup':
            shutil.copy2(DATABASE_NAME, os.path.join(BACKUP_FOLDER, f"bk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")); self.redirect("/page_system")
        elif parsed.path == '/do_restore':
            shutil.copy2(os.path.join(BACKUP_FOLDER, q['file'][0]), DATABASE_NAME); self.redirect("/page_system")
        elif parsed.path == '/do_delete_customer':
            c = get_db(); c.execute("DELETE FROM customers WHERE id=?", (q['id'][0],)); c.execute("DELETE FROM ledger WHERE customer_id=?", (q['id'][0],)); c.commit(); self.redirect("/")
        elif parsed.path == '/do_del_curr':
            c = get_db(); c.execute("DELETE FROM currencies WHERE c_name=?", (q['name'][0],)); c.commit(); self.redirect("/page_system")
        
        self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
        if parsed.path == '/':
            c = get_db(); rows = c.execute("SELECT id, fullname, mobile FROM customers ORDER BY id DESC").fetchall(); c.close()
            t_rows = "".join([f"<tr><td><b><a href='/report_customer_statement?id={r[0]}'>{r[1]}</a></b></td><td>{r[2] or '-'}</td><td>{''.join([f'<span class=\"badge {'bg-pos' if b[1]>=0 else 'bg-neg'}\">{b[0]}: {b[1]:,.2f}</span>' for b in get_all_balances(r[0])])}</td><td class='no-print'><a href='/ui_edit_customer?id={r[0]}' class='btn-action btn-edit' style='background:#e3f2fd; color:#1565c0;'>تعديل</a> <a href='/do_delete_customer?id={r[0]}' class='btn-action btn-del' onclick='return confirm(\"حذف؟\")'>حذف</a></td></tr>" for r in rows])
            content = f"<div class='content-card no-print'><h3>إضافة عميل</h3><form action='/do_save_customer' method='POST'><div class='grid-container'><input name='fullname' placeholder='الاسم' class='input-field' required><input name='mobile' placeholder='الجوال' class='input-field'><input name='work_address' placeholder='العنوان' class='input-field'><input name='vat_number' placeholder='الرقم الضريبي' class='input-field'></div><button class='btn-action btn-save'>حفظ</button></form></div><div class='content-card'><table><thead><tr><th>الاسم</th><th>الجوال</th><th>الأرصدة</th><th class='no-print'>التحكم</th></tr></thead>{t_rows}</table></div>"
            self.wfile.write(build_layout("العملاء", content, "/").encode())
        elif parsed.path == '/page_new_entry':
            c = get_db(); ps = c.execute("SELECT id, fullname FROM customers").fetchall(); currs = [r[0] for r in c.execute("SELECT c_name FROM currencies").fetchall()]; c.close()
            p_o = "".join([f"<option value='{p[0]}'>{p[1]}</option>" for p in ps]); c_o = "".join([f"<option>{cr}</option>" for cr in currs])
            content = f"<div class='content-card'><h3>تسجيل حركة</h3><form action='/do_save_tx' method='POST'><select name='cid' class='input-field'>{p_o}</select><div class='grid-container'><input name='amt' type='number' step='any' class='input-field' placeholder='المبلغ'><select name='curr' class='input-field'>{c_o}</select><select name='type' class='input-field'><option>له (إيداع)</option><option>عليه (سحب)</option></select></div><textarea name='notes' class='input-field' placeholder='البيان'></textarea><button class='btn-action btn-save'>تأكيد</button></form></div>"
            self.wfile.write(build_layout("حركة جديدة", content, "/page_new_entry").encode())
        elif parsed.path == '/page_exchange': self.wfile.write(ui_exchange_page(q).encode())
        elif parsed.path == '/page_reports': self.wfile.write(ui_report_center().encode())
        elif parsed.path == '/report_all_balances': self.wfile.write(ui_report_all_balances().encode())
        elif parsed.path == '/report_customer_statement': self.wfile.write(ui_report_customer_statement(q['id'][0]).encode())
        elif parsed.path == '/page_system': self.wfile.write(ui_system_settings().encode())
        elif parsed.path == '/ui_edit_customer':
            c = get_db(); p = c.execute("SELECT * FROM customers WHERE id=?", (q['id'][0],)).fetchone(); c.close()
            self.wfile.write(build_layout("تعديل", f"<div class='content-card'><form action='/do_update_customer' method='POST'><input type='hidden' name='id' value='{p[0]}'><div class='grid-container'><input name='fullname' value='{p[1]}' class='input-field'><input name='mobile' value='{p[2] or ''}' class='input-field'><input name='work_address' value='{p[3] or ''}' class='input-field'><input name='vat_number' value='{p[4] or ''}' class='input-field'></div><button class='btn-action btn-save'>تحديث</button></form></div>").encode())

    def do_POST(self):
        f = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
        c = get_db(); cur = c.cursor()
        if self.path == '/do_save_customer':
            cur.execute("INSERT INTO customers (fullname, mobile, work_address, vat_number) VALUES (?,?,?,?)", (f.getvalue('fullname'), f.getvalue('mobile'), f.getvalue('work_address'), f.getvalue('vat_number')))
        elif self.path == '/do_update_customer':
            cur.execute("UPDATE customers SET fullname=?, mobile=?, work_address=?, vat_number=? WHERE id=?", (f.getvalue('fullname'), f.getvalue('mobile'), f.getvalue('work_address'), f.getvalue('vat_number'), f.getvalue('id')))
        elif self.path == '/do_save_tx':
            cur.execute("INSERT INTO ledger (customer_id, val_amount, val_currency, val_type, val_notes, entry_date) VALUES (?,?,?,?,?,?)", (f.getvalue('cid'), float(f.getvalue('amt')), f.getvalue('curr'), f.getvalue('type'), f.getvalue('notes'), datetime.now().strftime("%Y-%m-%d %H:%M")))
        elif self.path == '/do_add_curr':
            cur.execute("INSERT OR IGNORE INTO currencies VALUES (?)", (f.getvalue('cname'),))
        elif self.path == '/do_update_store':
            cur.execute("UPDATE store_info SET value=? WHERE property='name'", (f.getvalue('s_name'),))
            cur.execute("UPDATE store_info SET value=? WHERE property='loc'", (f.getvalue('s_loc'),))
        c.commit(); c.close(); self.redirect("/page_system" if 'do_update_store' in self.path or 'do_add_curr' in self.path else "/")

    def redirect(self, p): self.send_response(303); self.send_header('Location', p); self.end_headers()

# --- جزء التشغيل المطور للسحابة ---
if __name__ == '__main__':
    # الحصول على المنفذ تلقائياً من الاستضافة أو استخدام 8080 كافتراضي
    PORT = int(os.environ.get("PORT", 8080))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), FinalBahjatHandler) as httpd:
        print(f"نظام بهجة طيبة V9 يعمل الآن عالمياً على المنفذ: {PORT}")
        httpd.serve_forever()
