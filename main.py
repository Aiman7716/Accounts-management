from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# بيانات مخزنة في الذاكرة (سريعة جداً)
DATA = {"customers": [], "ledger": []}

CSS = """
<style>
    :root { --p: #0d47a1; --bg: #f8fafc; --w: #ffffff; }
    body { font-family: 'Segoe UI', Tahoma; background: var(--bg); direction: rtl; margin: 0; padding: 10px; }
    .header { background: #0d47a1; color: white; padding: 15px; text-align: center; border-radius: 10px; margin-bottom: 15px; }
    .card { background: var(--w); padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 15px; border: 1px solid #eee; }
    .btn { background: #0d47a1; color: white; padding: 12px; border: none; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold; margin-top: 5px; text-decoration: none; display: block; text-align: center; }
    input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 10px; border: 1px solid #eee; text-align: center; font-size: 14px; }
    .nav-tabs { display: flex; gap: 5px; margin-bottom: 15px; overflow-x: auto; }
    .nav-tabs a { flex: 1; text-align: center; background: #e2e8f0; padding: 10px; border-radius: 5px; text-decoration: none; color: #475569; font-size: 12px; font-weight: bold; min-width: 80px; }
    .nav-tabs a.active { background: #0d47a1; color: white; }
</style>
"""

@app.route('/')
def main():
    page = request.args.get('p', 'cust') # الصفحة الحالية
    
    # 1. صفحة العملاء
    if page == 'cust':
        content = "<h3>👥 العملاء</h3><form action='/add_c'><input name='n' placeholder='اسم العميل' required><button class='btn'>➕ إضافة</button></form>"
        rows = "".join([f"<tr><td>{c}</td><td><a href='/?p=tx&id={i}'>➕ حركة</a></td></tr>" for i, c in enumerate(DATA['customers'])])
        content += f"<table><tr><th>الاسم</th><th>إجراء</th></tr>{rows or '<tr><td colspan=2>لا يوجد عملاء</td></tr>'}</table>"
    
    # 2. صفحة إضافة حركة
    elif page == 'tx':
        cid = request.args.get('id')
        name = DATA['customers'][int(cid)] if cid else "غير معروف"
        content = f"<h3>📥 حركة لـ: {name}</h3><form action='/add_l'><input type='hidden' name='cid' value='{cid}'><input name='a' type='number' placeholder='المبلغ' required><select name='t'><option>له</option><option>عليه</option></select><button class='btn'>حفظ الحركة</button></form>"
    
    # 3. صفحة التقارير
    elif page == 'rep':
        rows = "".join([f"<tr><td>{l['n']}</td><td>{l['a']}</td><td>{l['t']}</td><td>{l['d']}</td></tr>" for l in DATA['ledger']])
        content = f"<h3>📊 التقارير</h3><table><tr><th>العميل</th><th>المبلغ</th><th>النوع</th><th>الوقت</th></tr>{rows or '<tr><td colspan=4>لا توجد حركات</td></tr>'}</table>"
    
    # 4. صفحة التواصل
    else:
        content = "<h3>📞 تواصل</h3><p>م. أيمن الحميري</p><p>واتساب: 0556868717</p>"

    # التنقل السفلي
    nav = f"""<div class='nav-tabs'>
        <a href='/?p=cust' class='{"active" if page=="cust" else ""}'>👥 العملاء</a>
        <a href='/?p=rep' class='{"active" if page=="rep" else ""}'>📊 تقارير</a>
        <a href='/?p=con' class='{"active" if page=="con" else ""}'>📞 تواصل</a>
    </div>"""

    return render_template_string(f"<html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>{CSS}</head><body><div class='header'><h2>بهجة برو V26.6</h2></div>{nav}<div class='card'>{content}</div></body></html>")

@app.route('/add_c')
def add_c():
    DATA['customers'].append(request.args.get('n'))
    return "<script>window.location.href='/?p=cust';</script>"

@app.route('/add_l')
def add_l():
    cid = int(request.args.get('cid'))
    DATA['ledger'].append({
        "n": DATA['customers'][cid],
        "a": request.args.get('a'),
        "t": request.args.get('t'),
        "d": datetime.now().strftime("%H:%M")
    })
    return "<script>window.location.href='/?p=rep';</script>"

if __name__ == "__main__":
    app.run()
