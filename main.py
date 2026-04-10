from flask import Flask, render_template_string

app = Flask(__name__)

# نسخة النخبة المستقرة V28.2 - م. أيمن الحميري
HTML_FINAL = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بهجة برو V28.2</title>
    <style>
        :root { --p: #0d47a1; --s: #1976d2; --bg: #f4f7f9; --w: #ffffff; --red: #d32f2f; --green: #388e3c; }
        body { font-family: 'Segoe UI', Tahoma; background: var(--bg); margin: 0; padding-bottom: 80px; text-align: right; }
        .header { background: linear-gradient(135deg, var(--p), var(--s)); color: white; padding: 15px; text-align: center; }
        .container { padding: 10px; max-width: 800px; margin: auto; }
        .card { background: var(--w); padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 15px; display: none; }
        .card.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .btn { padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; width: 100%; margin-top: 5px; text-align: center; }
        .btn-p { background: var(--p); }
        .btn-del { background: var(--red); font-size: 11px; width: auto; padding: 5px 8px; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px; border-bottom: 1px solid #eee; text-align: center; }
        .pos { color: var(--green); font-weight: bold; }
        .neg { color: var(--red); font-weight: bold; }
        .nav { position: fixed; bottom: 0; width: 100%; background: white; display: flex; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
        .nav-item { flex: 1; text-align: center; padding: 15px 2px; color: #667; cursor: pointer; font-size: 12px; }
        .nav-item.active { color: var(--p); border-top: 3px solid var(--p); background: #f0f4ff; }
        .total-box { background: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body onload="checkAuth()">

<div id="loginPage" class="container" style="display:none;">
    <div class="card active" style="margin-top:50px; text-align:center;">
        <h2 style="color:var(--p);">🔐 تسجيل الدخول</h2>
        <input type="text" id="user" placeholder="اسم المستخدم (admin)">
        <input type="password" id="pass" placeholder="كلمة المرور (123456)">
        <button class="btn btn-p" onclick="login()">دخول للنظام</button>
    </div>
</div>

<div id="mainSys" style="display:none;">
    <div class="header"><h2 id="storeT">بهجة برو V28.2</h2></div>
    <div class="container">
        
        <div id="pgCust" class="card active">
            <h3>👥 العملاء</h3>
            <input type="text" id="cn" placeholder="اسم العميل">
            <button class="btn btn-p" onclick="addCust()">➕ إضافة عميل</button>
            <table id="cTable"><thead><tr><th>الاسم</th><th>التحكم</th></tr></thead><tbody id="cBody"></tbody></table>
        </div>

        <div id="pgTx" class="card">
            <h3>📥 إضافة حركة</h3>
            <select id="txSel"></select>
            <input type="number" id="txA" placeholder="المبلغ">
            <select id="txT"><option value="له">له</option><option value="عليه">عليه</option></select>
            <textarea id="txN" placeholder="بيان الحركة"></textarea>
            <button class="btn btn-p" onclick="addTx()">✅ حفظ</button>
        </div>

        <div id="pgRep" class="card">
            <h3>📊 كشوفات الحساب</h3>
            <select id="repSel" onchange="loadRep()"></select>
            <div id="repView">
                <table><thead><tr><th>التاريخ</th><th>البيان</th><th>المبلغ</th><th>الحالة</th></tr></thead><tbody id="stBody"></tbody></table>
                <div id="stFoot" class="total-box"></div>
            </div>
        </div>

        <div id="pgSet" class="card">
            <h3>⚙️ الإعدادات</h3>
            <input type="text" id="sS" placeholder="اسم المتجر">
            <button class="btn btn-p" onclick="saveSet()">حفظ</button>
            <button class="btn" style="background:green;" onclick="exportDB()">📥 نسخة احتياطية</button>
            <button class="btn btn-del" style="width:100%" onclick="logout()">🚪 خروج</button>
        </div>

    </div>

    <nav class="nav">
        <div class="nav-item active" onclick="show('pgCust', this)">👥 العملاء</div>
        <div class="nav-item" onclick="show('pgTx', this)">📥 إضافة</div>
        <div class="nav-item" onclick="show('pgRep', this)">📊 تقارير</div>
        <div class="nav-item" onclick="show('pgSet', this)">⚙️ إعدادات</div>
    </nav>
</div>

<script>
    let db = JSON.parse(localStorage.getItem('bahjat_db')) || { customers: [], ledger: [], store: 'بهجة برو V28.2' };

    function login() {
        if(document.getElementById('user').value==='admin' && document.getElementById('pass').value==='123456') {
            localStorage.setItem('auth', 'true'); checkAuth();
        } else { alert('خطأ!'); }
    }

    function checkAuth() {
        if(localStorage.getItem('auth')==='true') {
            document.getElementById('loginPage').style.display='none';
            document.getElementById('mainSys').style.display='block';
            document.getElementById('storeT').innerText = db.store;
            render();
        } else { document.getElementById('loginPage').style.display='block'; }
    }

    function logout() { localStorage.removeItem('auth'); location.reload(); }

    function show(id, el) {
        document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
        render();
    }

    function addCust() {
        let n = document.getElementById('cn').value; if(!n) return;
        db.customers.push(n); save(); document.getElementById('cn').value='';
    }

    function addTx() {
        let cid = document.getElementById('txSel').value;
        let amt = document.getElementById('txA').value;
        if(cid==="" || !amt) return;
        db.ledger.push({cid, amt:parseFloat(amt), type:document.getElementById('txT').value, note:document.getElementById('txN').value, date:new Date().toLocaleDateString()});
        save(); alert('تم الحفظ'); show('pgRep', document.querySelectorAll('.nav-item')[2]);
    }

    function render() {
        let cb = document.getElementById('cBody'); let ts = document.getElementById('txSel'); let rs = document.getElementById('repSel');
        cb.innerHTML = ''; ts.innerHTML = '<option value="">-- اختر --</option>'; rs.innerHTML = ts.innerHTML;
        db.customers.forEach((c, i) => {
            cb.innerHTML += `<tr><td>${c}</td><td><button class="btn btn-del" onclick="db.customers.splice(${i},1);save()">🗑️</button></td></tr>`;
            ts.innerHTML += `<option value="${i}">${c}</option>`;
            rs.innerHTML += `<option value="${i}">${c}</option>`;
        });
    }

    function loadRep() {
        let cid = document.getElementById('repSel').value; let sb = document.getElementById('stBody'); let total = 0;
        sb.innerHTML = ''; if(cid==="") return;
        db.ledger.filter(l => l.cid == cid).forEach(l => {
            total += (l.type==='له' ? l.amt : -l.amt);
            sb.innerHTML += `<tr><td>${l.date}</td><td>${l.note}</td><td>${l.amt}</td><td class="${l.type==='له'?'pos':'neg'}">${l.type}</td></tr>`;
        });
        document.getElementById('stFoot').innerHTML = `الرصيد: <span class="${total>=0?'pos':'neg'}">${total.toFixed(2)}</span>`;
    }

    function saveSet() { db.store = document.getElementById('sS').value; save(); location.reload(); }
    function save() { localStorage.setItem('bahjat_db', JSON.stringify(db)); render(); }
    function exportDB() {
        let blob = new Blob([JSON.stringify(db)], {type: "application/json"});
        let a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = "backup.json"; a.click();
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_FINAL)

if __name__ == "__main__":
    app.run()
