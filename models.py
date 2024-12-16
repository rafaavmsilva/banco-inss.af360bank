from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    income = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with proposals
    proposals = db.relationship('INSSProposal', backref='client', lazy=True)

class INSSProposal(db.Model):
    __tablename__ = 'inss_proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    proposal_type = db.Column(db.String(20), nullable=False)  # 'new', 'portability', 'refinancing'
    proposal_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    term = db.Column(db.Integer, nullable=False)  # in months
    interest_rate = db.Column(db.Numeric(5, 2))
    monthly_payment = db.Column(db.Numeric(10, 2))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('inss_proposals.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # 'rg', 'cpf', 'proof_of_income', etc
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50))  # 'proposal', 'client', 'document'
    entity_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
