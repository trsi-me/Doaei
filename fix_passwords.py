#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت إصلاح كلمات المرور للمستخدمين الموجودين
"""

from app import create_app
from models import db, User
from utils import SecurityUtils

def fix_all_passwords():
    """إصلاح كلمات المرور لجميع المستخدمين"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔧 إصلاح كلمات المرور...")
        print("=" * 60)
        
        # كلمة المرور الموحدة
        default_password = ''
        
        # الحصول على جميع المستخدمين
        users = User.query.all()
        
        if not users:
            print("⚠️  لا يوجد مستخدمون في قاعدة البيانات!")
            print("   يرجى تشغيل reset_database.py لإعادة تهيئة قاعدة البيانات")
            return
        
        print(f"\n📋 تم العثور على {len(users)} مستخدم")
        print("-" * 60)
        
        # تحديث كلمات المرور
        updated_count = 0
        for user in users:
            try:
                # تحديث كلمة المرور
                user.password_hash = SecurityUtils.hash_password(default_password)
                user.is_active = True  # التأكد من تفعيل الحساب
                db.session.add(user)
                updated_count += 1
                print(f"   ✅ تم تحديث: {user.email} ({user.role})")
            except Exception as e:
                print(f"   ❌ خطأ في تحديث {user.email}: {e}")
        
        # حفظ التغييرات
        try:
            db.session.commit()
            print("-" * 60)
            print(f"✅ تم تحديث {updated_count} مستخدم بنجاح!")
            print("=" * 60)
            print("\n📋 كلمة المرور الموحدة غير منشورة")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ خطأ في حفظ التغييرات: {e}")

def create_missing_users():
    """إنشاء المستخدمين المفقودين"""
    app = create_app()
    
    with app.app_context():
        print("\n👤 التحقق من المستخدمين المفقودين...")
        
        default_password = ''
        
        required_users = [
            {
                'email': 'admin@doaei.com',
                'full_name': 'مدير النظام',
                'role': 'user',  # admin role
                'phone': '+966500000000'
            },
            {
                'email': 'patient@doaei.com',
                'full_name': 'أحمد محمد المريض',
                'role': 'patient',
                'phone': '+966501234567'
            },
            {
                'email': 'doctor1@doaei.com',
                'full_name': 'د. أحمد محمد العلي',
                'role': 'doctor',
                'phone': '+966502345678'
            },
            {
                'email': 'pharmacist@doaei.com',
                'full_name': 'خالد الصيدلي',
                'role': 'pharmacist',
                'phone': '+966503456789'
            }
        ]
        
        created_count = 0
        for user_data in required_users:
            existing = User.query.filter_by(email=user_data['email']).first()
            if not existing:
                user = User(
                    email=user_data['email'],
                    password_hash=SecurityUtils.hash_password(default_password),
                    full_name=user_data['full_name'],
                    role=user_data['role'],
                    phone=user_data['phone'],
                    is_active=True
                )
                db.session.add(user)
                created_count += 1
                print(f"   ✅ تم إنشاء: {user_data['email']}")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✅ تم إنشاء {created_count} مستخدم جديد")
        else:
            print("   ✅ جميع المستخدمين المطلوبين موجودون")

if __name__ == '__main__':
    try:
        fix_all_passwords()
        create_missing_users()
        
        print("\n" + "=" * 60)
        print("🎉 اكتملت العملية بنجاح!")
        print("=" * 60)
        print("\nيمكنك الآن تسجيل الدخول باستخدام:")
        print("   كلمة المرور الموحدة غير منشورة")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        import traceback
        traceback.print_exc()

