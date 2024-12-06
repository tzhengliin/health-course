import os
import json
from flask import Flask, render_template, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import bcrypt

# 載入 .env 檔案
load_dotenv()

# 讀取 FIREBASE_SERVICE_KEY
firebase_service_key = os.getenv("FIREBASE_SERVICE_KEY")
if not firebase_service_key:
    raise ValueError("FIREBASE_SERVICE_KEY is not set or empty")

try:
    service_account_info = json.loads(firebase_service_key)
    print("Service account successfully loaded!")
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    raise

app = Flask(__name__)

# 從環境變數讀取 Firebase 憑證內容
cred = credentials.Certificate(service_account_info)
initialize_app(cred)

# 初始化 Firestore 資料庫
db = firestore.client()

# 路由：主頁，顯示學員清單
@app.route('/')
def index():
    student_docs = db.collection('studentData').stream()
    students = []
    for doc in student_docs:
        data = doc.to_dict()
        data['id'] = doc.id  # 文件 ID，便於操作詳情
        students.append(data)
    return render_template('index.html', students=students)

# 路由：新增學員資料
@app.route('/students', methods=['POST'])
def add_student():
    print('addstudent')
    data = request.json
    student_id = data.get('name')  
    if not student_id:
        print('Student ID is required')
        return jsonify({"error": "Student ID is required"}), 400

    student_ref = db.collection('studentData').document(student_id)
    if student_ref.get().exists:
        print('Student ID already exists')
        return jsonify({"error": "Student ID already exists"}), 400

    student_data = {
        'name': data.get('name'),
        'coach': data.get('coach'),
        'start': data.get('start'),
        'end': data.get('end'),
        'recipe': data.get('recipe'),
    }
    student_ref.set(student_data)
    return jsonify({"message": "Student added successfully"}), 201

# 路由：修改學員資料
@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    student_ref = db.collection('studentData').document(student_id)
    if not student_ref.get().exists:
        return jsonify({"error": "Student not found"}), 404

    data = request.json
    updated_data = {
        'name': data.get('name'),
        'coach': data.get('coach'),
        'start': data.get('start'),
        'end': data.get('end'),
        'recipe': data.get('recipe'),
    }
    student_ref.update(updated_data)
    return jsonify({"message": "Student updated successfully"}), 200

# 路由：刪除學員資料
@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    student_ref = db.collection('studentData').document(student_id)
    if not student_ref.get().exists:
        return jsonify({"error": "Student not found"}), 404

    student_ref.delete()
    return jsonify({"message": "Student deleted successfully"}), 200

# 路由：獲取學員詳細資訊
@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student_ref = db.collection('studentData').document(student_id)
    student = student_ref.get()
    if not student.exists:
        return jsonify({"error": "Student not found"}), 404

    student_data = student.to_dict()
    student_data['id'] = student.id
    return jsonify(student_data), 200

# 路由：獲取所有學員資料
@app.route('/students', methods=['GET'])
def get_students():
    students = []
    student_docs = db.collection('studentData').stream()
    for student in student_docs:
        student_data = student.to_dict()
        student_data['id'] = student.id  # 包含文件 ID
        students.append(student_data)
    return jsonify(students), 200

# 路由：註冊
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    account = data.get('account')
    password = data.get('password')

    # 檢查帳號是否已存在
    user_ref = db.collection('users').document(account).get()
    if user_ref.exists:
        return jsonify({"error": "Account already exists"}), 400

    # 加密密碼
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # 將使用者資訊存入 Firestore，文件 ID 為 account
    db.collection('users').document(account).set({
        'account': account,
        'password': hashed_password.decode('utf-8')
    })

    return jsonify({"message": "Registration successful"}), 201

# 路由：登入
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    account = data.get('account')
    password = data.get('password')

    # 查找使用者
    user_ref = db.collection('users').document(account).get()
    if not user_ref.exists:
        return jsonify({"error": "Invalid account or password"}), 400

    user_data = user_ref.to_dict()

    # 驗證密碼
    if not bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
        return jsonify({"error": "Invalid account or password"}), 400

    return jsonify({"message": "Login successful"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
