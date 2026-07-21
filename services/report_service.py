import os
from datetime import datetime
from pathlib import Path
from io import BytesIO

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

from config.settings import Settings
from database.database import DatabaseManager
from database.models import Report, Prediction, DiseaseRecord, Farm, User
from utils.logger import get_logger
from utils.helpers import format_datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

logger = get_logger(__name__)

class ReportService:
    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager
        
        # Ensure reports directory exists
        Settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_base_elements(self, title: str, subtitle: str, user=None):
        """Get standard header elements for reports."""
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
            fontSize=22, textColor=colors.HexColor('#2E7D32'), spaceAfter=6, alignment=1)
        subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'],
            fontSize=12, textColor=colors.HexColor('#757575'), spaceAfter=20, alignment=1)
        
        elements.append(Paragraph('University Name Placeholder', subtitle_style))
        elements.append(Paragraph('AgriSense AI', title_style))
        elements.append(Paragraph('Intelligent Agriculture Decision Support System', subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Report Title
        report_title_style = ParagraphStyle('ReportTitle', parent=styles['Heading2'],
            fontSize=16, textColor=colors.HexColor('#1B5E20'), spaceAfter=10, alignment=1)
        elements.append(Paragraph(title, report_title_style))
        elements.append(Paragraph(subtitle, subtitle_style))
        
        if user:
            farmer_info_style = ParagraphStyle('FarmerInfo', parent=styles['Normal'],
                fontSize=10, textColor=colors.black, spaceAfter=5)
            elements.append(Paragraph(f"<b>Farmer:</b> {user.full_name} ({user.email})", farmer_info_style))
            elements.append(Paragraph(f"<b>Generated:</b> {format_datetime()}", farmer_info_style))
        
        elements.append(Spacer(1, 15))
        return elements

    def _add_qr_code(self, elements, data: str):
        if QR_AVAILABLE:
            try:
                qr = qrcode.QRCode(version=1, box_size=5, border=2)
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                img_buffer = BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                qr_img = Image(img_buffer, width=1.5*inch, height=1.5*inch)
                elements.append(Spacer(1, 20))
                elements.append(qr_img)
            except Exception as e:
                logger.error(f"Failed to generate QR code: {str(e)}")

    def generate_prediction_report(self, user_id, prediction_id=None, report_title='Prediction Report') -> str:
        """Generate a PDF report for predictions. Returns file path."""
        logger.info(f"Generating prediction report for user_id={user_id}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'report_prediction_{timestamp}.pdf'
        file_path = str(Settings.REPORTS_DIR / filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4, 
            topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)
        
        session = self._db.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            
            elements = self._get_base_elements(report_title, "Prediction Data Summary", user)
            
            styles = getSampleStyleSheet()
            heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'],
                fontSize=14, textColor=colors.HexColor('#1B5E20'), spaceBefore=15, spaceAfter=8)
            
            elements.append(Paragraph("Predictions History", heading_style))
            
            query = session.query(Prediction).filter_by(user_id=user_id)
            if prediction_id:
                query = query.filter_by(id=prediction_id)
            predictions = query.order_by(Prediction.created_at.desc()).limit(20).all()
            
            if not predictions:
                elements.append(Paragraph("No prediction records found.", styles['Normal']))
            else:
                data = [['Date', 'Type', 'Model', 'Result', 'Confidence']]
                for p in predictions:
                    conf_str = f"{p.confidence*100:.1f}%" if p.confidence else "N/A"
                    data.append([
                        p.created_at.strftime("%Y-%m-%d %H:%M"),
                        p.prediction_type.capitalize(),
                        p.model_used,
                        str(p.result_data),
                        conf_str
                    ])
                
                table = Table(data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 2*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 12),
                    ('BOTTOMPADDING', (0,0), (-1,0), 12),
                    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F1F8E9')),
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#C8E6C9'))
                ]))
                elements.append(table)
            
            self._add_qr_code(elements, f"AgriSense AI Prediction Report - {timestamp}")
            
            doc.build(elements)
            self._save_report_record(session, user_id, 'prediction', report_title, file_path)
            
            return file_path
        finally:
            session.close()
    
    def generate_farm_report(self, user_id) -> str:
        """Generate farm summary report."""
        logger.info(f"Generating farm report for user_id={user_id}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'report_farm_{timestamp}.pdf'
        file_path = str(Settings.REPORTS_DIR / filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4, 
            topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)
        
        session = self._db.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            elements = self._get_base_elements("Farm Summary Report", "Registered Farms Overview", user)
            
            styles = getSampleStyleSheet()
            heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'],
                fontSize=14, textColor=colors.HexColor('#1B5E20'), spaceBefore=15, spaceAfter=8)
            
            elements.append(Paragraph("Farms Details", heading_style))
            
            farms = session.query(Farm).filter_by(user_id=user_id).all()
            if not farms:
                elements.append(Paragraph("No farm records found.", styles['Normal']))
            else:
                data = [['Name', 'Location', 'Area (Acres)', 'Soil Type']]
                for f in farms:
                    data.append([
                        f.name,
                        f.location,
                        str(f.area_acres),
                        f.soil_type
                    ])
                
                table = Table(data, colWidths=[2*inch, 2*inch, 1*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2196F3')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#BBDEFB'))
                ]))
                elements.append(table)
            
            self._add_qr_code(elements, f"AgriSense AI Farm Report - {timestamp}")
            
            doc.build(elements)
            self._save_report_record(session, user_id, 'farm', 'Farm Summary Report', file_path)
            
            return file_path
        finally:
            session.close()
    
    def generate_disease_report(self, user_id) -> str:
        """Generate disease detection report."""
        logger.info(f"Generating disease report for user_id={user_id}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'report_disease_{timestamp}.pdf'
        file_path = str(Settings.REPORTS_DIR / filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4, 
            topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)
        
        session = self._db.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            elements = self._get_base_elements("Disease Detection Report", "Recent Plant Disease Analysis", user)
            
            styles = getSampleStyleSheet()
            heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'],
                fontSize=14, textColor=colors.HexColor('#1B5E20'), spaceBefore=15, spaceAfter=8)
            
            elements.append(Paragraph("Disease Records", heading_style))
            
            records = session.query(DiseaseRecord).filter_by(user_id=user_id).order_by(DiseaseRecord.detected_at.desc()).limit(20).all()
            if not records:
                elements.append(Paragraph("No disease records found.", styles['Normal']))
            else:
                data = [['Date', 'Crop', 'Disease Detected', 'Confidence', 'Severity']]
                for r in records:
                    conf_str = f"{r.confidence*100:.1f}%" if r.confidence else "N/A"
                    data.append([
                        r.detected_at.strftime("%Y-%m-%d"),
                        r.crop_name,
                        r.disease_name,
                        conf_str,
                        r.severity
                    ])
                
                table = Table(data, colWidths=[1.2*inch, 1*inch, 2*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F44336')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#FFCDD2'))
                ]))
                elements.append(table)
            
            self._add_qr_code(elements, f"AgriSense AI Disease Report - {timestamp}")
            
            doc.build(elements)
            self._save_report_record(session, user_id, 'disease', 'Disease Detection Report', file_path)
            
            return file_path
        finally:
            session.close()
    
    def get_reports(self, user_id) -> list:
        """Get all generated reports for a user."""
        session = self._db.get_session()
        try:
            reports = session.query(Report).filter_by(user_id=user_id).order_by(Report.created_at.desc()).all()
            # Return list of dicts for UI use
            result = []
            for r in reports:
                result.append({
                    'id': r.id,
                    'title': r.title,
                    'report_type': r.report_type,
                    'file_path': r.file_path,
                    'created_at': r.created_at
                })
            return result
        finally:
            session.close()

    def delete_report(self, report_id: int):
        session = self._db.get_session()
        try:
            report = session.query(Report).filter_by(id=report_id).first()
            if report:
                # delete file if exists
                if os.path.exists(report.file_path):
                    os.remove(report.file_path)
                session.delete(report)
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete report: {str(e)}")
        finally:
            session.close()
    
    def _save_report_record(self, session, user_id, report_type, title, file_path):
        """Save report metadata to database."""
        try:
            report = Report(
                user_id=user_id,
                report_type=report_type,
                title=title,
                file_path=file_path,
                created_at=datetime.now()
            )
            session.add(report)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save report record: {str(e)}")
