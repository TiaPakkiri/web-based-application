import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
import os
from functools import wraps
from flask import session, redirect, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase if credentials are provided
firebase_admin_cred = os.getenv('FIREBASE_ADMIN_CREDENTIAL')
if firebase_admin_cred:
    try:
        cred = credentials.Certificate(firebase_admin_cred)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✓ Firebase connected successfully")
    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        print("Running in demo mode without Firebase")
        db = None
else:
    print("FIREBASE_ADMIN_CREDENTIAL not set. Running in demo mode.")
    db = None

# Role-based access control decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') != required_role:
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# User management functions
def create_user(email, password, full_name, role='student'):
    """Create a new user in Firestore"""
    if not db:
        return None
    
    try:
        user_ref = db.collection('users').add({
            'email': email,
            'full_name': full_name,
            'role': role,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return user_ref[1].id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user(email):
    """Get user by email from Firestore"""
    if not db:
        return None
    
    try:
        users = db.collection('users').where('email', '==', email).stream()
        for user in users:
            return {'id': user.id, **user.to_dict()}
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def update_user_role(user_id, new_role):
    """Update user role"""
    if not db:
        return False
    
    try:
        db.collection('users').document(user_id).update({
            'role': new_role,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"Error updating user role: {e}")
        return False
