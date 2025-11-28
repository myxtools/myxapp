# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import json

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    referred_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    permissions = db.relationship('Permission', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def has_permission(self, app_id):
        return Permission.query.filter_by(user_id=self.id, app_id=app_id).first() is not None
    
    def __repr__(self):
        return f'<User {self.email}>'

class App(db.Model):
    __tablename__ = 'apps'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    route = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    permissions = db.relationship('Permission', backref='app', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<App {self.name}>'

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'app_id', name='unique_user_app'),)
    
    def __repr__(self):
        return f'<Permission User:{self.user_id} App:{self.app_id}>'

# ============================================
# TABELAS DO EMAIL VALIDATOR (DO ORIGINAL)
# ============================================

class EmailValidation(db.Model):
    """Sessão de validação (agrupa múltiplos emails)"""
    __tablename__ = 'email_validations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship com emails individuais
    emails = db.relationship('EmailResult', backref='validation', lazy=True, cascade='all, delete-orphan')
    
    user = db.relationship('User', backref=db.backref('email_validations', lazy=True))
    
    @property
    def total_emails(self):
        return len(self.emails)
    
    @property
    def valid_count(self):
        return sum(1 for e in self.emails if e.is_valid and not e.is_duplicate)
    
    @property
    def invalid_count(self):
        return sum(1 for e in self.emails if not e.is_valid and not e.is_duplicate)
    
    @property
    def duplicate_count(self):
        return sum(1 for e in self.emails if e.is_duplicate)
    
    def get_success_rate(self):
        non_duplicates = [e for e in self.emails if not e.is_duplicate]
        if not non_duplicates:
            return 0
        valid = sum(1 for e in non_duplicates if e.is_valid)
        return round((valid / len(non_duplicates)) * 100, 2)
    
    def __repr__(self):
        return f'<EmailValidation {self.id} - User:{self.user_id}>'

class EmailResult(db.Model):
    """Resultado individual de cada email validado"""
    __tablename__ = 'email_results'
    
    id = db.Column(db.Integer, primary_key=True)
    validation_id = db.Column(db.Integer, db.ForeignKey('email_validations.id'), nullable=False)
    
    # Dados do email
    email = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Resultado da validação
    is_valid = db.Column(db.Boolean, default=False)
    is_duplicate = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(500))
    
    # Tipo de validação
    validation_type = db.Column(db.String(20), default='bulk')  # 'single' ou 'bulk'
    
    def __repr__(self):
        return f'<EmailResult {self.email} - Valid:{self.is_valid}>'