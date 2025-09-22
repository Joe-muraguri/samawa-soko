import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

def generate_pdf(order_id, amount, phone, shipping_details, expected_time):
    # Create buffer for PDF
    buffer = io.BytesIO()
    
    # Use letter size with custom margins
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          topMargin=0.4*inch,
                          bottomMargin=0.4*inch,
                          leftMargin=0.6*inch,
                          rightMargin=0.6*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Color scheme
    primary_color = '#2C3E50'      # Dark blue-gray
    accent_color = '#E74C3C'       # Red accent
    secondary_color = '#3498DB'    # Blue
    light_bg = '#ECF0F1'           # Light gray background
    border_color = '#BDC3C7'       # Border gray
    
    # Header Section
    header_data = [
        [Paragraph("<b>ORDER CONFIRMATION</b>", ParagraphStyle(
            'Header',
            fontSize=20,
            textColor=colors.white,
            alignment=1,
            fontName='Helvetica-Bold'
        ))],
        [Paragraph(f"Order #: {order_id}", ParagraphStyle(
            'SubHeader',
            fontSize=12,
            textColor=colors.white,
            alignment=1,
            fontName='Helvetica'
        ))]
    ]
    
    header_table = Table(header_data, colWidths=[6.8*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(secondary_color)),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 25))
    
    # Order Details Section
    story.append(Paragraph("ORDER DETAILS", ParagraphStyle(
        'SectionTitle',
        fontSize=14,
        textColor=colors.HexColor(primary_color),
        fontName='Helvetica-Bold',
        spaceAfter=12
    )))
    
    # Order information table
    order_data = [
        ['Order Date:', datetime.now().strftime("%B %d, %Y")],
        ['Order Time:', datetime.now().strftime("%I:%M %p")],
        ['Amount Paid:', f'<b><font color="{accent_color}">KES {amount:,.2f}</font></b>'],
        ['Phone Number:', phone],
        ['Expected Delivery:', f'<b><font color="#27AE60">{expected_time}</font></b>'],
        ['Status:', '<b><font color="#27AE60">Confirmed</font></b>']
    ]
    
    order_table = Table(order_data, colWidths=[2.2*inch, 4.6*inch])
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(light_bg)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(primary_color)),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495E')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 2), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(border_color)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(order_table)
    story.append(Spacer(1, 25))
    
    # Shipping Information Section
    story.append(Paragraph("SHIPPING INFORMATION", ParagraphStyle(
        'SectionTitle',
        fontSize=14,
        textColor=colors.HexColor(primary_color),
        fontName='Helvetica-Bold',
        spaceAfter=12
    )))
    
    shipping_table = Table([
        [Paragraph(shipping_details, ParagraphStyle(
            'ShippingText',
            fontSize=11,
            textColor=colors.HexColor(primary_color),
            leading=14
        ))]
    ], colWidths=[6.8*inch])
    
    shipping_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9F9')),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D5DBDB')),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    
    story.append(shipping_table)
    story.append(Spacer(1, 25))
    
    # Payment Summary Section
    story.append(Paragraph("PAYMENT SUMMARY", ParagraphStyle(
        'SectionTitle',
        fontSize=14,
        textColor=colors.HexColor(primary_color),
        fontName='Helvetica-Bold',
        spaceAfter=12
    )))
    
    payment_data = [
        ['Subtotal:', f'KES {amount:,.2f}'],
        ['Shipping:', 'KES 0.00'],
        ['Tax:', 'KES 0.00'],
        ['', ''],
        ['TOTAL:', f'<b>KES {amount:,.2f}</b>']
    ]
    
    payment_table = Table(payment_data, colWidths=[3.4*inch, 3.4*inch])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 4), (-1, 4), 1, colors.HexColor(primary_color)),
        ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 4), (-1, 4), 12),
        ('TEXTCOLOR', (0, 4), (-1, 4), colors.HexColor(accent_color)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(payment_table)
    story.append(Spacer(1, 30))
    
    # Thank You Message
    thank_you_text = """
    <b>Thank you for your purchase!</b><br/><br/>
    Your order has been successfully confirmed and is now being processed. 
    You will receive a shipping confirmation email once your order is on its way.<br/><br/>
    If you have any questions about your order, please contact our customer service team.
    """
    
    story.append(Paragraph(thank_you_text, ParagraphStyle(
        'ThankYou',
        fontSize=10,
        textColor=colors.HexColor('#7F8C8D'),
        leading=14,
        alignment=1
    )))
    
    story.append(Spacer(1, 15))
    
    # Footer
    footer_text = f"""
    <i>This is an automated receipt. Please keep this document for your records.</i><br/>
    <font size="8">Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}</font>
    """
    
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        fontSize=8,
        textColor=colors.HexColor('#95A5A6'),
        alignment=1
    )))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
