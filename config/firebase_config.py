import firebase_admin
from firebase_admin import credentials, db
import os

class FirebaseConfig:
    _initialized = False
    
    @classmethod
    def initialize(cls, credential_path='serviceAccountKey.json', database_url=None):
        if cls._initialized:
            return
        
        try:
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url or os.getenv('FIREBASE_DATABASE_URL')
            })
            cls._initialized = True
            print("✅ Firebase initialized")
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            raise
    
    @staticmethod
    def get_reference(path):
        return db.reference(path)
