from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_pdf(order_id, amount, phone, shipping_details, expected_time):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    c.setFont("Helvetica", 14)
    c.drawString(100, 750, "Order Receipt")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Order ID: {order_id}")
    c.drawString(100, 700, f"Amount Paid: KES {amount}")
    c.drawString(100, 680, f"Phone: {phone}")
    c.drawString(100, 660, f"Shipping Details: {shipping_details}")
    c.drawString(100, 640, f"Expected Delivery: {expected_time}")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
