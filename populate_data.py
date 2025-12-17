#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت ملء قاعدة البيانات بالبيانات التجريبية
"""

import sqlite3
from init_db import create_sample_data

def populate_database():
    """ملء قاعدة البيانات بالبيانات التجريبية"""
    print("=" * 60)
    print("📊 ملء قاعدة البيانات بالبيانات التجريبية...")
    print("=" * 60)
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('doaei.db')
        cursor = conn.cursor()
        
        print("\n✅ تم الاتصال بقاعدة البيانات")
        
        # ملء البيانات التجريبية
        print("\n📦 جاري ملء البيانات...")
        create_sample_data(cursor)
        
        # حفظ التغييرات
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ تم ملء قاعدة البيانات بالبيانات التجريبية بنجاح!")
        print("=" * 60)
        print("\n📋 البيانات التي تم إضافتها:")
        print("   ✅ المستخدمون (مرضى، أطباء، صيادلة)")
        print("   ✅ الصيدليات")
        print("   ✅ المنتجات")
        print("   ✅ الأدوية")
        print("   ✅ الاستشارات")
        print("   ✅ التقييمات الطبية")
        print("   ✅ المراجعات")
        print("   ✅ المواعيد")
        print("   ✅ البيانات المالية (دخل ومصروفات)")
        print("   ✅ الأقسام والموظفين")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    populate_database()

