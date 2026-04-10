from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# مخازن بيانات في الذاكرة لضمان السرعة والعمل على السحاب
DATABASE = {
    "customers": [],
    "ledger": []
}

CSS = """
<style>
    :root { --p: #0d47a1; --s: #1976d2; --bg: #f1f5f9; --w: #ffffff; }
    body { font-family: 'Segoe UI', Tahoma; background: var(--bg); direction: rtl; margin: 0; text-align: right; }
    .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 15px; text-align: center; }
    .nav { display: flex; justify-content: center; background: var(--w); padding: 10px; gap: 10px; border-bottom: 2px solid var(--p); }
    .nav a { text-decoration: none; color: var(--p); font-weight: bold; padding: 8px 15px; border-radius: 20px; border: 1px solid var(--p); font-size: 13px; }
    .card { background: var(--w); padding: 20px; margin: 15px auto; max-width: 700px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .btn { padding: 10px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; display: block; text-align: center; text-decoration: none; background: var(--p); color: white; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; background: white; }
    th, td { padding: 12px; border: 1px solid #ddd; text-align: center; }
    th { background: #f8fafc; }
    input, select, textarea { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
    .section-title { border-right: 4px solid var(--p); padding-right: 10px; margin-top: 25px; color: var(--p); }
</style>
"""

@app.route('/')
def dashboard():
    # صفحة العملاء
    cust_html = "".join([f"<tr><td>{c}</td><td><a href='/add_tx_page?id={i}'>إضافة حركة</a></td></tr>" for i, c in enumerate(DATABASE['customers'])])
    
    # صفحة التقارير
    report_html = "".join([f"<tr><td>{tx['name']}</td><td>{tx['amt']}</td><td>{tx['type']}</td><td>{tx['date']}</td></tr>" for tx in DATABASE['ledger']])

    content = f"""
    <div class='card'>
        <h3 class='section-title'>👤 صفحة العملاء</h3>
        <form action='/add_cust' method='POST'>
            <input name='n' placeholder='اسم العميل الجديد' required>
            <button class='btn'>➕ إضافة عميل</button>
        </form>
        <table>
            <thead><tr><th>اسم العميل</th><th>الإجراء</th></tr></thead>
            <tbody>{cust_html or '<tr><td colspan="2">لا يوجد عملاء بعد</td></tr>'}</tbody>
        </table>
    </div>

    <div class='card'>
        <h3 class='section-title'>📊 صفحة التقارير (الحركات)</h3>
        <table>
            <thead><tr><th>العميل</th><th>المبلغ</th><th>النوع</th><th>الوقت</th></tr></thead>
            <tbody>{report_html or '<tr><td colspan="4">لا توجد حركات مسجلة</td></tr>'}</tbody>
        </table>
    </div>

    <div class='card'>
        <h3 class='section-title'>📞 صفحة تواصل</h3>
        <p>المطور: م. أيمن الحميري</p>
        <p>واتساب: 0556868717</p>
    </div>
    """
    return render_template_string(f"<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>بهجة برو</title>{CSS}</head><body><div class='header'><h2>بهجة برو V26.5 (نسخة التشغيل المباشر)</h2></div>{content}</body></html>")

@app.route('/add_cust', methods=['POST'])
def add_cust():
    DATABASE['customers'].append(request.form['n'])
    return redirect_home()

@app.route('/add_tx_page')
def add_tx_page():
    cid = request.args.get('id')
    name = DATABASE['customers'][int(cid)]
    form = f"""
    <div class='card'>
        <h3>📥 إضافة حركة لـ: {name}</h3>
        <form action='/save_tx' method='POST'>
            <input type='hidden' name='cid' value='{cid}'>
            <input name='amt' type='number' placeholder='المبلغ' required>
            <select name='type'>
                <option>له (إيداع)</option>
                <option>عليه (سحب)</option>
            </select>
            <button class='btn'>حفظ الحركة</button>
        </form>
        <br><a href='/' style='color:var(--p)'>⬅️ عودة للرئيسية</a>
    </div>
    """
    return render_template_string(f"<html><head><meta charset='UTF-8'>{CSS}</head><body>{form}</body></html>")

@app.route('/save_tx', methods=['POST'])
def save_tx():
    cid = int(request.form['cid'])
    DATABASE['ledger'].append({
        "name": DATABASE['customers'][cid],
        "amt": request.form['amt'],
        "type": request.form['type'],
        "date": datetime.now().strftime("%H:%M")
    })
    return redirect_home()

def redirect_home():
    return "<script>window.location.href='/';</script>"

if __name__ == "__main__":
    app.run()
