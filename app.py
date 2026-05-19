import os
import sqlite3
import csv
from io import StringIO
from flask import Flask, request, jsonify, Response, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # للسماح لتطبيق الهاتف بالاتصال بالسيرفر دون قيود حماية المتصفح

# إعداد قاعدة البيانات المركزية
DB_NAME = "central_erp_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            dr_acc TEXT,
            cr_acc TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

ACCOUNTS = [
    {"id": "1101", "name": "الصندوق الرئيسي", "nature": "debit", "type": "asset"},
    {"id": "1102", "name": "البنك", "nature": "debit", "type": "asset"},
    {"id": "1103", "name": "العملاء", "nature": "debit", "type": "asset"},
    {"id": "2101", "name": "الموردون", "nature": "credit", "type": "liability"},
    {"id": "3101", "name": "رأس المال", "nature": "credit", "type": "equity"},
    {"id": "4101", "name": "إيرادات المبيعات", "nature": "credit", "type": "revenue"},
    {"id": "5101", "name": "مصروفات الرواتب", "nature": "debit", "type": "expense"}
]

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "ERP Cloud Server is running perfectly."})

# 1. جلب شجرة الحسابات
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify(ACCOUNTS)

# 2. جلب كافة القيود
@app.route('/api/journal', methods=['GET'])
def get_journal():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM journal ORDER BY id DESC")
    entries = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(entries)

# 3. إضافة قيد محاسبي جديد مع التحقق من صحته
@app.route('/api/journal', methods=['POST'])
def add_journal():
    data = request.json
    if not data or not all(k in data for k in ('date', 'desc', 'drAcc', 'crAcc', 'amount')):
        return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400
    
    if data['drAcc'] == data['crAcc']:
        return jsonify({"status": "error", "message": "خطأ محاسبي: الطرف المدين والدائن متطابقان"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO journal (date, description, dr_acc, cr_acc, amount) VALUES (?, ?, ?, ?, ?)",
              (data['date'], data['desc'], data['drAcc'], data['crAcc'], float(data['amount'])))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "تم تسجيل القيد بنجاح"})

# 4. حذف قيد يومية
@app.route('/api/journal/<int:entry_id>', methods=['DELETE'])
def delete_journal(entry_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM journal WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "تم حذف القيد"})

# 5. تصدير التقارير بصيغة Excel/CSV متوافقة مع الهواتف
@app.route('/api/export')
def export_journal():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, date, description, dr_acc, cr_acc, amount FROM journal")
    rows = c.fetchall()
    conn.close()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['رقم القيد', 'التاريخ', 'البيان', 'الطرف المدين', 'الطرف الدائن', 'المبلغ'])
    cw.writerows(rows)
    
    output = si.getvalue().encode('utf-8-sig')
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=erp_report.csv"}
    )

if __name__ == '__main__':
    # التشغيل على منفذ 8080 ليتوافق مع الخوادم السحابية بسهولة
    app.run(host='0.0.0.0', port=8080, debug=True)
