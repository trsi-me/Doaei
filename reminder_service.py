#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منصة دوائي - خدمة التذكيرات
إدارة الأدوية والتذكيرات الطبية
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from app import create_app
from models import db, Reminder, MedicationDose, Medication, User
from utils import NotificationService

class ReminderService:
    """خدمة التذكيرات"""
    
    def __init__(self):
        self.app = create_app()
        self.notification_service = NotificationService()
        self.running = False
        
    def start(self):
        """بدء خدمة التذكيرات"""
        self.running = True
        
        # جدولة فحص التذكيرات كل دقيقة
        schedule.every(1).minutes.do(self.check_and_send_reminders)
        
        # جدولة تنظيف التذكيرات القديمة كل ساعة
        schedule.every().hour.do(self.cleanup_old_reminders)
        
        print("🔔 تم بدء خدمة التذكيرات")
        
        # تشغيل الجدولة في خيط منفصل
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
    def stop(self):
        """إيقاف خدمة التذكيرات"""
        self.running = False
        print("🔔 تم إيقاف خدمة التذكيرات")
        
    def run_scheduler(self):
        """تشغيل الجدولة"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(f"❌ خطأ في خدمة التذكيرات : {e}")
                time.sleep(60)  # انتظار دقيقة قبل المحاولة مرة أخرى
    
    def check_and_send_reminders(self):
        """فحص وإرسال التذكيرات"""
        with self.app.app_context():
            try:
                now = datetime.utcnow()
                # البحث عن التذكيرات المستحقة في الدقائق القادمة
                upcoming_reminders = Reminder.query.filter(
                    Reminder.reminder_time <= now + timedelta(minutes=5),
                    Reminder.reminder_time >= now - timedelta(minutes=1),
                    Reminder.status == 'pending'
                ).all()
                
                for reminder in upcoming_reminders:
                    self.send_reminder(reminder)
                    
            except Exception as e:
                print(f"❌ خطأ في فحص التذكيرات : {e}")
    
    def send_reminder(self, reminder):
        """إرسال تذكير واحد"""
        try:
            with self.app.app_context():
                # الحصول على معلومات الجرعة والدواء والمستخدم
                dose = MedicationDose.query.get(reminder.medication_dose_id)
                if not dose:
                    reminder.status = 'failed'
                    reminder.error_message = 'الجرعة غير موجودة'
                    db.session.commit()
                    return
                
                medication = Medication.query.get(dose.medication_id)
                if not medication:
                    reminder.status = 'failed'
                    reminder.error_message = 'الدواء غير موجود'
                    db.session.commit()
                    return
                
                user = User.query.get(medication.user_id)
                if not user or not user.is_active:
                    reminder.status = 'failed'
                    reminder.error_message = 'المستخدم غير موجود أو غير نشط'
                    db.session.commit()
                    return
                
                # إرسال التذكير
                success = self.notification_service.send_medication_reminder(user, medication, dose)
                
                if success:
                    reminder.status = 'sent'
                    reminder.sent_at = datetime.utcnow()
                    print(f"✅ تم إرسال تذكير لـ {user.full_name} : {medication.name}")
                else:
                    reminder.status = 'failed'
                    reminder.error_message = 'فشل في إرسال التذكير'
                    print(f"❌ فشل في إرسال تذكير لـ {user.full_name} : {medication.name}")
                
                db.session.commit()
                
        except Exception as e:
            print(f"❌ خطأ في إرسال التذكير : {e}")
            reminder.status = 'failed'
            reminder.error_message = str(e)
            db.session.commit()
    
    def cleanup_old_reminders(self):
        """تنظيف التذكيرات القديمة"""
        with self.app.app_context():
            try:
                # حذف التذكيرات المرسلة منذ أكثر من 7 أيام
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                old_reminders = Reminder.query.filter(
                    Reminder.status.in_(['sent', 'failed']),
                    Reminder.sent_at < cutoff_date
                ).all()
                
                for reminder in old_reminders:
                    db.session.delete(reminder)
                
                db.session.commit()
                
                if old_reminders:
                    print(f"🧹 تم حذف {len(old_reminders)} تذكير قديم")
                    
            except Exception as e:
                print(f"❌ خطأ في تنظيف التذكيرات : {e}")
    
    def create_reminders_for_medication(self, medication):
        """إنشاء التذكيرات لدواء جديد"""
        with self.app.app_context():
            try:
                # حذف التذكيرات القديمة للدواء
                old_doses = MedicationDose.query.filter_by(medication_id=medication.id).all()
                for dose in old_doses:
                    Reminder.query.filter_by(medication_dose_id=dose.id).delete()
                    db.session.delete(dose)
                
                # إنشاء الجرعات الجديدة
                self.create_medication_doses(medication)
                
                db.session.commit()
                print(f"✅ تم إنشاء التذكيرات لدواء {medication.name}")
                
            except Exception as e:
                print(f"❌ خطأ في إنشاء التذكيرات : {e}")
                db.session.rollback()
    
    def create_medication_doses(self, medication):
        """إنشاء الجرعات المحددة للدواء"""
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
            db.session.flush()  # للحصول على معرف الجرعة
            
            # إنشاء التذكيرات
            self.create_reminders_for_dose(dose)
    
    def create_reminders_for_dose(self, dose):
        """إنشاء التذكيرات للجرعة"""
        from models import SystemSetting
        
        advance_minutes = int(SystemSetting.get_setting('reminder_advance_minutes', 10))
        
        # حساب وقت التذكير
        reminder_time = datetime.combine(datetime.today(), dose.scheduled_time) - timedelta(minutes=advance_minutes)
        
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

def main():
    """تشغيل خدمة التذكيرات"""
    reminder_service = ReminderService()
    
    try:
        reminder_service.start()
        
        print("🔔 خدمة التذكيرات تعمل...")
        print("اضغط Ctrl+C للإيقاف")
        
        # انتظار حتى يتم إيقاف الخدمة
        while reminder_service.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف خدمة التذكيرات")
        reminder_service.stop()
    except Exception as e:
        print(f"❌ خطأ في خدمة التذكيرات : {e}")

if __name__ == '__main__':
    main()
