#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Doaei Platform - Database Initialization
# Electronic Medicine Management System

import sqlite3
import os
from datetime import datetime, timedelta, time

def init_database():
    # Initialize database and create tables
    
    # Create database directory if not exists
    os.makedirs('database', exist_ok=True)
    
    # Connect to database
    db_path = 'doaei.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read schema.sql file and create tables
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Remove comments
        lines = []
        for line in schema_sql.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('--'):
                lines.append(line)
        
        schema_sql = '\n'.join(lines)
        
        # Execute using executescript - it handles multiple statements
        cursor.executescript(schema_sql)
        
        # Create default admin user
        create_default_admin(cursor)
        
        # Create sample data always (not just in development)
        create_sample_data(cursor)
        
        conn.commit()
        print("Database created successfully!")
        print(f"Database path : {os.path.abspath(db_path)}")
        
    except Exception as e:
        print(f"Error creating database : {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def create_default_admin(cursor):
    # Create default admin user
    import bcrypt
    
    # Unified password removed from source
    password_hash = bcrypt.hashpw(''.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute('''
        INSERT OR IGNORE INTO users 
        (email, password_hash, full_name, role, phone, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        'admin@doaei.com',
        password_hash.decode('utf-8'),
        'System Administrator',
        'user',
        '+966500000000',
        1
    ))
    
    print("Created default admin user:")
    print("   Email : admin@doaei.com")
    print("   Password :")

def create_sample_data(cursor):
    # Create sample data for development
    import bcrypt
    
    # Create sample users
    users_data = [
        {
            'email': 'patient@doaei.com',
            'password': '',
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
            'password': '',
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
            'password': '',
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
            'password': '',
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
            'password': '',
            'full_name': 'د. أحمد محمد العلي',
            'role': 'doctor',
            'phone': '+966502345678'
        },
        {
            'email': 'doctor2@doaei.com',
            'password': '',
            'full_name': 'د. فاطمة سعد الخالدي',
            'role': 'doctor',
            'phone': '+966502345679'
        },
        {
            'email': 'doctor3@doaei.com',
            'password': '',
            'full_name': 'د. خالد عبدالله النجار',
            'role': 'doctor',
            'phone': '+966502345680'
        },
        {
            'email': 'doctor4@doaei.com',
            'password': '',
            'full_name': 'د. سارة علي المطيري',
            'role': 'doctor',
            'phone': '+966502345681'
        },
        {
            'email': 'pharmacist@doaei.com',
            'password': '',
            'full_name': 'خالد الصيدلي',
            'role': 'pharmacist',
            'phone': '+966503456789'
        }
    ]
    
    # Create sample pharmacies
    pharmacies_data = [
        {
            'name': 'صيدلية النور',
            'address': 'الرياض، حي العليا',
            'phone': '+966112345678',
            'email': 'noor@pharmacy.com',
            'city': 'الرياض',
            'is_active': 1
        },
        {
            'name': 'صيدلية الشفاء',
            'address': 'جدة، حي الزهراء',
            'phone': '+966122345678',
            'email': 'shifa@pharmacy.com',
            'city': 'جدة',
            'is_active': 1
        },
        {
            'name': 'صيدلية الحياة',
            'address': 'الدمام، حي الفيصلية',
            'phone': '+966133456789',
            'email': 'hayat@pharmacy.com',
            'city': 'الدمام',
            'is_active': 1
        },
        {
            'name': 'صيدلية الأمل',
            'address': 'المدينة المنورة، حي العقيق',
            'phone': '+966144567890',
            'email': 'amal@pharmacy.com',
            'city': 'المدينة المنورة',
            'is_active': 1
        },
        {
            'name': 'صيدلية الصحة',
            'address': 'الرياض، حي المطار',
            'phone': '+966115678901',
            'email': 'seha@pharmacy.com',
            'city': 'الرياض',
            'is_active': 1
        }
    ]
    
    for pharm_data in pharmacies_data:
        cursor.execute('''
            INSERT OR IGNORE INTO pharmacies 
            (name, address, phone, email, city, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pharm_data['name'],
            pharm_data['address'],
            pharm_data['phone'],
            pharm_data['email'],
            pharm_data['city'],
            pharm_data['is_active'],
            datetime.now()
        ))
    
    print("Created sample pharmacies")
    
    # Get pharmacy IDs for products
    cursor.execute("SELECT id FROM pharmacies")
    pharmacy_ids_list = [row[0] for row in cursor.fetchall()]
    
    # Create sample pharmacy products
    products_data = [
        {'name': 'Metformin', 'generic_name': 'Metformin HCl', 'form': 'tablet', 'strength': '500mg', 'price': 25.50, 'stock_quantity': 100},
        {'name': 'Aspirin', 'generic_name': 'Acetylsalicylic Acid', 'form': 'tablet', 'strength': '100mg', 'price': 15.00, 'stock_quantity': 200},
        {'name': 'Ventolin', 'generic_name': 'Salbutamol', 'form': 'inhaler', 'strength': '100mcg', 'price': 45.00, 'stock_quantity': 50},
        {'name': 'Vitamin D', 'generic_name': 'Cholecalciferol', 'form': 'tablet', 'strength': '1000 IU', 'price': 30.00, 'stock_quantity': 150},
        {'name': 'Lisinopril', 'generic_name': 'Lisinopril', 'form': 'tablet', 'strength': '10mg', 'price': 35.00, 'stock_quantity': 80},
        {'name': 'Amlodipine', 'generic_name': 'Amlodipine Besylate', 'form': 'tablet', 'strength': '5mg', 'price': 28.00, 'stock_quantity': 90},
        {'name': 'Multivitamin', 'generic_name': 'Multivitamin Complex', 'form': 'tablet', 'strength': '1 tablet', 'price': 40.00, 'stock_quantity': 120},
        {'name': 'Calcium', 'generic_name': 'Calcium Carbonate', 'form': 'tablet', 'strength': '500mg', 'price': 20.00, 'stock_quantity': 180}
    ]
    
    for prod_data in products_data:
        for pharmacy_id in pharmacy_ids_list[:2]:  # Add to first 2 pharmacies
            cursor.execute('''
                INSERT OR IGNORE INTO pharmacy_products 
                (pharmacy_id, name, generic_name, form, strength, price, stock_quantity, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pharmacy_id,
                prod_data['name'],
                prod_data['generic_name'],
                prod_data['form'],
                prod_data['strength'],
                prod_data['price'],
                prod_data['stock_quantity'],
                1,
                datetime.now()
            ))
    
    print("Created sample pharmacy products")
    
    for user_data in users_data:
        password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute('''
            INSERT OR IGNORE INTO users 
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
    
    # Get all patient IDs
    cursor.execute("SELECT id, email FROM users WHERE role = 'patient'")
    patients = cursor.fetchall()
    
    # Default medications for all patients (different medications for each patient)
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
    
    # Create medications for each patient
    for idx, (patient_id, patient_email) in enumerate(patients):
        if idx < len(default_medications):
            medications_data = default_medications[idx]
            for med_data in medications_data:
                # التحقق من وجود الدواء أولاً
                cursor.execute('''
                    SELECT id FROM medications 
                    WHERE user_id = ? AND name = ? AND dosage = ?
                ''', (patient_id, med_data['name'], med_data['dosage']))
                existing = cursor.fetchone()
                
                if not existing:
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
            print(f"Created medications for patient {patient_email}")
    
    if patients:
        print(f"Created default medications for {len(patients)} patients")
    else:
        print("No patients found, skipping sample medications")
    
    # Get pharmacist ID
    cursor.execute("SELECT id FROM users WHERE role = 'pharmacist' LIMIT 1")
    pharmacist_result = cursor.fetchone()
    pharmacist_id = pharmacist_result[0] if pharmacist_result else None
    
    # Get doctor IDs
    cursor.execute("SELECT id FROM users WHERE role = 'doctor'")
    doctors = cursor.fetchall()
    doctor_ids = [doc[0] for doc in doctors] if doctors else []
    
    # Default consultations for all patients (different consultations for each patient)
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
    
    # Create consultations for each patient
    for idx, (patient_id, patient_email) in enumerate(patients):
        if idx < len(default_consultations) and pharmacist_id:
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
                    datetime.now() - timedelta(days=idx*2)  # Different dates for each patient
                ))
            print(f"Created consultations for patient {patient_email}")
    
    # Default evaluations for all patients (different evaluations for each patient)
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
    
    # Create evaluations for each patient
    for idx, (patient_id, patient_email) in enumerate(patients):
        if idx < len(default_evaluations) and doctor_ids:
            evaluations_data = default_evaluations[idx]
            # Use different doctor for each evaluation
            for eval_idx, eval_data in enumerate(evaluations_data):
                doctor_id = doctor_ids[eval_idx % len(doctor_ids)] if doctor_ids else None
                if doctor_id:
                    cursor.execute('''
                        INSERT OR IGNORE INTO evaluations 
                        (patient_id, doctor_id, evaluation_date, evaluation_type, symptoms, 
                         diagnosis, vital_signs, physical_examination, lab_results, recommendations, 
                         next_visit_date, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        patient_id,
                        doctor_id,
                        datetime.now().date() - timedelta(days=eval_idx*15),  # Different dates
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
            print(f"Created evaluations for patient {patient_email}")
    
    # Get pharmacy IDs for reviews
    cursor.execute("SELECT id FROM pharmacies LIMIT 5")
    pharmacies = cursor.fetchall()
    pharmacy_ids = [ph[0] for ph in pharmacies] if pharmacies else []
    
    # Get product IDs for reviews
    cursor.execute("SELECT id FROM pharmacy_products LIMIT 10")
    products = cursor.fetchall()
    product_ids = [prod[0] for prod in products] if products else []
    
    # Default reviews for all patients (different reviews for each patient)
    default_reviews = [
        # Patient 1 reviews
        [
            {
                'pharmacy_id': pharmacy_ids[0] if pharmacy_ids else None,
                'product_id': None,
                'rating': 5,
                'title': 'صيدلية ممتازة',
                'comment': 'خدمة ممتازة وتوصيل سريع. الصيادلة محترفون ومتعاونون جداً.'
            },
            {
                'pharmacy_id': None,
                'product_id': product_ids[0] if product_ids else None,
                'rating': 4,
                'title': 'دواء فعال',
                'comment': 'دواء الميتفورمين ساعدني كثيراً في التحكم في السكر. أنصح به.'
            }
        ],
        # Patient 2 reviews
        [
            {
                'pharmacy_id': pharmacy_ids[1] if len(pharmacy_ids) > 1 else pharmacy_ids[0] if pharmacy_ids else None,
                'product_id': None,
                'rating': 5,
                'title': 'خدمة رائعة',
                'comment': 'بخاخ الفنتولين متوفر دائماً والخدمة ممتازة. شكراً لكم.'
            },
            {
                'pharmacy_id': None,
                'product_id': product_ids[1] if len(product_ids) > 1 else product_ids[0] if product_ids else None,
                'rating': 5,
                'title': 'فيتامين د ممتاز',
                'comment': 'فيتامين د عالي الجودة وسعره معقول. أنصح به بشدة.'
            }
        ],
        # Patient 3 reviews
        [
            {
                'pharmacy_id': pharmacy_ids[2] if len(pharmacy_ids) > 2 else pharmacy_ids[0] if pharmacy_ids else None,
                'product_id': None,
                'rating': 4,
                'title': 'صيدلية جيدة',
                'comment': 'الأدوية متوفرة والأسعار مناسبة. التوصيل سريع.'
            },
            {
                'pharmacy_id': None,
                'product_id': product_ids[2] if len(product_ids) > 2 else product_ids[0] if product_ids else None,
                'rating': 4,
                'title': 'دواء الضغط فعال',
                'comment': 'ليزينوبريل ساعدني في خفض ضغط الدم. أشعر بتحسن كبير.'
            }
        ],
        # Patient 4 reviews
        [
            {
                'pharmacy_id': pharmacy_ids[3] if len(pharmacy_ids) > 3 else pharmacy_ids[0] if pharmacy_ids else None,
                'product_id': None,
                'rating': 5,
                'title': 'أفضل صيدلية',
                'comment': 'خدمة ممتازة ومهنية. الصيادلة يقدمون استشارات مفيدة.'
            },
            {
                'pharmacy_id': None,
                'product_id': product_ids[3] if len(product_ids) > 3 else product_ids[0] if product_ids else None,
                'rating': 5,
                'title': 'مكملات ممتازة',
                'comment': 'الفيتامينات المتعددة والكالسيوم عالية الجودة. أنصح بها.'
            }
        ]
    ]
    
    # Create reviews for each patient
    for idx, (patient_id, patient_email) in enumerate(patients):
        if idx < len(default_reviews):
            reviews_data = default_reviews[idx]
            for review_data in reviews_data:
                if review_data['pharmacy_id'] or review_data['product_id']:
                    cursor.execute('''
                        INSERT OR IGNORE INTO reviews 
                        (user_id, pharmacy_id, product_id, rating, title, comment, is_active, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        patient_id,
                        review_data['pharmacy_id'],
                        review_data['product_id'],
                        review_data['rating'],
                        review_data['title'],
                        review_data['comment'],
                        1,
                        datetime.now() - timedelta(days=idx*3)  # Different dates
                    ))
            print(f"Created reviews for patient {patient_email}")
    
    # Default product ratings for all patients (different ratings for each patient)
    default_product_ratings = [
        # Patient 1 product ratings
        [
            {'product_name': 'Metformin', 'rating': 5, 'review': 'دواء ممتاز للتحكم في السكر. أنصح به بشدة.'},
            {'product_name': 'Aspirin', 'rating': 4, 'review': 'مفيد للقلب والدورة الدموية.'}
        ],
        # Patient 2 product ratings
        [
            {'product_name': 'Ventolin', 'rating': 5, 'review': 'بخاخ فعال جداً لنوبات الربو. أنقذ حياتي عدة مرات.'},
            {'product_name': 'Vitamin D', 'rating': 5, 'review': 'فيتامين د عالي الجودة. أشعر بتحسن كبير.'}
        ],
        # Patient 3 product ratings
        [
            {'product_name': 'Lisinopril', 'rating': 4, 'review': 'دواء فعال لضغط الدم. آثار جانبية قليلة.'},
            {'product_name': 'Amlodipine', 'rating': 4, 'review': 'يساعد في خفض ضغط الدم بشكل جيد.'}
        ],
        # Patient 4 product ratings
        [
            {'product_name': 'Multivitamin', 'rating': 5, 'review': 'مكمل غذائي شامل وممتاز. أنصح به.'},
            {'product_name': 'Calcium', 'rating': 5, 'review': 'كالسيوم عالي الجودة. مفيد للعظام.'}
        ]
    ]
    
    # Create product ratings for each patient
    for idx, (patient_id, patient_email) in enumerate(patients):
        if idx < len(default_product_ratings):
            ratings_data = default_product_ratings[idx]
            for rating_data in ratings_data:
                cursor.execute('''
                    INSERT OR IGNORE INTO product_ratings 
                    (user_id, product_name, rating, review, is_verified, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id,
                    rating_data['product_name'],
                    rating_data['rating'],
                    rating_data['review'],
                    1,
                    datetime.now() - timedelta(days=idx*2)  # Different dates
                ))
            print(f"Created product ratings for patient {patient_email}")
    
    # Default appointments for all patients (different appointments for each patient)
    default_appointments = [
        # Patient 1 appointments
        [
            {
                'appointment_date': (datetime.now() + timedelta(days=7)).date(),
                'appointment_time': time(10, 0),
                'appointment_type': 'routine',
                'status': 'scheduled',
                'reason': 'فحص دوري لمتابعة حالة السكري',
                'notes': 'يرجى إحضار نتائج فحوصات السكر الأخيرة'
            },
            {
                'appointment_date': (datetime.now() + timedelta(days=30)).date(),
                'appointment_time': time(14, 30),
                'appointment_type': 'follow_up',
                'status': 'scheduled',
                'reason': 'متابعة العلاج',
                'notes': 'مراجعة الأدوية والجرعات'
            }
        ],
        # Patient 2 appointments
        [
            {
                'appointment_date': (datetime.now() + timedelta(days=10)).date(),
                'appointment_time': time(9, 0),
                'appointment_type': 'routine',
                'status': 'scheduled',
                'reason': 'فحص دوري للربو',
                'notes': 'مراجعة استخدام بخاخ الفنتولين'
            },
            {
                'appointment_date': (datetime.now() + timedelta(days=45)).date(),
                'appointment_time': time(11, 0),
                'appointment_type': 'follow_up',
                'status': 'scheduled',
                'reason': 'متابعة حالة الربو',
                'notes': 'فحص وظائف الرئة'
            }
        ],
        # Patient 3 appointments
        [
            {
                'appointment_date': (datetime.now() + timedelta(days=5)).date(),
                'appointment_time': time(15, 0),
                'appointment_type': 'routine',
                'status': 'scheduled',
                'reason': 'فحص ضغط الدم',
                'notes': 'مراقبة ضغط الدم بعد بدء العلاج'
            },
            {
                'appointment_date': (datetime.now() + timedelta(days=20)).date(),
                'appointment_time': time(16, 0),
                'appointment_type': 'follow_up',
                'status': 'scheduled',
                'reason': 'متابعة ضغط الدم',
                'notes': 'تعديل الجرعات إذا لزم الأمر'
            }
        ],
        # Patient 4 appointments
        [
            {
                'appointment_date': (datetime.now() + timedelta(days=14)).date(),
                'appointment_time': time(10, 30),
                'appointment_type': 'routine',
                'status': 'scheduled',
                'reason': 'فحص دوري عام',
                'notes': 'مراجعة المكملات الغذائية'
            },
            {
                'appointment_date': (datetime.now() + timedelta(days=60)).date(),
                'appointment_time': time(13, 0),
                'appointment_type': 'follow_up',
                'status': 'scheduled',
                'reason': 'متابعة الفيتامينات',
                'notes': 'فحص مستويات الفيتامينات في الدم'
            }
        ]
    ]
    
    # Create appointments for each patient
    for idx, (patient_id, patient_email) in enumerate(patients):
        if idx < len(default_appointments) and doctor_ids:
            appointments_data = default_appointments[idx]
            for appt_idx, appt_data in enumerate(appointments_data):
                doctor_id = doctor_ids[appt_idx % len(doctor_ids)] if doctor_ids else None
                if doctor_id:
                    # Convert time object to string format
                    appointment_time_str = appt_data['appointment_time'].strftime('%H:%M:%S') if isinstance(appt_data['appointment_time'], time) else str(appt_data['appointment_time'])
                    cursor.execute('''
                        INSERT OR IGNORE INTO appointments 
                        (patient_id, doctor_id, appointment_date, appointment_time, 
                         appointment_type, status, reason, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        patient_id,
                        doctor_id,
                        appt_data['appointment_date'],
                        appointment_time_str,
                        appt_data['appointment_type'],
                        appt_data['status'],
                        appt_data.get('reason'),
                        appt_data.get('notes'),
                        datetime.now() - timedelta(days=appt_idx*2)
                    ))
            print(f"Created appointments for patient {patient_email}")
    
    if patients:
        print(f"Created default consultations, evaluations, reviews, appointments, and product ratings for {len(patients)} patients")
    
    # إضافة بيانات مالية افتراضية
    print("\n💰 Adding default financial data...")
    
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
            
            print(f"✅ Added {len(default_incomes)} default income records")
    
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
        
        print(f"✅ Added {len(default_expenses)} default expense records")
    
    # إضافة أقسام وموظفين افتراضيين
    print("\n👥 Adding default departments and employees...")
    
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
                dept_id = cursor.fetchone()[0]
            department_ids[dept_name] = dept_id
        
        print(f"✅ Added {len(default_departments)} default departments")
        
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
                
                print(f"✅ Added {len(default_employees)} default employees")
    
    # إضافة تقييمات افتراضية للأطباء والصيادلة من المرضى
    print("إضافة تقييمات افتراضية للأطباء والصيادلة...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reviews'")
    if cursor.fetchone():
        # التحقق من وجود الأعمدة الجديدة doctor_id و pharmacist_id
        cursor.execute("PRAGMA table_info(reviews)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'doctor_id' not in columns:
            cursor.execute("ALTER TABLE reviews ADD COLUMN doctor_id INTEGER")
            print("Added doctor_id column to reviews table")
        
        if 'pharmacist_id' not in columns:
            cursor.execute("ALTER TABLE reviews ADD COLUMN pharmacist_id INTEGER")
            print("Added pharmacist_id column to reviews table")
        
        # الحصول على معرفات المرضى
        cursor.execute("SELECT id FROM users WHERE role = 'patient' LIMIT 4")
        patients = [row[0] for row in cursor.fetchall()]
        
        # الحصول على معرفات الأطباء
        cursor.execute("SELECT id FROM users WHERE role = 'doctor' LIMIT 4")
        doctors = [row[0] for row in cursor.fetchall()]
        
        # الحصول على معرفات الصيادلة
        cursor.execute("SELECT id FROM users WHERE role = 'pharmacist' LIMIT 1")
        pharmacists = [row[0] for row in cursor.fetchall()]
        
        if patients and doctors:
            # تقييمات للأطباء من المرضى المختلفين
            doctor_reviews = [
                # تقييمات للطبيب الأول
                (patients[0], doctors[0] if len(doctors) > 0 else None, 5, 'طبيب ممتاز', 'د. أحمد طبيب متميز وحريص جداً على المرضى. استفدت كثيراً من استشارته.', 1, datetime.now() - timedelta(days=10)),
                (patients[1], doctors[0] if len(doctors) > 0 else None, 4, 'تجربة جيدة', 'طبيب جيد ويعطي وقتاً كافياً للمريض. أنصح به.', 1, datetime.now() - timedelta(days=15)),
                (patients[2], doctors[0] if len(doctors) > 0 else None, 5, 'احترافية عالية', 'الدكتور محترف جداً وذو خبرة واسعة. شكراً لك دكتور.', 1, datetime.now() - timedelta(days=20)),
                
                # تقييمات للطبيب الثاني
                (patients[0], doctors[1] if len(doctors) > 1 else None, 4, 'طبيب موثوق', 'د. محمد طبيب موثوق ويشرح الحالة بوضوح.', 1, datetime.now() - timedelta(days=12)),
                (patients[1], doctors[1] if len(doctors) > 1 else None, 5, 'ممتاز في التشخيص', 'التشخيص دقيق والعلاج فعال. شكراً دكتور.', 1, datetime.now() - timedelta(days=18)),
                (patients[3], doctors[1] if len(doctors) > 1 else None, 5, 'أفضل طبيب', 'أفضل طبيب زرته. أنصح بزيارته بشدة.', 1, datetime.now() - timedelta(days=25)),
                
                # تقييمات للطبيب الثالث
                (patients[0], doctors[2] if len(doctors) > 2 else None, 5, 'خدمة رائعة', 'د. سارة رائعة في التعامل مع المرضى وتعطي اهتماماً كبيراً.', 1, datetime.now() - timedelta(days=8)),
                (patients[2], doctors[2] if len(doctors) > 2 else None, 4, 'تجربة إيجابية', 'تجربة إيجابية بشكل عام. الدكتورة متعاونة جداً.', 1, datetime.now() - timedelta(days=14)),
                (patients[3], doctors[2] if len(doctors) > 2 else None, 5, 'طبيبة متميزة', 'طبيبة متميزة وذات أخلاق عالية. جزاها الله خيراً.', 1, datetime.now() - timedelta(days=22)),
                
                # تقييمات للطبيب الرابع
                (patients[1], doctors[3] if len(doctors) > 3 else None, 4, 'خبرة واسعة', 'د. فاطمة لديها خبرة واسعة ومعرفة شاملة.', 1, datetime.now() - timedelta(days=11)),
                (patients[2], doctors[3] if len(doctors) > 3 else None, 5, 'ممتازة', 'ممتازة في التعامل والتشخيص. أنصح بها.', 1, datetime.now() - timedelta(days=16)),
                (patients[3], doctors[3] if len(doctors) > 3 else None, 4, 'جيدة جداً', 'طبيبة جيدة جداً وسريعة في الرد على الاستفسارات.', 1, datetime.now() - timedelta(days=23)),
            ]
            
            for review_data in doctor_reviews:
                if review_data[1]:  # تحقق من وجود doctor_id
                    cursor.execute('''
                        INSERT OR IGNORE INTO reviews 
                        (user_id, doctor_id, rating, title, comment, is_active, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', review_data)
            
            print(f"✅ Added {len(doctor_reviews)} reviews for doctors")
        
        if patients and pharmacists:
            # تقييمات للصيدلي من المرضى المختلفين
            pharmacist_reviews = [
                (patients[0], pharmacists[0] if len(pharmacists) > 0 else None, 5, 'صيدلي ممتاز', 'صيدلي محترف ويقدم استشارات دوائية ممتازة. شكراً له.', 1, datetime.now() - timedelta(days=9)),
                (patients[1], pharmacists[0] if len(pharmacists) > 0 else None, 5, 'خدمة رائعة', 'الصيدلي متعاون جداً ويشرح طريقة استخدام الأدوية بوضوح.', 1, datetime.now() - timedelta(days=13)),
                (patients[2], pharmacists[0] if len(pharmacists) > 0 else None, 4, 'تجربة جيدة', 'صيدلي جيد وسريع في الرد على الاستفسارات الدوائية.', 1, datetime.now() - timedelta(days=17)),
                (patients[3], pharmacists[0] if len(pharmacists) > 0 else None, 5, 'احترافي', 'صيدلي احترافي ولديه معرفة واسعة بالأدوية. أنصح به.', 1, datetime.now() - timedelta(days=21)),
            ]
            
            for review_data in pharmacist_reviews:
                if review_data[1]:  # تحقق من وجود pharmacist_id
                    cursor.execute('''
                        INSERT OR IGNORE INTO reviews 
                        (user_id, pharmacist_id, rating, title, comment, is_active, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', review_data)
            
            print(f"✅ Added {len(pharmacist_reviews)} reviews for pharmacists")

if __name__ == '__main__':
    print("Starting database initialization...")
    init_database()
    print("Database initialization completed!")
