#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منصة دوائي - الخدمات المساعدة (Utils)
إدارة الأدوية والتذكيرات الطبية
"""

import os
import json
import bcrypt
import requests
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app, request, flash, redirect, url_for
from flask_login import current_user
from functools import wraps
from cryptography.fernet import Fernet
import base64

class SecurityUtils:
    """أدوات الأمان"""
    
    @staticmethod
    def hash_password(password):
        """تشفير كلمة المرور"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(password, hashed):
        """التحقق من كلمة المرور"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def encrypt_data(data, key=None):
        """تشفير البيانات الحساسة"""
        if key is None:
            key = current_app.config.get('ENCRYPTION_KEY', 'default-key')
        
        # تحويل المفتاح إلى مفتاح Fernet صالح
        key_bytes = key.encode('utf-8')
        key_b64 = base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b'0'))
        
        fernet = Fernet(key_b64)
        return fernet.encrypt(data.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def decrypt_data(encrypted_data, key=None):
        """فك تشفير البيانات الحساسة"""
        if key is None:
            key = current_app.config.get('ENCRYPTION_KEY', 'default-key')
        
        # تحويل المفتاح إلى مفتاح Fernet صالح
        key_bytes = key.encode('utf-8')
        key_b64 = base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b'0'))
        
        fernet = Fernet(key_b64)
        return fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')

class SMSProvider:
    """مزود خدمة الرسائل النصية"""
    
    def __init__(self, provider='smsto'):
        self.provider = provider
        self.api_key = current_app.config.get('SMS_TO_API_KEY')
        self.sender_id = current_app.config.get('SMS_TO_SENDER_ID', 'دوائي')
    
    def send_sms(self, phone_number, message):
        """إرسال رسالة نصية"""
        try:
            if self.provider == 'smsto':
                return self._send_smsto(phone_number, message)
            elif self.provider == 'stc':
                return self._send_stc(phone_number, message)
            elif self.provider == 'mobily':
                return self._send_mobily(phone_number, message)
            elif self.provider == 'zain':
                return self._send_zain(phone_number, message)
            elif self.provider == 'plivo':
                return self._send_plivo(phone_number, message)
            else:
                raise ValueError(f"مزود SMS غير مدعوم: {self.provider}")
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال SMS: {e}")
            return False, str(e)
    
    def _send_smsto(self, phone_number, message):
        """إرسال عبر SMS.to"""
        url = "https://api.sms.to/sms/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "to": phone_number,
            "message": message,
            "sender_id": self.sender_id
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return True, "تم الإرسال بنجاح"
        else:
            return False, f"خطأ في الإرسال: {response.text}"
    
    def _send_stc(self, phone_number, message):
        """إرسال عبر STC (مثال)"""
        # تنفيذ API STC هنا
        return False, "STC API غير متاح حالياً"
    
    def _send_mobily(self, phone_number, message):
        """إرسال عبر Mobily (مثال)"""
        # تنفيذ API Mobily هنا
        return False, "Mobily API غير متاح حالياً"
    
    def _send_zain(self, phone_number, message):
        """إرسال عبر Zain (مثال)"""
        # تنفيذ API Zain هنا
        return False, "Zain API غير متاح حالياً"
    
    def _send_plivo(self, phone_number, message):
        """إرسال عبر Plivo (مثال)"""
        # تنفيذ API Plivo هنا
        return False, "Plivo API غير متاح حالياً"

class EmailProvider:
    """مزود خدمة البريد الإلكتروني"""
    
    def __init__(self, provider='mailtrap'):
        self.provider = provider
        self.smtp_server = current_app.config.get('MAIL_SERVER')
        self.smtp_port = current_app.config.get('MAIL_PORT', 587)
        self.username = current_app.config.get('MAIL_USERNAME')
        self.password = current_app.config.get('MAIL_PASSWORD')
        self.sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """إرسال بريد إلكتروني"""
        try:
            if self.provider == 'mailtrap':
                return self._send_smtp(to_email, subject, body, html_body, attachments)
            elif self.provider == 'mailgun':
                return self._send_mailgun(to_email, subject, body, html_body, attachments)
            elif self.provider == 'sendgrid':
                return self._send_sendgrid(to_email, subject, body, html_body, attachments)
            else:
                raise ValueError(f"مزود البريد الإلكتروني غير مدعوم: {self.provider}")
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال البريد الإلكتروني: {e}")
            return False, str(e)
    
    def _send_smtp(self, to_email, subject, body, html_body=None, attachments=None):
        """إرسال عبر SMTP"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # إضافة النص العادي
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # إضافة HTML إذا كان متوفراً
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        # إضافة المرفقات
        if attachments:
            for attachment in attachments:
                with open(attachment['path'], 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
        
        # إرسال البريد
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.username, self.password)
        text = msg.as_string()
        server.sendmail(self.sender, to_email, text)
        server.quit()
        
        return True, "تم الإرسال بنجاح"
    
    def _send_mailgun(self, to_email, subject, body, html_body=None, attachments=None):
        """إرسال عبر Mailgun"""
        api_key = current_app.config.get('MAILGUN_API_KEY')
        domain = current_app.config.get('MAILGUN_DOMAIN')
        
        url = f"https://api.mailgun.net/v3/{domain}/messages"
        auth = ("api", api_key)
        
        data = {
            "from": self.sender,
            "to": to_email,
            "subject": subject,
            "text": body
        }
        
        if html_body:
            data["html"] = html_body
        
        files = []
        if attachments:
            for attachment in attachments:
                files.append(("attachment", open(attachment['path'], 'rb')))
        
        response = requests.post(url, auth=auth, data=data, files=files)
        
        # إغلاق الملفات
        for file_tuple in files:
            file_tuple[1].close()
        
        if response.status_code == 200:
            return True, "تم الإرسال بنجاح"
        else:
            return False, f"خطأ في الإرسال: {response.text}"
    
    def _send_sendgrid(self, to_email, subject, body, html_body=None, attachments=None):
        """إرسال عبر SendGrid (مثال)"""
        # تنفيذ SendGrid API هنا
        return False, "SendGrid API غير متاح حالياً"

class NotificationService:
    """خدمة الإشعارات"""
    
    def __init__(self):
        self.sms_provider = SMSProvider()
        self.email_provider = EmailProvider()
    
    def send_medication_reminder(self, user, medication, dose):
        """إرسال تذكير دواء"""
        preferences = user.get_notification_preferences()
        
        # إعداد الرسالة
        message = f"تذكير: حان وقت تناول دواء {medication.name} - الجرعة: {medication.dosage}"
        
        # إرسال SMS
        if preferences.get('sms', False) and user.phone:
            success, error = self.sms_provider.send_sms(user.phone, message)
            if not success:
                current_app.logger.error(f"فشل إرسال SMS: {error}")
        
        # إرسال البريد الإلكتروني
        if preferences.get('email', False):
            subject = f"تذكير دواء - {medication.name}"
            html_body = f"""
            <html dir="rtl">
            <body>
                <h2>تذكير دواء</h2>
                <p>مرحباً {user.full_name}،</p>
                <p>حان وقت تناول دواء <strong>{medication.name}</strong></p>
                <p><strong>الجرعة:</strong> {medication.dosage}</p>
                <p><strong>الوقت:</strong> {dose.scheduled_time}</p>
                <p><strong>الملاحظات:</strong> {medication.notes or 'لا توجد ملاحظات'}</p>
                <hr>
                <p><small>هذا تذكير تلقائي من منصة دوائي</small></p>
            </body>
            </html>
            """
            
            success, error = self.email_provider.send_email(
                user.email, subject, message, html_body
            )
            if not success:
                current_app.logger.error(f"فشل إرسال البريد الإلكتروني: {error}")
    
    def send_consultation_notification(self, pharmacist, consultation):
        """إرسال إشعار استشارة جديدة للصيدلي"""
        subject = "استشارة جديدة - منصة دوائي"
        message = f"تم استلام استشارة جديدة من {consultation.patient.full_name}"
        
        html_body = f"""
        <html dir="rtl">
        <body>
            <h2>استشارة جديدة</h2>
            <p>مرحباً {pharmacist.full_name}،</p>
            <p>تم استلام استشارة جديدة من المريض <strong>{consultation.patient.full_name}</strong></p>
            <p><strong>الموضوع:</strong> {consultation.subject}</p>
            <p><strong>الرسالة:</strong> {consultation.message}</p>
            <hr>
            <p><small>منصة دوائي</small></p>
        </body>
        </html>
        """
        
        success, error = self.email_provider.send_email(
            pharmacist.email, subject, message, html_body
        )
        
        return success, error
    
    def send_medication_added_notification(self, user, medication):
        # إرسال إشعار عند إضافة دواء جديد
        preferences = user.get_notification_preferences()
        
        subject = "تم إضافة دواء جديد - منصة دوائي"
        message = f"تم إضافة دواء جديد: {medication.name}"
        
        html_body = f"""
        <html dir="rtl">
        <body>
            <h2>تم إضافة دواء جديد</h2>
            <p>مرحباً {user.full_name}،</p>
            <p>تم إضافة دواء جديد إلى قائمتك:</p>
            <p><strong>اسم الدواء:</strong> {medication.name}</p>
            <p><strong>الشكل:</strong> {medication.form}</p>
            <p><strong>الجرعة:</strong> {medication.dosage}</p>
            <p><strong>التكرار:</strong> {medication.frequency}</p>
            <p><strong>تاريخ البدء:</strong> {medication.start_date}</p>
            {f'<p><strong>الملاحظات:</strong> {medication.notes}</p>' if medication.notes else ''}
            <hr>
            <p><small>منصة دوائي</small></p>
        </body>
        </html>
        """
        
        # إرسال البريد الإلكتروني
        if preferences.get('email', False):
            success, error = self.email_provider.send_email(
                user.email, subject, message, html_body
            )
            if not success:
                current_app.logger.error(f"فشل إرسال البريد الإلكتروني: {error}")
        
        # إرسال SMS
        if preferences.get('sms', False) and user.phone:
            success, error = self.sms_provider.send_sms(user.phone, message)
            if not success:
                current_app.logger.error(f"فشل إرسال SMS: {error}")
        
        return True

class AuditLogger:
    """سجل التدقيق"""
    
    @staticmethod
    def log_action(user_id, action, table_name=None, record_id=None, 
                   old_values=None, new_values=None):
        """تسجيل إجراء في سجل التدقيق"""
        from models import AuditLog
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        
        from models import db
        db.session.add(audit_log)
        db.session.commit()

class FileUtils:
    """أدوات الملفات"""
    
    @staticmethod
    def save_uploaded_file(file, upload_folder):
        """حفظ الملف المرفق"""
        if file and file.filename:
            # إنشاء اسم ملف فريد
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(upload_folder, exist_ok=True)
            
            # حفظ الملف
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            return file_path
        return None
    
    @staticmethod
    def delete_file(file_path):
        """حذف ملف"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            current_app.logger.error(f"خطأ في حذف الملف: {e}")
        return False

def admin_required(f):
    """ديكوراتور للتحقق من صلاحيات المدير (مستمر للتوافق)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('login'))
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """ديكوراتور للتحقق من صلاحيات المستخدم"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('login'))
        if current_user.role != 'user':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

class ValidationUtils:
    """أدوات التحقق"""
    
    @staticmethod
    def validate_phone(phone):
        """التحقق من صحة رقم الهاتف"""
        import re
        if phone:
            # إزالة المسافات والرموز الخاصة
            clean_phone = re.sub(r'[^\d+]', '', phone)
            # التحقق من أن الرقم يبدأ بـ + أو رقم
            return re.match(r'^\+?[1-9]\d{7,14}$', clean_phone) is not None
        return True
    
    @staticmethod
    def validate_saudi_phone(phone):
        """التحقق من صحة رقم الهاتف السعودي"""
        import re
        if phone:
            clean_phone = re.sub(r'[^\d+]', '', phone)
            # التحقق من أن الرقم سعودي
            return re.match(r'^(\+966|966|0)?[5][0-9]{8}$', clean_phone) is not None
        return True
    
    @staticmethod
    def validate_email(email):
        """التحقق من صحة البريد الإلكتروني"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
