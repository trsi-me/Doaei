#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# منصة دوائي - التطبيق الرئيسي
# إدارة الأدوية والتذكيرات الطبية

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date, time
import os
import json
from config import Config
from models import db, User, Medication, MedicationDose, Reminder, SharedRecord, Consultation, ProductRating, Report, AuditLog, SystemSetting, Pharmacy, PharmacyProduct, Order, OrderItem, OrderTracking, AIRecommendation, Review, Evaluation, Notification
from forms import *
from utils import SecurityUtils, NotificationService, AuditLogger, FileUtils, ValidationUtils, admin_required, user_required

def create_app():
    # إنشاء التطبيق
    # Disable instance folder to prevent creating database there
    app = Flask(__name__, instance_relative_config=False)
    
    # Force use DevelopmentConfig to ensure main database
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    
    # Force absolute path for database
    import os
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'doaei.db')
    
    # تهيئة الإضافات
    db.init_app(app)
    
    # تهيئة Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # إنشاء الجداول دائماً إذا لم تكن موجودة
    with app.app_context():
        import os
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # التحقق من وجود قاعدة البيانات والجداول
        need_init = False
        if not os.path.exists(db_path):
            print(f"Creating new database at: {db_path}")
            need_init = True
        else:
            # قاعدة البيانات موجودة، لكن نتحقق من وجود الجداول
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchall()
                conn.close()
                if not tables:
                    print(f"Database exists but tables missing. Creating tables...")
                    need_init = True
                else:
                    print(f"Using existing database at: {db_path}")
                    # إضافة الأعمدة المفقودة إذا لم تكن موجودة
                    try:
                        import sqlite3
                        temp_conn = sqlite3.connect(db_path)
                        temp_cursor = temp_conn.cursor()
                        temp_cursor.execute("PRAGMA table_info(users)")
                        columns = [col[1] for col in temp_cursor.fetchall()]
                        
                        # قائمة الأعمدة المطلوب إضافتها
                        columns_to_add = [
                            ('blood_type', 'VARCHAR(10)'),
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
                        
                        for column_name, column_type in columns_to_add:
                            if column_name not in columns:
                                try:
                                    alter_sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                                    temp_cursor.execute(alter_sql)
                                    print(f"✅ Added column: {column_name}")
                                except sqlite3.OperationalError as e:
                                    print(f"⚠️  Warning: Could not add {column_name}: {e}")
                        
                        # التحقق من وجود جدول evaluations وإضافته إذا لم يكن موجوداً
                        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evaluations'")
                        if not temp_cursor.fetchone():
                            print("Creating evaluations table...")
                            temp_cursor.execute('''
                                CREATE TABLE evaluations (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    patient_id INTEGER NOT NULL,
                                    doctor_id INTEGER NOT NULL,
                                    evaluation_date DATE NOT NULL,
                                    evaluation_type VARCHAR(50) NOT NULL,
                                    symptoms TEXT,
                                    diagnosis TEXT,
                                    vital_signs TEXT,
                                    physical_examination TEXT,
                                    lab_results TEXT,
                                    recommendations TEXT,
                                    prescribed_medications TEXT,
                                    next_visit_date DATE,
                                    notes TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (patient_id) REFERENCES users (id),
                                    FOREIGN KEY (doctor_id) REFERENCES users (id)
                                )
                            ''')
                            temp_cursor.execute('CREATE INDEX idx_evaluations_patient_id ON evaluations(patient_id)')
                            temp_cursor.execute('CREATE INDEX idx_evaluations_doctor_id ON evaluations(doctor_id)')
                            temp_cursor.execute('CREATE INDEX idx_evaluations_date ON evaluations(evaluation_date)')
                            print("✅ Evaluations table created!")
                        
                        # التحقق من وجود جدول appointments وإضافته إذا لم يكن موجوداً
                        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments'")
                        if not temp_cursor.fetchone():
                            print("Creating appointments table...")
                            temp_cursor.execute('''
                                CREATE TABLE appointments (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    patient_id INTEGER NOT NULL,
                                    doctor_id INTEGER NOT NULL,
                                    appointment_date DATE NOT NULL,
                                    appointment_time TIME NOT NULL,
                                    appointment_type VARCHAR(50) NOT NULL,
                                    status VARCHAR(20) DEFAULT 'scheduled',
                                    reason TEXT,
                                    notes TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (patient_id) REFERENCES users (id),
                                    FOREIGN KEY (doctor_id) REFERENCES users (id)
                                )
                            ''')
                            temp_cursor.execute('CREATE INDEX idx_appointments_patient_id ON appointments(patient_id)')
                            temp_cursor.execute('CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id)')
                            temp_cursor.execute('CREATE INDEX idx_appointments_date ON appointments(appointment_date)')
                            temp_cursor.execute('CREATE INDEX idx_appointments_status ON appointments(status)')
                            print("✅ Appointments table created!")
                        
                        # التحقق من وجود جدول incomes وإضافته إذا لم يكن موجوداً
                        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incomes'")
                        if not temp_cursor.fetchone():
                            print("Creating incomes table...")
                            temp_cursor.execute('''
                                CREATE TABLE incomes (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title VARCHAR(255) NOT NULL,
                                    description TEXT,
                                    amount REAL NOT NULL,
                                    category VARCHAR(100),
                                    source VARCHAR(255),
                                    transaction_date DATE NOT NULL,
                                    payment_method VARCHAR(50),
                                    reference_number VARCHAR(100),
                                    created_by INTEGER,
                                    notes TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (created_by) REFERENCES users (id)
                                )
                            ''')
                            print("✅ Incomes table created!")
                        
                        # التحقق من وجود جدول expenses وإضافته إذا لم يكن موجوداً
                        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
                        if not temp_cursor.fetchone():
                            print("Creating expenses table...")
                            temp_cursor.execute('''
                                CREATE TABLE expenses (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title VARCHAR(255) NOT NULL,
                                    description TEXT,
                                    amount REAL NOT NULL,
                                    category VARCHAR(100),
                                    vendor VARCHAR(255),
                                    transaction_date DATE NOT NULL,
                                    payment_method VARCHAR(50),
                                    reference_number VARCHAR(100),
                                    receipt_url VARCHAR(500),
                                    created_by INTEGER,
                                    notes TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (created_by) REFERENCES users (id)
                                )
                            ''')
                            print("✅ Expenses table created!")
                        
                        # التحقق من وجود جدول departments وإضافته إذا لم يكن موجوداً
                        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
                        if not temp_cursor.fetchone():
                            print("Creating departments table...")
                            temp_cursor.execute('''
                                CREATE TABLE departments (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name VARCHAR(255) NOT NULL UNIQUE,
                                    description TEXT,
                                    manager_id INTEGER,
                                    budget REAL DEFAULT 0.0,
                                    is_active BOOLEAN DEFAULT 1,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (manager_id) REFERENCES users (id)
                                )
                            ''')
                            print("✅ Departments table created!")
                        
                        # التحقق من وجود جدول employees وإضافته إذا لم يكن موجوداً
                        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
                        if not temp_cursor.fetchone():
                            print("Creating employees table...")
                            temp_cursor.execute('''
                                CREATE TABLE employees (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    user_id INTEGER NOT NULL UNIQUE,
                                    department_id INTEGER,
                                    employee_number VARCHAR(50) NOT NULL UNIQUE,
                                    position VARCHAR(255) NOT NULL,
                                    hire_date DATE NOT NULL,
                                    salary REAL DEFAULT 0.0,
                                    employment_type VARCHAR(50) DEFAULT 'full_time',
                                    status VARCHAR(50) DEFAULT 'active',
                                    manager_id INTEGER,
                                    phone_extension VARCHAR(20),
                                    office_location VARCHAR(255),
                                    notes TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (user_id) REFERENCES users (id),
                                    FOREIGN KEY (department_id) REFERENCES departments (id),
                                    FOREIGN KEY (manager_id) REFERENCES users (id)
                                )
                            ''')
                            temp_cursor.execute('CREATE INDEX idx_employees_user_id ON employees(user_id)')
                            temp_cursor.execute('CREATE INDEX idx_employees_department_id ON employees(department_id)')
                            temp_cursor.execute('CREATE INDEX idx_employees_status ON employees(status)')
                            print("✅ Employees table created!")
                        
                        # التحقق من وجود جدول notifications وإضافته إذا لم يكن موجوداً
                        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
                        if not temp_cursor.fetchone():
                            print("Creating notifications table...")
                            temp_cursor.execute('''
                                CREATE TABLE notifications (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    user_id INTEGER NOT NULL,
                                    title VARCHAR(255) NOT NULL,
                                    message TEXT NOT NULL,
                                    notification_type VARCHAR(50) DEFAULT 'info',
                                    is_read BOOLEAN DEFAULT 0,
                                    scheduled_time TIMESTAMP,
                                    sent_at TIMESTAMP,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (user_id) REFERENCES users (id)
                                )
                            ''')
                            temp_cursor.execute('CREATE INDEX idx_notifications_user_id ON notifications(user_id)')
                            temp_cursor.execute('CREATE INDEX idx_notifications_is_read ON notifications(is_read)')
                            temp_cursor.execute('CREATE INDEX idx_notifications_scheduled_time ON notifications(scheduled_time)')
                            temp_cursor.execute('CREATE INDEX idx_notifications_sent_at ON notifications(sent_at)')
                            print("✅ Notifications table created!")
                        
                        # تحديث role من admin إلى user
                        temp_cursor.execute("UPDATE users SET role = 'user' WHERE role = 'admin'")
                        print("✅ Updated admin roles to user!")
                        
                        temp_conn.commit()
                        temp_conn.close()
                        print("✅ Database columns updated!")
                    except Exception as col_error:
                        print(f"⚠️  Warning: Could not update columns: {col_error}")
                    
                    # إصلاح بريد المريض تلقائياً
                    try:
                        old_patient = User.query.filter_by(email='patient@example.com').first()
                        if old_patient:
                            print("Fixing patient email from patient@example.com to patient@doaei.com...")
                            old_patient.email = 'patient@doaei.com'
                            db.session.commit()
                            print("✅ Patient email fixed!")
                        
                        # التأكد من وجود المريض بالبريد الجديد
                        new_patient = User.query.filter_by(email='patient@doaei.com').first()
                        if not new_patient:
                            print("Creating patient account...")
                            import bcrypt
                            password_hash = bcrypt.hashpw('patient123'.encode('utf-8'), bcrypt.gensalt())
                            patient = User(
                                email='patient@doaei.com',
                                password_hash=password_hash.decode('utf-8'),
                                full_name='Ahmed Mohammed Patient',
                                role='patient',
                                phone='+966501234567',
                                is_active=True
                            )
                            db.session.add(patient)
                            db.session.commit()
                            print("✅ Patient account created!")
                    except Exception as fix_error:
                        print(f"Warning: Could not fix patient email: {fix_error}")
            except Exception as e:
                print(f"Error checking database: {e}. Recreating...")
                need_init = True
        
        if need_init:
            # استخدام init_database لإنشاء الجداول من schema.sql
            try:
                from init_db import init_database
                if os.path.exists(db_path):
                    # نسخ قاعدة البيانات القديمة
                    backup_path = db_path + '.backup'
                    import shutil
                    shutil.copy2(db_path, backup_path)
                    print(f"Backed up existing database to: {backup_path}")
                    os.remove(db_path)
                init_database()
                print("Database initialized successfully!")
            except Exception as e:
                print(f"Error using init_database, falling back to db.create_all(): {e}")
                db.create_all()
                print("Tables created using db.create_all()")
        else:
            # قاعدة البيانات موجودة، التحقق من وجود البيانات الافتراضية
            try:
                # التحقق من وجود الأطباء الافتراضيين
                doctor_count = User.query.filter_by(role='doctor', is_active=True).count()
                patient_count = User.query.filter_by(role='patient', is_active=True).count()
                admin_count = User.query.filter_by(email='admin@doaei.com').count()
                
                # إذا لم تكن هناك بيانات افتراضية، أضفها
                if doctor_count == 0 or patient_count == 0 or admin_count == 0:
                    print("⚠️ قاعدة البيانات موجودة لكن لا تحتوي على بيانات افتراضية")
                    print("🔧 إضافة البيانات الافتراضية...")
                    from init_db import init_database
                    # نسخ قاعدة البيانات الحالية
                    import shutil
                    backup_path = db_path + '.backup'
                    if os.path.exists(db_path):
                        shutil.copy2(db_path, backup_path)
                        print(f"تم نسخ قاعدة البيانات إلى: {backup_path}")
                    # إعادة إنشاء قاعدة البيانات بالبيانات الافتراضية
                    try:
                        os.remove(db_path)
                        init_database()
                        print("✅ تم إضافة البيانات الافتراضية بنجاح!")
                    except Exception as e:
                        print(f"⚠️ خطأ في إضافة البيانات الافتراضية: {e}")
                        # استعادة النسخة الاحتياطية
                        if os.path.exists(backup_path):
                            shutil.copy2(backup_path, db_path)
                            print("تم استعادة قاعدة البيانات من النسخة الاحتياطية")
            except Exception as e:
                print(f"⚠️ تحذير: لا يمكن التحقق من البيانات الافتراضية: {e}")
    
    # تسجيل المسارات
    register_routes(app)
    
    return app

def register_routes(app):
    # تسجيل المسارات
    
    # الصفحة الرئيسية
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # تسجيل الدخول
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            # البحث عن المستخدم
            email = form.email.data.strip()
            # البحث بالبريد كما هو أولاً
            user = User.query.filter_by(email=email).first()
            # إذا لم يوجد، البحث بدون حساسية لحالة الأحرف
            if not user:
                from sqlalchemy import func
                user = User.query.filter(func.lower(User.email) == email.lower()).first()
            if user:
                password_check = SecurityUtils.check_password(form.password.data, user.password_hash)
                if password_check:
                    if not user.is_active:
                        flash('حسابك معطل. يرجى الاتصال بالدعم', 'error')
                    else:
                        login_user(user, remember=True)
                        AuditLogger.log_action(user.id, 'login')
                        flash('تم تسجيل الدخول بنجاح!', 'success')
                        return redirect(url_for('dashboard'))
                else:
                    flash('كلمة المرور غير صحيحة', 'error')
            else:
                flash('البريد الإلكتروني غير موجود', 'error')
        
        return render_template('auth/login.html', form=form)
    
    # التسجيل
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegisterForm()
        if form.validate_on_submit():
            # التحقق من وجود المستخدم
            if User.query.filter_by(email=form.email.data).first():
                flash('البريد الإلكتروني مستخدم بالفعل', 'error')
                return render_template('auth/register.html', form=form)
            
            # إنشاء مستخدم جديد
            user = User(
                email=form.email.data,
                password_hash=SecurityUtils.hash_password(form.password.data),
                full_name=form.full_name.data,
                phone=form.phone.data,
                role=form.role.data
            )
            
            db.session.add(user)
            db.session.commit()
            
            AuditLogger.log_action(user.id, 'register')
            flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول', 'success')
            return redirect(url_for('login'))
        
        return render_template('auth/register.html', form=form)
    
    # تسجيل الخروج
    @app.route('/logout')
    @login_required
    def logout():
        AuditLogger.log_action(current_user.id, 'logout')
        logout_user()
        flash('تم تسجيل الخروج بنجاح', 'info')
        return redirect(url_for('index'))
    
    # لوحة التحكم
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'admin' or current_user.role == 'user':
            stats = get_user_stats()
            return render_template('dashboard/admin.html', stats=stats)
        elif current_user.role == 'patient':
            # المرضى
            medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).all()
            upcoming_reminders = get_upcoming_reminders(current_user.id)
            # Get available doctors (at least 4)
            available_doctors = User.query.filter_by(role='doctor', is_active=True).limit(10).all()
            # Get current doctor if assigned
            current_doctor = User.query.get(current_user.doctor_id) if current_user.doctor_id else None
            # Get recent consultations
            recent_consultations = Consultation.query.filter_by(patient_id=current_user.id).order_by(Consultation.created_at.desc()).limit(5).all()
            return render_template('dashboard/patient.html', 
                                 medications=medications, 
                                 reminders=upcoming_reminders,
                                 available_doctors=available_doctors,
                                 current_doctor=current_doctor,
                                 consultations=recent_consultations)
        elif current_user.role == 'doctor':
            # الأطباء - عرض المرضى والزيارات
            # الحصول على المرضى الذين اختاروا هذا الطبيب
            patients = User.query.filter_by(doctor_id=current_user.id, role='patient', is_active=True).all()
            # الحصول على الزيارات (evaluations) الأخيرة
            from models import Evaluation
            recent_evaluations = Evaluation.query.filter_by(doctor_id=current_user.id).order_by(Evaluation.evaluation_date.desc()).limit(5).all()
            # الحصول على المواعيد القادمة
            try:
                import sqlite3
                import os
                BASE_DIR = os.path.abspath(os.path.dirname(__file__))
                db_path = os.path.join(BASE_DIR, 'doaei.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.*, u.full_name as patient_name 
                    FROM appointments a
                    JOIN users u ON a.patient_id = u.id
                    WHERE a.doctor_id = ? AND a.status IN ('scheduled', 'confirmed')
                    ORDER BY a.appointment_date, a.appointment_time
                    LIMIT 5
                ''', (current_user.id,))
                upcoming_appointments = cursor.fetchall()
                conn.close()
            except Exception as e:
                print(f"Error fetching appointments: {e}")
                upcoming_appointments = []
            return render_template('dashboard/doctor.html', 
                                 patients=patients,
                                 recent_evaluations=recent_evaluations,
                                 upcoming_appointments=upcoming_appointments)
        elif current_user.role == 'pharmacist':
            # الصيادلة - عرض الاستشارات المعلقة
            # الحصول على جميع الاستشارات المعلقة (بدون pharmacist_id محدد)
            pending_consultations = Consultation.query.filter_by(
                status='pending'
            ).order_by(Consultation.created_at.desc()).limit(10).all()
            # الحصول على آخر الاستشارات المردودة من قبل هذا الصيدلي
            recent_replied = Consultation.query.filter_by(
                pharmacist_id=current_user.id,
                status='replied'
            ).order_by(Consultation.replied_at.desc()).limit(5).all()
            return render_template('dashboard/pharmacist.html',
                                 pending_consultations=pending_consultations,
                                 recent_replied=recent_replied)
        else:
            # Other roles
            medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).all()
            upcoming_reminders = get_upcoming_reminders(current_user.id)
            return render_template('dashboard/patient.html', medications=medications, reminders=upcoming_reminders)
    
    # إدارة الأدوية
    @app.route('/medications')
    @login_required
    def medications():
        """صفحة الأدوية - للمرضى فقط"""
        if current_user.role != 'patient':
            flash('هذه الصفحة للمرضى فقط', 'error')
            return redirect(url_for('dashboard'))
        # المرضى يرون أدويتهم فقط
        medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).order_by(Medication.created_at.desc()).all()
        return render_template('medications/list.html', medications=medications)
    
    @app.route('/medications/add', methods=['GET', 'POST'])
    @app.route('/add_medication', methods=['GET', 'POST'])
    @login_required
    def add_medication():
        """إضافة دواء جديد - للمرضى فقط"""
        if current_user.role != 'patient':
            flash('هذه الصفحة للمرضى فقط', 'error')
            return redirect(url_for('dashboard'))
        
        form = MedicationForm()
        if form.validate_on_submit():
            # معالجة تاريخ البدء من النموذج أو من request
            start_date_value = form.start_date.data
            if not start_date_value:
                # محاولة الحصول من request.form
                start_date_str = request.form.get('start_date', '').strip()
                if start_date_str:
                    try:
                        from datetime import datetime
                        start_date_value = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    except Exception as e:
                        app.logger.error(f'خطأ في تحويل التاريخ: {e}, القيمة: {start_date_str}')
                        start_date_value = datetime.now().date()
                else:
                    start_date_value = datetime.now().date()
            
            # التحقق من صحة البيانات قبل الحفظ
            if not form.name.data or not form.form.data or not form.dosage.data or not form.frequency.data:
                flash('يرجى ملء جميع الحقول المطلوبة', 'error')
                return render_template('medications/add.html', form=form)
            
            # معالجة مدة العلاج: تحويل duration إلى duration_days
            duration_days_value = form.duration_days.data
            if not duration_days_value and form.duration.data:
                # محاولة استخراج الرقم من حقل duration
                import re
                duration_str = str(form.duration.data).strip()
                # البحث عن رقم في النص (مثال: "30 يوم" -> 30)
                numbers = re.findall(r'\d+', duration_str)
                if numbers:
                    try:
                        duration_days_value = int(numbers[0])
                    except ValueError:
                        duration_days_value = None
            
            medication = Medication(
                user_id=current_user.id,
                name=form.name.data,
                form=form.form.data,
                dosage=form.dosage.data,
                frequency=form.frequency.data,
                duration_days=duration_days_value,
                start_date=start_date_value,
                quantity=form.quantity.data,
                notes=form.notes.data,
                doctor_notes=form.doctor_notes.data,
                is_active=True  # التأكد من أن الدواء نشط عند الإضافة
            )
            
            # حساب تاريخ الانتهاء
            medication.calculate_end_date()
            
            db.session.add(medication)
            db.session.flush()  # الحصول على ID قبل commit
            
            # إنشاء الجرعات المحددة
            try:
                create_medication_doses(medication)
            except Exception as e:
                app.logger.error(f'خطأ في إنشاء الجرعات: {e}')
                db.session.rollback()
                flash('حدث خطأ في إضافة الدواء. يرجى المحاولة مرة أخرى.', 'error')
                return render_template('medications/add.html', form=form)
            
            # التأكد من حفظ التغييرات
            try:
                db.session.commit()
                app.logger.info(f'تم إضافة الدواء بنجاح: {medication.name} للمستخدم {current_user.id}')
            except Exception as e:
                app.logger.error(f'خطأ في حفظ الدواء: {e}')
                db.session.rollback()
                flash('حدث خطأ في حفظ الدواء. يرجى المحاولة مرة أخرى.', 'error')
                return render_template('medications/add.html', form=form)
            
            # إرسال إشعار عند إضافة دواء
            try:
                notification_service = NotificationService()
                notification_service.send_medication_added_notification(current_user, medication)
            except Exception as e:
                app.logger.error(f'خطأ في إرسال الإشعار: {e}')
            
            AuditLogger.log_action(current_user.id, 'add_medication', 'medications', medication.id)
            flash('تم إضافة الدواء بنجاح!', 'success')
            return redirect(url_for('medications'))
        else:
            # عرض أخطاء التحقق
            if request.method == 'POST':
                app.logger.warning(f'فشل التحقق من النموذج. الأخطاء: {form.errors}')
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'خطأ في {field}: {error}', 'error')
        
        return render_template('medications/add.html', form=form)
    
    @app.route('/medications/<int:medication_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_medication(medication_id):
        """تعديل دواء - للمرضى فقط"""
        if current_user.role != 'patient':
            flash('هذه الصفحة للمرضى فقط', 'error')
            return redirect(url_for('dashboard'))
        
        medication = Medication.query.get_or_404(medication_id)
        
        # التحقق من أن الدواء يخص المستخدم الحالي فقط
        if medication.user_id != current_user.id:
            flash('ليس لديك صلاحية لتعديل هذا الدواء', 'error')
            return redirect(url_for('medications'))
        
        form = MedicationForm(obj=medication)
        if form.validate_on_submit():
            old_values = {
                'name': medication.name,
                'dosage': medication.dosage,
                'frequency': medication.frequency
            }
            
            # معالجة تاريخ البدء من النموذج أو من request
            start_date_value = form.start_date.data
            if not start_date_value:
                # محاولة الحصول من request.form
                start_date_str = request.form.get('start_date', '').strip()
                if start_date_str:
                    try:
                        from datetime import datetime
                        start_date_value = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    except Exception as e:
                        app.logger.error(f'خطأ في تحويل التاريخ: {e}, القيمة: {start_date_str}')
                        start_date_value = medication.start_date  # الاحتفاظ بالقيمة القديمة
                else:
                    start_date_value = medication.start_date  # الاحتفاظ بالقيمة القديمة
            
            # معالجة مدة العلاج: تحويل duration إلى duration_days
            duration_days_value = form.duration_days.data
            if not duration_days_value and form.duration.data:
                # محاولة استخراج الرقم من حقل duration
                import re
                duration_str = str(form.duration.data).strip()
                # البحث عن رقم في النص (مثال: "30 يوم" -> 30)
                numbers = re.findall(r'\d+', duration_str)
                if numbers:
                    try:
                        duration_days_value = int(numbers[0])
                    except ValueError:
                        duration_days_value = medication.duration_days  # الاحتفاظ بالقيمة القديمة
            
            medication.name = form.name.data
            medication.form = form.form.data
            medication.dosage = form.dosage.data
            medication.frequency = form.frequency.data
            medication.duration_days = duration_days_value if duration_days_value else medication.duration_days
            medication.start_date = start_date_value
            medication.quantity = form.quantity.data
            medication.notes = form.notes.data
            medication.doctor_notes = form.doctor_notes.data
            
            medication.calculate_end_date()
            
            new_values = {
                'name': medication.name,
                'dosage': medication.dosage,
                'frequency': medication.frequency
            }
            
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'edit_medication', 'medications', medication.id, old_values, new_values)
            flash('تم تحديث الدواء بنجاح!', 'success')
            return redirect(url_for('medications'))
        
        return render_template('medications/edit.html', form=form, medication=medication)
    
    @app.route('/medications/<int:medication_id>/delete', methods=['POST'])
    @login_required
    def delete_medication(medication_id):
        """حذف دواء - للمرضى فقط"""
        if current_user.role != 'patient':
            flash('هذه الصفحة للمرضى فقط', 'error')
            return redirect(url_for('dashboard'))
        
        medication = Medication.query.get_or_404(medication_id)
        
        # التحقق من أن الدواء يخص المستخدم الحالي فقط
        if medication.user_id != current_user.id:
            flash('ليس لديك صلاحية لحذف هذا الدواء', 'error')
            return redirect(url_for('medications'))
        
        AuditLogger.log_action(current_user.id, 'delete_medication', 'medications', medication.id)
        
        medication.is_active = False
        db.session.commit()
        
        flash('تم حذف الدواء بنجاح!', 'success')
        return redirect(url_for('medications'))
    
    # استشارات الصيدلي - مفتوحة للكل
    @app.route('/consultations')
    def consultations():
        # قائمة الاستشارات - مفتوحة للكل
        page = request.args.get('page', 1, type=int)
        
        if current_user.is_authenticated:
            if current_user.role == 'user':
                # المستخدمون يرون جميع الاستشارات
                consultations = Consultation.query.order_by(Consultation.created_at.desc())\
                                                .paginate(page=page, per_page=10, error_out=False)
            else:
                # المستخدمون العاديون يرون استشاراتهم فقط أو الاستشارات العامة (patient_id = None)
                from sqlalchemy import or_
                consultations = Consultation.query.filter(
                    or_(Consultation.patient_id == current_user.id, Consultation.patient_id.is_(None))
                ).order_by(Consultation.created_at.desc())\
                 .paginate(page=page, per_page=10, error_out=False)
        else:
            # الزوار يرون جميع الاستشارات العامة (patient_id = None)
            consultations = Consultation.query.filter(Consultation.patient_id.is_(None))\
                                            .order_by(Consultation.created_at.desc())\
                                            .paginate(page=page, per_page=10, error_out=False)
        
        return render_template('consultations/list.html', consultations=consultations)
    
    @app.route('/consultations/add', methods=['GET', 'POST'])
    @app.route('/add_consultation', methods=['GET', 'POST'])
    def add_consultation():
        # إضافة استشارة - مفتوحة للكل
        try:
            if current_user.is_authenticated and current_user.role == 'user':
                flash('المستخدمون لا يمكنهم إرسال استشارات', 'error')
                return redirect(url_for('consultations'))
            
            form = ConsultationForm()
            if form.validate_on_submit():
                # إذا كان المستخدم مسجل دخول، استخدم ID الخاص به، وإلا استخدم None
                patient_id = current_user.id if current_user.is_authenticated else None
                
                consultation = Consultation(
                    patient_id=patient_id,
                    subject=form.subject.data,
                    message=form.description.data
                )
                
                # حفظ المرفق إذا كان موجوداً
                if form.attachment.data:
                    try:
                        file_path = FileUtils.save_uploaded_file(form.attachment.data, app.config['UPLOAD_FOLDER'])
                        if file_path:
                            consultation.attachment_path = file_path
                    except Exception as e:
                        app.logger.error(f'خطأ في حفظ المرفق: {e}')
                
                db.session.add(consultation)
                db.session.commit()
                
                # إرسال إشعار للصيدليين
                try:
                    notification_service = NotificationService()
                    pharmacists = User.query.filter_by(role='pharmacist', is_active=True).all()
                    for pharmacist in pharmacists:
                        notification_service.send_consultation_notification(pharmacist, consultation)
                except Exception as e:
                    app.logger.error(f'خطأ في إرسال الإشعارات: {e}')
                
                if current_user.is_authenticated:
                    AuditLogger.log_action(current_user.id, 'add_consultation', 'consultations', consultation.id)
                flash('تم إرسال الاستشارة بنجاح!', 'success')
                return redirect(url_for('consultations'))
            
            return render_template('consultations/add.html', form=form)
        except Exception as e:
            app.logger.error(f'خطأ في إضافة الاستشارة: {e}')
            db.session.rollback()
            flash('حدث خطأ أثناء إضافة الاستشارة. يرجى المحاولة مرة أخرى.', 'error')
            return redirect(url_for('consultations'))
    
    @app.route('/consultations/<int:consultation_id>', endpoint='view_consultation')
    @app.route('/consultations/<int:consultation_id>/view', endpoint='view_consultation')
    @login_required
    def view_consultation(consultation_id):
        """عرض تفاصيل الاستشارة"""
        consultation = Consultation.query.get_or_404(consultation_id)
        # التحقق من الصلاحيات
        if current_user.role == 'patient' and consultation.patient_id != current_user.id:
            flash('ليس لديك صلاحية لعرض هذه الاستشارة', 'error')
            return redirect(url_for('consultations'))
        return render_template('consultations/detail.html', consultation=consultation)
    
    @app.route('/patient/ratings', endpoint='patient_ratings')
    @app.route('/ratings', endpoint='ratings')
    @login_required
    def patient_ratings():
        """صفحة تقييمات المريض - خاصة بكل مستخدم فقط"""
        if current_user.role != 'patient':
            flash('هذه الصفحة للمرضى فقط', 'error')
            return redirect(url_for('dashboard'))
        from models import Review, Evaluation
        # الحصول على التقييمات والمراجعات للمريض الحالي فقط
        reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
        evaluations = Evaluation.query.filter_by(patient_id=current_user.id).order_by(Evaluation.evaluation_date.desc()).all()
        return render_template('patient/ratings.html', reviews=reviews, evaluations=evaluations)
    
    @app.route('/patient/ratings/add', methods=['GET', 'POST'])
    @app.route('/add_rating', methods=['GET', 'POST'])
    @login_required
    def add_rating():
        """إضافة تقييم جديد - للمرضى فقط"""
        if current_user.role != 'patient':
            flash('هذه الصفحة للمرضى فقط', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            try:
                from models import Review
                doctor_id = request.form.get('doctor_id', type=int)
                pharmacist_id = request.form.get('pharmacist_id', type=int)
                rating = request.form.get('rating', type=int)
                title = request.form.get('title', '')
                comment = request.form.get('comment', '')
                
                if not rating or rating < 1 or rating > 5:
                    flash('يرجى اختيار تقييم صحيح (1-5)', 'error')
                    return redirect(url_for('add_rating'))
                
                review = Review(
                    user_id=current_user.id,  # المستخدم الحالي فقط
                    doctor_id=doctor_id if doctor_id else None,
                    pharmacist_id=pharmacist_id if pharmacist_id else None,
                    rating=rating,
                    title=title,
                    comment=comment
                )
                
                db.session.add(review)
                db.session.commit()
                
                AuditLogger.log_action(current_user.id, 'add_rating', 'reviews', review.id)
                flash('تم إضافة التقييم بنجاح', 'success')
                return redirect(url_for('patient_ratings'))
            except Exception as e:
                app.logger.error(f'خطأ في إضافة التقييم: {e}')
                db.session.rollback()
                flash('حدث خطأ أثناء إضافة التقييم', 'error')
                return redirect(url_for('add_rating'))
        
        # عرض النموذج
        from models import User
        doctors = User.query.filter_by(role='doctor', is_active=True).all()
        pharmacists = User.query.filter_by(role='pharmacist', is_active=True).all()
        return render_template('patient/add_rating.html', doctors=doctors, pharmacists=pharmacists)
    
    @app.route('/patient/appointments')
    @app.route('/upcoming-appointments')
    @login_required
    def upcoming_appointments():
        """صفحة المواعيد القادمة"""
        if current_user.role != 'patient':
            flash('هذه الصفحة للمرضى فقط', 'error')
            return redirect(url_for('dashboard'))
        try:
            import sqlite3
            import os
            BASE_DIR = os.path.abspath(os.path.dirname(__file__))
            db_path = os.path.join(BASE_DIR, 'doaei.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, u.full_name as doctor_name 
                FROM appointments a
                JOIN users u ON a.doctor_id = u.id
                WHERE a.patient_id = ? AND a.status IN ('scheduled', 'confirmed')
                ORDER BY a.appointment_date, a.appointment_time
            ''', (current_user.id,))
            appointments = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"Error fetching appointments: {e}")
            appointments = []
        return render_template('patient/appointments.html', appointments=appointments)
    
    # Admin routes
    @app.route('/admin/users', endpoint='admin_users')
    @login_required
    def admin_users():
        """صفحة إدارة المستخدمين"""
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        users = User.query.filter_by(is_active=True).order_by(User.created_at.desc()).all()
        return render_template('admin/users.html', users=users)
    
    @app.route('/admin/employees', endpoint='admin_employees')
    @login_required
    def admin_employees():
        """صفحة إدارة الموظفين"""
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        from models import Employee, Department
        # ترتيب الموظفين حسب القسم ثم حسب الرقم الوظيفي
        employees = Employee.query.join(User, Employee.user_id == User.id).order_by(
            Employee.department_id.asc(),
            Employee.employee_number.asc()
        ).all()
        departments = Department.query.filter_by(is_active=True).order_by(Department.name.asc()).all()
        return render_template('admin/employees.html', employees=employees, departments=departments)
    
    @app.route('/admin/income', endpoint='admin_income')
    @login_required
    def admin_income():
        """صفحة إدارة الدخل"""
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        from models import Income
        incomes = Income.query.order_by(Income.transaction_date.desc()).limit(50).all()
        return render_template('admin/income.html', incomes=incomes)
    
    @app.route('/admin/expenses', endpoint='admin_expenses')
    @login_required
    def admin_expenses():
        """صفحة إدارة المصروفات"""
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        from models import Expense
        expenses = Expense.query.order_by(Expense.transaction_date.desc()).limit(50).all()
        return render_template('admin/expenses.html', expenses=expenses)
    
    @app.route('/admin/financial-reports', endpoint='admin_financial_reports')
    @login_required
    def admin_financial_reports():
        """صفحة التقارير المالية"""
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        stats = get_user_stats()
        return render_template('admin/financial_reports.html', stats=stats)
    
    @app.route('/admin/analytics', endpoint='admin_analytics')
    @login_required
    def admin_analytics():
        """صفحة التحليلات"""
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        stats = get_user_stats()
        return render_template('admin/analytics.html', stats=stats)
    
    # Doctor routes
    @app.route('/doctor/patients', endpoint='doctor_patients')
    @login_required
    def doctor_patients():
        """صفحة قائمة المرضى - للأطباء فقط"""
        if current_user.role != 'doctor':
            flash('هذه الصفحة للأطباء فقط', 'error')
            return redirect(url_for('dashboard'))
        patients = User.query.filter_by(doctor_id=current_user.id, role='patient', is_active=True).all()
        return render_template('doctor/patients.html', patients=patients)
    
    @app.route('/doctor/patients/<int:patient_id>', endpoint='doctor_patient_detail')
    @login_required
    def doctor_patient_detail(patient_id):
        """صفحة تفاصيل المريض - للأطباء فقط"""
        if current_user.role != 'doctor':
            flash('هذه الصفحة للأطباء فقط', 'error')
            return redirect(url_for('dashboard'))
        patient = User.query.get_or_404(patient_id)
        if patient.doctor_id != current_user.id:
            flash('ليس لديك صلاحية لعرض هذا المريض', 'error')
            return redirect(url_for('doctor_patients'))
        from models import Medication, Evaluation, Consultation
        medications = Medication.query.filter_by(user_id=patient_id, is_active=True).all()
        evaluations = Evaluation.query.filter_by(patient_id=patient_id, doctor_id=current_user.id).order_by(Evaluation.evaluation_date.desc()).all()
        consultations = Consultation.query.filter_by(patient_id=patient_id).order_by(Consultation.created_at.desc()).limit(10).all()
        return render_template('doctor/patient_detail.html', patient=patient, medications=medications, evaluations=evaluations, consultations=consultations)
    
    @app.route('/doctor/evaluations', endpoint='doctor_evaluations')
    @login_required
    def doctor_evaluations():
        """صفحة قائمة التقييمات - للأطباء فقط"""
        if current_user.role != 'doctor':
            flash('هذه الصفحة للأطباء فقط', 'error')
            return redirect(url_for('dashboard'))
        from models import Evaluation
        evaluations = Evaluation.query.filter_by(doctor_id=current_user.id).order_by(Evaluation.evaluation_date.desc()).all()
        return render_template('doctor/evaluations.html', evaluations=evaluations)
    
    @app.route('/doctor/evaluations/<int:evaluation_id>', endpoint='doctor_evaluation_detail')
    @login_required
    def doctor_evaluation_detail(evaluation_id):
        """صفحة تفاصيل التقييم - للأطباء فقط"""
        if current_user.role != 'doctor':
            flash('هذه الصفحة للأطباء فقط', 'error')
            return redirect(url_for('dashboard'))
        from models import Evaluation
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        if evaluation.doctor_id != current_user.id:
            flash('ليس لديك صلاحية لعرض هذا التقييم', 'error')
            return redirect(url_for('doctor_evaluations'))
        return render_template('doctor/evaluation_detail.html', evaluation=evaluation)
    
    @app.route('/doctor/evaluations/add', methods=['GET', 'POST'], endpoint='doctor_add_evaluation')
    @login_required
    def doctor_add_evaluation():
        """صفحة إضافة تقييم جديد - للأطباء فقط"""
        if current_user.role != 'doctor':
            flash('هذه الصفحة للأطباء فقط', 'error')
            return redirect(url_for('dashboard'))
        from models import Evaluation
        if request.method == 'POST':
            try:
                patient_id = request.form.get('patient_id', type=int)
                evaluation_date = request.form.get('evaluation_date')
                evaluation_type = request.form.get('evaluation_type', '')
                symptoms = request.form.get('symptoms', '')
                diagnosis = request.form.get('diagnosis', '')
                vital_signs = request.form.get('vital_signs', '')
                physical_examination = request.form.get('physical_examination', '')
                lab_results = request.form.get('lab_results', '')
                recommendations = request.form.get('recommendations', '')
                prescribed_medications = request.form.get('prescribed_medications', '')
                next_visit_date = request.form.get('next_visit_date')
                notes = request.form.get('notes', '')
                
                if not patient_id:
                    flash('يرجى اختيار المريض', 'error')
                    return redirect(url_for('doctor_add_evaluation'))
                
                # التحقق من أن المريض يخص هذا الطبيب
                patient = User.query.get(patient_id)
                if not patient or patient.doctor_id != current_user.id:
                    flash('ليس لديك صلاحية لإضافة تقييم لهذا المريض', 'error')
                    return redirect(url_for('doctor_add_evaluation'))
                
                evaluation = Evaluation(
                    patient_id=patient_id,
                    doctor_id=current_user.id,
                    evaluation_date=datetime.strptime(evaluation_date, '%Y-%m-%d').date() if evaluation_date else date.today(),
                    evaluation_type=evaluation_type,
                    symptoms=symptoms,
                    diagnosis=diagnosis,
                    vital_signs=vital_signs,
                    physical_examination=physical_examination,
                    lab_results=lab_results,
                    recommendations=recommendations,
                    prescribed_medications=prescribed_medications,
                    next_visit_date=datetime.strptime(next_visit_date, '%Y-%m-%d').date() if next_visit_date else None,
                    notes=notes
                )
                
                db.session.add(evaluation)
                db.session.commit()
                
                AuditLogger.log_action(current_user.id, 'add_evaluation', 'evaluations', evaluation.id)
                flash('تم إضافة التقييم بنجاح', 'success')
                return redirect(url_for('doctor_evaluation_detail', evaluation_id=evaluation.id))
            except Exception as e:
                app.logger.error(f'خطأ في إضافة التقييم: {e}')
                db.session.rollback()
                flash('حدث خطأ أثناء إضافة التقييم', 'error')
                return redirect(url_for('doctor_add_evaluation'))
        
        # عرض النموذج
        patients = User.query.filter_by(doctor_id=current_user.id, role='patient', is_active=True).all()
        today = date.today().strftime('%Y-%m-%d')
        return render_template('doctor/add_evaluation.html', patients=patients, today=today)
    
    @app.route('/doctor/appointments', endpoint='doctor_appointments')
    @login_required
    def doctor_appointments():
        """صفحة قائمة المواعيد - للأطباء فقط"""
        if current_user.role != 'doctor':
            flash('هذه الصفحة للأطباء فقط', 'error')
            return redirect(url_for('dashboard'))
        try:
            import sqlite3
            import os
            BASE_DIR = os.path.abspath(os.path.dirname(__file__))
            db_path = os.path.join(BASE_DIR, 'doaei.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, u.full_name as patient_name 
                FROM appointments a
                JOIN users u ON a.patient_id = u.id
                WHERE a.doctor_id = ?
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            ''', (current_user.id,))
            appointments = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"Error fetching appointments: {e}")
            appointments = []
        return render_template('doctor/appointments.html', appointments=appointments)
    
    @app.route('/doctor/appointments/add', methods=['GET', 'POST'], endpoint='doctor_add_appointment')
    @login_required
    def doctor_add_appointment():
        """صفحة إضافة موعد جديد - للأطباء فقط"""
        if current_user.role != 'doctor':
            flash('هذه الصفحة للأطباء فقط', 'error')
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            try:
                import sqlite3
                import os
                BASE_DIR = os.path.abspath(os.path.dirname(__file__))
                db_path = os.path.join(BASE_DIR, 'doaei.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                patient_id = request.form.get('patient_id', type=int)
                appointment_date = request.form.get('appointment_date')
                appointment_time = request.form.get('appointment_time')
                reason = request.form.get('reason', '')
                notes = request.form.get('notes', '')
                
                if not patient_id or not appointment_date or not appointment_time:
                    flash('يرجى ملء جميع الحقول المطلوبة', 'error')
                    conn.close()
                    return redirect(url_for('doctor_add_appointment'))
                
                # التحقق من أن المريض يخص هذا الطبيب
                patient = User.query.get(patient_id)
                if not patient or patient.doctor_id != current_user.id:
                    flash('ليس لديك صلاحية لإضافة موعد لهذا المريض', 'error')
                    conn.close()
                    return redirect(url_for('doctor_add_appointment'))
                
                cursor.execute('''
                    INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, notes, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'scheduled', datetime('now'))
                ''', (patient_id, current_user.id, appointment_date, appointment_time, reason, notes))
                
                conn.commit()
                conn.close()
                
                AuditLogger.log_action(current_user.id, 'add_appointment', 'appointments', cursor.lastrowid)
                flash('تم إضافة الموعد بنجاح', 'success')
                return redirect(url_for('doctor_appointments'))
            except Exception as e:
                app.logger.error(f'خطأ في إضافة الموعد: {e}')
                flash('حدث خطأ أثناء إضافة الموعد', 'error')
                return redirect(url_for('doctor_add_appointment'))
        
        # عرض النموذج
        patients = User.query.filter_by(doctor_id=current_user.id, role='patient', is_active=True).all()
        return render_template('doctor/add_appointment.html', patients=patients)
    
    @app.route('/consultations/<int:consultation_id>/reply', methods=['GET', 'POST'])
    @login_required
    def reply_consultation(consultation_id):
        # السماح للصيادلة والمستخدمين بالرد
        if current_user.role not in ['pharmacist', 'user']:
            flash('يمكن للصيادلة والمستخدمين فقط الرد على الاستشارات', 'error')
            return redirect(url_for('consultations'))
        
        consultation = Consultation.query.get_or_404(consultation_id)
        
        # إذا كانت الاستشارة قد تم الرد عليها بالفعل
        if consultation.status == 'replied':
            flash('تم الرد على هذه الاستشارة بالفعل', 'info')
            return redirect(url_for('view_consultation', consultation_id=consultation_id))
        
        form = ConsultationReplyForm()
        
        if form.validate_on_submit():
            consultation.reply = form.reply.data
            consultation.pharmacist_id = current_user.id
            consultation.status = 'replied'
            consultation.replied_at = datetime.utcnow()
            
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'reply_consultation', 'consultations', consultation.id)
            flash('تم إرسال الرد بنجاح!', 'success')
            return redirect(url_for('view_consultation', consultation_id=consultation_id))
        
        return render_template('consultations/reply.html', form=form, consultation=consultation)
    
    # تقييمات المنتجات
    
    # التقارير
    @app.route('/reports')
    @login_required
    def reports():
        user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.generated_at.desc()).all()
        return render_template('reports/list.html', reports=user_reports)
    
    @app.route('/statistics')
    @login_required
    def statistics():
        # صفحة الإحصائيات
        # إحصائيات الأدوية
        total_medications = Medication.query.filter_by(user_id=current_user.id).count()
        active_medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).count()
        
        # إحصائيات التذكيرات
        total_reminders = Reminder.query.filter_by(user_id=current_user.id).count()
        completed_reminders = Reminder.query.filter_by(user_id=current_user.id, is_completed=True).count()
        
        # إحصائيات الطلبات
        total_orders = Order.query.filter_by(user_id=current_user.id).count()
        completed_orders = Order.query.filter_by(user_id=current_user.id, status='delivered').count()
        
        # إحصائيات التوصيات الذكية
        total_recommendations = AIRecommendation.query.filter_by(user_id=current_user.id).count()
        accepted_recommendations = AIRecommendation.query.filter_by(user_id=current_user.id, status='accepted').count()
        
        # إحصائيات التقارير
        total_reports = Report.query.filter_by(user_id=current_user.id).count()
        
        stats = {
            'medications': {
                'total': total_medications,
                'active': active_medications,
                'percentage': (active_medications / total_medications * 100) if total_medications > 0 else 0
            },
            'reminders': {
                'total': total_reminders,
                'completed': completed_reminders,
                'percentage': (completed_reminders / total_reminders * 100) if total_reminders > 0 else 0
            },
            'orders': {
                'total': total_orders,
                'completed': completed_orders,
                'percentage': (completed_orders / total_orders * 100) if total_orders > 0 else 0
            },
            'recommendations': {
                'total': total_recommendations,
                'accepted': accepted_recommendations,
                'percentage': (accepted_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
            },
            'reports': {
                'total': total_reports
            }
        }
        
        return render_template('statistics/dashboard.html', stats=stats)
    
    @app.route('/reports/generate', methods=['GET', 'POST'])
    @app.route('/generate_report', methods=['GET', 'POST'])
    @login_required
    def generate_report():
        try:
            form = ReportForm()
            if form.validate_on_submit():
                # إنشاء التقرير
                report = Report(
                    user_id=current_user.id,
                    report_type=form.report_type.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    title=form.title.data if hasattr(form, 'title') else f'تقرير {form.report_type.data}',
                    doctor_name=form.doctor_name.data if hasattr(form, 'doctor_name') else None,
                    summary=form.summary.data if hasattr(form, 'summary') else None
                )
                
                db.session.add(report)
                db.session.commit()
                
                # توليد ملف PDF
                try:
                    pdf_path = generate_pdf_report(report)
                    if pdf_path:
                        report.file_path = pdf_path
                        db.session.commit()
                        
                        AuditLogger.log_action(current_user.id, 'generate_report', 'reports', report.id)
                        flash('تم إنشاء التقرير بنجاح!', 'success')
                        return redirect(url_for('download_report', report_id=report.id))
                    else:
                        flash('تم إنشاء التقرير ولكن حدث خطأ في توليد ملف PDF', 'warning')
                        return redirect(url_for('reports'))
                except Exception as e:
                    app.logger.error(f'خطأ في توليد PDF: {e}')
                    flash('تم إنشاء التقرير ولكن حدث خطأ في توليد ملف PDF', 'warning')
                    return redirect(url_for('reports'))
            
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            return render_template('reports/generate.html', form=form, current_date=current_date)
        except Exception as e:
            app.logger.error(f'خطأ في إنشاء التقرير: {e}')
            db.session.rollback()
            flash('حدث خطأ أثناء إنشاء التقرير. يرجى المحاولة مرة أخرى.', 'error')
            return redirect(url_for('reports'))
    
    @app.route('/reports/<int:report_id>/download')
    @login_required
    def download_report(report_id):
        report = Report.query.get_or_404(report_id)
        
        if report.user_id != current_user.id and current_user.role != 'user':
            flash('ليس لديك صلاحية لتحميل هذا التقرير', 'error')
            return redirect(url_for('reports'))
        
        if report.file_path and os.path.exists(report.file_path):
            return send_file(report.file_path, as_attachment=True)
        else:
            flash('ملف التقرير غير موجود', 'error')
            return redirect(url_for('reports'))
    
    # الملف الشخصي
    @app.route('/profile')
    @login_required
    def profile():
        # جلب الأدوية النشطة
        active_medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).order_by(Medication.created_at.desc()).all()
        # جلب الأدوية المحذوفة (أرشيف)
        archived_medications = Medication.query.filter_by(user_id=current_user.id, is_active=False).order_by(Medication.updated_at.desc()).all()
        return render_template('profile/view.html', 
                             active_medications=active_medications,
                             archived_medications=archived_medications)
    
    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = PatientProfileForm(obj=current_user)
        
        # إضافة قائمة الأطباء
        doctors = User.query.filter_by(role='doctor', is_active=True).all()
        form.doctor_id.choices = [(0, 'لا يوجد')] + [(d.id, d.full_name) for d in doctors]
        
        if form.validate_on_submit():
            old_values = {
                'full_name': current_user.full_name,
                'phone': current_user.phone
            }
            
            current_user.full_name = form.full_name.data
            current_user.phone = form.phone.data
            
            if hasattr(form, 'date_of_birth') and form.date_of_birth.data:
                current_user.date_of_birth = form.date_of_birth.data
            if hasattr(form, 'gender') and form.gender.data:
                current_user.gender = form.gender.data
            if hasattr(form, 'weight') and form.weight.data:
                current_user.weight = form.weight.data
            if hasattr(form, 'height') and form.height.data:
                current_user.height = form.height.data
            if hasattr(form, 'chronic_diseases') and form.chronic_diseases.data:
                current_user.chronic_diseases = form.chronic_diseases.data
            if hasattr(form, 'drug_allergies') and form.drug_allergies.data:
                current_user.drug_allergies = form.drug_allergies.data
            if hasattr(form, 'emergency_contact_name') and form.emergency_contact_name.data:
                current_user.emergency_contact_name = form.emergency_contact_name.data
            if hasattr(form, 'emergency_contact_phone') and form.emergency_contact_phone.data:
                current_user.emergency_contact_phone = form.emergency_contact_phone.data
            if hasattr(form, 'doctor_id') and form.doctor_id.data:
                current_user.doctor_id = form.doctor_id.data if form.doctor_id.data > 0 else None
            if hasattr(form, 'blood_type'):
                current_user.blood_type = form.blood_type.data if form.blood_type.data else None
            # حفظ حقول العنوان
            if hasattr(form, 'address') and form.address.data:
                current_user.address = form.address.data
            if hasattr(form, 'city') and form.city.data:
                current_user.city = form.city.data
            if hasattr(form, 'postal_code') and form.postal_code.data:
                current_user.postal_code = form.postal_code.data
            # حفظ الحقول الطبية الإضافية
            if hasattr(form, 'medical_conditions') and form.medical_conditions.data:
                current_user.medical_conditions = form.medical_conditions.data
            if hasattr(form, 'allergies') and form.allergies.data:
                current_user.allergies = form.allergies.data
            if hasattr(form, 'emergency_contact') and form.emergency_contact.data:
                current_user.emergency_contact = form.emergency_contact.data
            # حفظ الإعدادات
            if hasattr(form, 'language') and form.language.data:
                current_user.language = form.language.data
            if hasattr(form, 'timezone') and form.timezone.data:
                current_user.timezone = form.timezone.data
            if hasattr(form, 'email_notifications'):
                current_user.email_notifications = form.email_notifications.data
            if hasattr(form, 'sms_notifications'):
                current_user.sms_notifications = form.sms_notifications.data
            
            new_values = {
                'full_name': current_user.full_name,
                'phone': current_user.phone
            }
            
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'edit_profile', 'users', current_user.id, old_values, new_values)
            flash('تم تحديث الملف الشخصي بنجاح!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('profile/edit.html', form=form)
    
    # إعدادات الإشعارات
    @app.route('/settings/notifications', methods=['GET', 'POST'])
    @login_required
    def notification_settings():
        form = NotificationSettingsForm()
        
        if request.method == 'GET':
            # تهيئة الحقول من بيانات المستخدم
            form.email_notifications.data = current_user.email_notifications if hasattr(current_user, 'email_notifications') else True
            form.sms_notifications.data = current_user.sms_notifications if hasattr(current_user, 'sms_notifications') else False
            
            preferences = current_user.get_notification_preferences() if hasattr(current_user, 'get_notification_preferences') else {}
            form.email_reminders.data = preferences.get('email', True)
            form.sms_reminders.data = preferences.get('sms', True)
            form.reminder_advance_minutes.data = SystemSetting.get_setting('reminder_advance_minutes', 10) if hasattr(SystemSetting, 'get_setting') else 10
        
        if form.validate_on_submit():
            # حفظ إعدادات البريد الإلكتروني والرسائل النصية العامة
            if hasattr(current_user, 'email_notifications'):
                current_user.email_notifications = form.email_notifications.data
            if hasattr(current_user, 'sms_notifications'):
                current_user.sms_notifications = form.sms_notifications.data
            
            # حفظ التفضيلات الأخرى
            if hasattr(current_user, 'set_notification_preferences'):
                preferences = {
                    'email': form.email_reminders.data,
                    'sms': form.sms_reminders.data
                }
                current_user.set_notification_preferences(preferences)
            
            if hasattr(SystemSetting, 'set_setting'):
                SystemSetting.set_setting('reminder_advance_minutes', form.reminder_advance_minutes.data)
            
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'update_notification_settings')
            flash('تم تحديث إعدادات الإشعارات بنجاح!', 'success')
            return redirect(url_for('notification_settings'))
        
        return render_template('settings/notifications.html', form=form)
    
    # ===== مسارات التذكيرات =====
    
    @app.route('/reminders')
    @login_required
    def reminders_list():
        """قائمة التذكيرات"""
        return render_template('reminders/list.html')
    
    @app.route('/api/reminders')
    @login_required
    def api_reminders():
        """API للحصول على التذكيرات"""
        try:
            reminders = get_upcoming_reminders(current_user.id)
            return jsonify([{
                'id': r.id,
                'medication_name': r.medication_dose.medication.name,
                'dosage': r.medication_dose.medication.dosage,
                'time': r.reminder_time.strftime('%H:%M'),
                'reminder_time': r.reminder_time.isoformat(),
                'notification_type': r.notification_type,
                'status': r.status
            } for r in reminders])
        except Exception as e:
            app.logger.error(f'خطأ في API التذكيرات: {e}')
            return jsonify({'error': 'خطأ في جلب التذكيرات'}), 500
    
    @app.route('/api/reminders', methods=['POST'])
    @login_required
    def api_add_reminder():
        """إضافة تذكير جديد"""
        try:
            data = request.get_json()
            
            # إنشاء تذكير جديد
            reminder = Reminder(
                medication_dose_id=data.get('medication_id'),
                reminder_time=datetime.fromisoformat(data.get('reminder_time')),
                notification_type=data.get('notification_methods', ['in_app'])[0],
                status='pending'
            )
            
            db.session.add(reminder)
            db.session.commit()
            
            return jsonify({'success': True, 'id': reminder.id})
        except Exception as e:
            app.logger.error(f'خطأ في إضافة التذكير: {e}')
            return jsonify({'error': 'خطأ في إضافة التذكير'}), 500
    
    @app.route('/api/reminders/<int:reminder_id>/mark-taken', methods=['POST'])
    @login_required
    def api_mark_reminder_taken(reminder_id):
        """تسجيل تناول الدواء"""
        try:
            reminder = Reminder.query.get_or_404(reminder_id)
            dose = MedicationDose.query.get(reminder.medication_dose_id)
            
            if dose:
                dose.is_taken = True
                dose.taken_at = datetime.utcnow()
                reminder.status = 'sent'
                reminder.sent_at = datetime.utcnow()
                
                db.session.commit()
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'الجرعة غير موجودة'}), 404
        except Exception as e:
            app.logger.error(f'خطأ في تسجيل تناول الدواء: {e}')
            return jsonify({'error': 'خطأ في تسجيل تناول الدواء'}), 500
    
    @app.route('/api/reminders/<int:reminder_id>/snooze', methods=['POST'])
    @login_required
    def api_snooze_reminder(reminder_id):
        """تأجيل التذكير"""
        try:
            data = request.get_json()
            minutes = data.get('minutes', 15)
            
            reminder = Reminder.query.get_or_404(reminder_id)
            reminder.reminder_time = reminder.reminder_time + timedelta(minutes=minutes)
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في تأجيل التذكير: {e}')
            return jsonify({'error': 'خطأ في تأجيل التذكير'}), 500
    
    @app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
    @login_required
    def api_delete_reminder(reminder_id):
        """حذف التذكير"""
        try:
            reminder = Reminder.query.get_or_404(reminder_id)
            db.session.delete(reminder)
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في حذف التذكير: {e}')
            return jsonify({'error': 'خطأ في حذف التذكير'}), 500
    
    @app.route('/api/medications')
    @login_required
    def api_medications():
        """API للحصول على الأدوية"""
        try:
            medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).all()
            return jsonify([{
                'id': m.id,
                'name': m.name,
                'dosage': m.dosage,
                'notes': m.notes
            } for m in medications])
        except Exception as e:
            app.logger.error(f'خطأ في API الأدوية: {e}')
            return jsonify({'error': 'خطأ في جلب الأدوية'}), 500
    
    # ===== مسارات الإشعارات =====
    
    def get_notification_icon(notification_type):
        # الحصول على أيقونة حسب نوع الإشعار
        icons = {
            'medication': 'fas fa-pills',
            'appointment': 'fas fa-calendar',
            'system': 'fas fa-cog',
            'info': 'fas fa-info-circle',
            'warning': 'fas fa-exclamation-triangle',
            'success': 'fas fa-check-circle',
            'error': 'fas fa-times-circle',
            'reminder': 'fas fa-stethoscope'
        }
        return icons.get(notification_type, 'fas fa-bell')
    
    @app.route('/notifications')
    @login_required
    def notifications_list():
        """قائمة الإشعارات"""
        return render_template('notifications/list.html')
    
    @app.route('/api/notifications')
    @login_required
    def api_notifications():
        # جلب الإشعارات من قاعدة البيانات (الإشعارات المرسلة فقط)
        try:
            notifications = Notification.query.filter(
                Notification.user_id == current_user.id,
                Notification.sent_at.isnot(None)
            ).order_by(Notification.sent_at.desc()).limit(50).all()
            return jsonify([{
                'id': n.id,
                'title': n.title,
                'body': n.message,
                'type': n.notification_type,
                'time': n.sent_at.isoformat() if n.sent_at else (n.created_at.isoformat() if n.created_at else None),
                'isRead': n.is_read,
                'icon': get_notification_icon(n.notification_type)
            } for n in notifications])
        except Exception as e:
            app.logger.error(f'خطأ في API الإشعارات: {e}')
            return jsonify({'error': 'خطأ في جلب الإشعارات'}), 500
    
    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    @login_required
    def api_mark_notification_read(notification_id):
        # تعيين الإشعار كمقروء
        try:
            notification = Notification.query.get_or_404(notification_id)
            if notification.user_id != current_user.id:
                return jsonify({'error': 'غير مصرح'}), 403
            notification.is_read = True
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في تعيين الإشعار كمقروء: {e}')
            return jsonify({'error': 'خطأ في تعيين الإشعار كمقروء'}), 500
    
    @app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
    @login_required
    def api_delete_notification(notification_id):
        # حذف الإشعار
        try:
            notification = Notification.query.get_or_404(notification_id)
            if notification.user_id != current_user.id:
                return jsonify({'error': 'غير مصرح'}), 403
            db.session.delete(notification)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في حذف الإشعار: {e}')
            return jsonify({'error': 'خطأ في حذف الإشعار'}), 500
    
    @app.route('/api/notifications/schedule', methods=['POST'])
    @login_required
    def api_schedule_notification():
        # جدولة إشعار جديد
        try:
            data = request.get_json()
            patient_id = data.get('patient_id')
            title = data.get('title', 'إشعار جديد')
            message = data.get('message', '')
            delay_minutes = data.get('delay_minutes', 1)
            notification_type = data.get('type', 'info')
            
            # إذا كان المريض يرسل لنفسه
            if current_user.role == 'patient':
                if patient_id != current_user.id:
                    return jsonify({'error': 'يمكنك إرسال إشعار لنفسك فقط'}), 403
                target_user_id = current_user.id
            # إذا كان الطبيب يرسل لمريض
            elif current_user.role == 'doctor':
                patient = User.query.get_or_404(patient_id)
                if patient.doctor_id != current_user.id:
                    return jsonify({'error': 'ليس لديك صلاحية لإرسال إشعار لهذا المريض'}), 403
                target_user_id = patient_id
            else:
                return jsonify({'error': 'غير مصرح'}), 403
            
            # حساب وقت الإرسال
            scheduled_time = datetime.utcnow() + timedelta(minutes=delay_minutes)
            
            # إنشاء الإشعار المجدول
            notification = Notification(
                user_id=target_user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                scheduled_time=scheduled_time,
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'notification_id': notification.id,
                'scheduled_time': scheduled_time.isoformat(),
                'message': f'تم جدولة الإشعار ليظهر بعد {delay_minutes} دقيقة'
            })
        except Exception as e:
            app.logger.error(f'خطأ في جدولة الإشعار: {e}')
            return jsonify({'error': 'خطأ في جدولة الإشعار'}), 500
    
    @app.route('/api/notifications/check-scheduled', methods=['POST'])
    @login_required
    def api_check_scheduled_notifications():
        # التحقق من الإشعارات المجدولة وإرسالها
        try:
            now = datetime.utcnow()
            scheduled_notifications = Notification.query.filter(
                Notification.scheduled_time <= now,
                Notification.sent_at.is_(None)
            ).all()
            
            sent_count = 0
            for notification in scheduled_notifications:
                notification.sent_at = now
                db.session.commit()
                sent_count += 1
            
            return jsonify({
                'success': True,
                'sent_count': sent_count,
                'message': f'تم إرسال {sent_count} إشعار'
            })
        except Exception as e:
            app.logger.error(f'خطأ في التحقق من الإشعارات المجدولة: {e}')
            return jsonify({'error': 'خطأ في التحقق من الإشعارات'}), 500
    
    # ===== مسارات الذكاء الاصطناعي =====
    
    @app.route('/ai/dashboard')
    @login_required
    def ai_dashboard():
        """لوحة تحكم الذكاء الاصطناعي"""
        return render_template('ai/dashboard.html')
    
    @app.route('/api/ai/dashboard')
    @login_required
    def api_ai_dashboard():
        """API لبيانات لوحة تحكم الذكاء الاصطناعي"""
        try:
            from ai_service import AIService
            ai_service = AIService()
            dashboard_data = ai_service.get_ai_dashboard_data(current_user.id)
            
            # تحويل البيانات إلى JSON
            data = {
                'recommendations': [{
                    'id': r.id,
                    'title': r.title,
                    'description': r.description,
                    'status': r.status,
                    'confidence_score': r.confidence_score,
                    'created_at': r.created_at.isoformat()
                } for r in dashboard_data.get('recommendations', [])],
                'stats': dashboard_data.get('stats', {}),
                'interactions': dashboard_data.get('interactions', []),
                'timing_suggestions': dashboard_data.get('timing_suggestions', []),
                'adherence': dashboard_data.get('adherence', {}),
                'insights': dashboard_data.get('insights', [])
            }
            
            return jsonify(data)
        except Exception as e:
            app.logger.error(f'خطأ في API لوحة تحكم الذكاء الاصطناعي: {e}')
            return jsonify({'error': 'خطأ في جلب بيانات لوحة التحكم'}), 500
    
    @app.route('/api/ai/recommendations', methods=['POST'])
    @login_required
    def api_request_recommendation():
        """طلب توصية ذكية جديدة"""
        try:
            data = request.get_json()
            
            from ai_service import AIService
            ai_service = AIService()
            
            recommendation = ai_service.generate_recommendation(
                user_id=current_user.id,
                symptoms=data.get('symptoms', ''),
                medical_history=data.get('medical_history', ''),
                current_medications=data.get('current_medications', ''),
                age=data.get('age'),
                gender=data.get('gender', '')
            )
            
            if recommendation:
                return jsonify({'success': True, 'id': recommendation.id})
            else:
                return jsonify({'error': 'فشل في إنشاء التوصية'}), 500
                
        except Exception as e:
            app.logger.error(f'خطأ في طلب التوصية الذكية: {e}')
            return jsonify({'error': 'خطأ في إنشاء التوصية'}), 500
    
    @app.route('/api/ai/recommendations/<int:recommendation_id>/accept', methods=['POST'])
    @login_required
    def api_accept_recommendation(recommendation_id):
        """قبول التوصية الذكية"""
        try:
            from ai_service import AIService
            ai_service = AIService()
            
            success = ai_service.update_recommendation_feedback(recommendation_id, True)
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'فشل في قبول التوصية'}), 500
                
        except Exception as e:
            app.logger.error(f'خطأ في قبول التوصية: {e}')
            return jsonify({'error': 'خطأ في قبول التوصية'}), 500
    
    @app.route('/api/ai/recommendations/<int:recommendation_id>/reject', methods=['POST'])
    @login_required
    def api_reject_recommendation(recommendation_id):
        """رفض التوصية الذكية"""
        try:
            from ai_service import AIService
            ai_service = AIService()
            
            success = ai_service.update_recommendation_feedback(recommendation_id, False)
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'فشل في رفض التوصية'}), 500
                
        except Exception as e:
            app.logger.error(f'خطأ في رفض التوصية: {e}')
            return jsonify({'error': 'خطأ في رفض التوصية'}), 500
    
    # ===== API endpoints إضافية =====
    
    @app.route('/api/medications', methods=['POST'])
    @login_required
    def api_add_medication():
        """إضافة دواء جديد"""
        try:
            data = request.get_json()
            
            medication = Medication(
                user_id=current_user.id,
                name=data.get('name'),
                dosage=data.get('dosage'),
                notes=data.get('notes', ''),
                is_active=True
            )
            
            db.session.add(medication)
            db.session.commit()
            
            # إنشاء الجرعات والتذكيرات
            create_medication_doses(medication)
            
            return jsonify({'success': True, 'id': medication.id})
        except Exception as e:
            app.logger.error(f'خطأ في إضافة الدواء: {e}')
            return jsonify({'error': 'خطأ في إضافة الدواء'}), 500
    
    @app.route('/api/medications/<int:medication_id>', methods=['PUT'])
    @login_required
    def api_update_medication(medication_id):
        """تحديث دواء"""
        try:
            medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first_or_404()
            data = request.get_json()
            
            medication.name = data.get('name', medication.name)
            medication.dosage = data.get('dosage', medication.dosage)
            medication.notes = data.get('notes', medication.notes)
            
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في تحديث الدواء: {e}')
            return jsonify({'error': 'خطأ في تحديث الدواء'}), 500
    
    @app.route('/api/medications/<int:medication_id>', methods=['DELETE'])
    @login_required
    def api_delete_medication(medication_id):
        """حذف دواء"""
        try:
            medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first_or_404()
            medication.is_active = False
            
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في حذف الدواء: {e}')
            return jsonify({'error': 'خطأ في حذف الدواء'}), 500
    
    @app.route('/api/user/profile')
    @login_required
    def api_user_profile():
        """معلومات الملف الشخصي"""
        try:
            return jsonify({
                'id': current_user.id,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'email': current_user.email,
                'phone': current_user.phone,
                'date_of_birth': current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
                'gender': current_user.gender,
                'address': current_user.address,
                'city': current_user.city,
                'state': current_user.state,
                'postal_code': current_user.postal_code,
                'country': current_user.country,
                'blood_type': current_user.blood_type,
                'allergies': current_user.allergies,
                'medical_conditions': current_user.medical_conditions,
                'emergency_contact': current_user.emergency_contact,
                'language': current_user.language,
                'timezone': current_user.timezone,
                'date_format': current_user.date_format
            })
        except Exception as e:
            app.logger.error(f'خطأ في جلب الملف الشخصي: {e}')
            return jsonify({'error': 'خطأ في جلب الملف الشخصي'}), 500
    
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def api_update_profile():
        """تحديث الملف الشخصي"""
        try:
            data = request.get_json()
            
            # تحديث المعلومات الأساسية
            if 'first_name' in data:
                current_user.first_name = data['first_name']
            if 'last_name' in data:
                current_user.last_name = data['last_name']
            if 'email' in data:
                current_user.email = data['email']
            if 'phone' in data:
                current_user.phone = data['phone']
            if 'date_of_birth' in data:
                current_user.date_of_birth = datetime.fromisoformat(data['date_of_birth']) if data['date_of_birth'] else None
            if 'gender' in data:
                current_user.gender = data['gender']
            
            # تحديث العنوان
            if 'address' in data:
                current_user.address = data['address']
            if 'city' in data:
                current_user.city = data['city']
            if 'state' in data:
                current_user.state = data['state']
            if 'postal_code' in data:
                current_user.postal_code = data['postal_code']
            if 'country' in data:
                current_user.country = data['country']
            
            # تحديث المعلومات الطبية
            if 'blood_type' in data:
                current_user.blood_type = data['blood_type']
            if 'allergies' in data:
                current_user.allergies = data['allergies']
            if 'medical_conditions' in data:
                current_user.medical_conditions = data['medical_conditions']
            if 'emergency_contact' in data:
                current_user.emergency_contact = data['emergency_contact']
            
            # تحديث إعدادات اللغة والمنطقة
            if 'language' in data:
                current_user.language = data['language']
            if 'timezone' in data:
                current_user.timezone = data['timezone']
            if 'date_format' in data:
                current_user.date_format = data['date_format']
            
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في تحديث الملف الشخصي: {e}')
            return jsonify({'error': 'خطأ في تحديث الملف الشخصي'}), 500
    
    @app.route('/api/user/change-password', methods=['POST'])
    @login_required
    def api_change_password():
        """تغيير كلمة المرور"""
        try:
            data = request.get_json()
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            # التحقق من كلمة المرور الحالية
            if not SecurityUtils.check_password(current_password, current_user.password_hash):
                return jsonify({'error': 'كلمة المرور الحالية غير صحيحة'}), 400
            
            # تحديث كلمة المرور
            current_user.password_hash = SecurityUtils.hash_password(new_password)
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f'خطأ في تغيير كلمة المرور: {e}')
            return jsonify({'error': 'خطأ في تغيير كلمة المرور'}), 500
    
    @app.route('/api/statistics/dashboard')
    @login_required
    def api_dashboard_statistics():
        """إحصائيات لوحة التحكم"""
        try:
            # إحصائيات الأدوية
            total_medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).count()
            active_reminders = Reminder.query.join(MedicationDose).join(Medication).filter(
                Medication.user_id == current_user.id,
                Reminder.status == 'pending'
            ).count()
            
            # إحصائيات الطلبات
            total_orders = Order.query.filter_by(user_id=current_user.id).count()
            pending_orders = Order.query.filter_by(user_id=current_user.id, status='pending').count()
            
            # إحصائيات التوصيات الذكية
            total_recommendations = AIRecommendation.query.filter_by(user_id=current_user.id).count()
            accepted_recommendations = AIRecommendation.query.filter_by(
                user_id=current_user.id, 
                status='accepted'
            ).count()
            
            # إحصائيات التقارير
            total_reports = Report.query.filter_by(user_id=current_user.id, is_active=True).count()
            
            return jsonify({
                'medications': {
                    'total': total_medications,
                    'active_reminders': active_reminders
                },
                'orders': {
                    'total': total_orders,
                    'pending': pending_orders
                },
                'recommendations': {
                    'total': total_recommendations,
                    'accepted': accepted_recommendations,
                    'acceptance_rate': (accepted_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
                },
                'reports': {
                    'total': total_reports
                }
            })
        except Exception as e:
            app.logger.error(f'خطأ في جلب إحصائيات لوحة التحكم: {e}')
            return jsonify({'error': 'خطأ في جلب الإحصائيات'}), 500
    
    @app.route('/api/search')
    @login_required
    def api_search():
        """البحث العام"""
        try:
            query = request.args.get('q', '').strip()
            if not query:
                return jsonify({'results': []})
            
            results = {
                'medications': [],
                'orders': [],
                'recommendations': [],
                'reports': []
            }
            
            # البحث في الأدوية
            medications = Medication.query.filter(
                Medication.user_id == current_user.id,
                Medication.is_active == True,
                (Medication.name.contains(query) | Medication.notes.contains(query))
            ).limit(5).all()
            
            results['medications'] = [{
                'id': m.id,
                'name': m.name,
                'dosage': m.dosage,
                'type': 'medication'
            } for m in medications]
            
            # البحث في الطلبات
            orders = Order.query.filter(
                Order.user_id == current_user.id,
                Order.order_number.contains(query)
            ).limit(5).all()
            
            results['orders'] = [{
                'id': o.id,
                'order_number': o.order_number,
                'status': o.status,
                'type': 'order'
            } for o in orders]
            
            # البحث في التوصيات
            recommendations = AIRecommendation.query.filter(
                AIRecommendation.user_id == current_user.id,
                (AIRecommendation.title.contains(query) | AIRecommendation.description.contains(query))
            ).limit(5).all()
            
            results['recommendations'] = [{
                'id': r.id,
                'title': r.title,
                'status': r.status,
                'type': 'recommendation'
            } for r in recommendations]
            
            return jsonify({'results': results})
        except Exception as e:
            app.logger.error(f'خطأ في البحث: {e}')
            return jsonify({'error': 'خطأ في البحث'}), 500
    
    # API لتسجيل تناول الجرعة
    @app.route('/api/take-dose/<int:dose_id>', methods=['POST'])
    @login_required
    def api_take_dose(dose_id):
        dose = MedicationDose.query.get_or_404(dose_id)
        
        if not can_view_medication(current_user, dose.medication):
            return jsonify({'error': 'ليس لديك صلاحية'}), 403
        
        dose.is_taken = True
        dose.taken_at = datetime.utcnow()
        
        db.session.commit()
        
        AuditLogger.log_action(current_user.id, 'take_dose', 'medication_doses', dose_id)
        return jsonify({'success': True})

    # ===== مسارات الصيدليات والطلبات =====
    
    @app.route('/pharmacy')
    @login_required
    @admin_required
    def pharmacy_list():
        """قائمة الصيدليات - للمديرين فقط"""
        pharmacies = Pharmacy.query.filter_by(is_active=True).all()
        return render_template('pharmacy/list.html', pharmacies=pharmacies)
    
    @app.route('/pharmacy/<int:pharmacy_id>')
    @login_required
    @admin_required
    def pharmacy_detail(pharmacy_id):
        """تفاصيل الصيدلية - للمديرين فقط"""
        pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
        products = PharmacyProduct.query.filter_by(
            pharmacy_id=pharmacy_id, 
            is_active=True
        ).all()
        return render_template('pharmacy/view.html', pharmacy=pharmacy, products=products)
    
    @app.route('/pharmacy/add', methods=['GET', 'POST'])
    @app.route('/add_pharmacy', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_pharmacy():
        """إضافة صيدلية جديدة - للمديرين فقط"""
        
        form = PharmacyForm()
        if form.validate_on_submit():
            pharmacy = Pharmacy(
                name=form.name.data,
                address=form.address.data,
                phone=form.phone.data,
                email=form.email.data,
                license_number=form.license_number.data,
                owner_name=form.owner_name.data,
                city=form.city.data,
                district=form.district.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                delivery_radius=form.delivery_radius.data,
                delivery_fee=form.delivery_fee.data,
                min_order_amount=form.min_order_amount.data,
                rating=form.rating.data,
                is_active=form.is_active.data
            )
            
            # إضافة الحقول الجديدة إذا كانت متوفرة
            # لا توجد حاجة لحقل description في الوقت الحالي
            
            # حفظ ساعات العمل
            if form.working_hours.data:
                pharmacy.set_working_hours(json.loads(form.working_hours.data))
            
            db.session.add(pharmacy)
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'add_pharmacy', 'pharmacies', pharmacy.id)
            flash('تم إضافة الصيدلية بنجاح!', 'success')
            return redirect(url_for('pharmacy_detail', pharmacy_id=pharmacy.id))
        
        return render_template('pharmacy/add.html', form=form)
    
    @app.route('/pharmacy/<int:pharmacy_id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def edit_pharmacy(pharmacy_id):
        """تعديل الصيدلية - للمديرين فقط"""
        
        pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
        form = PharmacyForm(obj=pharmacy)
        
        if form.validate_on_submit():
            old_values = {
                'name': pharmacy.name,
                'address': pharmacy.address,
                'phone': pharmacy.phone
            }
            
            pharmacy.name = form.name.data
            pharmacy.address = form.address.data
            pharmacy.phone = form.phone.data
            pharmacy.email = form.email.data
            pharmacy.license_number = form.license_number.data
            pharmacy.owner_name = form.owner_name.data
            pharmacy.city = form.city.data
            pharmacy.district = form.district.data
            pharmacy.latitude = form.latitude.data
            pharmacy.longitude = form.longitude.data
            pharmacy.delivery_radius = form.delivery_radius.data
            pharmacy.delivery_fee = form.delivery_fee.data
            pharmacy.min_order_amount = form.min_order_amount.data
            pharmacy.rating = form.rating.data
            pharmacy.is_active = form.is_active.data
            
            # حفظ ساعات العمل
            if form.working_hours.data:
                pharmacy.set_working_hours(json.loads(form.working_hours.data))
            
            new_values = {
                'name': pharmacy.name,
                'address': pharmacy.address,
                'phone': pharmacy.phone
            }
            
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'edit_pharmacy', 'pharmacies', pharmacy.id, old_values, new_values)
            flash('تم تحديث الصيدلية بنجاح!', 'success')
            return redirect(url_for('pharmacy_detail', pharmacy_id=pharmacy.id))
        
        return render_template('pharmacy/edit.html', form=form, pharmacy=pharmacy)
    
    @app.route('/pharmacy/<int:pharmacy_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def delete_pharmacy(pharmacy_id):
        """حذف الصيدلية - للمديرين فقط"""
        
        pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
        
        AuditLogger.log_action(current_user.id, 'delete_pharmacy', 'pharmacies', pharmacy.id)
        
        pharmacy.is_active = False
        db.session.commit()
        
        flash('تم حذف الصيدلية بنجاح!', 'success')
        return redirect(url_for('pharmacy_list'))
    
    @app.route('/products')
    @login_required
    def products_list():
        """قائمة المنتجات"""
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '')
        search_query = request.args.get('q', '')
        
        query = PharmacyProduct.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if search_query:
            query = query.filter(
                PharmacyProduct.name.ilike(f'%{search_query}%')
            )
        
        products = query.paginate(
            page=page, per_page=20, error_out=False
        )
        
        categories = db.session.query(PharmacyProduct.category).distinct().all()
        return render_template('products/list.html', 
                             products=products, 
                             categories=categories,
                             current_category=category,
                             search_query=search_query)
    
    @app.route('/products/<int:product_id>')
    @login_required
    def product_detail(product_id):
        """تفاصيل المنتج"""
        product = PharmacyProduct.query.get_or_404(product_id)
        return render_template('products/detail.html', product=product)
    
    @app.route('/products/add', methods=['GET', 'POST'])
    @app.route('/add_product', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_product():
        """إضافة منتج جديد - للمديرين فقط"""
        
        form = PharmacyProductForm()
        # إضافة خيارات الصيدليات
        pharmacies = Pharmacy.query.filter_by(is_active=True).all()
        form.pharmacy_id.choices = [(p.id, p.name) for p in pharmacies]
        
        if form.validate_on_submit():
            product = PharmacyProduct(
                pharmacy_id=form.pharmacy_id.data,
                name=form.name.data,
                generic_name=form.generic_name.data,
                manufacturer=form.manufacturer.data,
                form=form.form.data,
                strength=form.strength.data,
                description=form.description.data,
                price=form.price.data,
                stock_quantity=form.stock_quantity.data,
                requires_prescription=form.is_prescription_required.data,
                category=form.category.data,
                side_effects=form.side_effects.data,
                contraindications=form.contraindications.data,
                dosage_instructions=form.dosage_instructions.data,
                is_active=form.is_active.data
            )
            
            db.session.add(product)
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'add_product', 'pharmacy_products', product.id)
            flash('تم إضافة المنتج بنجاح!', 'success')
            return redirect(url_for('product_detail', product_id=product.id))
        
        return render_template('products/add.html', form=form)
    
    @app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def edit_product(product_id):
        """تعديل المنتج - للمديرين فقط"""
        
        product = PharmacyProduct.query.get_or_404(product_id)
        form = PharmacyProductForm(obj=product)
        
        # إضافة خيارات الصيدليات
        pharmacies = Pharmacy.query.filter_by(is_active=True).all()
        form.pharmacy_id.choices = [(p.id, p.name) for p in pharmacies]
        
        if form.validate_on_submit():
            old_values = {
                'name': product.name,
                'price': str(product.price),
                'stock_quantity': product.stock_quantity
            }
            
            product.pharmacy_id = form.pharmacy_id.data
            product.name = form.name.data
            product.generic_name = form.generic_name.data
            product.manufacturer = form.manufacturer.data
            product.form = form.form.data
            product.strength = form.strength.data
            product.description = form.description.data
            product.price = form.price.data
            product.stock_quantity = form.stock_quantity.data
            product.requires_prescription = form.is_prescription_required.data
            product.category = form.category.data
            product.side_effects = form.side_effects.data
            product.contraindications = form.contraindications.data
            product.dosage_instructions = form.dosage_instructions.data
            product.is_active = form.is_active.data
            
            new_values = {
                'name': product.name,
                'price': str(product.price),
                'stock_quantity': product.stock_quantity
            }
            
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'edit_product', 'pharmacy_products', product.id, old_values, new_values)
            flash('تم تحديث المنتج بنجاح!', 'success')
            return redirect(url_for('product_detail', product_id=product.id))
        
        return render_template('products/edit.html', form=form, product=product)
    
    @app.route('/products/<int:product_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def delete_product(product_id):
        """حذف المنتج - للمديرين فقط"""
        
        product = PharmacyProduct.query.get_or_404(product_id)
        
        AuditLogger.log_action(current_user.id, 'delete_product', 'pharmacy_products', product.id)
        
        product.is_active = False
        db.session.commit()
        
        flash('تم حذف المنتج بنجاح!', 'success')
        return redirect(url_for('products_list'))
    
    @app.route('/cart')
    @login_required
    def cart():
        """سلة التسوق"""
        cart_items = request.session.get('cart', [])
        total = 0
        
        for item in cart_items:
            product = PharmacyProduct.query.get(item['product_id'])
            if product:
                item['product'] = product
                item['subtotal'] = item['quantity'] * float(product.price)
                total += item['subtotal']
        
        return render_template('orders/cart.html', cart_items=cart_items, total=total)
    
    @app.route('/cart/add', methods=['POST'])
    @app.route('/add_to_cart', methods=['POST'])
    @login_required
    def add_to_cart():
        """إضافة منتج للسلة"""
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', 1, type=int)
        
        if not product_id or quantity < 1:
            return jsonify({'success': False, 'message': 'بيانات غير صحيحة'})
        
        product = PharmacyProduct.query.get(product_id)
        if not product or not product.is_in_stock():
            return jsonify({'success': False, 'message': 'المنتج غير متوفر'})
        
        # إضافة للسلة (في حالة حقيقية، ستكون في قاعدة البيانات أو Redis)
        cart = request.session.get('cart', [])
        
        # التحقق من وجود المنتج في السلة
        for item in cart:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                break
        else:
            cart.append({
                'product_id': product_id,
                'quantity': quantity
            })
        
        request.session['cart'] = cart
        
        return jsonify({
            'success': True, 
            'message': 'تم إضافة المنتج للسلة',
            'cart_count': len(cart)
        })
    
    @app.route('/cart/remove', methods=['POST'])
    @login_required
    def remove_from_cart():
        """إزالة منتج من السلة"""
        product_id = request.form.get('product_id', type=int)
        
        if not product_id:
            return jsonify({'success': False, 'message': 'بيانات غير صحيحة'})
        
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['product_id'] != product_id]
        request.session['cart'] = cart
        
        return jsonify({
            'success': True, 
            'message': 'تم إزالة المنتج من السلة',
            'cart_count': len(cart)
        })
    
    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        """صفحة الدفع"""
        if request.method == 'GET':
            cart_items = request.session.get('cart', [])
            if not cart_items:
                flash('السلة فارغة', 'warning')
                return redirect(url_for('products_list'))
            
            # حساب المجموع
            total = 0
            for item in cart_items:
                product = PharmacyProduct.query.get(item['product_id'])
                if product:
                    item['product'] = product
                    item['subtotal'] = item['quantity'] * float(product.price)
                    total += item['subtotal']
            
            # الحصول على الصيدليات المتاحة
            pharmacies = Pharmacy.query.filter_by(is_active=True).all()
            
            form = OrderForm()
            form.pharmacy_id.choices = [(p.id, p.name) for p in pharmacies]
            
            return render_template('orders/checkout.html', 
                                 cart_items=cart_items, 
                                 total=total, 
                                 form=form)
        
        else:
            form = OrderForm()
            if form.validate_on_submit():
                cart_items = request.session.get('cart', [])
                if not cart_items:
                    flash('السلة فارغة', 'error')
                    return redirect(url_for('checkout'))
                
                # تحويل عناصر السلة إلى تنسيق الطلب
                order_items = []
                for item in cart_items:
                    order_items.append({
                        'product_id': item['product_id'],
                        'quantity': item['quantity']
                    })
                
                # إنشاء الطلب
                from order_management import create_medication_order
                
                success, message, order = create_medication_order(
                    user_id=current_user.id,
                    pharmacy_id=form.pharmacy_id.data,
                    items=order_items,
                    delivery_address=form.delivery_address.data,
                    delivery_phone=form.delivery_phone.data,
                    payment_method=form.payment_method.data,
                    delivery_notes=form.delivery_notes.data
                )
                
                if success:
                    # مسح السلة
                    request.session['cart'] = []
                    flash(f'تم إنشاء الطلب بنجاح! رقم الطلب: {order.order_number}', 'success')
                    return redirect(url_for('order_detail', order_id=order.id))
                else:
                    flash(f'خطأ في إنشاء الطلب: {message}', 'error')
            
            return redirect(url_for('checkout'))
    
    @app.route('/orders')
    @login_required
    def orders_list():
        """قائمة طلبات المستخدم"""
        from order_management import OrderManagementSystem
        
        order_system = OrderManagementSystem()
        orders = order_system.get_user_orders(current_user.id)
        
        return render_template('orders/list.html', orders=orders)
    
    @app.route('/orders/<int:order_id>')
    @login_required
    def order_detail(order_id):
        """تفاصيل الطلب"""
        from order_management import OrderManagementSystem
        
        order_system = OrderManagementSystem()
        order = order_system.get_order_details(order_id)
        
        if not order or (order.user_id != current_user.id and current_user.role != 'user'):
            flash('الطلب غير موجود', 'error')
            return redirect(url_for('orders_list'))
        
        tracking = order_system.get_order_tracking(order_id)
        
        return render_template('orders/detail.html', order=order, tracking=tracking)
    
    @app.route('/orders/<int:order_id>/cancel', methods=['POST'])
    @login_required
    def cancel_order(order_id):
        """إلغاء الطلب"""
        from order_management import OrderManagementSystem
        
        order_system = OrderManagementSystem()
        order = Order.query.get_or_404(order_id)
        
        if order.user_id != current_user.id:
            flash('ليس لديك صلاحية لإلغاء هذا الطلب', 'error')
            return redirect(url_for('orders_list'))
        
        if order.status in ['delivered', 'cancelled']:
            flash('لا يمكن إلغاء هذا الطلب', 'error')
            return redirect(url_for('order_detail', order_id=order_id))
        
        success, message = order_system.update_order_status(
            order_id, 'cancelled', current_user.full_name, 'تم الإلغاء من قبل المستخدم'
        )
        
        if success:
            flash('تم إلغاء الطلب بنجاح', 'success')
        else:
            flash(f'خطأ في إلغاء الطلب: {message}', 'error')
        
        return redirect(url_for('order_detail', order_id=order_id))
    
    @app.route('/orders/track', methods=['GET', 'POST'])
    def track_order():
        """تتبع الطلب"""
        if request.method == 'POST':
            form = OrderTrackingForm()
            if form.validate_on_submit():
                order_number = form.order_number.data
                order = Order.query.filter_by(order_number=order_number).first()
                
                if order:
                    from order_management import OrderManagementSystem
                    order_system = OrderManagementSystem()
                    tracking = order_system.get_order_tracking(order.id)
                    
                    return render_template('orders/tracking.html', 
                                         order=order, 
                                         tracking=tracking)
                else:
                    flash('رقم الطلب غير صحيح', 'error')
            
            return render_template('orders/track_form.html', form=form)
        
        form = OrderTrackingForm()
        return render_template('orders/track_form.html', form=form)
    
    # ===== مسارات إدارة الطلبات للصيادلة =====
    
    @app.route('/pharmacy/orders')
    @login_required
    @admin_required
    def pharmacy_orders():
        """طلبات الصيدلية - للمديرين فقط"""
        
        from order_management import OrderManagementSystem
        
        order_system = OrderManagementSystem()
        # في التطبيق الحقيقي، ستحتاج لربط الصيدلي بالصيدلية
        orders = Order.query.filter_by(pharmacy_id=1).all()  # مثال
        
        return render_template('pharmacy/orders.html', orders=orders)
    
    @app.route('/pharmacy/orders/<int:order_id>/update', methods=['POST'])
    @login_required
    @admin_required
    def update_order_status():
        """تحديث حالة الطلب - للمديرين فقط"""
        
        order_id = request.form.get('order_id', type=int)
        new_status = request.form.get('status')
        notes = request.form.get('notes', '')
        
        if not order_id or not new_status:
            return jsonify({'success': False, 'message': 'بيانات غير صحيحة'})
        
        from order_management import OrderManagementSystem
        
        order_system = OrderManagementSystem()
        success, message = order_system.update_order_status(
            order_id, new_status, current_user.full_name, notes
        )
        
        return jsonify({'success': success, 'message': message})
    
    # ===== مسارات الذكاء الاصطناعي =====
    
    @app.route('/recommendations')
    @login_required
    def recommendations():
        """صفحة التوصيات الذكية"""
        recommendations = AIRecommendation.query.filter_by(
            user_id=current_user.id
        ).order_by(AIRecommendation.created_at.desc()).all()
        
        return render_template('ai/recommendations.html', recommendations=recommendations)
    
    @app.route('/ai/recommendations/request', methods=['GET', 'POST'])
    @login_required
    def request_recommendation():
        """طلب توصية جديدة"""
        if request.method == 'POST':
            from ai_service import AIService
            
            ai_service = AIService()
            symptoms = request.form.get('symptoms', '')
            medical_history = request.form.get('medical_history', '')
            current_medications = request.form.get('current_medications', '')
            age = request.form.get('age', type=int)
            gender = request.form.get('gender', '')
            
            # إنشاء توصية ذكية
            recommendation = ai_service.generate_recommendation(
                user_id=current_user.id,
                symptoms=symptoms,
                medical_history=medical_history,
                current_medications=current_medications,
                age=age,
                gender=gender
            )
            
            if recommendation:
                flash('تم إنشاء التوصية الذكية بنجاح!', 'success')
                return redirect(url_for('recommendations'))
            else:
                flash('خطأ في إنشاء التوصية الذكية', 'error')
        
        return render_template('ai/request_recommendation.html')
    
    @app.route('/ai/recommendations/<int:recommendation_id>/accept', methods=['POST'])
    @login_required
    def accept_recommendation(recommendation_id):
        """قبول التوصية"""
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        
        if recommendation.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لقبول هذه التوصية'})
        
        recommendation.status = 'accepted'
        recommendation.accepted_at = datetime.utcnow()
        db.session.commit()
        
        AuditLogger.log_action(current_user.id, 'accept_recommendation', 'ai_recommendations', recommendation_id)
        
        return jsonify({'success': True, 'message': 'تم قبول التوصية بنجاح'})
    
    @app.route('/ai/recommendations/<int:recommendation_id>/reject', methods=['POST'])
    @login_required
    def reject_recommendation(recommendation_id):
        """رفض التوصية"""
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        
        if recommendation.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لرفض هذه التوصية'})
        
        recommendation.status = 'rejected'
        recommendation.rejected_at = datetime.utcnow()
        db.session.commit()
        
        AuditLogger.log_action(current_user.id, 'reject_recommendation', 'ai_recommendations', recommendation_id)
        
        return jsonify({'success': True, 'message': 'تم رفض التوصية'})
    
    @app.route('/ai/recommendations/<int:recommendation_id>/save', methods=['POST'])
    @login_required
    def save_recommendation(recommendation_id):
        """حفظ التوصية"""
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        
        if recommendation.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لحفظ هذه التوصية'})
        
        recommendation.is_saved = True
        db.session.commit()
        
        AuditLogger.log_action(current_user.id, 'save_recommendation', 'ai_recommendations', recommendation_id)
        
        return jsonify({'success': True, 'message': 'تم حفظ التوصية بنجاح'})
    
    @app.route('/recommendations/feedback', methods=['POST'])
    @login_required
    def recommendation_feedback():
        """تقييم التوصيات"""
        recommendation_id = request.form.get('recommendation_id', type=int)
        is_accepted = request.form.get('is_accepted') == 'true'
        feedback_score = request.form.get('feedback_score', type=int)
        
        if not recommendation_id:
            return jsonify({'success': False, 'message': 'بيانات غير صحيحة'})
        
        from ai_recommendation_engine import AIRecommendationEngine
        
        engine = AIRecommendationEngine()
        success = engine.update_recommendation_feedback(
            recommendation_id, is_accepted, feedback_score
        )
        
        return jsonify({
            'success': success, 
            'message': 'تم حفظ التقييم' if success else 'خطأ في حفظ التقييم'
        })
    
    @app.route('/recommendations/dosage/<medication_name>')
    @login_required
    def dosage_recommendation(medication_name):
        """توصيات الجرعات"""
        from ai_recommendation_engine import AIRecommendationEngine
        
        engine = AIRecommendationEngine()
        recommendation = engine.get_dosage_recommendations(
            current_user.id, medication_name
        )
        
        return jsonify(recommendation)
    
    # ===== مسارات إعدادات النظام =====
    
    
    @app.route('/settings/privacy', methods=['GET', 'POST'])
    @login_required
    def privacy_settings():
        """إعدادات الخصوصية"""
        if request.method == 'POST':
            # حفظ إعدادات الخصوصية
            current_user.profile_visibility = request.form.get('profile_visibility', 'private')
            current_user.data_sharing = request.form.get('data_sharing', 'false') == 'true'
            current_user.analytics_tracking = request.form.get('analytics_tracking', 'false') == 'true'
            
            db.session.commit()
            flash('تم حفظ إعدادات الخصوصية بنجاح!', 'success')
            return redirect(url_for('privacy_settings'))
        
        return render_template('settings/privacy.html')
    
    @app.route('/settings/security', methods=['GET', 'POST'])
    @login_required
    def security_settings():
        """إعدادات الأمان"""
        if request.method == 'POST':
            # تغيير كلمة المرور
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password and confirm_password:
                if new_password != confirm_password:
                    flash('كلمات المرور غير متطابقة', 'error')
                    return redirect(url_for('security_settings'))
                
                if not SecurityUtils.check_password(current_password, current_user.password_hash):
                    flash('كلمة المرور الحالية غير صحيحة', 'error')
                    return redirect(url_for('security_settings'))
                
                current_user.password_hash = SecurityUtils.hash_password(new_password)
                db.session.commit()
                flash('تم تغيير كلمة المرور بنجاح!', 'success')
                return redirect(url_for('security_settings'))
        
        return render_template('settings/security.html')
    
    @app.route('/settings/account', methods=['GET', 'POST'])
    @login_required
    def account_settings():
        """إعدادات الحساب"""
        if request.method == 'POST':
            # تحديث معلومات الحساب
            current_user.full_name = request.form.get('full_name', current_user.full_name)
            current_user.phone = request.form.get('phone', current_user.phone)
            current_user.date_of_birth = request.form.get('date_of_birth')
            current_user.gender = request.form.get('gender', current_user.gender)
            current_user.emergency_contact = request.form.get('emergency_contact', current_user.emergency_contact)
            
            db.session.commit()
            flash('تم تحديث معلومات الحساب بنجاح!', 'success')
            return redirect(url_for('account_settings'))
        
        return render_template('settings/account.html')
    
    @app.route('/settings/system', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def system_settings():
        """إعدادات النظام - للمديرين فقط"""
        
        if request.method == 'POST':
            # حفظ إعدادات النظام
            setting_name = request.form.get('setting_name')
            setting_value = request.form.get('setting_value')
            
            if setting_name and setting_value:
                setting = SystemSetting.query.filter_by(name=setting_name).first()
                if setting:
                    setting.value = setting_value
                else:
                    setting = SystemSetting(name=setting_name, value=setting_value)
                    db.session.add(setting)
                
                db.session.commit()
                flash('تم حفظ إعدادات النظام بنجاح!', 'success')
                return redirect(url_for('system_settings'))
        
        settings = SystemSetting.query.all()
        # إنشاء كائن system_settings من قائمة settings
        class SystemSettingsDict:
            def __init__(self, settings_list):
                for setting in settings_list:
                    setattr(self, setting.name, setting.value)
                # القيم الافتراضية
                defaults = {
                    'force_2fa': False,
                    'auto_lockout': False,
                    'session_timeout': False,
                    'session_timeout_minutes': 30,
                    'email_notifications': True,
                    'sms_notifications': False,
                    'whatsapp_notifications': False,
                    'notification_frequency': 'immediate',
                    'ai_recommendations': True,
                    'data_analysis': False,
                    'ai_confidence_threshold': 70,
                    'auto_backup': False,
                    'backup_frequency': 'daily',
                    'backup_retention_days': 30,
                    'auto_reports': False,
                    'report_frequency': 'monthly',
                    'usage_analytics': True
                }
                for key, value in defaults.items():
                    if not hasattr(self, key):
                        setattr(self, key, value)
        
        system_settings = SystemSettingsDict(settings)
        return render_template('settings/system.html', settings=settings, system_settings=system_settings)

    # ===== مسارات المراجعات =====
    @app.route('/reviews')
    @login_required
    def reviews_list():
        """قائمة المراجعات - خاصة بكل مستخدم فقط"""
        page = request.args.get('page', 1, type=int)
        # عرض مراجعات المستخدم الحالي فقط
        reviews = Review.query.filter_by(user_id=current_user.id, is_active=True)\
                            .order_by(Review.created_at.desc())\
                            .paginate(page=page, per_page=10, error_out=False)
        return render_template('reviews/list.html', reviews=reviews)

    @app.route('/reviews/add', methods=['GET', 'POST'])
    @app.route('/add_review', methods=['GET', 'POST'])
    @login_required
    def add_review():
        """إضافة مراجعة جديدة - خاصة بكل مستخدم فقط"""
        try:
            if request.method == 'POST':
                pharmacy_id = request.form.get('pharmacy_id', type=int)
                product_id = request.form.get('product_id', type=int)
                rating = request.form.get('rating', type=int)
                title = request.form.get('title')
                comment = request.form.get('comment')
                
                if not rating or rating < 1 or rating > 5:
                    flash('يرجى اختيار تقييم صحيح', 'error')
                    return redirect(url_for('add_review'))
                
                if not comment or len(comment.strip()) == 0:
                    flash('يرجى كتابة تعليق', 'error')
                    return redirect(url_for('add_review'))
                
                review = Review(
                    user_id=current_user.id,  # المستخدم الحالي فقط
                    pharmacy_id=pharmacy_id if pharmacy_id else None,
                    product_id=product_id if product_id else None,
                    rating=rating,
                    title=title,
                    comment=comment
                )
                
                db.session.add(review)
                db.session.commit()
                
                AuditLogger.log_action(current_user.id, 'add_review', 'reviews', review.id)
                flash('تم إضافة المراجعة بنجاح', 'success')
                return redirect(url_for('reviews_list'))
            
            pharmacies = Pharmacy.query.filter_by(is_active=True).all()
            products = PharmacyProduct.query.filter_by(is_active=True).all()
            return render_template('reviews/add.html', pharmacies=pharmacies, products=products)
        except Exception as e:
            app.logger.error(f'خطأ في إضافة المراجعة: {e}')
            db.session.rollback()
            flash('حدث خطأ أثناء إضافة المراجعة. يرجى المحاولة مرة أخرى.', 'error')
            return redirect(url_for('reviews_list'))

    @app.route('/reviews/<int:review_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_review(review_id):
        """تعديل مراجعة"""
        review = Review.query.get_or_404(review_id)
        
        if review.user_id != current_user.id:
            flash('ليس لديك صلاحية لتعديل هذه المراجعة', 'error')
            return redirect(url_for('reviews_list'))
        
        if request.method == 'POST':
            review.rating = request.form.get('rating', type=int)
            review.title = request.form.get('title')
            review.comment = request.form.get('comment')
            
            db.session.commit()
            flash('تم تحديث المراجعة بنجاح', 'success')
            return redirect(url_for('reviews_list'))
        
        pharmacies = Pharmacy.query.filter_by(is_active=True).all()
        products = PharmacyProduct.query.filter_by(is_active=True).all()
        return render_template('reviews/edit.html', review=review, pharmacies=pharmacies, products=products)

    @app.route('/reviews/<int:review_id>/delete', methods=['POST'])
    @login_required
    def delete_review(review_id):
        """حذف مراجعة"""
        review = Review.query.get_or_404(review_id)
        
        if review.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لحذف هذه المراجعة'})
        
        review.is_active = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم حذف المراجعة بنجاح'})

    @app.route('/profile/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        """تغيير كلمة المرور"""
        form = ChangePasswordForm()
        
        if form.validate_on_submit():
            # التحقق من كلمة المرور الحالية
            if not SecurityUtils.check_password(form.current_password.data, current_user.password_hash):
                flash('كلمة المرور الحالية غير صحيحة', 'error')
                return render_template('profile/change_password.html', form=form)
            
            # تحديث كلمة المرور
            current_user.password_hash = SecurityUtils.hash_password(form.new_password.data)
            db.session.commit()
            
            AuditLogger.log_action(current_user.id, 'change_password', 'users', current_user.id)
            flash('تم تغيير كلمة المرور بنجاح!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('profile/change_password.html', form=form)

# الدوال المساعدة
def get_upcoming_reminders(user_id, hours=24):
    """الحصول على التذكيرات القادمة"""
    now = datetime.utcnow()
    future = now + timedelta(hours=hours)
    
    reminders = Reminder.query.join(MedicationDose).join(Medication).filter(
        Medication.user_id == user_id,
        Reminder.reminder_time >= now,
        Reminder.reminder_time <= future,
        Reminder.status == 'pending'
    ).all()
    
    return reminders

def get_doctor_patients(doctor_id):
    # الحصول على مرضى الطبيب
    shared_records = SharedRecord.query.filter_by(
        shared_with_user_id=doctor_id,
        permission_type='read_write',
        is_active=True
    ).all()
    
    patient_ids = list(set([record.patient_id for record in shared_records]))
    patients = User.query.filter(User.id.in_(patient_ids)).all()
    
    return patients

def get_user_stats():
    # الحصول على إحصائيات المستخدمين
    from models import Income, Expense
    
    # حساب الإيرادات من الطلبات
    orders_revenue = sum([float(order.total_amount) for order in Order.query.filter_by(status='delivered').all()]) if Order.query.filter_by(status='delivered').count() > 0 else 0
    
    # حساب إجمالي الدخل من جدول الدخل
    total_income = db.session.query(db.func.sum(Income.amount)).scalar() or 0
    
    # حساب إجمالي المصروفات
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    # حساب الأرباح (الدخل - المصروفات)
    total_profit = float(total_income) - float(total_expenses)
    
    # حساب الدخل والمصروفات لهذا الشهر
    today = datetime.utcnow().date()
    first_day_of_month = today.replace(day=1)
    monthly_income = db.session.query(db.func.sum(Income.amount)).filter(Income.transaction_date >= first_day_of_month).scalar() or 0
    monthly_expenses = db.session.query(db.func.sum(Expense.amount)).filter(Expense.transaction_date >= first_day_of_month).scalar() or 0
    
    stats = {
        'total_users': User.query.count(),
        'total_patients': User.query.filter_by(role='patient', is_active=True).count(),
        'total_doctors': User.query.filter_by(role='doctor', is_active=True).count(),
        'total_pharmacists': User.query.filter_by(role='pharmacist', is_active=True).count(),
        'total_admins': User.query.filter_by(role='user', is_active=True).count(),
        'total_medications': Medication.query.filter_by(is_active=True).count(),
        'pending_consultations': Consultation.query.filter_by(status='pending').count(),
        'total_reviews': Review.query.count(),
        'total_orders': Order.query.count(),
        'total_pharmacies': Pharmacy.query.filter_by(is_active=True).count(),
        'active_users': User.query.filter(User.updated_at >= datetime.utcnow() - timedelta(days=30)).count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'total_revenue': float(orders_revenue),
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'total_profit': float(total_profit),
        'monthly_income': float(monthly_income),
        'monthly_expenses': float(monthly_expenses),
        'monthly_profit': float(monthly_income) - float(monthly_expenses)
    }
    return stats

def can_edit_medication(user, medication):
    # التحقق من إمكانية تعديل الدواء
    if user.role in ['user', 'patient'] and medication.user_id == user.id:
        return True
    elif user.role == 'user':
        return True
    return False

def can_view_medication(user, medication):
    # التحقق من إمكانية عرض الدواء
    if can_edit_medication(user, medication):
        return True
    return False

def create_medication_doses(medication):
    # إنشاء الجرعات المحددة للدواء
    frequency = medication.frequency
    
    # تحديد الأوقات حسب التكرار
    times = []
    if 'مرة واحدة يومياً' in frequency:
        times = [time(8, 0)]  # 8:00 صباحاً
    elif 'مرتين يومياً' in frequency:
        times = [time(8, 0), time(20, 0)]  # 8:00 صباحاً و 8:00 مساءً
    elif 'ثلاث مرات يومياً' in frequency:
        times = [time(8, 0), time(14, 0), time(20, 0)]  # 8:00، 2:00، 8:00
    elif 'أربع مرات يومياً' in frequency:
        times = [time(8, 0), time(12, 0), time(16, 0), time(20, 0)]  # كل 4 ساعات
    elif 'كل 6 ساعات' in frequency:
        times = [time(6, 0), time(12, 0), time(18, 0), time(0, 0)]  # كل 6 ساعات
    elif 'كل 8 ساعات' in frequency:
        times = [time(8, 0), time(16, 0), time(0, 0)]  # كل 8 ساعات
    elif 'كل 12 ساعة' in frequency:
        times = [time(8, 0), time(20, 0)]  # كل 12 ساعة
    
    # إنشاء الجرعات
    for scheduled_time in times:
        dose = MedicationDose(
            medication_id=medication.id,
            scheduled_time=scheduled_time
        )
        db.session.add(dose)
        
        # إنشاء التذكيرات
        create_reminders_for_dose(dose)
    
    # لا نستخدم commit هنا لأن الـ commit يتم في الدالة التي تستدعيها

def create_reminders_for_dose(dose):
    # إنشاء التذكيرات للجرعة
    advance_minutes = int(SystemSetting.get_setting('reminder_advance_minutes', 10))
    
    # حساب وقت التذكير
    reminder_time = datetime.combine(date.today(), dose.scheduled_time) - timedelta(minutes=advance_minutes)
    
    # إنشاء تذكير للبريد الإلكتروني
    email_reminder = Reminder(
        medication_dose_id=dose.id,
        reminder_time=reminder_time,
        notification_type='email'
    )
    db.session.add(email_reminder)
    
    # إنشاء تذكير للرسائل النصية
    sms_reminder = Reminder(
        medication_dose_id=dose.id,
        reminder_time=reminder_time,
        notification_type='sms'
    )
    db.session.add(sms_reminder)

def generate_pdf_report(report):
    # توليد تقرير PDF
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # إنشاء ملف PDF
        filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # إعداد النص العربي
        arabic_style = ParagraphStyle(
            'Arabic',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            alignment=2,  # محاذاة إلى اليمين
            rightIndent=20
        )
        
        # محتوى التقرير
        story = []
        
        # العنوان
        title = Paragraph("تقرير الأدوية - منصة دوائي", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # معلومات التقرير
        info_data = [
            ['نوع التقرير:', report.report_type],
            ['تاريخ البداية:', report.start_date.strftime('%Y-%m-%d')],
            ['تاريخ النهاية:', report.end_date.strftime('%Y-%m-%d')],
            ['تاريخ الإنشاء:', report.generated_at.strftime('%Y-%m-%d %H:%M')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # قائمة الأدوية
        medications = Medication.query.filter(
            Medication.user_id == report.user_id,
            Medication.start_date <= report.end_date,
            Medication.is_active == True
        ).all()
        
        if medications:
            med_title = Paragraph("الأدوية الموصوفة", styles['Heading2'])
            story.append(med_title)
            story.append(Spacer(1, 10))
            
            med_data = [['اسم الدواء', 'الشكل', 'الجرعة', 'التكرار', 'تاريخ البدء', 'الملاحظات']]
            
            for med in medications:
                med_data.append([
                    med.name,
                    med.form,
                    med.dosage,
                    med.frequency,
                    med.start_date.strftime('%Y-%m-%d'),
                    med.notes or ''
                ])
            
            med_table = Table(med_data, colWidths=[1.5*inch, 0.8*inch, 1*inch, 1.2*inch, 1*inch, 1.5*inch])
            med_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(med_table)
        
        # إنشاء PDF
        doc.build(story)
        
        return filepath
        
    except Exception as e:
        app.logger.error(f"خطأ في إنشاء PDF: {e}")
        return None
    @app.route('/ai/recommendations')
    @login_required
    def ai_recommendations():
        """صفحة توصيات الذكاء الاصطناعي"""
        try:
            from ai_service import AIService
            ai_service = AIService()
            data = ai_service.get_ai_dashboard_data(current_user.id)
            return render_template('ai/recommendations.html', data=data)
        except Exception as e:
            app.logger.error(f'خطأ في صفحة التوصيات: {e}')
            flash('حدث خطأ في تحميل التوصيات', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/ai/generate', methods=['POST'])
    @login_required
    def ai_generate_recommendation():
        """إنشاء توصية جديدة"""
        try:
            from ai_service import AIService
            ai_service = AIService()
            
            symptoms = request.form.get('symptoms', '')
            medical_history = request.form.get('medical_history', '')
            current_medications = request.form.get('current_medications', '')
            
            recommendation = ai_service.generate_recommendation(
                user_id=current_user.id,
                symptoms=symptoms,
                medical_history=medical_history,
                current_medications=current_medications
            )
            
            if recommendation:
                flash('تم إنشاء التوصية بنجاح!', 'success')
            else:
                flash('حدث خطأ في إنشاء التوصية', 'error')
            
            return redirect(url_for('ai_recommendations'))
        except Exception as e:
            app.logger.error(f'خطأ في إنشاء التوصية: {e}')
            flash('حدث خطأ في إنشاء التوصية', 'error')
            return redirect(url_for('ai_recommendations'))
    
    @app.route('/ai/feedback/<int:recommendation_id>', methods=['POST'])
    @login_required
    def ai_recommendation_feedback(recommendation_id):
        """تقديم تغذية راجعة على التوصية"""
        try:
            from ai_service import AIService
            ai_service = AIService()
            
            is_accepted = request.form.get('is_accepted') == 'true'
            feedback_score = request.form.get('feedback_score', type=int)
            
            success = ai_service.update_recommendation_feedback(
                recommendation_id, is_accepted, feedback_score
            )
            
            if success:
                return jsonify({'success': True, 'message': 'تم حفظ التقييم'})
            else:
                return jsonify({'success': False, 'message': 'حدث خطأ'}), 400
        except Exception as e:
            app.logger.error(f'خطأ في حفظ التقييم: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # Admin routes
    @app.route('/user/dashboard', endpoint='admin_dashboard')
    @app.route('/admin/dashboard', endpoint='admin_dashboard')  # للتوافق مع الروابط القديمة
    @login_required
    def admin_dashboard():
        """لوحة تحكم المستخدم/الإدارة"""
        if current_user.role == 'user':
            stats = get_user_stats()
            return render_template('dashboard/admin.html', stats=stats)
        else:
            flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
    
    
    @app.route('/select-doctor', methods=['POST'])
    @login_required
    def select_doctor():
        """اختيار الطبيب للمريض"""
        if current_user.role != 'patient':
            return jsonify({'success': False, 'message': 'هذه الميزة متاحة للمرضى فقط'}), 403
        
        data = request.get_json()
        doctor_id = data.get('doctor_id')
        
        if not doctor_id:
            return jsonify({'success': False, 'message': 'لم يتم تحديد الطبيب'}), 400
        
        # التحقق من وجود الطبيب وأنه طبيب
        doctor = User.query.filter_by(id=doctor_id, role='doctor', is_active=True).first()
        if not doctor:
            return jsonify({'success': False, 'message': 'الطبيب غير موجود أو غير نشط'}), 404
        
        # تحديث طبيب المريض
        current_user.doctor_id = doctor_id
        db.session.commit()
        
        AuditLogger.log_action(current_user.id, 'select_doctor', 'users', current_user.id)
        
        return jsonify({
            'success': True, 
            'message': f'تم اختيار {doctor.full_name} كطبيبك الخاص'
        })

if __name__ == '__main__':
    import sys
    import os
    import threading
    import time
    
    print("🏥 منصة دوائي - إدارة الأدوية والتذكيرات الطبية")
    print("=" * 60)
    
    # التحقق من إصدار Python
    if sys.version_info < (3, 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        sys.exit(1)
    
    # التحقق من المكتبات المطلوبة
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import bcrypt
    except ImportError as e:
        print(f"❌ مكتبة مفقودة: {e}")
        print("يرجى تشغيل: pip install -r requirements.txt")
        sys.exit(1)
    
    # التحقق من قاعدة البيانات
    db_path = 'doaei.db'
    if not os.path.exists(db_path):
        print("⚠️ قاعدة البيانات غير موجودة")
        print("🔧 إنشاء قاعدة البيانات...")
        try:
            from init_db import init_database
            init_database()
            print("✅ تم إنشاء قاعدة البيانات بنجاح")
        except Exception as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
            sys.exit(1)
    
    # بدء خدمة التذكيرات في thread منفصل
    def start_reminder_service():
        """بدء خدمة التذكيرات"""
        try:
            time.sleep(2)  # انتظار بدء التطبيق
            from reminder_service import ReminderService
            service = ReminderService()
            service.start()
            print("✅ خدمة التذكيرات تعمل في الخلفية")
        except Exception as e:
            print(f"⚠️ تحذير: لا يمكن بدء خدمة التذكيرات: {e}")
    
    # بدء خدمة التذكيرات
    reminder_thread = threading.Thread(target=start_reminder_service, daemon=True)
    reminder_thread.start()
    
    # إنشاء وتشغيل التطبيق
    print("🌐 بدء التطبيق...")
    print("=" * 60)
    print("🌐 التطبيق متاح على: http://localhost:5000")
    print("📊 قاعدة البيانات: doaei.db")
    print("👤 حساب المستخدم: admin@doaei.com")
    print("🔑 كلمة المرور: admin123")
    print("=" * 60)
    print("اضغط Ctrl+C لإيقاف التطبيق")
    print("=" * 60)
    
    try:
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف التطبيق بنجاح")
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)
