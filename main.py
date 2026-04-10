from flask import Flask, request, make_response, redirect, render_template_string
from datetime import datetime

app = Flask(__name__)

# --- بيانات ثابتة لضمان الدخول (بما أن السحاب يمنع الكتابة) ---
ADMIN_EMAIL = "admin@bahjat.com"
ADMIN_PASS = "123456"

# مخازن بيانات مؤقتة في الذاكرة (للتجربة الفورية)
DATA = {
    "customers": [],
    "ledger": []
}

# --- التصميم الفاخر (بصمة م. أيمن) ---
CSS = """
<style>
    :root { --p: #0d47a1; --s: #1976d2; --bg: #f8fafc; --w: #ffffff; }
    body { font-family: 'Segoe UI', Tahoma; background: var(--bg); direction: rtl; margin: 0; text-align: right; }
    .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 20px; text-align: center; }
    .nav { display: flex; justify-content: center; background: var(--w); padding: 10px; gap: 8px; border-bottom: 2px solid var(--p); overflow-x: auto; }
    .nav a { text-decoration: none; color: var(--p); font-weight: bold; padding: 8px 15px; border-radius: 20px; border: 1px solid var(--p); font-size: 12px; white-space: nowrap; }
    .nav a.active { background: var(--p); color: white; }
    .card { background: var(--w); padding: 25px; margin: 20px auto; max-width: 600px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    .btn { padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; display: block; text-align: center; text-decoration: none; border: 1px solid var(--p); }
    .btn-p { background: var(--p); color: white; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 10px; border-bottom: 1px solid #eee; text-align: center; }
    input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
</style>
"""

def render_ui(title, content, logged_in=False, active=""):
    nav = ""
    if logged_in:
        links = [('/', '👥 العملاء'), ('/new_tx', '📥 حركة'), ('/reports', '📊 تقارير'), ('/contact', '📞 تواصل')]
        nav = "<div class='nav'>" + "".join([f'<a href="{p}" class="{"active" if active==p else ""}">{n}</a>' for p, n in links]) + "<a href='/logout' style='color:red'>🚪 خروج</a></div>"
    return render_template_string(f"<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title>{CSS}</head><body><div class='header'><h2>بهجة برو V26</h2></div>{nav}<div class='card'>{content}</div></body></html>")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['e'] == ADMIN_EMAIL and request.form['p'] == ADMIN_PASS:
            resp = make_response(redirect('/'))
            resp.set_cookie('auth', 'true')
            return resp
        return "بيانات خطأ!"
    return render_ui("دخول", f"<h3>🔐 دخول</h3><p>استخدم: {ADMIN_EMAIL} | {ADMIN_PASS}</p><form method='POST'><input name='e' placeholder='البريد'><input name='p' type='password' placeholder='كلمة السر'><button class='btn btn-p'>دخول</button></form>")

@app.route('/')
def page_customers():
    if request.cookies.get('auth') != 'true': return redirect('/login')
    f = "<h3>👥 العملاء</h3><form action='/add_cust' method='POST'><input name='n' placeholder='اسم العميل' required><button class='btn btn-p'>إضافة</button></form><table>"
    for i, c in enumerate(DATA['customers']):
        f += f"<tr><td>{c}</td><td><a href='/new_tx?id={i}'>إضافة حركة</a></td></tr>"
    return render_ui("العملاء", f + "</table>", True, "/")

@app.route('/add_cust', methods=['POST'])
def add_cust():
    DATA['customers'].append(request.form['n'])
    return redirect('/')

@app.route('/new_tx', methods=['GET', 'POST'])
def page_new_tx():
    if request.cookies.get('auth') != 'true': return redirect('/login')
    if request.method == 'POST':
        DATA['ledger'].append({
            "name": DATA['customers'][int(request.form['cid'])],
            "amt": float(request.form['amt']),
            "type": request.form['type'],
            "date": datetime.now().strftime("%H:%M")
        })
        return redirect('/reports')
    opts = "".join([f"<option value='{i}'>{n}</option>" for i, n in enumerate(DATA['customers'])])
    return render_ui("حركة", f"<h3>📥 حركة مالية</h3><form method='POST'><select name='cid'>{opts}</select><input name='amt' type='number' placeholder='المبلغ'><select name='type'><option>له</option><option>عليه</option></select><button class='btn btn-p'>حفظ</button></form>", True, "/new_tx")

@app.route('/reports')
def page_reports():
    if request.cookies.get('auth') != 'true': return redirect('/login')
    rows = "".join([f"<tr><td>{tx['name']}</td><td>{tx['amt']}</td><td>{tx['type']}</td></tr>" for tx in DATA['ledger']])
    return render_ui("التقارير", f"<h3>📊 التقارير</h3><table><tr><th>الاسم</th><th>المبلغ</th><th>النوع</th></tr>{rows}</table>", True, "/reports")

@app.route('/contact')
def page_contact():
    return render_ui("تواصل", "<h3>م. أيمن الحميري</h3><p>واتساب: 0556868717</p>", True, "/contact")

@app.route('/logout')
def logout():
    resp = make_response(redirect('/login')); resp.set_cookie('auth', '', expires=0); return resp

if __name__ == "__main__":
    app.run()
