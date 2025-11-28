from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

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