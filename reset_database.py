#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت إعادة تهيئة قاعدة البيانات وحل مشاكل تسجيل الدخول
"""

import os
import shutil
from datetime import datetime
from app import create_app
from models import db, User
from utils import SecurityUtils

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    db_path = 'doaei.db'
    if os.path.exists(db_path):
        backup_path = f'doaei.db.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy2(db_path, backup_path)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
        return backup_path
    return None

def reset_database():
    """إعادة تهيئة قاعدة البيانات بالكامل"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔄 بدء إعادة تهيئة قاعدة البيانات...")
        print("=" * 60)
        
        # إنشاء نسخة احتياطية
        backup_database()
        
        # حذف جميع الجداول
        print("\n🗑️  حذف الجداول القديمة...")
        db.drop_all()
        
        # إنشاء جميع الجداول من جديد
        print("📦 إنشاء الجداول الجديدة...")
        db.create_all()
        
        # إنشاء المستخدمين الافتراضيين
        print("\n👤 إنشاء المستخدمين الافتراضيين...")
        create_default_users()
        
        # حفظ التغييرات
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ تم إعادة تهيئة قاعدة البيانات بنجاح!")
        print("=" * 60)
        print("\n📋 بيانات تسجيل الدخول:")
        print("-" * 60)
        print("👨‍💼 المدير:")
        print("   البريد: admin@doaei.com")
        print("   كلمة المرور: 123456")
        print("-" * 60)
        print("👤 المرضى:")
        print("   البريد: patient@doaei.com")
        print("   كلمة المرور: 123456")
        print("-" * 60)
        print("👨‍⚕️ الأطباء:")
        print("   البريد: doctor1@doaei.com")
        print("   كلمة المرور: 123456")
        print("-" * 60)
        print("💊 الصيادلة:")
        print("   البريد: pharmacist@doaei.com")
        print("   كلمة المرور: 123456")
        print("=" * 60)

def create_default_users():
    """إنشاء المستخدمين الافتراضيين"""
    
    # كلمة المرور الموحدة لجميع المستخدمين
    default_password = '123456'
    
    users_data = [
        {
            'email': 'admin@doaei.com',
            'password': default_password,
            'full_name': 'مدير النظام',
            'role': 'user',  # role='user' يعني admin في هذا النظام
            'phone': '+966500000000',
            'is_active': True
        },
        {
            'email': 'patient@doaei.com',
            'password': default_password,
            'full_name': 'أحمد محمد المريض',
            'role': 'patient',
            'phone': '+966501234567',
            'date_of_birth': '1985-05-15',
            'gender': 'male',
            'weight': 75.5,
            'height': 175.0,
            'is_active': True
        },
        {
            'email': 'patient2@doaei.com',
            'password': default_password,
            'full_name': 'سارة علي المطيري',
            'role': 'patient',
            'phone': '+966501234568',
            'date_of_birth': '1990-08-20',
            'gender': 'female',
            'weight': 65.0,
            'height': 165.0,
            'is_active': True
        },
        {
            'email': 'patient3@doaei.com',
            'password': default_password,
            'full_name': 'محمد خالد النجار',
            'role': 'patient',
            'phone': '+966501234569',
            'date_of_birth': '1978-12-10',
            'gender': 'male',
            'weight': 82.0,
            'height': 180.0,
            'is_active': True
        },
        {
            'email': 'patient4@doaei.com',
            'password': default_password,
            'full_name': 'فاطمة سعد الخالدي',
            'role': 'patient',
            'phone': '+966501234570',
            'date_of_birth': '1995-03-25',
            'gender': 'female',
            'weight': 58.0,
            'height': 160.0,
            'is_active': True
        },
        {
            'email': 'doctor1@doaei.com',
            'password': default_password,
            'full_name': 'د. أحمد محمد العلي',
            'role': 'doctor',
            'phone': '+966502345678',
            'is_active': True
        },
        {
            'email': 'doctor2@doaei.com',
            'password': default_password,
            'full_name': 'د. فاطمة سعد الخالدي',
            'role': 'doctor',
            'phone': '+966502345679',
            'is_active': True
        },
        {
            'email': 'doctor3@doaei.com',
            'password': default_password,
            'full_name': 'د. خالد عبدالله النجار',
            'role': 'doctor',
            'phone': '+966502345680',
            'is_active': True
        },
        {
            'email': 'doctor4@doaei.com',
            'password': default_password,
            'full_name': 'د. سارة علي المطيري',
            'role': 'doctor',
            'phone': '+966502345681',
            'is_active': True
        },
        {
            'email': 'pharmacist@doaei.com',
            'password': default_password,
            'full_name': 'خالد الصيدلي',
            'role': 'pharmacist',
            'phone': '+966503456789',
            'is_active': True
        }
    ]
    
    for user_data in users_data:
        # التحقق من وجود المستخدم
        existing_user = User.query.filter_by(email=user_data['email']).first()
        
        if existing_user:
            # تحديث كلمة المرور إذا كان المستخدم موجوداً
            existing_user.password_hash = SecurityUtils.hash_password(user_data['password'])
            existing_user.is_active = True
            print(f"   ✅ تم تحديث: {user_data['email']}")
        else:
            # إنشاء مستخدم جديد
            user = User(
                email=user_data['email'],
                password_hash=SecurityUtils.hash_password(user_data['password']),
                full_name=user_data['full_name'],
                role=user_data['role'],
                phone=user_data.get('phone'),
                is_active=user_data.get('is_active', True)
            )
            
            # إضافة الحقول الاختيارية
            if 'date_of_birth' in user_data:
                from datetime import datetime
                user.date_of_birth = datetime.strptime(user_data['date_of_birth'], '%Y-%m-%d').date()
            if 'gender' in user_data:
                user.gender = user_data['gender']
            if 'weight' in user_data:
                user.weight = user_data['weight']
            if 'height' in user_data:
                user.height = user_data['height']
            
            db.session.add(user)
            print(f"   ✅ تم إنشاء: {user_data['email']}")
    
    # حفظ التغييرات
    db.session.commit()
    
    print(f"\n✅ تم إنشاء/تحديث {len(users_data)} مستخدم")

def populate_sample_data():
    """ملء قاعدة البيانات ببيانات تجريبية"""
    print("\n📊 ملء قاعدة البيانات ببيانات تجريبية...")
    
    # استيراد init_db لملء البيانات
    try:
        from init_db import create_sample_data
        import sqlite3
        
        # الاتصال بقاعدة البيانات مباشرة
        conn = sqlite3.connect('doaei.db')
        cursor = conn.cursor()
        
        # ملء البيانات التجريبية
        create_sample_data(cursor)
        
        conn.commit()
        conn.close()
        
        print("✅ تم ملء البيانات التجريبية بنجاح")
    except Exception as e:
        print(f"⚠️  تحذير: لم يتم ملء البيانات التجريبية: {e}")
        import traceback
        traceback.print_exc()
        print("   يمكنك تشغيل init_db.py لاحقاً لملء البيانات")

if __name__ == '__main__':
    try:
        reset_database()
        
        # ملء البيانات التجريبية
        print("\n" + "=" * 60)
        response = input("هل تريد ملء قاعدة البيانات ببيانات تجريبية؟ (y/n): ")
        if response.lower() == 'y':
            populate_sample_data()
        
        print("\n" + "=" * 60)
        print("🎉 اكتملت العملية بنجاح!")
        print("=" * 60)
        print("\nيمكنك الآن تسجيل الدخول باستخدام:")
        print("   البريد: admin@doaei.com")
        print("   كلمة المرور: 123456")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        import traceback
        traceback.print_exc()

