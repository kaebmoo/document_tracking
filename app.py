# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from models import db, Document, DocumentStatus, DocumentBatch
import qrcode
import os
from uuid import uuid4
from datetime import datetime, timezone
import pytz  # ใช้ pytz สำหรับการแปลง timezone
import random
import string

def generate_batch_id():
    prefix = ''.join(random.choices(string.ascii_uppercase, k=2))  # ตัวอักษรสองตัว
    suffix = ''.join(random.choices(string.digits, k=6))  # ตัวเลขหกตัว
    return f"{prefix}{suffix}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
app.config['SECRET_KEY'] = 'your_secret_key'
# กำหนด BASE_URL เพื่อให้ยืดหยุ่นในการตั้งค่า URL ของเซิร์ฟเวอร์
BASE_URL = "http://127.0.0.1:5000"  # เปลี่ยน URL ได้ตามที่ต้องการ
db.init_app(app)

# ตั้งค่า Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # แทนที่ด้วย SMTP Server ของคุณ
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # แทนที่ด้วย Email ของคุณ
app.config['MAIL_PASSWORD'] = 'your_email_password'     # แทนที่ด้วยรหัสผ่าน
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

mail = Mail(app)

# ฟิลเตอร์สำหรับแปลงเวลา
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if value.tzinfo is None:
        # ถ้าเวลายังเป็น naive datetime (ไม่มี timezone) กำหนดเป็น UTC ก่อน
        value = value.replace(tzinfo=timezone.utc)
    
    # แปลงจาก UTC ไปยัง timezone ท้องถิ่นที่ต้องการ
    local_timezone = pytz.timezone("Asia/Bangkok")  # เปลี่ยน timezone ตามต้องการ
    local_time = value.astimezone(local_timezone)
    return local_time.strftime(format)

# ฟังก์ชันส่งอีเมลแจ้งเตือนเมื่ออัปเดตสถานะ
def send_status_update_email(doc_id, title, status, receiver_email):
    try:
        msg = Message(
            subject=f"Status Update for Document ID {doc_id}",
            recipients=[receiver_email],
            body=f"Document '{title}' has been updated to status: {status}."
        )
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# ฟังก์ชันสำหรับสร้าง batch พร้อมสร้าง QR Code ที่เชื่อมโยงกับ search_batches
@app.route('/create_batch', methods=['GET', 'POST'])
def create_batch():
    if request.method == 'POST':
        doc_id = generate_batch_id()  # สร้าง batch_id เมื่อกดปุ่ม create batch
        sender_name = request.form['sender_name']
        receiver_name = request.form['receiver_name']
        document_titles = request.form.getlist('document_titles')
        created_at = datetime.now(timezone.utc)  # ใช้ timezone-aware datetime

        # สร้างการส่งเอกสาร (DocumentBatch)
        batch = DocumentBatch(batch_id=doc_id, sender_name=sender_name, receiver_name=receiver_name, created_at=created_at)
        db.session.add(batch)
        db.session.commit()

        # เพิ่มสถานะเริ่มต้นใน DocumentStatus
        initial_status = DocumentStatus(
            batch_id=batch.batch_id,
            location="ผู้ส่งเอกสารต้นทาง",
            signed_by=sender_name,
            signed_at=created_at
        )
        db.session.add(initial_status)

        # สร้างเอกสารแต่ละรายการที่เชื่อมโยงกับ batch
        documents = []
        for index, title in enumerate(document_titles, start=1):
            doc_id_item = f"{batch.batch_id}-{index}"
            new_document = Document(doc_id=doc_id_item, title=title, batch_id=batch.batch_id)
            db.session.add(new_document)
            documents.append(new_document)

        # สร้าง URL ที่จะใช้ใน QR Code
        qr_url = f"{BASE_URL}/search_batches?query={batch.batch_id}"
        
        # สร้าง QR Code สำหรับ URL
        qr = qrcode.make(qr_url)
        qr_path = os.path.join('static', 'qr_codes', f"{batch.batch_id}.png")
        qr.save(qr_path)

        db.session.commit()
        flash(f'Document batch with ID {batch.batch_id} created successfully!', 'success')
        
        # ส่งข้อมูลไปแสดงในหน้าเว็บหลังสร้าง batch
        return render_template('create_batch.html', batch=batch, documents=documents, qr_path=qr_path)

    return render_template('create_batch.html')  # ไม่แสดง batch_id ตอนเริ่ม

# ฟังก์ชันค้นหา batch เพื่อเตรียมสำหรับการอัปเดตสถานะ
@app.route('/search_batches', methods=['GET', 'POST'])
def search_batches():
    search_query = request.args.get('query', None)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    results = []

    # ตรวจสอบว่ามีการค้นหาหรือไม่
    if request.method == 'POST' or (search_query and search_query.strip()):
        # ถ้าไม่มีค่า query ให้เป็นการเรียกข้อมูลทั้งหมด
        if not search_query:
            search_query = request.form['query']
            

        # ค้นหา batch ที่ตรงกับ query ใน `batch_id`, `sender_name`, หรือ `receiver_name`
        batches = DocumentBatch.query.filter(
            (DocumentBatch.batch_id.like(f"%{search_query}%")) |
            (DocumentBatch.sender_name.like(f"%{search_query}%")) |
            (DocumentBatch.receiver_name.like(f"%{search_query}%"))
        ).paginate(page=page, per_page=per_page)
        
        for batch in batches.items:
            documents = Document.query.filter_by(batch_id=batch.batch_id).all()
            statuses = DocumentStatus.query.filter_by(batch_id=batch.batch_id).order_by(DocumentStatus.signed_at.asc()).all()
            results.append({
                'batch': batch,
                'documents': documents,
                'statuses': statuses
            })
    
    return render_template('search_batches.html', results=results, search_query=search_query, batches=batches if results else None)

# ฟังก์ชันสำหรับอัปเดตสถานะของเอกสาร
@app.route('/update_status/<batch_id>', methods=['GET', 'POST'])
def update_status(batch_id):
    batch = DocumentBatch.query.get_or_404(batch_id)
    
    if request.method == 'POST':
        location = request.form['location']
        signed_by = request.form['signed_by']
        signed_at = datetime.now(timezone.utc)

        # ตรวจสอบว่ามีการบันทึกสถานะสำหรับ location นั้นหรือยัง
        status = DocumentStatus.query.filter_by(batch_id=batch_id, location=location).first()
        if status:
            # ถ้ามีอยู่แล้ว ให้แก้ไขข้อมูลการลงชื่อและเวลาที่ลงชื่อ
            status.signed_by = signed_by
            status.signed_at = signed_at
        else:
            # ถ้าไม่มี ให้สร้างสถานะใหม่สำหรับ location นั้น
            status = DocumentStatus(
                batch_id=batch_id,
                location=location,
                signed_by=signed_by,
                signed_at=signed_at
            )
            db.session.add(status)
        
        db.session.commit()
        flash('Status updated successfully!', 'success')
        return redirect(url_for('search_batches', query=batch_id))  # รีไดเรกต์ไปที่หน้า search_batches พร้อม batch_id

    return render_template('update_status.html', batch=batch)


# ฟังก์ชันตรวจสอบสถานะเอกสาร พร้อมการค้นหาและการแบ่งหน้า
@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    search_query = request.args.get('query', None)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    results = []

    if request.method == 'POST' or search_query:
        if not search_query:
            search_query = request.form['query']

        # ค้นหา batch ที่ตรงกับ query ใน `batch_id`, `sender_name`, หรือ `receiver_name`
        batches = DocumentBatch.query.filter(
            (DocumentBatch.batch_id.like(f"%{search_query}%")) |
            (DocumentBatch.sender_name.like(f"%{search_query}%")) |
            (DocumentBatch.receiver_name.like(f"%{search_query}%"))
        ).paginate(page=page, per_page=per_page)
    else:
        # แสดง batch ทั้งหมด โดยเรียงลำดับจากล่าสุด แบ่งเป็นหน้า
        batches = DocumentBatch.query.order_by(DocumentBatch.created_at.desc()).paginate(page=page, per_page=per_page)

    for batch in batches.items:
        documents = Document.query.filter_by(batch_id=batch.batch_id).all()
        statuses = DocumentStatus.query.filter_by(batch_id=batch.batch_id).order_by(DocumentStatus.signed_at.asc()).all()

        results.append({
            'batch': batch,
            'documents': documents,
            'statuses': statuses
        })
    
    return render_template('check_status.html', results=results, search_query=search_query, batches=batches)

# หน้าแรก
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
