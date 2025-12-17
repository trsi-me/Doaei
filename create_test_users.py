#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء مستخدمين تجريبيين
"""

from app import create_app
from models import User, db
from utils import SecurityUtils

def create_test_users():
    app = create_app()
    
    with app.app_context():
        # إنشاء المستخدمين التجريبيين
        test_users = [
            {
                'email': 'admin@doaei.com',
                'password': 'admin123',
                'full_name': 'مدير النظام',
                'role': 'admin',
                'phone': '+966501234567'
            },
            {
                'email': 'patient@example.com',
                'password': 'patient123',
                'full_name': 'مريض تجريبي',
                'role': 'patient',
                'phone': '+966501234568'
            },
            {
                'email': 'doctor@example.com',
                'password': 'doctor123',
                'full_name': 'طبيب تجريبي',
                'role': 'doctor',
                'phone': '+966501234569'
            },
            {
                'email': 'pharmacist@example.com',
                'password': 'pharmacist123',
                'full_name': 'صيدلي تجريبي',
                'role': 'pharmacist',
                'phone': '+966501234570'
            }
        ]
        
        print("=== إنشاء المستخدمين التجريبيين ===")
        
        for user_data in test_users:
            # التحقق من وجود المستخدم
            existing_user = User.query.filter_by(email=user_data['email']).first()
            
            if existing_user:
                print(f"المستخدم {user_data['email']} موجود بالفعل")
                continue
            
            # إنشاء مستخدم جديد
            user = User(
                email=user_data['email'],
                password_hash=SecurityUtils.hash_password(user_data['password']),
                full_name=user_data['full_name'],
                role=user_data['role'],
                phone=user_data['phone'],
                is_active=True
            )
            
            db.session.add(user)
            print(f"تم إنشاء المستخدم: {user_data['email']}")
        
        # حفظ التغييرات
        db.session.commit()
        print("\nتم حفظ جميع المستخدمين بنجاح!")
        
        # عرض المستخدمين
        print("\n=== المستخدمون في قاعدة البيانات ===")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}")

if __name__ == "__main__":
    create_test_users()