from flask import Flask, render_template_string

app = Flask(__name__)

# نسخة النخبة المستقرة V28 - تطوير م. أيمن الحميري
HTML_FINAL = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بهجة برو V28</title>
    <style>
        :root { --p: #0d47a1; --s: #1976d2; --bg: #f4f7f9; --w: #ffffff; --red: #d32f2f; --green: #388e3c; }
        body { font-family: 'Segoe UI', Tahoma; background: var(--bg); margin: 0; padding-bottom: 80px; }
        .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 15px; text-align: center; position: sticky; top: 0; z-index: 1000; }
        .container { padding: 15px; max-width: 800px; margin: auto; }
        .card { background: var(--w); padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; display: none; animation: fadeIn 0.3s; }
        .card.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .btn { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        .btn-p { background: var(--p); width: 100%; margin-top: 10px; }
        .btn-del { background: var(--red); font-size: 11px; padding: 5px 10px; }
        .btn-edit { background: orange; font-size: 11px; padding: 5px 10px; margin-left: 5px; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; font-size: 13px; }
        th, td { padding: 10px; border-bottom: 1px solid #eee; text-align: center; }
        th { background: #f8f9fa; color: var(--p); }
        .pos { color: var(--green); font-weight: bold; }
        .neg { color: var(--red); font-weight: bold; }
        .nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
        .nav-item { flex: 1; text-align: center; padding: 12px 5px; color: #667; cursor: pointer; font-size: 11px; }
        .nav-item.active { color: var(--p); border-top: 3px solid var(--p); background: #f0f4ff; }
        .total-row { background: #eee; font-weight: bold; font-size: 15px; }
    </style>
</head>
<body onload="checkLogin()">

<div id="loginPage" style="display:none;" class="container">
    <div class="card active" style="margin-top:50px;">
        <h2 style="text-align:center; color:var(--p);">🔐 تسجيل الدخول</h2>
        <input type="text" id="userInp" placeholder="اسم المستخدم أو البريد">
        <input type="password" id="passInp" placeholder="كلمة المرور">
        <button class="btn btn-p" onclick="login()">دخول للنظام</button>
        <p style="text-align:center; font-size:12px; color:gray; cursor:pointer;" onclick="alert('تواصل مع م. أيمن لاستعادة الحساب: 0556868717')">نسيت كلمة السر؟</p>
    </div>
</div>

<div id="mainSystem" style="display:none;">
    <div class="header">
        <h2 id="storeTitle">بهجة برو V28</h2>
    </div>

    <div class="container">
        <div id="custPage" class="card active">
            <h3>👥 إدارة العملاء</h3>
            <input type="text" id="cName" placeholder="اسم العميل">
            <input type="text" id="cPhone" placeholder="رقم الجوال">
            <button class="btn btn-p" onclick="addCustomer()">➕ إضافة عميل جديد</button>
            <table id="cTable">
                <thead><tr><th>العميل</th><th>التحكم</th></tr></thead>
                <tbody id="cBody"></tbody>
            </table>
        </div>

        <div id="txPage" class="card">
            <h3>📥 تسجيل حركة مالية</h3>
            <select id="txSelect"></select>
            <input type="number" id="txAmt" placeholder="المبلغ">
            <select id="txType">
                <option value="له">له (إيداع)</option>
                <option value="عليه">عليه (سحب)</option>
            </select>
            <textarea id="txNote" placeholder="بيان الحركة..."></textarea>
            <button class="btn btn-p" onclick="addTransaction()">✅ حفظ العملية</button>
        </div>

        <div id="repPage" class="card">
            <h3>📊 التقارير والكشوفات</h3>
            <select id="repSelect" onchange="loadStatement()"></select>
            <div id="statementView">
                <table id="stTable">
                    <thead><tr><th>التاريخ</th><th>البيان</th><th>المبلغ</th><th>الحالة</th></tr></thead>
                    <tbody id="stBody"></tbody>
                    <tfoot id="stFoot"></tfoot>
                </table>
            </div>
            <hr>
            <h4>📋 كشف الإجمالي العام</h4>
            <table id="allTable">
                <thead><tr><th>العميل</th><th>الرصيد التراكمي</th></tr></thead>
                <tbody id="allBody"></tbody>
            </table>
        </div>

        <div id="setPage" class="card">
            <h3>⚙️ الإعدادات والنسخ الاحتياطي</h3>
            <label>اسم المتجر:</label>
            <input type="text" id="setStore" placeholder="اسم محلك">
            <button class="btn btn-p" onclick="saveSettings()">حفظ التعديلات</button>
            <hr>
            <h4>💾 النسخ الاحتياطي</h4>
            <button class="btn" style="background:green;" onclick="exportData()">تحميل نسخة احتياطية (JSON)</button>
            <p style="font-size:11px; color:red;">* لرفع النسخة، تواصل مع الدعم الفني.</p>
            <button class="btn btn-del" onclick="logout()">🚪 تسجيل الخروج</button>
        </div>

        <div id="conPage" class="card">
            <h3>📞 تواصل معنا</h3>
            <div style="text-align:center;">
                <p><b>المطور: م. أيمن الحميري</b></p>
                <p>واتساب: 0556868717</p>
                <p>البريد: kebriay2030@gmail.com</p>
                <p>نسخة مخصصة لنظام إدارة المبيعات والديون</p>
            </div>
        </div>
    </div>

    <nav class="nav">
        <div class="nav-item active" onclick="show('custPage', this)">👥 العملاء</div>
        <div class="nav-item" onclick="show('txPage', this)">📥 حركة</div>
        <div class="nav-item" onclick="show('repPage', this)">📊 تقارير</div>
        <div class="nav-item" onclick="show('setPage', this)">⚙️ إعدادات</div>
        <div class="nav-item" onclick="show('conPage', this)">📞 تواصل</div>
    </nav>
</div>

<script>
    let db = JSON.parse(localStorage.getItem('bahjat_db')) || { customers: [], ledger: [], store: 'بهجة برو V28', user: 'admin', pass: '123456' };

    function login() {
        let u = document.getElementById('userInp').value;
        let p = document.getElementById('passInp').value;
        if(u === db.user && p === db.pass) {
            localStorage.setItem('isAuth', 'true');
            checkLogin();
        } else { alert('بيانات الدخول خاطئة!'); }
    }

    function checkLogin() {
        if(localStorage.getItem('isAuth') === 'true') {
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('mainSystem').style.display = 'block';
            document.getElementById('storeTitle').innerText = db.store;
            renderAll();
        } else {
            document.getElementById('loginPage').style.display = 'block';
            document.getElementById('mainSystem').style.display = 'none';
        }
    }

    function logout() { localStorage.removeItem('isAuth'); location.reload(); }

    function show(id, el) {
        document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
        renderAll();
    }

    function addCustomer() {
        let n = document.getElementById('cName').value;
        if(!n) return;
        db.customers.push({name: n, phone: document.getElementById('cPhone').value});
        save();
        document.getElementById('cName').value = '';
    }

    function deleteCustomer(i) { if(confirm('حذف العميل سيمسح كافة حركاته، هل أنت متأكد؟')) { db.customers.splice(i,1); db.ledger = db.ledger.filter(l => l.cid != i); save(); } }

    function addTransaction() {
        let id = document.getElementById('txSelect').value;
        let amt = document.getElementById('txAmt').value;
        if(id === "" || !amt) return;
        db.ledger.push({
            cid: id,
            amt: parseFloat(amt),
            type: document.getElementById('txType').value,
            note: document.getElementById('txNote').value,
            date: new Date().toLocaleDateString()
        });
        save();
        alert('تم الحفظ بنجاح');
        show('repPage', document.querySelectorAll('.nav-item')[2]);
    }

    function renderAll() {
        let cBody = document.getElementById('cBody');
        let txSel = document.getElementById('txSelect');
        let repSel = document.getElementById('repSelect');
        cBody.innerHTML = ''; 
        txSel.innerHTML = '<option value="">-- اختر عميل --</option>';
        repSel.innerHTML = '<option value="">-- اختر عميل للكشف --</option>';

        db.customers.forEach((c, i) => {
            cBody.innerHTML += `<tr><td>${c.name}</td><td><button class="btn btn-edit" onclick="editCust(${i})">✏️</button><button class="btn btn-del" onclick="deleteCustomer(${i})">🗑️</button></td></tr>`;
            txSel.innerHTML += `<option value="${i}">${c.name}</option>`;
            repSel.innerHTML += `<option value="${i}">${c.name}</option>`;
        });

        // كشف الإجمالي العام
        let allBody = document.getElementById('allBody');
        allBody.innerHTML = '';
        db.customers.forEach((c, i) => {
            let bal = 0;
            db.ledger.filter(l => l.cid == i).forEach(l => { if(l.type === 'له') bal += l.amt; else bal -= l.amt; });
            allBody.innerHTML += `<tr><td>${c.name}</td><td class="${bal >=0 ? 'pos':'neg'}">${bal.toFixed(2)}</td></tr>`;
        });
    }

    function loadStatement() {
        let cid = document.getElementById('repSelect').value;
        let stBody = document.getElementById('stBody');
        let stFoot = document.getElementById('stFoot');
        stBody.innerHTML = '';
        if(cid === "") return;
        let total = 0;
        db.ledger.filter(l => l.cid == cid).forEach(l => {
            let color = l.type === 'له' ? 'pos' : 'neg';
            total += (l.type === 'له' ? l.amt : -l.amt);
            stBody.innerHTML += `<tr><td>${l.date}</td><td>${l.note}</td><td>${l.amt}</td><td class="${color}">${l.type}</td></tr>`;
        });
        stFoot.innerHTML = `<tr class="total-row"><td colspan="2">الرصيد النهائي</td><td colspan="2" class="${total>=0?'pos':'neg'}">${total.toFixed(2)}</td></tr>`;
    }

    function saveSettings() { db.store = document.getElementById('setStore').value; save(); location.reload(); }

    function exportData() {
        let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(db));
        let downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "bahjat_backup.json");
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }

    function save() { localStorage.setItem('bahjat_db', JSON.stringify(db)); renderAll(); }
    function editCust(i) { let n = prompt('الاسم الجديد:', db.customers[i].name); if(n) { db.customers[i].name = n; save(); } }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_FINAL)

if __name__ == "__main__":
    app.run()
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
