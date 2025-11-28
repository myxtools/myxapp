# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, flash, session, request
from config import Config
from models import db, bcrypt, User, App, Permission
from core.auth import auth_bp
from core.admin import admin_bp
from apps.email_validator.routes import email_validator_bp
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(email_validator_bp, url_prefix='/apps/email-validator')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para aceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # CORRIGIDO: Usar db.session.get() em vez de User.query.get()
    user = db.session.get(User, session['user_id'])
    
    if user.role == 'admin':
        apps = App.query.filter_by(is_active=True).all()
    else:
        permitted_app_ids = [p.app_id for p in user.permissions]
        apps = App.query.filter(App.id.in_(permitted_app_ids), App.is_active == True).all()
    
    return render_template('dashboard.html', user=user, apps=apps)

def init_db():
    with app.app_context():
        db.create_all()
        
        if not App.query.filter_by(name='Email Validator').first():
            email_app = App(
                name='Email Validator',
                description='Validação e verificação de emails',
                route='/apps/email-validator'
            )
            db.session.add(email_app)
            db.session.commit()
            print('✅ Email Validator app registada!')
        
        if not User.query.filter_by(email='admin@myxapp.com').first():
            admin = User(email='admin@myxapp.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin criado: admin@myxapp.com / admin123')

if __name__ == '__main__':
    init_db()
    print('🚀 MyXAPP a correr em http://localhost:5000')
    app.run(debug=True)