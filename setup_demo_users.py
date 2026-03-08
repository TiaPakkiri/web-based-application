"""
Setup script to create demo users in Firebase Firestore
Run this script once to populate the database with test users
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from firebase_setup import db, create_user

# Demo users to create
DEMO_USERS = [
    {
        'email': 'admin@dut.edu.za',
        'password': 'Admin@123',
        'full_name': 'Admin User',
        'role': 'admin'
    },
    {
        'email': 'student@dut.edu.za',
        'password': 'Student@123',
        'full_name': 'John Student',
        'role': 'student'
    },
    {
        'email': 'student2@dut.edu.za',
        'password': 'Student@123',
        'full_name': 'Jane Sustainable',
        'role': 'student'
    }
]

def setup_demo_users():
    """Create demo users in Firestore"""
    if not db:
        print("❌ Firebase not connected. Check your FIREBASE_ADMIN_CREDENTIAL in .env")
        return False
    
    print("\n📝 Creating demo users...\n")
    
    for user in DEMO_USERS:
        try:
            user_id = create_user(
                email=user['email'],
                password=user['password'],
                full_name=user['full_name'],
                role=user['role']
            )
            
            if user_id:
                print(f"✅ Created {user['role'].upper()}: {user['email']}")
                print(f"   Password: {user['password']}")
                print(f"   Name: {user['full_name']}\n")
            else:
                print(f"❌ Failed to create user: {user['email']}\n")
        except Exception as e:
            print(f"❌ Error creating {user['email']}: {e}\n")
    
    print("\n✨ Demo users setup complete!\n")
    print("=" * 60)
    print("ADMIN CREDENTIALS:")
    print("=" * 60)
    print(f"Email:    admin@dut.edu.za")
    print(f"Password: Admin@123")
    print(f"Role:     Admin")
    print("\n" + "=" * 60)
    print("STUDENT CREDENTIALS:")
    print("=" * 60)
    print(f"Email:    student@dut.edu.za")
    print(f"Password: Student@123")
    print(f"Role:     Student")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    setup_demo_users()
