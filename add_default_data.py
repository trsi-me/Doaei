#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# إضافة البيانات الافتراضية إلى قاعدة البيانات الموجودة

import sqlite3
import os
from datetime import datetime, timedelta, time

def add_default_data():
    """إضافة البيانات الافتراضية إلى قاعدة البيانات"""
    db_path = 'doaei.db'
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة!")
        print("يرجى تشغيل init_db.py أولاً لإنشاء قاعدة البيانات")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # التحقق من وجود جدول users
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ جدول users غير موجود في قاعدة البيانات!")
            print("يرجى تشغيل init_db.py أولاً لإنشاء قاعدة البيانات والجداول")
            return False
        
        import bcrypt
        
        # كلمة المرور الموحدة لجميع المستخدمين
        UNIFIED_PASSWORD = ''
        password_hash = bcrypt.hashpw(UNIFIED_PASSWORD.encode('utf-8'), bcrypt.gensalt())
        
        print("🔧 تحديث كلمات المرور وإضافة البيانات الافتراضية...")
        
        # التحقق من وجود المستخدمين قبل التحديث
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            # تحديث كلمات المرور لجميع المستخدمين الموجودين
            cursor.execute("UPDATE users SET password_hash = ?", (password_hash.decode('utf-8'),))
            print("✅ تم توحيد كلمات المرور لجميع المستخدمين ")
        else:
            print("⚠️ لا توجد مستخدمين في قاعدة البيانات. سيتم إنشاء المستخدمين الافتراضيين...")
        
        # إضافة المستخدمين الافتراضيين
        users_data = [
            {
                'email': 'admin@doaei.com',
                'full_name': 'System Administrator',
                'role': 'user',
                'phone': '+966500000000'
            },
            {
                'email': 'patient@doaei.com',
                'full_name': 'أحمد محمد المريض',
                'role': 'patient',
                'phone': '+966501234567',
                'date_of_birth': '1985-05-15',
                'gender': 'male',
                'weight': 75.5,
                'height': 175.0,
                'chronic_diseases': 'Diabetes, High Blood Pressure',
                'drug_allergies': 'Penicillin'
            },
            {
                'email': 'patient2@doaei.com',
                'full_name': 'سارة علي المطيري',
                'role': 'patient',
                'phone': '+966501234568',
                'date_of_birth': '1990-08-20',
                'gender': 'female',
                'weight': 65.0,
                'height': 165.0,
                'chronic_diseases': 'Asthma',
                'drug_allergies': 'None'
            },
            {
                'email': 'patient3@doaei.com',
                'full_name': 'محمد خالد النجار',
                'role': 'patient',
                'phone': '+966501234569',
                'date_of_birth': '1978-12-10',
                'gender': 'male',
                'weight': 82.0,
                'height': 180.0,
                'chronic_diseases': 'Hypertension',
                'drug_allergies': 'Sulfa drugs'
            },
            {
                'email': 'patient4@doaei.com',
                'full_name': 'فاطمة سعد الخالدي',
                'role': 'patient',
                'phone': '+966501234570',
                'date_of_birth': '1995-03-25',
                'gender': 'female',
                'weight': 58.0,
                'height': 160.0,
                'chronic_diseases': 'None',
                'drug_allergies': 'None'
            },
            {
                'email': 'doctor1@doaei.com',
                'full_name': 'د. أحمد محمد العلي',
                'role': 'doctor',
                'phone': '+966502345678'
            },
            {
                'email': 'doctor2@doaei.com',
                'full_name': 'د. فاطمة سعد الخالدي',
                'role': 'doctor',
                'phone': '+966502345679'
            },
            {
                'email': 'doctor3@doaei.com',
                'full_name': 'د. خالد عبدالله النجار',
                'role': 'doctor',
                'phone': '+966502345680'
            },
            {
                'email': 'doctor4@doaei.com',
                'full_name': 'د. سارة علي المطيري',
                'role': 'doctor',
                'phone': '+966502345681'
            },
            {
                'email': 'pharmacist@doaei.com',
                'full_name': 'خالد الصيدلي',
                'role': 'pharmacist',
                'phone': '+966503456789'
            }
        ]
        
        # إضافة أو تحديث المستخدمين
        for user_data in users_data:
            cursor.execute("SELECT id FROM users WHERE email = ?", (user_data['email'],))
            existing = cursor.fetchone()
            
            if existing:
                # تحديث المستخدم الموجود
                cursor.execute('''
                    UPDATE users SET 
                        password_hash = ?, full_name = ?, role = ?, phone = ?,
                        date_of_birth = ?, gender = ?, weight = ?, height = ?,
                        chronic_diseases = ?, drug_allergies = ?, is_active = 1
                    WHERE email = ?
                ''', (
                    password_hash.decode('utf-8'),
                    user_data['full_name'],
                    user_data['role'],
                    user_data['phone'],
                    user_data.get('date_of_birth'),
                    user_data.get('gender'),
                    user_data.get('weight'),
                    user_data.get('height'),
                    user_data.get('chronic_diseases'),
                    user_data.get('drug_allergies'),
                    user_data['email']
                ))
                print(f"🔄 تم تحديث: {user_data['full_name']} ({user_data['email']})")
            else:
                # إضافة مستخدم جديد
                cursor.execute('''
                    INSERT INTO users 
                    (email, password_hash, full_name, role, phone, date_of_birth, 
                     gender, weight, height, chronic_diseases, drug_allergies, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['email'],
                    password_hash.decode('utf-8'),
                    user_data['full_name'],
                    user_data['role'],
                    user_data['phone'],
                    user_data.get('date_of_birth'),
                    user_data.get('gender'),
                    user_data.get('weight'),
                    user_data.get('height'),
                    user_data.get('chronic_diseases'),
                    user_data.get('drug_allergies'),
                    1
                ))
                print(f"✅ تم إضافة: {user_data['full_name']} ({user_data['email']})")
        
        # تحديث البريد الإلكتروني من @example.com إلى @doaei.com
        cursor.execute("SELECT id, email FROM users WHERE email LIKE '%@example.com'")
        old_emails = cursor.fetchall()
        for user_id, old_email in old_emails:
            new_email = old_email.replace('@example.com', '@doaei.com')
            # التحقق من عدم وجود البريد الجديد
            cursor.execute("SELECT id FROM users WHERE email = ?", (new_email,))
            if not cursor.fetchone():
                cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
                print(f"✅ تم تحديث البريد: {old_email} → {new_email}")
            else:
                # البريد الجديد موجود، حذف القديم
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                print(f"⚠️ تم حذف المستخدم المكرر: {old_email}")
        
        conn.commit()
        
        # الحصول على معرفات المرضى والأطباء والصيدلي
        cursor.execute("SELECT id FROM users WHERE role = 'patient' ORDER BY id")
        patients = cursor.fetchall()
        patient_ids = [p[0] for p in patients]
        
        cursor.execute("SELECT id FROM users WHERE role = 'doctor' ORDER BY id")
        doctors = cursor.fetchall()
        doctor_ids = [d[0] for d in doctors]
        
        cursor.execute("SELECT id FROM users WHERE role = 'pharmacist' LIMIT 1")
        pharmacist_result = cursor.fetchone()
        pharmacist_id = pharmacist_result[0] if pharmacist_result else None
        
        # إضافة الأدوية الافتراضية لكل مريض
        print("\n🔧 إضافة الأدوية الافتراضية...")
        default_medications = [
            # Patient 1 medications
            [
                {'name': 'Metformin', 'form': 'tablets', 'dosage': '500mg', 'frequency': 'twice daily', 'duration_days': 30, 'quantity': 60, 'notes': 'Take with food'},
                {'name': 'Aspirin', 'form': 'tablets', 'dosage': '100mg', 'frequency': 'once daily', 'duration_days': 90, 'quantity': 90, 'notes': 'Take after breakfast'}
            ],
            # Patient 2 medications
            [
                {'name': 'Ventolin', 'form': 'inhaler', 'dosage': '100mcg', 'frequency': 'as needed', 'duration_days': 365, 'quantity': 1, 'notes': 'Use during asthma attacks'},
                {'name': 'Vitamin D', 'form': 'tablets', 'dosage': '1000 IU', 'frequency': 'once daily', 'duration_days': 90, 'quantity': 90, 'notes': 'Take with meal'}
            ],
            # Patient 3 medications
            [
                {'name': 'Lisinopril', 'form': 'tablets', 'dosage': '10mg', 'frequency': 'once daily', 'duration_days': 90, 'quantity': 90, 'notes': 'Take in the morning'},
                {'name': 'Amlodipine', 'form': 'tablets', 'dosage': '5mg', 'frequency': 'once daily', 'duration_days': 90, 'quantity': 90, 'notes': 'Take with water'}
            ],
            # Patient 4 medications
            [
                {'name': 'Multivitamin', 'form': 'tablets', 'dosage': '1 tablet', 'frequency': 'once daily', 'duration_days': 60, 'quantity': 60, 'notes': 'Take with breakfast'},
                {'name': 'Calcium', 'form': 'tablets', 'dosage': '500mg', 'frequency': 'twice daily', 'duration_days': 90, 'quantity': 180, 'notes': 'Take with meals'}
            ]
        ]
        
        for idx, patient_id in enumerate(patient_ids[:4]):
            if idx < len(default_medications):
                medications_data = default_medications[idx]
                for med_data in medications_data:
                    cursor.execute('''
                        SELECT id FROM medications 
                        WHERE user_id = ? AND name = ? AND dosage = ?
                    ''', (patient_id, med_data['name'], med_data['dosage']))
                    if not cursor.fetchone():
                        cursor.execute('''
                            INSERT INTO medications 
                            (user_id, name, form, dosage, frequency, duration_days, 
                             start_date, quantity, notes, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            patient_id,
                            med_data['name'],
                            med_data['form'],
                            med_data['dosage'],
                            med_data['frequency'],
                            med_data['duration_days'],
                            datetime.now().date(),
                            med_data['quantity'],
                            med_data['notes'],
                            1
                        ))
                print(f"✅ تم إضافة أدوية للمريض {idx + 1}")
        
        # إضافة الاستشارات الافتراضية لكل مريض
        print("\n🔧 إضافة الاستشارات الافتراضية...")
        if pharmacist_id:
            default_consultations = [
                # Patient 1 consultations
                [
                    {
                        'subject': 'استفسار عن دواء الميتفورمين',
                        'message': 'أريد معرفة ما إذا كان يمكنني تناول الميتفورمين مع دواء الضغط؟ وهل هناك أي آثار جانبية يجب أن أكون على علم بها؟',
                        'status': 'replied',
                        'reply': 'نعم، يمكنك تناول الميتفورمين مع دواء الضغط. الميتفورمين آمن بشكل عام، لكن قد يسبب بعض الآثار الجانبية مثل اضطراب المعدة. يُنصح بتناوله مع الطعام لتقليل هذه الآثار.'
                    },
                    {
                        'subject': 'استفسار عن جرعة الأسبرين',
                        'message': 'ما هي الجرعة المناسبة من الأسبرين يومياً؟ وهل يجب تناوله في الصباح أم المساء؟',
                        'status': 'pending'
                    }
                ],
                # Patient 2 consultations
                [
                    {
                        'subject': 'استخدام بخاخ الفنتولين',
                        'message': 'متى يجب استخدام بخاخ الفنتولين؟ وهل يمكن استخدامه قبل ممارسة الرياضة؟',
                        'status': 'replied',
                        'reply': 'يُستخدم بخاخ الفنتولين عند الحاجة أثناء نوبات الربو أو ضيق التنفس. يمكن استخدامه قبل ممارسة الرياضة إذا كنت تعاني من الربو الناجم عن التمارين، لكن يُفضل استشارة طبيبك أولاً.'
                    },
                    {
                        'subject': 'جرعة فيتامين د',
                        'message': 'هل جرعة 1000 وحدة دولية من فيتامين د مناسبة؟ ومتى أفضل وقت لتناوله؟',
                        'status': 'replied',
                        'reply': 'نعم، جرعة 1000 وحدة دولية مناسبة للبالغين. يُفضل تناوله مع وجبة تحتوي على دهون لتحسين الامتصاص. يمكن تناوله في أي وقت من اليوم.'
                    }
                ],
                # Patient 3 consultations
                [
                    {
                        'subject': 'تفاعل الأدوية',
                        'message': 'أتناول دواء ليزينوبريل وأملوديبين معاً. هل هذا آمن؟',
                        'status': 'replied',
                        'reply': 'نعم، يمكن تناول ليزينوبريل وأملوديبين معاً. في الواقع، غالباً ما يتم وصفهما معاً لعلاج ارتفاع ضغط الدم. تأكد من مراقبة ضغط الدم بانتظام وإبلاغ طبيبك بأي آثار جانبية.'
                    },
                    {
                        'subject': 'آثار جانبية لدواء الضغط',
                        'message': 'أشعر بدوخة بعد تناول دواء الضغط. هل هذا طبيعي؟',
                        'status': 'pending'
                    }
                ],
                # Patient 4 consultations
                [
                    {
                        'subject': 'الفيتامينات المتعددة',
                        'message': 'هل يمكنني تناول الفيتامينات المتعددة مع الكالسيوم في نفس الوقت؟',
                        'status': 'replied',
                        'reply': 'نعم، يمكن تناول الفيتامينات المتعددة مع الكالسيوم، لكن يُفضل تناولهما مع وجبات مختلفة لتحسين الامتصاص. يمكن تناول الفيتامينات المتعددة مع الإفطار والكالسيوم مع وجبة أخرى.'
                    },
                    {
                        'subject': 'مكملات الكالسيوم',
                        'message': 'ما هي أفضل طريقة لتناول مكملات الكالسيوم؟',
                        'status': 'pending'
                    }
                ]
            ]
            
            for idx, patient_id in enumerate(patient_ids[:4]):
                if idx < len(default_consultations):
                    consultations_data = default_consultations[idx]
                    for cons_data in consultations_data:
                        cursor.execute('''
                            INSERT OR IGNORE INTO consultations 
                            (patient_id, pharmacist_id, subject, message, status, reply, replied_at, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            patient_id,
                            pharmacist_id,
                            cons_data['subject'],
                            cons_data['message'],
                            cons_data['status'],
                            cons_data.get('reply'),
                            datetime.now() if cons_data.get('reply') else None,
                            datetime.now() - timedelta(days=idx*2)
                        ))
                    print(f"✅ تم إضافة استشارات للمريض {idx + 1}")
        
        # إضافة التقييمات الافتراضية لكل مريض
        print("\n🔧 إضافة التقييمات الافتراضية...")
        if doctor_ids:
            default_evaluations = [
                # Patient 1 evaluations
                [
                    {
                        'evaluation_type': 'routine',
                        'symptoms': 'ارتفاع في مستوى السكر، تعب عام، عطش مستمر',
                        'diagnosis': 'داء السكري من النوع الثاني - يحتاج متابعة',
                        'vital_signs': '{"blood_pressure": "140/90", "temperature": "36.8", "heart_rate": "78", "blood_sugar": "180"}',
                        'physical_examination': 'الوزن: 75.5 كجم، الطول: 175 سم، مؤشر كتلة الجسم: 24.7',
                        'recommendations': 'متابعة نظام غذائي صحي، ممارسة الرياضة بانتظام، فحص السكر يومياً',
                        'next_visit_date': (datetime.now() + timedelta(days=30)).date()
                    },
                    {
                        'evaluation_type': 'follow_up',
                        'symptoms': 'تحسن في مستوى السكر، لكن لا يزال يحتاج متابعة',
                        'diagnosis': 'داء السكري من النوع الثاني - تحت السيطرة',
                        'vital_signs': '{"blood_pressure": "135/85", "temperature": "36.7", "heart_rate": "75", "blood_sugar": "145"}',
                        'recommendations': 'الاستمرار في الأدوية الموصوفة، متابعة النظام الغذائي',
                        'next_visit_date': (datetime.now() + timedelta(days=60)).date()
                    }
                ],
                # Patient 2 evaluations
                [
                    {
                        'evaluation_type': 'routine',
                        'symptoms': 'ضيق في التنفس عند ممارسة الرياضة، سعال جاف',
                        'diagnosis': 'ربو خفيف - تحت السيطرة',
                        'vital_signs': '{"blood_pressure": "120/80", "temperature": "36.5", "heart_rate": "82", "oxygen_saturation": "96%"}',
                        'physical_examination': 'الوزن: 65 كجم، الطول: 165 سم، مؤشر كتلة الجسم: 23.9، صوت صفير خفيف في الصدر',
                        'recommendations': 'استخدام بخاخ الفنتولين عند الحاجة، تجنب مسببات الحساسية',
                        'next_visit_date': (datetime.now() + timedelta(days=45)).date()
                    }
                ],
                # Patient 3 evaluations
                [
                    {
                        'evaluation_type': 'routine',
                        'symptoms': 'صداع متكرر، دوخة أحياناً',
                        'diagnosis': 'ارتفاع ضغط الدم - يحتاج متابعة',
                        'vital_signs': '{"blood_pressure": "150/95", "temperature": "36.9", "heart_rate": "88"}',
                        'physical_examination': 'الوزن: 82 كجم، الطول: 180 سم، مؤشر كتلة الجسم: 25.3',
                        'recommendations': 'تقليل الملح في الطعام، ممارسة الرياضة، متابعة ضغط الدم يومياً',
                        'next_visit_date': (datetime.now() + timedelta(days=30)).date()
                    },
                    {
                        'evaluation_type': 'follow_up',
                        'symptoms': 'تحسن في ضغط الدم بعد استخدام الأدوية',
                        'diagnosis': 'ارتفاع ضغط الدم - تحت السيطرة',
                        'vital_signs': '{"blood_pressure": "130/85", "temperature": "36.8", "heart_rate": "80"}',
                        'recommendations': 'الاستمرار في الأدوية، متابعة ضغط الدم',
                        'next_visit_date': (datetime.now() + timedelta(days=60)).date()
                    }
                ],
                # Patient 4 evaluations
                [
                    {
                        'evaluation_type': 'routine',
                        'symptoms': 'تعب عام، نقص في الطاقة',
                        'diagnosis': 'نقص فيتامينات - يحتاج مكملات',
                        'vital_signs': '{"blood_pressure": "110/70", "temperature": "36.6", "heart_rate": "72"}',
                        'physical_examination': 'الوزن: 58 كجم، الطول: 160 سم، مؤشر كتلة الجسم: 22.7',
                        'lab_results': 'نقص في فيتامين د والكالسيوم',
                        'recommendations': 'تناول مكملات الفيتامينات والكالسيوم، التعرض لأشعة الشمس',
                        'next_visit_date': (datetime.now() + timedelta(days=90)).date()
                    }
                ]
            ]
            
            for idx, patient_id in enumerate(patient_ids[:4]):
                if idx < len(default_evaluations):
                    evaluations_data = default_evaluations[idx]
                    for eval_idx, eval_data in enumerate(evaluations_data):
                        doctor_id = doctor_ids[eval_idx % len(doctor_ids)]
                        cursor.execute('''
                            INSERT OR IGNORE INTO evaluations 
                            (patient_id, doctor_id, evaluation_date, evaluation_type, symptoms, 
                             diagnosis, vital_signs, physical_examination, lab_results, recommendations, 
                             next_visit_date, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            patient_id,
                            doctor_id,
                            datetime.now().date() - timedelta(days=eval_idx*15),
                            eval_data['evaluation_type'],
                            eval_data.get('symptoms'),
                            eval_data.get('diagnosis'),
                            eval_data.get('vital_signs'),
                            eval_data.get('physical_examination'),
                            eval_data.get('lab_results'),
                            eval_data.get('recommendations'),
                            eval_data.get('next_visit_date'),
                            datetime.now() - timedelta(days=eval_idx*15)
                        ))
                    print(f"✅ تم إضافة تقييمات للمريض {idx + 1}")
        
        # إضافة بيانات مالية افتراضية
        print("\n💰 إضافة البيانات المالية الافتراضية...")
        
        # التحقق من وجود جداول incomes و expenses
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incomes'")
        if cursor.fetchone():
            # إضافة دخل افتراضي
            admin_user = cursor.execute("SELECT id FROM users WHERE role='user' LIMIT 1").fetchone()
            admin_id = admin_user[0] if admin_user else None
            
            if admin_id:
                default_incomes = [
                    ('مبيعات الطلبات', 'إيرادات من مبيعات الأدوية والمنتجات', 50000.0, 'sales', 'منصة دوائي', 
                     (datetime.now() - timedelta(days=30)).date(), 'bank_transfer', 'INC001'),
                    ('اشتراكات المستخدمين', 'إيرادات من الاشتراكات الشهرية', 15000.0, 'subscriptions', 'منصة دوائي',
                     (datetime.now() - timedelta(days=15)).date(), 'bank_transfer', 'INC002'),
                    ('خدمات الاستشارات', 'إيرادات من خدمات الاستشارات الطبية', 8000.0, 'services', 'منصة دوائي',
                     datetime.now().date(), 'bank_transfer', 'INC003'),
                ]
                
                for income in default_incomes:
                    cursor.execute('''
                        INSERT OR IGNORE INTO incomes 
                        (title, description, amount, category, source, transaction_date, payment_method, reference_number, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (*income, admin_id))
                
                print(f"✅ تم إضافة {len(default_incomes)} سجل دخل افتراضي")
        
        # إضافة مصروفات افتراضية
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        if cursor.fetchone() and admin_id:
            default_expenses = [
                ('رواتب الموظفين', 'رواتب شهرية للموظفين', 25000.0, 'salaries', 'الموارد البشرية',
                 datetime.now().date(), 'bank_transfer', 'EXP001', None),
                ('إيجار المكتب', 'إيجار المكتب الشهري', 5000.0, 'rent', 'مالك العقار',
                 datetime.now().date(), 'bank_transfer', 'EXP002', None),
                ('فواتير الكهرباء والماء', 'فواتير المرافق العامة', 2000.0, 'utilities', 'شركة الكهرباء',
                 (datetime.now() - timedelta(days=5)).date(), 'bank_transfer', 'EXP003', None),
                ('مستلزمات مكتبية', 'شراء مستلزمات مكتبية', 1500.0, 'supplies', 'متجر القرطاسية',
                 (datetime.now() - timedelta(days=10)).date(), 'cash', 'EXP004', None),
                ('تسويق وإعلان', 'حملات تسويقية وإعلانية', 3000.0, 'marketing', 'وكالة الإعلان',
                 (datetime.now() - timedelta(days=20)).date(), 'bank_transfer', 'EXP005', None),
            ]
            
            for expense in default_expenses:
                cursor.execute('''
                    INSERT OR IGNORE INTO expenses 
                    (title, description, amount, category, vendor, transaction_date, payment_method, reference_number, receipt_url, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (*expense, admin_id))
            
            print(f"✅ تم إضافة {len(default_expenses)} سجل مصروف افتراضي")
    
        # إضافة أقسام وموظفين افتراضيين
        print("\n👥 إضافة الأقسام والموظفين الافتراضيين...")
        
        # التحقق من وجود جداول departments و employees
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
        if cursor.fetchone():
            # إضافة أقسام افتراضية
            default_departments = [
                ('قسم الإدارة', 'إدارة شؤون المنصة والتخطيط الاستراتيجي', None, 100000.0),
                ('قسم التطوير', 'تطوير وصيانة المنصة التقنية', None, 150000.0),
                ('قسم المبيعات', 'إدارة المبيعات والتسويق', None, 80000.0),
                ('قسم الدعم الفني', 'دعم العملاء وحل المشاكل التقنية', None, 60000.0),
                ('قسم الموارد البشرية', 'إدارة شؤون الموظفين والتوظيف', None, 70000.0),
            ]
            
            department_ids = {}
            for dept_name, dept_desc, manager_id, budget in default_departments:
                cursor.execute('''
                    INSERT OR IGNORE INTO departments 
                    (name, description, manager_id, budget, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dept_name, dept_desc, manager_id, budget, 1))
                dept_id = cursor.lastrowid
                if dept_id == 0:
                    cursor.execute("SELECT id FROM departments WHERE name = ?", (dept_name,))
                    result = cursor.fetchone()
                    if result:
                        dept_id = result[0]
                department_ids[dept_name] = dept_id
            
            print(f"✅ تم إضافة {len(default_departments)} قسم افتراضي")
            
            # إضافة موظفين افتراضيين
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
            if cursor.fetchone():
                # الحصول على معرفات المستخدمين (الأطباء والصيادلة)
                cursor.execute("SELECT id, full_name, role FROM users WHERE role IN ('doctor', 'pharmacist') ORDER BY id")
                users_for_employees = cursor.fetchall()
                
                if users_for_employees:
                    default_employees = []
                    employee_counter = 1
                    
                    for user_id, user_name, user_role in users_for_employees[:8]:  # استخدام أول 8 مستخدمين
                        if user_role == 'doctor':
                            position = 'طبيب استشاري'
                            dept_name = 'قسم الإدارة' if employee_counter <= 2 else 'قسم التطوير'
                        else:
                            position = 'صيدلي'
                            dept_name = 'قسم المبيعات' if employee_counter <= 2 else 'قسم الدعم الفني'
                        
                        dept_id = department_ids.get(dept_name)
                        employee_number = f'EMP{employee_counter:03d}'
                        hire_date = (datetime.now() - timedelta(days=365 + employee_counter*30)).date()
                        salary = 8000.0 + (employee_counter * 500)
                        
                        default_employees.append((
                            user_id, dept_id, employee_number, position, hire_date, 
                            salary, 'full_time', 'active', None, None, None, None
                        ))
                        employee_counter += 1
                    
                    for emp_data in default_employees:
                        cursor.execute('''
                            INSERT OR IGNORE INTO employees 
                            (user_id, department_id, employee_number, position, hire_date, 
                             salary, employment_type, status, manager_id, phone_extension, 
                             office_location, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', emp_data)
                    
                    print(f"✅ تم إضافة {len(default_employees)} موظف افتراضي")
        
        # إضافة تقييمات افتراضية للأطباء والصيادلة
        print("\n⭐ إضافة تقييمات للأطباء والصيادلة...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reviews'")
        if cursor.fetchone():
            # التحقق من وجود الأعمدة الجديدة doctor_id و pharmacist_id
            cursor.execute("PRAGMA table_info(reviews)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'doctor_id' not in columns:
                cursor.execute("ALTER TABLE reviews ADD COLUMN doctor_id INTEGER")
                print("✅ تمت إضافة عمود doctor_id إلى جدول reviews")
            
            if 'pharmacist_id' not in columns:
                cursor.execute("ALTER TABLE reviews ADD COLUMN pharmacist_id INTEGER")
                print("✅ تمت إضافة عمود pharmacist_id إلى جدول reviews")
            
            # الحصول على معرفات المرضى
            cursor.execute("SELECT id FROM users WHERE role = 'patient' LIMIT 4")
            patients = [row[0] for row in cursor.fetchall()]
            
            # الحصول على معرفات الأطباء
            cursor.execute("SELECT id FROM users WHERE role = 'doctor' LIMIT 4")
            doctors = [row[0] for row in cursor.fetchall()]
            
            # الحصول على معرفات الصيادلة
            cursor.execute("SELECT id FROM users WHERE role = 'pharmacist' LIMIT 1")
            pharmacists = [row[0] for row in cursor.fetchall()]
            
            doctor_reviews_added = 0
            pharmacist_reviews_added = 0
            
            if patients and doctors:
                # تقييمات للأطباء من المرضى المختلفين
                doctor_reviews_data = [
                    # تقييمات للطبيب الأول
                    (patients[0], doctors[0], 5, 'طبيب ممتاز', 'د. أحمد طبيب متميز وحريص جداً على المرضى. استفدت كثيراً من استشارته.', 1),
                    (patients[1], doctors[0], 4, 'تجربة جيدة', 'طبيب جيد ويعطي وقتاً كافياً للمريض. أنصح به.', 1),
                    (patients[2], doctors[0], 5, 'احترافية عالية', 'الدكتور محترف جداً وذو خبرة واسعة. شكراً لك دكتور.', 1),
                ]
                
                if len(doctors) > 1:
                    doctor_reviews_data.extend([
                        (patients[0], doctors[1], 4, 'طبيب موثوق', 'د. محمد طبيب موثوق ويشرح الحالة بوضوح.', 1),
                        (patients[1], doctors[1], 5, 'ممتاز في التشخيص', 'التشخيص دقيق والعلاج فعال. شكراً دكتور.', 1),
                        (patients[3], doctors[1], 5, 'أفضل طبيب', 'أفضل طبيب زرته. أنصح بزيارته بشدة.', 1),
                    ])
                
                if len(doctors) > 2:
                    doctor_reviews_data.extend([
                        (patients[0], doctors[2], 5, 'خدمة رائعة', 'د. سارة رائعة في التعامل مع المرضى وتعطي اهتماماً كبيراً.', 1),
                        (patients[2], doctors[2], 4, 'تجربة إيجابية', 'تجربة إيجابية بشكل عام. الدكتورة متعاونة جداً.', 1),
                        (patients[3], doctors[2], 5, 'طبيبة متميزة', 'طبيبة متميزة وذات أخلاق عالية. جزاها الله خيراً.', 1),
                    ])
                
                if len(doctors) > 3:
                    doctor_reviews_data.extend([
                        (patients[1], doctors[3], 4, 'خبرة واسعة', 'د. فاطمة لديها خبرة واسعة ومعرفة شاملة.', 1),
                        (patients[2], doctors[3], 5, 'ممتازة', 'ممتازة في التعامل والتشخيص. أنصح بها.', 1),
                        (patients[3], doctors[3], 4, 'جيدة جداً', 'طبيبة جيدة جداً وسريعة في الرد على الاستفسارات.', 1),
                    ])
                
                for review_data in doctor_reviews_data:
                    try:
                        cursor.execute('''
                            INSERT INTO reviews 
                            (user_id, doctor_id, rating, title, comment, is_active)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', review_data)
                        doctor_reviews_added += 1
                    except:
                        pass  # تجاهل الأخطاء إذا كان التقييم موجوداً بالفعل
                
                print(f"✅ تم إضافة {doctor_reviews_added} تقييم للأطباء")
            
            if patients and pharmacists:
                # تقييمات للصيدلي من المرضى المختلفين
                pharmacist_reviews_data = [
                    (patients[0], pharmacists[0], 5, 'صيدلي ممتاز', 'صيدلي محترف ويقدم استشارات دوائية ممتازة. شكراً له.', 1),
                    (patients[1], pharmacists[0], 5, 'خدمة رائعة', 'الصيدلي متعاون جداً ويشرح طريقة استخدام الأدوية بوضوح.', 1),
                    (patients[2], pharmacists[0], 4, 'تجربة جيدة', 'صيدلي جيد وسريع في الرد على الاستفسارات الدوائية.', 1),
                    (patients[3], pharmacists[0], 5, 'احترافي', 'صيدلي احترافي ولديه معرفة واسعة بالأدوية. أنصح به.', 1),
                ]
                
                for review_data in pharmacist_reviews_data:
                    try:
                        cursor.execute('''
                            INSERT INTO reviews 
                            (user_id, pharmacist_id, rating, title, comment, is_active)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', review_data)
                        pharmacist_reviews_added += 1
                    except:
                        pass  # تجاهل الأخطاء إذا كان التقييم موجوداً بالفعل
                
                print(f"✅ تم إضافة {pharmacist_reviews_added} تقييم للصيادلة")
        
        conn.commit()
        print("\n✅ تم إضافة جميع البيانات الافتراضية بنجاح!")
        print(f"📋 كلمة المرور الموحدة غير منشورة")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إضافة البيانات: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("إضافة البيانات الافتراضية إلى قاعدة البيانات")
    print("=" * 60)
    add_default_data()
    print("=" * 60)
