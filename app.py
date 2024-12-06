import os
import json
from flask import Flask, render_template, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

app = Flask(__name__)

# 從環境變數讀取 Firebase 憑證內容
service_account_info = json.loads(os.getenv("FIREBASE_SERVICE_KEY"))
cred = credentials.Certificate(service_account_info)
initialize_app(cred)

db = firestore.client()


# 首頁路由
@app.route('/')
def index():
    # 從 Firestore 獲取所有學員資料
    student_docs = db.collection('studentData').stream()
    students = []
    for doc in student_docs:
        data = doc.to_dict()
        data['id'] = doc.id  # 包含文件 ID，便於操作詳情
        students.append(data)
    return render_template('index.html', students=students)

# API：獲取學員詳細資訊
@app.route('/student/<student_id>', methods=['GET'])
def get_student(student_id):
    try:
        doc = db.collection('studentData').document(student_id).get()
        if doc.exists:
            return jsonify(doc.to_dict()), 200
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 部署測試頁面
@app.route('/health')
def health():
    return "Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
