#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منصة دوائي - توليد التقارير PDF
إدارة الأدوية والتذكيرات الطبية
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from datetime import datetime, date, timedelta
import os
import json

class PDFReportGenerator:
    """مولد التقارير PDF"""
    
    def __init__(self):
        self.setup_fonts()
        self.setup_styles()
    
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # محاولة تسجيل خط عربي إذا كان متوفراً
            font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'NotoSansArabic-Regular.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                self.arabic_font = 'Arabic'
            else:
                # استخدام خط افتراضي
                self.arabic_font = 'Helvetica'
        except:
            self.arabic_font = 'Helvetica'
    
    def setup_styles(self):
        """إعداد أنماط النص"""
        self.styles = getSampleStyleSheet()
        
        # النمط العربي
        self.arabic_style = ParagraphStyle(
            'Arabic',
            parent=self.styles['Normal'],
            fontName=self.arabic_font,
            fontSize=12,
            alignment=TA_RIGHT,
            rightIndent=20,
            spaceAfter=12
        )
        
        # عنوان التقرير
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Title'],
            fontName=self.arabic_font,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#00BFA6')
        )
        
        # العنوان الفرعي
        self.heading_style = ParagraphStyle(
            'Heading',
            parent=self.styles['Heading2'],
            fontName=self.arabic_font,
            fontSize=14,
            alignment=TA_RIGHT,
            spaceAfter=12,
            textColor=colors.HexColor('#2196F3')
        )
        
        # النص العادي
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontName=self.arabic_font,
            fontSize=10,
            alignment=TA_RIGHT,
            spaceAfter=6
        )
    
    def generate_medication_report(self, user, start_date, end_date, report_type='monthly'):
        """توليد تقرير الأدوية"""
        try:
            # إنشاء ملف PDF
            filename = f"medication_report_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join('static', 'uploads', filename)
            
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm)
            story = []
            
            # العنوان الرئيسي
            title = Paragraph("تقرير الأدوية - منصة دوائي", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # معلومات التقرير
            info_data = [
                ['اسم المريض:', user.full_name],
                ['نوع التقرير:', self.get_report_type_name(report_type)],
                ['تاريخ البداية:', start_date.strftime('%Y-%m-%d')],
                ['تاريخ النهاية:', end_date.strftime('%Y-%m-%d')],
                ['تاريخ الإنشاء:', datetime.now().strftime('%Y-%m-%d %H:%M')]
            ]
            
            info_table = Table(info_data, colWidths=[3*cm, 6*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2D2D2D')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#00BFA6')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # قائمة الأدوية
            medications = self.get_user_medications(user, start_date, end_date)
            if medications:
                med_title = Paragraph("الأدوية الموصوفة", self.heading_style)
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
                
                med_table = Table(med_data, colWidths=[2.5*cm, 1*cm, 1.5*cm, 2*cm, 1.5*cm, 2.5*cm])
                med_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.arabic_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2D2D2D')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(med_table)
                story.append(Spacer(1, 20))
            
            # إحصائيات الالتزام
            compliance_stats = self.calculate_compliance_stats(user, start_date, end_date)
            if compliance_stats:
                stats_title = Paragraph("إحصائيات الالتزام", self.heading_style)
                story.append(stats_title)
                story.append(Spacer(1, 10))
                
                stats_data = [
                    ['المؤشر', 'القيمة', 'النسبة'],
                    ['إجمالي الجرعات المقررة', str(compliance_stats['total_doses']), '100%'],
                    ['الجرعات المتناولة', str(compliance_stats['taken_doses']), f"{compliance_stats['compliance_rate']:.1f}%"],
                    ['الجرعات المفقودة', str(compliance_stats['missed_doses']), f"{100 - compliance_stats['compliance_rate']:.1f}%"]
                ]
                
                stats_table = Table(stats_data, colWidths=[4*cm, 2*cm, 2*cm])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00BFA6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2D2D2D')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(stats_table)
                story.append(Spacer(1, 20))
            
            # مخطط الالتزام
            if compliance_stats and compliance_stats['total_doses'] > 0:
                chart_title = Paragraph("مخطط معدل الالتزام", self.heading_style)
                story.append(chart_title)
                story.append(Spacer(1, 10))
                
                # إنشاء مخطط دائري
                drawing = Drawing(400, 200)
                pie = Pie()
                pie.x = 150
                pie.y = 50
                pie.width = 150
                pie.height = 150
                
                pie.data = [compliance_stats['taken_doses'], compliance_stats['missed_doses']]
                pie.labels = ['متناولة', 'مفقودة']
                pie.slices[0].fillColor = colors.HexColor('#4CAF50')
                pie.slices[1].fillColor = colors.HexColor('#FF5252')
                
                drawing.add(pie)
                story.append(drawing)
                story.append(Spacer(1, 20))
            
            # ملاحظات إضافية
            notes_title = Paragraph("ملاحظات إضافية", self.heading_style)
            story.append(notes_title)
            story.append(Spacer(1, 10))
            
            notes_text = f"""
            <para align="right">
            هذا التقرير تم إنشاؤه تلقائياً من منصة دوائي.<br/>
            يرجى مراجعة طبيبك قبل إجراء أي تغييرات على أدويتك.<br/>
            للاستفسارات، يرجى التواصل مع فريق الدعم الفني.
            </para>
            """
            notes = Paragraph(notes_text, self.normal_style)
            story.append(notes)
            
            # إنشاء PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء تقرير PDF : {e}")
            return None
    
    def get_user_medications(self, user, start_date, end_date):
        """الحصول على أدوية المستخدم في الفترة المحددة"""
        from models import Medication
        
        medications = Medication.query.filter(
            Medication.user_id == user.id,
            Medication.start_date <= end_date,
            Medication.is_active == True
        ).all()
        
        return medications
    
    def calculate_compliance_stats(self, user, start_date, end_date):
        """حساب إحصائيات الالتزام"""
        from models import Medication, MedicationDose, Reminder
        
        # الحصول على جميع الجرعات في الفترة المحددة
        doses = MedicationDose.query.join(Medication).filter(
            Medication.user_id == user.id,
            Medication.is_active == True
        ).all()
        
        total_doses = len(doses)
        taken_doses = sum(1 for dose in doses if dose.is_taken)
        missed_doses = total_doses - taken_doses
        
        compliance_rate = (taken_doses / total_doses * 100) if total_doses > 0 else 0
        
        return {
            'total_doses': total_doses,
            'taken_doses': taken_doses,
            'missed_doses': missed_doses,
            'compliance_rate': compliance_rate
        }
    
    def get_report_type_name(self, report_type):
        """الحصول على اسم نوع التقرير بالعربية"""
        type_names = {
            'weekly': 'تقرير أسبوعي',
            'monthly': 'تقرير شهري',
            'custom': 'تقرير مخصص'
        }
        return type_names.get(report_type, 'تقرير مخصص')
    
    def generate_summary_report(self, start_date, end_date):
        """توليد تقرير ملخص للمنصة"""
        try:
            from models import User, Medication, Consultation, ProductRating
            
            filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join('static', 'uploads', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm)
            story = []
            
            # العنوان
            title = Paragraph("تقرير ملخص المنصة - دوائي", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # إحصائيات عامة
            stats_data = [
                ['المؤشر', 'القيمة'],
                ['إجمالي المستخدمين', str(User.query.count())],
                ['المرضى', str(User.query.filter_by(role='patient').count())],
                ['الأطباء', str(User.query.filter_by(role='doctor').count())],
                ['الصيادلة', str(User.query.filter_by(role='pharmacist').count())],
                ['الأدوية النشطة', str(Medication.query.filter_by(is_active=True).count())],
                ['الاستشارات المعلقة', str(Consultation.query.filter_by(status='pending').count())],
                ['التقييمات', str(ProductRating.query.count())]
            ]
            
            stats_table = Table(stats_data, colWidths=[6*cm, 3*cm])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00BFA6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2D2D2D')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(stats_table)
            
            doc.build(story)
            return filepath
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء تقرير الملخص : {e}")
            return None

def generate_pdf_report(report):
    """دالة مساعدة لتوليد تقرير PDF"""
    generator = PDFReportGenerator()
    
    if report.report_type == 'summary':
        return generator.generate_summary_report(report.start_date, report.end_date)
    else:
        return generator.generate_medication_report(
            report.user, 
            report.start_date, 
            report.end_date, 
            report.report_type
        )

if __name__ == '__main__':
    # اختبار توليد التقرير
    generator = PDFReportGenerator()
    
    # إنشاء تقرير تجريبي
    from models import User
    from app import create_app
    
    app = create_app()
    with app.app_context():
        user = User.query.first()
        if user:
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            
            filepath = generator.generate_medication_report(user, start_date, end_date)
            if filepath:
                print(f"✅ تم إنشاء التقرير : {filepath}")
            else:
                print("❌ فشل في إنشاء التقرير")
        else:
            print("❌ لا يوجد مستخدمين في قاعدة البيانات")
