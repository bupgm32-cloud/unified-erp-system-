import os
import json
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# مسار ملف حفظ البيانات الدائم على سيرفر Render لمنع فقدان قيود اليومية
DATA_FILE = '/opt/render/project/src/accounting_ultimate_db.json' if os.path.exists('/opt/render/project/src/') else 'accounting_ultimate_db.json'

def load_journal_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_journal_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# قالب التصميم المتكامل للنظام الاحترافي الذي طلبته تماماً مع ربطه بالسيرفر
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام ERP المحاسبي الشامل والمتكامل - الإصدار الختامي المطور</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0f172a; --primary-light: #1e293b;
            --accent: #2563eb; --accent-hover: #1d4ed8;
            --excel: #107c41; --excel-hover: #185c37;
            --bg-color: #f8fafc; --surface: #ffffff;
            --text-main: #1e293b; --text-muted: #64748b;
            --border: #e2e8f0;
            --sidebar-width: 290px; --header-height: 70px;
            
            /* ألوان الهوية المحاسبية */
            --color-asset: #0284c7;
            --color-liability: #dc2626;
            --color-equity: #7c3aed;
            --color-revenue: #16a34a;
            --color-expense: #ea580c;
            --color-cogs: #db2777;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; position: relative; }

        /* --- القائمة الجانبية المطورة والمستجيبة --- */
        .sidebar { 
            width: var(--sidebar-width); 
            background-color: var(--primary); 
            color: white; 
            display: flex; 
            flex-direction: column; 
            transition: transform 0.3s ease, width 0.3s ease; 
            z-index: 1010; 
            box-shadow: -4px 0 15px rgba(0,0,0,0.1); 
            height: 100vh;
        }
        .brand { height: var(--header-height); display: flex; align-items: center; padding: 0 24px; font-size: 20px; font-weight: 800; background-color: #0b1120; border-bottom: 1px solid #1e293b; justify-content: space-between; }
        .brand span { color: #3b82f6; margin-right: 8px; }
        
        .close-sidebar-btn { display: none; background: none; border: none; color: white; font-size: 20px; cursor: pointer; }

        .nav-section { padding: 20px 24px 6px; font-size: 11px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 1px; }
        .nav-item { padding: 11px 24px; display: flex; align-items: center; gap: 12px; cursor: pointer; font-size: 14px; font-weight: 600; color: #94a3b8; transition: 0.2s; border-right: 4px solid transparent; }
        .nav-item:hover, .nav-item.active { background-color: var(--primary-light); color: #fff; border-right-color: #3b82f6; }

        .sidebar-overlay { 
            position: fixed; top: 0; right: 0; width: 100vw; height: 100vh; 
            background: rgba(0,0,0,0.4); z-index: 1005; display: none; opacity: 0; transition: opacity 0.3s ease;
        }

        /* --- الإطار الرئيسي --- */
        .main-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; width: 100%; }
        .topbar { height: var(--header-height); background-color: var(--surface); display: flex; align-items: center; padding: 0 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); justify-content: space-between; z-index: 99; }
        .toggle-btn { background: none; border: none; font-size: 22px; cursor: pointer; color: var(--text-main); padding: 5px; display: flex; align-items: center; justify-content: center; }
        .content-area { flex: 1; overflow-y: auto; padding: 30px; }
        .tab-content { display: none; animation: fadeIn 0.3s ease; max-width: 1400px; margin: 0 auto; }
        .tab-content.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        /* --- المكونات الهيكلية --- */
        .page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px; flex-wrap: wrap; gap: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; }
        .page-title { font-size: 24px; font-weight: 800; color: var(--primary); }
        .page-desc { color: var(--text-muted); font-size: 13px; margin-top: 4px; }
        
        .panel { background: var(--surface); padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02); margin-bottom: 25px; border: 1px solid var(--border); }
        .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border); flex-wrap: wrap; gap: 10px; }
        .panel-title { font-size: 16px; font-weight: 800; color: var(--primary); }

        /* --- النماذج --- */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        label { font-weight: 700; font-size: 12px; color: var(--text-main); }
        input, select { padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; background-color: #f8fafc; transition: 0.2s; width: 100%; }
        input:focus, select:focus { outline: none; border-color: var(--accent); background-color: #fff; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
        .search-box { width: 100%; max-width: 400px; padding: 9px 15px; border-radius: 20px; border: 1px solid var(--border); }

        /* --- الأزرار --- */
        .btn { padding: 10px 18px; border: none; border-radius: 6px; font-size: 13px; font-weight: 700; cursor: pointer; transition: 0.2s; display: inline-flex; align-items: center; gap: 8px; justify-content: center; }
        .btn-primary { background-color: var(--accent); color: white; }
        .btn-primary:hover { background-color: var(--accent-hover); }
        .btn-excel { background-color: var(--excel); color: white; }
        .btn-excel:hover { background-color: var(--excel-hover); }
        .btn-danger { background-color: #fee2e2; color: #ef4444; padding: 6px 12px; font-size: 11px; }

        /* --- الجداول والوسوم --- */
        .table-responsive { overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); width: 100%; }
        table { width: 100%; border-collapse: collapse; text-align: right; background: white; }
        th { background-color: #f8fafc; padding: 14px 16px; font-size: 13px; font-weight: 800; color: #475569; border-bottom: 2px solid var(--border); white-space: nowrap; }
        td { padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 13px; color: var(--text-main); white-space: nowrap; }
        tr:hover td { background-color: #f1f5f9; }
        .amount { font-family: monospace; font-weight: 700; font-size: 14px; text-align: left; }
        
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 800; display: inline-block; }
        .badge-asset { background-color: #e0f2fe; color: var(--color-asset); }
        .badge-liability { background-color: #fee2e2; color: var(--color-liability); }
        .badge-equity { background-color: #ede9fe; color: var(--color-equity); }
        .badge-revenue { background-color: #d1fae5; color: var(--color-revenue); }
        .badge-expense { background-color: #fef3c7; color: var(--color-expense); }
        .badge-cogs { background-color: #fae8ff; color: var(--color-cogs); }
        
        /* كروت لوحة المؤشرات */
        .stat-card { background: white; padding: 22px; border-radius: 12px; border: 1px solid var(--border); border-right: 5px solid var(--accent); }
        .stat-card h3 { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
        .stat-card .val { font-size: 26px; font-weight: 800; color: var(--primary); font-family: monospace; text-align: left; }

        /* تنسيقات خاصة التقارير الختامية */
        .report-row-total { font-weight: bold; background-color: #f1f5f9 !important; border-top: 1px solid #94a3b8; border-bottom: 2px double #475569 !important; }
        .report-row-subtotal { font-weight: 600; background-color: #f8fafc; }
        .report-indent { padding-right: 35px; }

        @media (min-width: 992px) {
            body.sidebar-collapsed .sidebar { width: 0; overflow: hidden; }
        }

        @media (max-width: 991px) {
            .sidebar { position: fixed; top: 0; right: 0; transform: translateX(100%); width: var(--sidebar-width); box-shadow: -5px 0 25px rgba(0,0,0,0.2); }
            .sidebar.open { transform: translateX(0); }
            .close-sidebar-btn { display: block; }
            .content-area { padding: 15px; }
            .page-title { font-size: 20px; }
            .topbar { padding: 0 15px; }
        }
    </style>
</head>
<body>

    <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

    <div class="sidebar" id="sidebar">
        <div class="brand">
            <div><span>ERP</span> المحاسبي المتكامل</div>
            <button class="close-sidebar-btn" onclick="toggleSidebar()">✕</button>
        </div>
        
        <div class="nav-section">الرئيسية</div>
        <div class="nav-item active" onclick="switchTab('dashboard')">📊 لوحة المؤشرات والملخص</div>
        
        <div class="nav-section">إدارة الحسابات والعمليات</div>
        <div class="nav-item" onclick="switchTab('coa')">🗂️ شجرة الحسابات الموحدة</div>
        <div class="nav-item" onclick="switchTab('journal')">📝 شاشة قيود اليومية العامة</div>
        
        <div class="nav-section">التقارير التفصيلية</div>
        <div class="nav-item" onclick="switchTab('ledger')">📄 دفتر الأستاذ (كشف حساب)</div>
        <div class="nav-item" onclick="switchTab('trial-balance')">⚖️ ميزان المراجعة بالأرصدة</div>
        
        <div class="nav-section">القوائم المالية والنتائج</div>
        <div class="nav-item" onclick="switchTab('income-statement')">📈 قائمة الأرباح والخسائر</div>
        <div class="nav-item" onclick="switchTab('balance-sheet')">🏛️ الميزانية العمومية والمركز</div>
    </div>

    <div class="main-wrapper">
        <header class="topbar">
            <button class="toggle-btn" onclick="toggleSidebar()">☰</button>
            <div style="font-weight: 800; color: var(--primary); font-size: 13px; text-align: left;">نظام معتمد 🟢 قاعدة البيانات نشطة السحابة</div>
        </header>

        <div class="content-area">

            <div id="dashboard" class="tab-content active">
                <div class="page-header">
                    <div>
                        <h1 class="page-title">لوحة المؤشرات والتحليل المالي</h1>
                        <p class="page-desc">مراقبة حية للحسابات الختامية والأرباح</p>
                    </div>
                </div>
                <div class="form-grid">
                    <div class="stat-card" style="border-color: var(--color-asset)"><h3>إجمالي الأصول الحالية</h3><div class="val" id="stat-assets">0.00</div></div>
                    <div class="stat-card" style="border-color: var(--color-liability)"><h3>إجمالي الالتزامات</h3><div class="val" id="stat-liabilities">0.00</div></div>
                    <div class="stat-card" style="border-color: var(--color-revenue)"><h3>إيرادات النشاط</h3><div class="val" id="stat-revenue">0.00</div></div>
                    <div class="stat-card" id="net-profit-card" style="border-color: var(--color-equity)"><h3>صافي الأرباح / الخسائر</h3><div class="val" id="stat-net-profit">0.00</div></div>
                </div>
            </div>

            <div id="coa" class="tab-content">
                <div class="page-header">
                    <div>
                        <h1 class="page-title">الدليل المحاسبي الشامل (Chart of Accounts)</h1>
                        <p class="page-desc">الهيكل التنظيمي لكافة الحسابات المالية مع الترميز اللوني المتقدم</p>
                    </div>
                    <button class="btn btn-excel" onclick="exportExcel('الدليل_المحاسبي', 'coa-table')">📥 تصدير الدليل</button>
                </div>
                <div class="panel">
                    <div class="panel-header">
                        <input type="text" id="coa-search" class="search-box" placeholder="🔍 ابحث بالاسم، الرقم، أو نوع الحساب..." onkeyup="filterCOA()">
                    </div>
                    <div class="table-responsive">
                        <table id="coa-table">
                            <thead>
                                <tr><th>رقم الحساب</th><th>اسم الحساب المحاسبي</th><th>طبيعة الحساب</th><th>المجموعة الرئيسية</th><th>النوع الفرعي</th><th>الرصيد الحالي</th></tr>
                            </thead>
                            <tbody id="coa-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="journal" class="tab-content">
                <div class="page-header">
                    <div><h1 class="page-title">تسجيل وتدوين قيود اليومية العامة</h1></div>
                    <button class="btn btn-excel" onclick="exportExcel('دفتر_اليومية_العامة', 'journal-table')">📥 تصدير القيود</button>
                </div>
                <div class="panel">
                    <div class="panel-title" style="margin-bottom:15px;">إنشاء مستند قيد نظامي متوازن</div>
                    <form action="/add_entry" method="POST">
                        <div class="form-grid">
                            <div class="form-group"><label>التاريخ</label><input type="date" name="je-date" id="je-date" required></div>
                            <div class="form-group"><label>الشرح والبيان المحاسبي</label><input type="text" name="je-desc" placeholder="شرح وافٍ للعملية..." required></div>
                        </div>
                        <div class="form-grid">
                            <div class="form-group"><label>حساب الطرف المدين (من حـ/)</label><select name="je-dr-acc" class="select-grouped" required></select></div>
                            <div class="form-group"><label>حساب الطرف الدائن (إلى حـ/)</label><select name="je-cr-acc" class="select-grouped" required></select></div>
                            <div class="form-group"><label>القيمة المالية (المبلغ)</label><input type="number" name="je-amount" placeholder="0.00" min="0.01" step="0.01" required></div>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%; padding: 12px;">💾 ترحيل وحفظ القيد وإقفاله في الدفاتر</button>
                    </form>
                </div>
                <div class="panel">
                    <div class="table-responsive">
                        <table id="journal-table">
                            <thead>
                                <tr><th>رقم السند</th><th>التاريخ</th><th>البيان المحاسبي</th><th>الطرف المدين</th><th>الطرف الدائن</th><th>المبلغ</th><th>التحكم</th></tr>
                            </thead>
                            <tbody id="journal-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="ledger" class="tab-content">
                <div class="page-header">
                    <h1 class="page-title">دفتر الأستاذ العام والتحليلي</h1>
                    <button class="btn btn-excel" onclick="exportExcel('كشف_حساب_تفصيلي', 'ledger-table')">📥 تصدير كشف الحساب</button>
                </div>
                <div class="panel">
                    <div class="form-grid"><div class="form-group"><label>اختر الحساب لاستخراج كشف الحركة:</label><select id="ledger-select" class="select-grouped" onchange="generateLedger()"></select></div></div>
                </div>
                <div class="panel">
                    <div class="panel-header">
                        <span class="panel-title">كشف الحركة التفصيلي وعمليات المراجعة</span>
                        <div style="font-size:16px; font-weight:800; background:#f1f5f9; padding:8px 20px; border-radius:8px;" id="ledger-final-balance">الرصيد: 0.00</div>
                    </div>
                    <div class="table-responsive">
                        <table id="ledger-table">
                            <thead>
                                <tr><th>التاريخ</th><th>رقم القيد</th><th>البيان والحساب المقابل</th><th>الحركة المدينة (+)</th><th>الحركة الدائنة (-)</th><th>الرصيد التراكمي</th></tr>
                            </thead>
                            <tbody id="ledger-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="trial-balance" class="tab-content">
                <div class="page-header">
                    <h1 class="page-title">ميزان المراجعة بالأرصدة والمجاميع</h1>
                    <button class="btn btn-excel" onclick="exportExcel('ميزان_المراجعة', 'tb-table')">📥 تصدير ميزان المراجعة</button>
                </div>
                <div class="panel">
                    <div class="table-responsive">
                        <table id="tb-table">
                            <thead>
                                <tr><th>رقم الحساب</th><th>اسم الحساب</th><th>إجمالي المدين</th><th>إجمالي الدائن</th><th>الرصيد المدين</th><th>الرصيد الدائن</th></tr>
                            </thead>
                            <tbody id="tb-body"></tbody>
                            <tfoot id="tb-foot" style="background:#f1f5f9; font-weight:bold;"></tfoot>
                        </table>
                    </div>
                </div>
            </div>

            <div id="income-statement" class="tab-content">
                <div class="page-header">
                    <div>
                        <h1 class="page-title">قائمة الأرباح والخسائر (بيان الدخل الشامل)</h1>
                        <p class="page-desc">تحليل النشاط التجاري واحتساب هوامش الربح وصافي الأرباح التشغيلية والنهائية عن الفترة</p>
                    </div>
                    <button class="btn btn-excel" onclick="exportExcel('قائمة_الأرباح_والخسائر', 'is-table')">📥 تصدير القائمة</button>
                </div>
                <div class="panel">
                    <div class="table-responsive">
                        <table id="is-table">
                            <thead>
                                <tr><th>البنــد المالي التفصيلي</th><th style="text-align:left;">جزئي</th><th style="text-align:left;">كلي</th></tr>
                            </thead>
                            <tbody id="is-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="balance-sheet" class="tab-content">
                <div class="page-header">
                    <div>
                        <h1 class="page-title">الميزانية العمومية (قائمة المركز المالي)</h1>
                        <p class="page-desc">بيان المركز المالي للشركة المتوازن تلقائياً بناءً على ترحيل نتائج أرباح الفترة</p>
                    </div>
                    <button class="btn btn-excel" onclick="exportExcel('الميزانية_العمومية', 'bs-table')">📥 تصدير الميزانية</button>
                </div>
                <div class="panel">
                    <div class="table-responsive">
                        <table id="bs-table">
                            <thead>
                                <tr><th>الأصول / الالتزامات وحقوق الملكية</th><th style="text-align:left;">جزئي</th><th style="text-align:left;">كلي</th></tr>
                            </thead>
                            <tbody id="bs-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    </div>

<script>
const MASTER_DEVICE_KEY = "412-915-8-24"; 
let currentDeviceKey = screen.width + "-" + screen.height + "-" + navigator.hardwareConcurrency + "-" + screen.colorDepth;

function cryptoGenerateKey(deviceKey) {
    return deviceKey.split('-').map(num => (parseInt(num) * 5 + 13)).join('X');
}

let isMaster = (currentDeviceKey === MASTER_DEVICE_KEY);
let isActivated = (localStorage.getItem('erp_activation_license') === cryptoGenerateKey(currentDeviceKey));

if (!isMaster && !isActivated) {
    document.body.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; background-color:#0f172a; color:white; font-family:'Cairo',sans-serif; text-align:center; padding:20px; direction:rtl;">
            <span style="font-size:70px;">🔑</span>
            <h1 style="font-size:24px; margin-top:15px; font-weight:800; color:#3b82f6;">مطلوب تفعيل النظام المحاسبي</h1>
            <p style="color:#94a3b8; margin-top:10px; max-width:400px; font-size:14px;">هذه النسخة محمية برمجياً. يرجى نسخ كود التفعيل أدناه وإرساله للمالك الرسمي للحصول على مفتاح التشغيل الخاص بك.</p>
            <div style="background:#1e293b; padding:15px; border-radius:8px; margin-top:20px; border:1px solid #334155; width:100%; max-width:350px;">
                <label style="color:#64748b; font-size:12px; display:block; margin-bottom:5px;">كود جهازك (أرسله للمالك):</label>
                <div style="font-family:monospace; font-size:18px; font-weight:bold; color:#f8fafc;" id="client-code">${currentDeviceKey}</div>
            </div>
            <div style="margin-top:20px; width:100%; max-width:350px;">
                <input type="text" id="activation-input" placeholder="أدخل مفتاح التفعيل هنا..." style="padding:12px; border-radius:6px; border:1px solid #334155; background:#1e293b; color:white; width:100%; text-align:center; font-size:16px;">
                <button onclick="activateThisDevice()" style="background:#2563eb; color:white; border:none; padding:12px; width:100%; border-radius:6px; margin-top:10px; font-weight:bold; cursor:pointer;">تفعيل وتشغيل النظام الآن 🔓</button>
            </div>
        </div>
    `;
    window.activateThisDevice = function() {
        let inputKey = document.getElementById('activation-input').value.trim();
        if(inputKey === cryptoGenerateKey(currentDeviceKey)) {
            localStorage.setItem('erp_activation_license', inputKey);
            alert("🟢 تم التفعيل بنجاح! سيتم إعادة تشغيل النظام الآن.");
            location.reload();
        } else {
            alert("❌ مفتاح التفعيل غير صحيح أو لا يخص هذا الجهاز!");
        }
    };
    window.stop(); 
}

window.addEventListener('DOMContentLoaded', () => {
    if (isMaster) {
        let adminPanel = document.createElement('div');
        adminPanel.style.cssText = "position:fixed; bottom:10px; left:10px; background:#1e293b; padding:15px; border-radius:10px; border:2px solid #2563eb; z-index:9999; color:white; direction:rtl; max-width:280px; box-shadow:0 10px 25px rgba(0,0,0,0.3);";
        adminPanel.innerHTML = `
            <div style="font-size:12px; font-weight:bold; color:#3b82f6; margin-bottom:8px;">🛠️ لوحة المالك (توليد مفاتيح المشتركين)</div>
            <input type="text" id="master-target-code" placeholder="ضع كود جهاز العميل هنا..." style="padding:6px; font-size:12px; width:100%; margin-bottom:6px; border-radius:4px; border:none; color:black;">
            <button onclick="masterGenerateKeyForClient()" style="background:#2563eb; color:white; border:none; padding:6px; width:100%; border-radius:4px; font-size:12px; font-weight:bold; cursor:pointer;">توليد مفتاح التفعيل</button>
            <div id="master-result-key" style="margin-top:8px; font-family:monospace; font-size:11px; word-break:break-all; color:#10b981; user-select:all;"></div>
        `;
        document.body.appendChild(adminPanel);
        window.masterGenerateKeyForClient = function() {
            let targetCode = document.getElementById('master-target-code').value.trim();
            if(!targetCode) return alert("ضع كود جهاز العميل أولاً");
            try {
                let generated = cryptoGenerateKey(targetCode);
                document.getElementById('master-result-key').innerText = "المفتاح:\\n" + generated;
            } catch(e) { alert("الكود غير صالح"); }
        };
    }
});

    const accountsData = [
        { id: '1101', name: 'الصندوق الرئيسي (الخزينة)', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول متداولة' },
        { id: '1102', name: 'البنك - الحساب الجاري الكلي', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول متداولة' },
        { id: '1103', name: 'حساب العملاء والذمم المدينة', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول متداولة' },
        { id: '1104', name: 'مخزون السلع والبضائع آخر الفترة', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول متداولة' },
        { id: '1201', name: 'الأراضي العقارية', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول ثابتة' },
        { id: '1202', name: 'المباني والإنشاءات والمنشآت', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول ثابتة' },
        { id: '1203', name: 'السيارات وشاحنات النقل اللوجستي', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول ثابتة' },
        { id: '1204', name: 'الآلات ومعدات الإنتاج الصناعي', nature: 'debit', type: 'asset', category: 'الأصول', subCategory: 'أصول ثابتة' },
        { id: '2101', name: 'الموردون وحسابات الذمم الدائنة', nature: 'credit', type: 'liability', category: 'الخصوم', subCategory: 'خصوم متداولة' },
        { id: '2102', name: 'أوراق دفع وسندات تجارية مستحقة', nature: 'credit', type: 'liability', category: 'الخصوم', subCategory: 'خصوم متداولة' },
        { id: '2201', name: 'قروض تمويلية بنكية طويلة الأجل', nature: 'credit', type: 'liability', category: 'الخصوم', subCategory: 'خصوم غير متداولة' },
        { id: '3101', name: 'رأس المال المستثمر المدفوع', nature: 'credit', type: 'equity', category: 'حقوق الملكية', subCategory: 'حقوق ملكية' },
        { id: '3102', name: 'الأرباح المحتجزة / المبقاة', nature: 'credit', type: 'equity', category: 'حقوق الملكية', subCategory: 'حقوق ملكية' },
        { id: '4101', name: 'إيرادات المبيعات والنشاط الرئيسي', nature: 'credit', type: 'revenue', category: 'الإيرادات', subCategory: 'إيرادات تشغيلية' },
        { id: '4102', name: 'إيرادات الخدمات والاستشارات الفنية', nature: 'credit', type: 'revenue', category: 'الإيرادات', subCategory: 'إيرادات تشغيلية' },
        { id: '4103', name: 'إيرادات متنوعة وأرباح عرضية أخرى', nature: 'credit', type: 'revenue', category: 'الإيرادات', subCategory: 'إيرادات أخرى' },
        { id: '5101', name: 'تكلفة مشتريات البضائع والسلع', nature: 'debit', type: 'cogs', category: 'تكلفة المبيعات', subCategory: 'تكلفة مبيعات' },
        { id: '5102', name: 'مصاريف نقل وشحن واستيراد المشتريات', nature: 'debit', type: 'cogs', category: 'تكلفة المبيعات', subCategory: 'تكلفة مبيعات' },
        { id: '5201', name: 'مصروف رواتب وأجور الكادر الوظيفي', nature: 'debit', type: 'expense', category: 'المصروفات', subCategory: 'عمومية وإدارية' },
        { id: '5202', name: 'مصروف إيجار المكاتب والفروع', nature: 'debit', type: 'expense', category: 'المصروفات', subCategory: 'عمومية وإدارية' },
        { id: '5203', name: 'مصروف كهرباء ومياه واتصالات وإنترنت', nature: 'debit', type: 'expense', category: 'المصروفات', subCategory: 'عمومية وإدارية' },
        { id: '5204', name: 'مصروف الحملات التسويقية والإعلانات', nature: 'debit', type: 'expense', category: 'المصروفات', subCategory: 'تسويق وتوزيع' },
        { id: '5205', name: 'مصروف صيانة دورية وإصلاحات تشغيلية', nature: 'debit', type: 'expense', category: 'المصروفات', subCategory: 'عمومية وإدارية' }
    ];

    let db_journal = {{ journal_json|safe }}; 
    let db_balances = {}; 
    let netProfitGlobal = 0;

    window.onload = () => {
        document.getElementById('je-date').value = new Date().toISOString().split('T')[0];
        populateSelectGrouped();
        calculateSystem();
    };

    function toggleSidebar() { 
        let sidebar = document.getElementById('sidebar');
        let overlay = document.getElementById('sidebarOverlay');
        if (window.innerWidth < 992) {
            if (sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                overlay.style.opacity = '0';
                setTimeout(() => overlay.style.display = 'none', 300);
            } else {
                overlay.style.display = 'block';
                setTimeout(() => overlay.style.opacity = '1', 10);
                sidebar.classList.add('open');
            }
        } else {
            document.body.classList.toggle('sidebar-collapsed');
        }
    }
    
    function switchTab(tabId) {
        document.querySelectorAll('.tab-content, .nav-item').forEach(el => el.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        let navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            if(item.getAttribute('onclick').includes(tabId)) item.classList.add('active');
        });
        if (window.innerWidth < 992) {
            let sidebar = document.getElementById('sidebar');
            let overlay = document.getElementById('sidebarOverlay');
            sidebar.classList.remove('open');
            overlay.style.opacity = '0';
            setTimeout(() => overlay.style.display = 'none', 300);
        }
        if(tabId === 'ledger') generateLedger();
    }

    function populateSelectGrouped() {
        const selects = document.querySelectorAll('.select-grouped');
        const grouped = {};
        accountsData.forEach(acc => {
            if(!grouped[acc.category]) grouped[acc.category] = [];
            grouped[acc.category].push(acc);
        });
        let html = '<option value="">-- اختر الحساب المالي --</option>';
        for(let cat in grouped) {
            html += `<optgroup label="[ ${cat} ]">`;
            grouped[cat].forEach(acc => { html += `<option value="${acc.id}">${acc.id} - ${acc.name}</option>`; });
            html += `</optgroup>`;
        }
        selects.forEach(select => select.innerHTML = html);
    }

    function calculateSystem() {
        db_balances = {};
        accountsData.forEach(acc => { db_balances[acc.id] = { details: acc, totalDr: 0, totalCr: 0, balance: 0 }; });

        db_journal.forEach(je => {
            if(db_balances[je.drAcc]) db_balances[je.drAcc].totalDr += je.amount;
            if(db_balances[je.crAcc]) db_balances[je.crAcc].totalCr += je.amount;
        });

        let totalAssets = 0, totalLiabilities = 0, totalRevenue = 0, totalExpense = 0, totalCogs = 0;

        Object.values(db_balances).forEach(acc => {
            if (acc.details.nature === 'debit') {
                acc.balance = acc.totalDr - acc.totalCr;
            } else {
                acc.balance = acc.totalCr - acc.totalDr;
            }
            if(acc.details.type === 'asset') totalAssets += acc.balance;
            if(acc.details.type === 'liability') totalLiabilities += acc.balance;
            if(acc.details.type === 'revenue') totalRevenue += acc.balance;
            if(acc.details.type === 'cogs') totalCogs += acc.balance;
            if(acc.details.type === 'expense') totalExpense += acc.balance;
        });

        netProfitGlobal = totalRevenue - totalCogs - totalExpense;

        document.getElementById('stat-assets').innerText = totalAssets.toFixed(2);
        document.getElementById('stat-liabilities').innerText = totalLiabilities.toFixed(2);
        document.getElementById('stat-revenue').innerText = totalRevenue.toFixed(2);
        
        let profitElement = document.getElementById('stat-net-profit');
        profitElement.innerText = netProfitGlobal.toFixed(2);
        if(netProfitGlobal >= 0) {
            document.getElementById('net-profit-card').style.borderRightColor = 'var(--color-revenue)';
            profitElement.style.color = 'var(--color-revenue)';
        } else {
            document.getElementById('net-profit-card').style.borderRightColor = 'var(--color-liability)';
            profitElement.style.color = 'var(--color-liability)';
        }

        renderUI();
        buildIncomeStatement();
        buildBalanceSheet();
    }

    function renderUI() {
        filterCOA();

        document.getElementById('journal-body').innerHTML = [...db_journal].reverse().map(je => `
            <tr>
                <td>#${je.id}</td><td>${je.date}</td><td>${je.desc}</td>
                <td style="color:var(--accent); font-weight:700;">${accountsData.find(a=>a.id===je.drAcc)?.name}</td>
                <td style="color:var(--color-liability); font-weight:700;">${accountsData.find(a=>a.id===je.crAcc)?.name}</td>
                <td class="amount">${je.amount.toFixed(2)}</td>
                <td><button class="btn btn-danger" onclick="deleteEntry(${je.id})">حذف</button></td>
            </tr>
        `).join('');

        let sumDr = 0, sumCr = 0, sumBalDr = 0, sumBalCr = 0;
        document.getElementById('tb-body').innerHTML = Object.values(db_balances).filter(a => a.totalDr > 0 || a.totalCr > 0).map(acc => {
            let balDr = acc.details.nature === 'debit' && acc.balance > 0 ? acc.balance : (acc.details.nature === 'credit' && acc.balance < 0 ? Math.abs(acc.balance) : 0);
            let balCr = acc.details.nature === 'credit' && acc.balance > 0 ? acc.balance : (acc.details.nature === 'debit' && acc.balance < 0 ? Math.abs(acc.balance) : 0);
            
            sumDr += acc.totalDr; sumCr += acc.totalCr;
            sumBalDr += balDr; sumBalCr += balCr;

            return `<tr>
                <td>${acc.details.id}</td><td>${acc.details.name}</td>
                <td class="amount">${acc.totalDr > 0 ? acc.totalDr.toFixed(2) : '-'}</td>
                <td class="amount">${acc.totalCr > 0 ? acc.totalCr.toFixed(2) : '-'}</td>
                <td class="amount" style="color:var(--accent);">${balDr > 0 ? balDr.toFixed(2) : '-'}</td>
                <td class="amount" style="color:var(--color-liability);">${balCr > 0 ? balCr.toFixed(2) : '-'}</td>
            </tr>`;
        }).join('');

        document.getElementById('tb-foot').innerHTML = `
            <tr style="background:#e2e8f0;">
                <td colspan="2">المجاميع الكلية:</td>
                <td class="amount">${sumDr.toFixed(2)}</td><td class="amount">${sumCr.toFixed(2)}</td>
                <td class="amount">${sumBalDr.toFixed(2)}</td><td class="amount">${sumBalCr.toFixed(2)}</td>
            </tr>
        `;
    }

    function filterCOA() {
        const query = document.getElementById('coa-search').value.toLowerCase();
        document.getElementById('coa-body').innerHTML = Object.values(db_balances).filter(acc => {
            return acc.details.name.toLowerCase().includes(query) || acc.details.id.includes(query);
        }).map(acc => `
            <tr>
                <td style="font-weight:700; font-family:monospace;">${acc.details.id}</td>
                <td style="font-weight:700;">${acc.details.name}</td>
                <td>${acc.details.nature === 'debit' ? 'مدين 🟢' : 'دائن 🔴'}</td>
                <td><span class="badge badge-${acc.details.type}">${acc.details.category}</span></td>
                <td style="color:var(--text-muted); font-size:12px;">${acc.details.subCategory}</td>
                <td class="amount">${acc.balance.toFixed(2)}</td>
            </tr>
        `).join('');
    }

    function generateLedger() {
        const accId = document.getElementById('ledger-select').value;
        if(!accId) return;
        const accInfo = accountsData.find(a => a.id === accId);
        const isDebit = accInfo.nature === 'debit';
        const tbody = document.getElementById('ledger-body');
        tbody.innerHTML = '';
        let runningBalance = 0;

        const entries = db_journal.filter(j => j.drAcc === accId || j.crAcc === accId);
        if(entries.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">لا حركات مالية مسجلة حالياً.</td></tr>';
            document.getElementById('ledger-final-balance').innerText = 'الرصيد الحسابي: 0.00'; return;
        }

        entries.forEach(je => {
            let dr = je.drAcc === accId ? je.amount : 0;
            let cr = je.crAcc === accId ? je.amount : 0;
            let oppId = je.drAcc === accId ? je.crAcc : je.drAcc;
            let oppName = accountsData.find(a => a.id === oppId)?.name || '';
            runningBalance += isDebit ? (dr - cr) : (cr - dr);

            tbody.innerHTML += `
                <tr>
                    <td>${je.date}</td><td>#${je.id}</td>
                    <td>${je.desc} <br><small style="color:var(--text-muted)">الحساب المقابل: ${oppName}</small></td>
                    <td class="amount" style="color:var(--accent);">${dr > 0 ? dr.toFixed(2) : '-'}</td>
                    <td class="amount" style="color:var(--color-liability);">${cr > 0 ? cr.toFixed(2) : '-'}</td>
                    <td class="amount" style="font-weight:700;">${runningBalance.toFixed(2)}</td>
                </tr>
            `;
        });
        document.getElementById('ledger-final-balance').innerText = `الرصيد الختامي: ${runningBalance.toFixed(2)}`;
    }

    function buildIncomeStatement() {
        const tbody = document.getElementById('is-body');
        tbody.innerHTML = '';
        let revenues = Object.values(db_balances).filter(a => a.details.type === 'revenue');
        let cogs = Object.values(db_balances).filter(a => a.details.type === 'cogs');
        let expenses = Object.values(db_balances).filter(a => a.details.type === 'expense');

        let totalRev = revenues.reduce((sum, a) => sum + a.balance, 0);
        let totalCogs = cogs.reduce((sum, a) => sum + a.balance, 0);
        let grossProfit = totalRev - totalCogs;
        let totalExp = expenses.reduce((sum, a) => sum + a.balance, 0);
        let netIncome = grossProfit - totalExp;

        tbody.innerHTML += `<tr style="font-weight:bold; color:var(--color-revenue)"><td colspan="3">إيرادات النشاط التشغيلي والمبيعات</td></tr>`;
        revenues.forEach(a => { tbody.innerHTML += `<tr><td class="report-indent">${a.details.name}</td><td class="amount">${a.balance.toFixed(2)}</td><td></td></tr>`; });
        tbody.innerHTML += `<tr class="report-row-subtotal"><td class="report-indent">إجمالي الإيرادات الكلية</td><td></td><td class="amount">${totalRev.toFixed(2)}</td></tr>`;

        tbody.innerHTML += `<tr style="font-weight:bold; color:var(--color-cogs)"><td colspan="3">يخصم: تكلفة البضاعة والمبيعات</td></tr>`;
        cogs.forEach(a => { tbody.innerHTML += `<tr><td class="report-indent">${a.details.name}</td><td class="amount">${a.balance.toFixed(2)}</td><td></td></tr>`; });
        tbody.innerHTML += `<tr class="report-row-subtotal"><td class="report-indent">إجمالي تكاليف المبيعات</td><td></td><td class="amount">(${totalCogs.toFixed(2)})</td></tr>`;

        tbody.innerHTML += `<tr class="report-row-total" style="color:var(--color-revenue); background:#f0fdf4 !important;"><td style="font-size:14px;">إجمالي مجمل الربح للنشاط (Gross Profit)</td><td></td><td class="amount">${grossProfit.toFixed(2)}</td></tr>`;

        tbody.innerHTML += `<tr style="font-weight:bold; color:var(--color-expense)"><td colspan="3">يخصم: المصروفات التشغيلية والعمومية</td></tr>`;
        expenses.forEach(a => { tbody.innerHTML += `<tr><td class="report-indent">${a.details.name}</td><td class="amount">${a.balance.toFixed(2)}</td><td></td></tr>`; });
        tbody.innerHTML += `<tr class="report-row-subtotal"><td class="report-indent">إجمالي المصروفات الإدارية</td><td></td><td class="amount">(${totalExp.toFixed(2)})</td></tr>`;

        let finalColor = netIncome >= 0 ? 'var(--color-revenue)' : 'var(--color-liability)';
        tbody.innerHTML += `<tr class="report-row-total" style="color:${finalColor}; background:#f8fafc !important;"><td style="font-size:15px; font-weight:800;">صافي الأرباح / الخسائر النهائية (Net Income)</td><td></td><td class="amount">${netIncome.toFixed(2)}</td></tr>`;
    }

    function buildBalanceSheet() {
        const tbody = document.getElementById('bs-body');
        tbody.innerHTML = '';
        let assets = Object.values(db_balances).filter(a => a.details.type === 'asset');
        let liabilities = Object.values(db_balances).filter(a => a.details.type === 'liability');
        let equities = Object.values(db_balances).filter(a => a.details.type === 'equity');

        let totalAssets = assets.reduce((sum, a) => sum + a.balance, 0);
        let totalLiab = liabilities.reduce((sum, a) => sum + a.balance, 0);
        let totalEq = equities.reduce((sum, a) => sum + a.balance, 0);
        let totalEquitiesAndNetIncome = totalEq + netProfitGlobal; 
        let totalLiabAndEquityCombined = totalLiab + totalEquitiesAndNetIncome;

        tbody.innerHTML += `<tr style="font-weight:bold; color:var(--color-asset); background:#f0f9ff;"><td colspan="3">أولاً: جانب الأصول والموجودات (Assets)</td></tr>`;
        assets.forEach(a => { tbody.innerHTML += `<tr><td class="report-indent">${a.details.name}</td><td class="amount">${a.balance.toFixed(2)}</td><td></td></tr>`; });
        tbody.innerHTML += `<tr class="report-row-total" style="color:var(--color-asset);"><td style="font-size:14px;">إجمالي حجم الأصول الكلية</td><td></td><td class="amount">${totalAssets.toFixed(2)}</td></tr>`;

        tbody.innerHTML += `<tr style="font-weight:bold; color:var(--color-liability); background:#fff5f5;"><td colspan="3">ثانياً: جانب الالتزامات وحقوق الشركاء</td></tr>`;
        tbody.innerHTML += `<tr style="font-weight:600; color:var(--text-main);"><td class="report-indent" colspan="3">الخصوم والالتزامات للغير:</td></tr>`;
        liabilities.forEach(a => { tbody.innerHTML += `<tr><td class="report-indent" style="padding-right:45px;">${a.details.name}</td><td class="amount">${a.balance.toFixed(2)}</td><td></td></tr>`; });
        tbody.innerHTML += `<tr class="report-row-subtotal"><td class="report-indent">إجمالي الخصوم والالتزامات</td><td></td><td class="amount">${totalLiab.toFixed(2)}</td></tr>`;

        tbody.innerHTML += `<tr style="font-weight:600; color:var(--color-equity);"><td class="report-indent" colspan="3">حقوق الملكية ورأس المال:</td></tr>`;
        equities.forEach(a => { tbody.innerHTML += `<tr><td class="report-indent" style="padding-right:45px;">${a.details.name}</td><td class="amount">${a.balance.toFixed(2)}</td><td></td></tr>`; });
        tbody.innerHTML += `<tr style="font-style:italic;"><td class="report-indent" style="padding-right:45px; color:var(--color-revenue);">صافي أرباح الفترة الحالية المرحّلة</td><td class="amount" style="color:var(--color-revenue);">${netProfitGlobal.toFixed(2)}</td><td></td></tr>`;
        tbody.innerHTML += `<tr class="report-row-subtotal"><td class="report-indent">إجمالي حقوق الملكية</td><td></td><td class="amount">${totalEquitiesAndNetIncome.toFixed(2)}</td></tr>`;

        tbody.innerHTML += `<tr class="report-row-total" style="color:var(--color-equity); background:#faf5ff !important;"><td style="font-size:14px;">إجمالي الخصوم وحقوق الملكية معاً</td><td></td><td class="amount">${totalLiabAndEquityCombined.toFixed(2)}</td></tr>`;
    }

    function deleteEntry(id) {
        if(confirm("تحذير: أنت على وشك حذف قيد مرحل. تأكيد الحذف؟")) {
            window.location.href = '/delete_entry/' + id;
        }
    }

    function exportExcel(filename, tableId) {
        let table = document.getElementById(tableId);
        if (!table) return;
        let rows = table.querySelectorAll("tr");
        let csvContent = "";
        let csvData = ["\\uFEFF"]; 
        for (let i = 0; i < rows.length; i++) {
            let row = [], cols = rows[i].querySelectorAll("td, th");
            for (let j = 0; j < cols.length; j++) {
                let data = cols[j].innerText.trim().replace(/(\\r\\n|\\n|\\r)/gm, " ").replace(/,/g, "،");
                row.push(`"${data}"`);
            }
            csvContent += row.join(",") + "\\n";
        }
        csvData.push(csvContent);
        let blob = new Blob([csvData.join("")], { type: "text/csv;charset=utf-8;" });
        let link = document.createElement("a");
        link.setAttribute("href", window.URL.createObjectURL(blob));
        link.setAttribute("download", filename + "_" + new Date().toISOString().split('T')[0] + ".csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    journal_data = load_journal_data()
    return render_template_string(HTML_TEMPLATE, journal_json=json.dumps(journal_data))

@app.route('/add_entry', methods=['POST'])
def add_entry():
    date = request.form.get('je-date')
    desc = request.form.get('je-desc')
    dr_acc = request.form.get('je-dr-acc')
    cr_acc = request.form.get('je-cr-acc')
    amount = float(request.form.get('je-amount', 0))

    if desc and amount > 0 and dr_acc and cr_acc and dr_acc != cr_acc:
        journal_data = load_journal_data()
        entry_id = max([j['id'] for j in journal_data]) + 1 if journal_data else 5001
        
        new_entry = {
            "id": entry_id,
            "date": date,
            "desc": desc,
            "drAcc": dr_acc,
            "crAcc": cr_acc,
            "amount": amount
        }
        journal_data.append(new_entry)
        save_journal_data(journal_data)
        
    return redirect(url_for('index'))

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    journal_data = load_journal_data()
    journal_data = [j for j in journal_data if j['id'] != entry_id]
    save_journal_data(journal_data)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
