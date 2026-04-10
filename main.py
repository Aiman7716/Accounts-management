from flask import Flask, render_template_string, request

app = Flask(__name__)

# تصميم م. أيمن الحميري الفاخر مدمج في صفحة واحدة ذكية
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بهجة برو V27</title>
    <style>
        :root { --p: #0d47a1; --s: #1976d2; --bg: #f0f2f5; --w: #ffffff; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); margin: 0; padding-bottom: 70px; }
        .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 20px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
        .container { padding: 15px; max-width: 600px; margin: auto; }
        .card { background: var(--w); padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 15px; display: none; }
        .card.active { display: block; animation: fadeIn 0.4s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .btn { background: var(--p); color: white; border: none; padding: 12px; border-radius: 10px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 10px; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background: white; border-radius: 10px; overflow: hidden; }
        th, td { padding: 12px; border: 1px solid #eee; text-align: center; }
        th { background: #f8f9fa; color: var(--p); }
        .nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 1000; }
        .nav-item { flex: 1; text-align: center; padding: 12px; color: #667; text-decoration: none; font-size: 12px; cursor: pointer; }
        .nav-item.active { color: var(--p); border-top: 3px solid var(--p); font-weight: bold; }
    </style>
</head>
<body>

<div class="header">
    <h2>بهجة برو V27</h2>
    <small>تطوير م. أيمن الحميري</small>
</div>

<div class="container">
    <div id="cust" class="card active">
        <h3>👥 إدارة العملاء</h3>
        <input type="text" id="custName" placeholder="اسم العميل الجديد">
        <button class="btn" onclick="addCustomer()">➕ إضافة عميل</button>
        <table id="custTable">
            <thead><tr><th>اسم العميل</th><th>إجراء</th></tr></thead>
            <tbody id="custBody"></tbody>
        </table>
    </div>

    <div id="tx" class="card">
        <h3>📥 تسجيل حركة مالية</h3>
        <select id="txCustSelect"></select>
        <input type="number" id="txAmount" placeholder="المبلغ">
        <select id="txType">
            <option value="له">له (إيداع)</option>
            <option value="عليه">عليه (سحب)</option>
        </select>
        <button class="btn" onclick="addTransaction()">✅ حفظ الحركة</button>
    </div>

    <div id="reports" class="card">
        <h3>📊 ميزان المراجعة</h3>
        <table>
            <thead><tr><th>العميل</th><th>الرصيد التراكمي</th></tr></thead>
            <tbody id="reportBody"></tbody>
        </table>
    </div>

    <div id="contact" class="card">
        <h3>📞 تواصل مع المطور</h3>
        <p><b>م. أيمن الحميري</b></p>
        <p>واتساب: 0556868717</p>
        <p>النسخة: V27 (النخبة المستقرة)</p>
    </div>
</div>

<nav class="nav">
    <div class="nav-item active" onclick="showPage('cust', this)">👥 العملاء</div>
    <div class="nav-item" onclick="showPage('tx', this)">📥 حركة</div>
    <div class="nav-item" onclick="showPage('reports', this)">📊 تقارير</div>
    <div class="nav-item" onclick="showPage('contact', this)">📞 تواصل</div>
</nav>

<script>
    let customers = JSON.parse(localStorage.getItem('customers')) || [];
    let ledger = JSON.parse(localStorage.getItem('ledger')) || [];

    function showPage(pageId, el) {
        document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
        document.getElementById(pageId).classList.add('active');
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
        refreshData();
    }

    function addCustomer() {
        let name = document.getElementById('custName').value;
        if(name) {
            customers.push(name);
            localStorage.setItem('customers', JSON.stringify(customers));
            document.getElementById('custName').value = '';
            refreshData();
            alert('تم إضافة العميل بنجاح');
        }
    }

    function addTransaction() {
        let cid = document.getElementById('txCustSelect').value;
        let amt = document.getElementById('txAmount').value;
        let type = document.getElementById('txType').value;
        if(cid !== "" && amt) {
            ledger.push({name: customers[cid], amount: parseFloat(amt), type: type});
            localStorage.setItem('ledger', JSON.stringify(ledger));
            alert('تم حفظ الحركة');
            showPage('reports', document.querySelectorAll('.nav-item')[2]);
        }
    }

    function refreshData() {
        // تحديث جدول العملاء
        let cBody = document.getElementById('custBody');
        let select = document.getElementById('txCustSelect');
        cBody.innerHTML = ''; select.innerHTML = '<option value="">-- اختر عميل --</option>';
        customers.forEach((c, i) => {
            cBody.innerHTML += `<tr><td>${c}</td><td><button onclick="showPage('tx', document.querySelectorAll('.nav-item')[1])" style="background:none;border:none;color:blue;cursor:pointer;">إضافة حركة</button></td></tr>`;
            select.innerHTML += `<option value="${i}">${c}</option>`;
        });

        // تحديث التقارير
        let rBody = document.getElementById('reportBody');
        rBody.innerHTML = '';
        let balances = {};
        customers.forEach(c => balances[c] = 0);
        ledger.forEach(l => {
            if(l.type === 'له') balances[l.name] += l.amount;
            else balances[l.name] -= l.amount;
        });
        for(let c in balances) {
            rBody.innerHTML += `<tr><td>${c}</td><td style="color:${balances[c] >= 0 ? 'green' : 'red'}">${balances[c].toFixed(2)}</td></tr>`;
        }
    }
    refreshData();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run()
