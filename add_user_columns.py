#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add missing columns to users table
"""

import sqlite3
import os

def add_user_columns():
    """إضافة الأعمدة المفقودة إلى جدول users"""
    
    db_path = 'doaei.db'
    
    if not os.path.exists(db_path):
        print(f"خطأ: قاعدة البيانات {db_path} غير موجودة!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # قائمة الأعمدة المطلوب إضافتها
        columns_to_add = [
            ('address', 'TEXT'),
            ('city', 'VARCHAR(100)'),
            ('postal_code', 'VARCHAR(20)'),
            ('medical_conditions', 'TEXT'),
            ('allergies', 'TEXT'),
            ('emergency_contact', 'VARCHAR(255)'),
            ('language', 'VARCHAR(10) DEFAULT "ar"'),
            ('timezone', 'VARCHAR(50) DEFAULT "Asia/Riyadh"'),
            ('email_notifications', 'BOOLEAN DEFAULT 1'),
            ('sms_notifications', 'BOOLEAN DEFAULT 0'),
            ('last_login', 'TIMESTAMP'),
            ('avatar_url', 'VARCHAR(500)')
        ]
        
        # التحقق من الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # إضافة الأعمدة المفقودة فقط
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    alter_sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                    cursor.execute(alter_sql)
                    print(f"✓ تم إضافة العمود: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"✗ خطأ في إضافة العمود {column_name}: {e}")
            else:
                print(f"- العمود {column_name} موجود بالفعل")
        
        conn.commit()
        print("\nتم تحديث قاعدة البيانات بنجاح!")
        return True
        
    except Exception as e:
        print(f"خطأ: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("بدء تحديث قاعدة البيانات...")
    print("=" * 50)
    success = add_user_columns()
    print("=" * 50)
    if success:
        print("تم التحديث بنجاح!")
    else:
        print("فشل التحديث!")

