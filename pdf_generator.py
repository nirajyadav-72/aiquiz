import io
import logging
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

class HindiPDFGenerator:
    def __init__(self, font_path="NotoSansDevanagari-Regular.ttf"):
        self.font_path = font_path
        self.hindi_font_name = "HindiFont"
        self.setup_fonts()

    def setup_fonts(self):
        try:
            if os.path.exists(self.font_path):
                pdfmetrics.registerFont(TTFont(self.hindi_font_name, self.font_path, validate=0))
                logging.info("✅ Hindi font registered")
            else:
                logging.warning(f"⚠️ Font file not found: {self.font_path}")
                self.hindi_font_name = "Helvetica"
        except Exception as e:
            logging.error(f"❠ Font registration failed: {e}")
            self.hindi_font_name = "Helvetica"

    def _safe_text(self, text):
        if not text:
            return ""
        text = str(text)
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def generate_quiz_pdf(self, quiz_data):
        pdf_buffer = io.BytesIO()

        try:
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=0.5 * 72,
                leftMargin=0.5 * 72,
                topMargin=0.75 * 72,
                bottomMargin=0.75 * 72
            )

            story = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontName=self.hindi_font_name,
                fontSize=16,
                leading=20,
                spaceAfter=12
            )

            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontName=self.hindi_font_name,
                fontSize=11,
                leading=16
            )

            story.append(Paragraph(self._safe_text(quiz_data.get("title", "Quiz")), title_style))
            story.append(Spacer(1, 12))

            desc = quiz_data.get("description")
            if desc:
                story.append(Paragraph(self._safe_text(desc), body_style))
                story.append(Spacer(1, 12))

            for idx, q in enumerate(quiz_data.get("questions", []), 1):
                q_text = q.get("question", "")
                story.append(Paragraph(f"{idx}. {self._safe_text(q_text)}", body_style))

                for opt_idx, opt in enumerate(q.get("options", []), 0):
                    option_text = self._safe_text(opt)
                    label = chr(65 + opt_idx)
                    story.append(Paragraph(f"    {label}) {option_text}", body_style))

                expl = q.get("explanation")
                if expl:
                    story.append(Paragraph(f"    व्याख्या: {self._safe_text(expl)}", body_style))

                story.append(Spacer(1, 12))

            doc.build(story)
            pdf_buffer.seek(0)
            logging.info("✅ Hindi PDF generated successfully")
            return pdf_buffer

        except Exception as e:
            logging.error(f"❌ PDF generation failed: {e}")
            return self._fallback_pdf(quiz_data)

    def _fallback_pdf(self, quiz_data):
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, str(quiz_data.get("title", "Quiz")))
        y = height - 90

        c.setFont("Helvetica", 11)
        for idx, q in enumerate(quiz_data.get("questions", []), 1):
            if y < 60:
                c.showPage()
                y = height - 60
            c.drawString(50, y, f"Q{idx}: {str(q.get('question', ''))[:90]}")
            y -= 18

        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer
