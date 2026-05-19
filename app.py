import os
from flask import Flask, render_template_string, request, redirect, url_for
import json

app = Flask(__name__)

# مسار ملف حفظ البيانات بشكل دائم وثابت داخل سيرفر Render
DATA_FILE = '/opt/render/project/src/accounting_data.json' if os.path.exists('/opt/render/project/src/') else 'accounting_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"entries": [], "accounts": {"الصندوق": 0, "البنك": 0, "المشتريات": 0, "المبيعات": 0, "رأس المال": 0}}
    return {"entries": [], "accounts": {"الصندوق": 0, "البنك": 0, "المشتريات": 0, "المبيعات": 0, "رأس المال": 0}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# التصميم الفاخر والكامل للواجهة المحاسبية الموحدة بدعم كامل للعملة المحلية
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام ERP المحاسبي الذكي الموحد</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background-color: #1e1b4b !important; }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 12px; }
        .table-th { background-color: #1e1b4b; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="#">📁 نظام ERP المحاسبي الموحد الذكي</a>
        </div>
    </nav>

    <div class="container">
        <div class="row mb-4">
            {% for account, balance in data.accounts.items() %}
            <div class="col-md-2 col-sm-4 mb-2">
                <div class="card p-3 text-center">
                    <h6 class="text-muted">{{ account }}</h6>
                    <h5 class="text-primary fw-bold">{{ balance }} <small>R.Y</small></h5>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card p-4">
                    <h5 class="mb-3 text-dark fw-bold">📝 تسجيل قيد يومية جديد</h5>
                    <form action="/add_entry" method="POST">
                        <div class="mb-3">
                            <label class="form-label">البيان / الشرح</label>
                            <input type="text" name="description" class="form-control" placeholder="مثال: شراء بضاعة نقداً" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الحساب المدين (من حساب)</label>
                            <select name="debit_acc" class="form-select">
                                {% for acc in data.accounts.keys() %} <option value="{{ acc }}">{{ acc }}</option> {% endfor %}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">الحساب الدائن (إلى حساب)</label>
                            <select name="credit_acc" class="form-select">
                                {% for acc in data.accounts.keys() %} <option value="{{ acc }}">{{ acc }}</option> {% endfor %}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">المبلغ (R.Y)</label>
                            <input type="number" name="amount" class="form-control" min="1" placeholder="ادخل المبلغ بالريال اليمني" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100" style="background-color: #1e1b4b; border: none;">حفظ العملية وقيدها بشكل دائم</button>
                    </form>
                </div>
            </div>

            <div class="col-md-8">
                <div class="card p-4 mb-4">
                    <h5 class="mb-3 text-dark fw-bold">📋 دفتر اليومية العام والعمليات المسجلة</h5>
                    <div class="table-responsive">
                        <table class="table table-bordered table-striped text-center">
                            <thead class="table-dark">
                                <tr>
                                    <th>رقم القيد</th>
                                    <th>البيان</th>
                                    <th>من حـ/ (مدين)</th>
                                    <th>إلى حـ/ (دائن)</th>
                                    <th>المبلغ (R.Y)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% if not data.entries %}
                                <tr><td colspan="5" class="text-muted">لا توجد عمليات مسجلة حالياً.</td></tr>
                                {% endif %}
                                {% for entry in data.entries %}
                                <tr>
                                    <td>{{ entry.id }}</td>
                                    <td>{{ entry.description }}</td>
                                    <td class="table-success">{{ entry.debit }}</td>
                                    <td class="table-warning">{{ entry.credit }}</td>
                                    <td class="fw-bold text-dark">{{ entry.amount }} R.Y</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, data=data)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    description = request.form.get('description')
    debit_acc = request.form.get('debit_acc')
    credit_acc = request.form.get('credit_acc')
    amount = float(request.form.get('amount', 0))

    if amount > 0 and debit_acc != credit_acc:
        data = load_data()
        entry_id = len(data['entries']) + 1
        
        # إنشاء القيد وإضافته للدفتر
        new_entry = {
            "id": entry_id,
            "description": description,
            "debit": debit_acc,
            "credit": credit_acc,
            "amount": amount
        }
        data['entries'].append(new_entry)
        
        # التأثير التلقائي والمباشر على أرصدة الحسابات
        data['accounts'][debit_acc] += amount
        data['accounts'][credit_acc] -= amount
        
        save_data(data)
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
