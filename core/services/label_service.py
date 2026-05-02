"""
PDF label generation service for barcode labels.
"""
from typing import TYPE_CHECKING, List
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.core.files.base import ContentFile
import barcode
from barcode.writer import ImageWriter

if TYPE_CHECKING:
    from apps.inventory.models import ItemInstance


class LabelService:
    """Service for generating printable barcode labels."""
    
    # Label dimensions (in mm)
    LABEL_WIDTH = 70 * mm
    LABEL_HEIGHT = 40 * mm
    LABELS_PER_ROW = 3
    LABELS_PER_COL = 7
    MARGIN_LEFT = 5 * mm
    MARGIN_TOP = 10 * mm
    SPACING_H = 2 * mm
    SPACING_V = 2 * mm
    
    @staticmethod
    def generate_labels(items: List['ItemInstance']) -> bytes:
        """
        Generate PDF with barcode labels for items.
        
        Args:
            items: List of ItemInstance objects
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4
        
        label_count = 0
        
        for item in items:
            # Calculate position
            row = label_count // LabelService.LABELS_PER_ROW
            col = label_count % LabelService.LABELS_PER_ROW
            
            # Check if we need a new page
            if row >= LabelService.LABELS_PER_COL:
                pdf.showPage()
                label_count = 0
                row = 0
                col = 0
            
            # Calculate label position
            x = LabelService.MARGIN_LEFT + col * (LabelService.LABEL_WIDTH + LabelService.SPACING_H)
            y = page_height - LabelService.MARGIN_TOP - (row + 1) * (LabelService.LABEL_HEIGHT + LabelService.SPACING_V)
            
            # Draw label
            LabelService._draw_label(pdf, item, x, y)
            
            label_count += 1
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def _draw_label(pdf: canvas.Canvas, item: 'ItemInstance', x: float, y: float) -> None:
        """
        Draw a single label on the PDF.
        
        Args:
            pdf: ReportLab canvas
            item: ItemInstance to create label for
            x: X position
            y: Y position
        """
        # Draw border
        pdf.setStrokeColorRGB(0.8, 0.8, 0.8)
        pdf.setLineWidth(0.5)
        pdf.rect(x, y, LabelService.LABEL_WIDTH, LabelService.LABEL_HEIGHT)
        
        # Generate barcode image
        barcode_buffer = LabelService._generate_barcode_image(item.barcode)
        
        if barcode_buffer:
            # Draw barcode
            barcode_img = ImageReader(barcode_buffer)
            barcode_width = LabelService.LABEL_WIDTH - 10 * mm
            barcode_height = 20 * mm
            barcode_x = x + 5 * mm
            barcode_y = y + 15 * mm
            
            pdf.drawImage(
                barcode_img,
                barcode_x,
                barcode_y,
                width=barcode_width,
                height=barcode_height,
                preserveAspectRatio=True
            )
        
        # Draw product name
        pdf.setFont("Helvetica-Bold", 8)
        product_name = item.product.name
        if len(product_name) > 30:
            product_name = product_name[:27] + '...'
        
        text_y = y + LabelService.LABEL_HEIGHT - 8 * mm
        pdf.drawString(x + 5 * mm, text_y, product_name)
        
        # Draw serial number
        pdf.setFont("Helvetica", 7)
        pdf.drawString(x + 5 * mm, y + 8 * mm, f"S/N: {item.serial_number}")
        
        # Draw location
        pdf.setFont("Helvetica", 6)
        pdf.drawString(x + 5 * mm, y + 3 * mm, f"Location: {item.location.name}")
    
    @staticmethod
    def _generate_barcode_image(barcode_text: str) -> io.BytesIO:
        """
        Generate barcode image in memory.
        
        Args:
            barcode_text: Barcode text
            
        Returns:
            BytesIO buffer with barcode image
        """
        try:
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(barcode_text, writer=ImageWriter())
            
            buffer = io.BytesIO()
            barcode_instance.write(buffer, options={
                'module_width': 0.2,
                'module_height': 10.0,
                'quiet_zone': 2.0,
                'font_size': 8,
                'text_distance': 2.0,
            })
            buffer.seek(0)
            return buffer
        except Exception:
            return None
