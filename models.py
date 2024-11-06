from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DocumentBatch(db.Model):
    __tablename__ = 'document_batch'
    batch_id = db.Column(db.String(50), primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    receiver_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ความสัมพันธ์กับเอกสารและสถานะ
    documents = db.relationship('Document', backref='batch', lazy=True)
    statuses = db.relationship('DocumentStatus', backref='batch', lazy=True)


class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    batch_id = db.Column(db.String(50), db.ForeignKey('document_batch.batch_id'), nullable=False)


class DocumentStatus(db.Model):
    __tablename__ = 'document_status'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(50), db.ForeignKey('document_batch.batch_id'), nullable=False)
    location = db.Column(db.String(50), nullable=False)  # เช่น "ผู้ส่งเอกสารต้นทาง"
    signed_by = db.Column(db.String(100), nullable=True)  # ผู้ลงชื่อ
    signed_at = db.Column(db.DateTime, nullable=True)  # วันที่และเวลาที่ลงชื่อ
