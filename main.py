from flask import Flask, render_template_string

app = Flask(__name__)

# نسخة النخبة المستقرة V28.1 - تصميم وتطوير م. أيمن الحميري
HTML_FINAL = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بهجة برو V28.1</title>
    <style>
        :root { --p: #0d47a1; --s: #1976d2; --bg: #f4f7f9; --w: #ffffff; --red: #d32f2f; --green: #388e3c; }
        body { font-family: 'Segoe UI', Tahoma; background: var(--bg); margin: 0; padding-bottom: 80px; text-align: right; }
        .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 15px; text-align: center; position: sticky; top: 0; z-index: 1000; }
        .container { padding: 10px; max-width: 800px; margin: auto; }
        .card { background: var(--w); padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 15px; display: none; }
        .card.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .btn { padding: 10px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; text-align: center; }
        .btn-p { background: var(--p); width: 100%; margin-top: 5px; }
        .btn-del { background: var(--red); font-size: 12px; padding: 5px 8px; }
        .btn-edit { background: #ffa000; font-size: 12px; padding: 5px 8px; margin-left: 5px; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background: white; font-size: 13px; }
        th, td { padding: 8px; border-bottom: 1px solid #eee; text-align: center; }
        th { background: #f8f9fa; color: var(--p); }
        .pos { color: var(--green); font-weight: bold; } /* تلوين له */
        .neg { color: var(--red); font-weight: bold; }   /* تلوين عليه */
        .nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
        .nav-item { flex: 1; text-align: center; padding: 12px 2px; color: #667; cursor: pointer; font-size: 11px; }
        .nav-item.active { color: var(--p); border-top: 3px solid var(--p); background: #f0f4ff; }
        .total-box { background: #e8f5e9; padding: 15px; border-radius: 10px; border: 2px solid var(--green); text-align: center; margin-top: 10px; }
        .neg-box { background: #ffebee; border-color: var(--red); }
    </style>
</head>
<body onload="checkLogin()">

<div id="loginPage" class="container" style="display:none;">
    <div class="card active" style="margin-top:50px; text-align:center;">
        <h2 style="color:var(--p);">🔐 تسجيل الدخول</h2>
        <input type="text" id="uInp" placeholder="اسم المستخدم أو البريد">
        <input type="password" id="pInp" placeholder="كلمة المرور">
        <button class="btn btn-p" onclick="login()">دخول للنظام</button>
        <p style="font-size:12px; color:gray; margin-top:15px; cursor:pointer;" onclick="alert('تواصل مع م. أيمن: 0556868717')">استعادة الحساب / نسيان كلمة السر</p>
    </div>
</div>

<div id="mainSys" style="display:none;">
    <div class="header"><h2 id="storeTitle">بهجة برو V28.1</h2></div>

    <div class="container">
        <div id="pgCust" class="card active">
            <h3>👥 إدارة العملاء</h3>
            <input type="text" id="cn" placeholder="اسم العميل">
            <input type="text" id="cp" placeholder="رقم الجوال">
            <button class="btn btn-p" onclick="addCust()">➕ إضافة عميل جديد</button>
            <table id="cTable">
                <thead><tr><th>العميل</th><th>رقم الجوال</th><th>التحكم</th></tr></thead>
                <tbody id="cBody"></tbody>
            </table>
        </div>

        <div id="pgTx" class="card">
            <h3>📥 تسجيل حركة مالية</h3>
            <select id="txSel"></select>
            <input type="number" id="txA" placeholder="المبلغ">
            <select id="txT">
                <option value="له">له (إيداع/سداد من عميل)</option>
                <option value="عليه">عليه (سحب/دين على عميل)</option>
            </select>
            <textarea id="txN" placeholder="بيان الحركة (مثلاً: دفعة مبيعات)"></textarea>
            <button class="btn btn-p" onclick="addTx()">✅ حفظ العملية</button>
        </div>

        <div id="pgRep" class="card">
            <h3>📊 كشوفات الحسابات</h3>
            <select id="repSel" onchange="loadStatement()"></select>
            <div id="statementArea">
                <table id="stTable">
                    <thead><tr><th>التاريخ</th><th>البيان</th><th>المبلغ</th><th>الحالة</th></tr></thead>
                    <tbody id="stBody"></tbody>
                </table>
                <div id="stFoot" class="total-box">اختر عميلاً لعرض الإجمالي</div>
            </div>
            <hr>
            <h4>📋 كشف الإجمالي العام للديون</h4>
            <table id="allTable">
                <thead><tr><th>العميل</th><th>الرصيد النهائي</th></tr></thead>
                <tbody id="allBody"></tbody>
            </table>
        </div>

        <div id="pgSet" class="card">
            <h3>⚙️ الإعدادات والأمان</h3>
            <input type="text" id="sStore" placeholder="اسم المتجر">
            <input type="text" id="sUser" placeholder="تغيير اسم المستخدم">
            <input type="text" id="sPass" placeholder="تغيير كلمة السر">
            <button class="btn btn-p" onclick="saveSet()">حفظ الإعدادات</button>
            <hr>
            <h4>💾 النسخ الاحتياطي والاستعادة</h4>
            <button class="btn" style="background:#2e7d32; width:100%;" onclick="exportData()">📥 تحميل نسخة احتياطية</button>
            <p style="font-size:11px; color:#666;">* لتحميل بياناتك السابقة، اختر ملف الـ JSON الخاص بك:</p>
            <input type="file" id="importFile" onchange="importData(event)" style="font-size:11px;">
            <hr>
            <button class="btn btn-del" style="width:100%" onclick="logout()">🚪 تسجيل الخروج</button>
        </div>

        <div id="pgCon" class="card">
            <h3>📞 تواصل مع م. أيمن الحميري</h3>
            <div style="text-align:center;">
                <p><b>مستشارك التقني: أيمن الحميري</b></p>
                <p>رقم الجوال: 0556868717</p>
                <p>الإيميل: kebriay2030@gmail.com</p>
                <p style="color:var(--p)">نسخة ذكية مخصصة للمؤسسات والمحلات التجارية</p>
            </div>
        </div>
    </div>

    <nav class="nav">
        <div class="nav-item active" onclick="show('pgCust', this)">👥 العملاء</div>
        <div class="nav-item" onclick="show('pgTx', this)">📥 إضافة</div>
        <div class="nav-item" onclick="show('pgRep', this)">📊 تقارير</div>
        <div class="nav-item" onclick="show('pgSet', this)">⚙️ إعدادات</div>
        <div class="nav-item" onclick="show('pgCon', this)">📞 تواصل</div>
    </nav>
</div>

<script>
    let db = JSON.parse(localStorage.getItem('bahjat_v28')) || { 
        customers: [], ledger: [], store: 'بهجة برو V28.1', user: 'admin', pass: '123456' 
    };

    function login() {
        if(document.getElementById('uInp').value === db.user && document.getElementById('pInp').value === db.pass) {
            localStorage.setItem('auth', 'true'); checkLogin();
        } else { alert('خطأ في البيانات!'); }
    }

    function checkLogin() {
        if(localStorage.getItem('auth') === 'true') {
            document.getElementById('loginPage').style.display='none';
            document.getElementById('mainSys').style.display='block';
            document.getElementById('storeTitle').innerText = db.store;
            renderAll();
        } else { document.getElementById('loginPage').style.display='block'; }
    }

    function logout() { localStorage.removeItem('auth'); location.reload(); }

    function show(id, el) {
        document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
        renderAll();
    }

    function addCust() {
        let n = document.getElementById('cn').value; if(!n) return;
        db.customers.push({name: n, phone: document.getElementById('cp').value});
        save(); document.getElementById('cn').value=''; document.getElementById('cp').value='';
    }

    function editCust(i) {
        let n = prompt('الاسم الجديد:', db.customers[i].name);
        if(n) { db.customers[i].name = n; save(); }
    }

    function delCust(i) {
        if(confirm('سيتم حذف العميل وكافة سجلاته المالية!')) {
            db.customers.splice(i,1);
            db.ledger = db.ledger.filter(l => l.cid != i);
            save();
        }
    }

    function addTx() {
        let cid = document.getElementById('txSel').value;
        let amt = document.getElementById('txA').value;
        if(cid==="" || !amt) return;
        db.ledger.push({
            cid: cid, amt: parseFloat(amt), type: document.getElementById('txT').value,
            note: document.getElementById('txN').value, date: new Date().toLocaleDateString()
        });
        save(); alert('تم الحفظ');
        show('pgRep', document.querySelectorAll('.nav-item')[2]);
    }

    function renderAll() {
        let cb = document.getElementById('cBody');
        let ts = document.getElementById('txSel');
        let rs = document.getElementById('repSel');
        cb.innerHTML = ''; ts.innerHTML = '<option value="">-- اختر عميل --</option>';
        rs.innerHTML = '<option value="">-- اختر عميل للكشف --</option>';

        db.customers.forEach((c, i) => {
            cb.innerHTML += `<tr><td>${c.name}</td><td>${c.phone}</td><td>
                <button class="btn btn-edit" onclick="editCust(${i})">✏️</button>
                <button class="btn btn-del" onclick="delCust(${i})">🗑️</button></td></tr>`;
            ts.innerHTML += `<option value="${i}">${c.name}</option>`;
            rs.innerHTML += `<option value="${i}">${c.name}</option>`;
        });

        let ab = document.getElementById('allBody'); ab.innerHTML = '';
        db.customers.forEach((c, i) => {
            let bal = 0;
            db.ledger.filter(l => l.cid == i).forEach(l => { bal += (l.type==='له' ? l.amt : -l.amt); });
            ab.innerHTML += `<tr><td>${c.name}</td><td class="${bal>=0?'pos':'neg'}">${bal.toFixed(2)}</td></tr>`;
        });
    }

    function loadStatement() {
        let cid = document.getElementById('repSel').value;
        let sb = document.getElementById('stBody');
        let sf = document.getElementById('stFoot');
        sb.innerHTML = ''; if(cid==="") { sf.innerText='اختر عميلاً'; return; }
        let total = 0;
        db.ledger.filter(l => l.cid == cid).forEach(l => {
            total += (l.type==='له' ? l.amt : -l.amt);
            sb.innerHTML += `<tr><td>${l.date}</td><td>${l.note}</td><td>${l.amt}</td><td class="${l.type==='له'?'pos':'neg'}">${l.type}</td></tr>`;
        });
        sf.innerHTML = `<h4>الرصيد النهائي للعميل: <span class="${total>=0?'pos':'neg'}">${total.toFixed(2)}</span></h4>`;
        if(total < 0) sf.classList.add('neg-box'); else sf.classList.remove('neg-box');
    }

    function saveSet() {
        db.store = document.getElementById('sStore').value || db.store;
        db.user = document.getElementById('sUser').value || db.user;
        db.pass = document.getElementById('sPass').value || db.pass;
        save(); alert('تم تحديث البيانات بنجاح'); location.reload();
    }

    function exportData() {
        let blob = new Blob([JSON.stringify(db)], {type: "application/json"});
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a'); a.href = url; a.download = "bahjat_backup.json"; a.click();
    }

    function importData(e) {
        let reader = new FileReader();
        reader.onload = function(event) {
            db = JSON.parse(event.target.result);
            save(); location.reload();
        };
        reader.readAsText(e.target.files[0]);
    }

    function save() { localStorage.setItem('bahjat_v28', JSON.stringify(db)); renderAll(); }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_FINAL)

if __name__ == "__main__":
    app.run()
