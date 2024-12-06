import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase Admin
cred = credentials.Certificate("serviceToken.json")
firebase_admin.initialize_app(cred)

# 初始化 Firestore 資料庫
db = firestore.client()

# 列出所有集合及其文件的資料
collections = db.collections()

for collection in collections:
    print(f"Collection: {collection.id}")
    docs = collection.stream()
    for doc in docs:
        print(f"  Document ID: {doc.id}, Data: {doc.to_dict()}")