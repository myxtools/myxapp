# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, url_for, flash, session, request
from config import Config
from models import db, bcrypt, User, App, Permission
from core.auth import auth_bp
from core.admin import admin_bp
from apps.email_validator.routes import email_validator_bp
from apps.text_transformer.routes import text_transformer_bp
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

# ==============================================
# DATABASE CONFIGURATION
# ==============================================
# Usa PostgreSQL no Render, SQLite localmente
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Render/Produção: PostgreSQL
    # Fix para Render (muda postgres:// para postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Local: SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myxapp.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(email_validator_bp, url_prefix='/apps/email-validator')
app.register_blueprint(text_transformer_bp, url_prefix='/apps/text-transformer')

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
    user = db.session.get(User, session['user_id'])
    
    if user.role == 'admin':
        apps = App.query.filter_by(is_active=True).all()
    else:
        permitted_app_ids = [p.app_id for p in user.permissions]
        apps = App.query.filter(App.id.in_(permitted_app_ids), App.is_active == True).all()
    
    return render_template('dashboard.html', user=user, apps=apps)

# ==============================================
# ROTA TEMPORÁRIA PARA INICIALIZAR POSTGRESQL
# ==============================================
@app.route('/init-db-postgres-2024')
def init_database_postgres():
    """Inicializar PostgreSQL - APAGAR DEPOIS!"""
    try:
        db.create_all()
        
        messages = []
        
        # Criar apps
        if not App.query.filter_by(name='Email Validator').first():
            email_app = App(
                name='Email Validator',
                description='Validação e verificação de emails',
                route='/apps/email-validator'
            )
            db.session.add(email_app)
            messages.append('✅ Email Validator criada')
        else:
            messages.append('ℹ️ Email Validator já existe')
        
        if not App.query.filter_by(name='Text Transformer').first():
            text_app = App(
                name='Text Transformer',
                description='Transforme textos com 18 ferramentas profissionais',
                route='/apps/text-transformer'
            )
            db.session.add(text_app)
            messages.append('✅ Text Transformer criada')
        else:
            messages.append('ℹ️ Text Transformer já existe')
        
        # Criar admin
        if not User.query.filter_by(email='admin@myxapp.com').first():
            admin = User(email='admin@myxapp.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            messages.append('✅ Admin criado: admin@myxapp.com / admin123')
        else:
            messages.append('ℹ️ Admin já existe')
        
        db.session.commit()
        
        messages_html = ''.join(['<li>' + m + '</li>' for m in messages])
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>PostgreSQL Inicializado</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #28a745; }}
                ul {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                a {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
                a:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <h1>✅ PostgreSQL Inicializado com Sucesso!</h1>
            <ul>{messages_html}</ul>
            <a href="/">🏠 Ir para Home</a>
            <a href="/login">🔐 Login</a>
        </body>
        </html>
        '''
        
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #dc3545; }}
                pre {{ background: #f8f9fa; padding: 20px; border-radius: 8px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>❌ Erro ao inicializar:</h1>
            <pre>{str(e)}</pre>
            <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Voltar</a>
        </body>
        </html>
        '''

def init_db():
    """Inicializa base de dados e dados iniciais (apenas em desenvolvimento local)"""
    with app.app_context():
        db.create_all()
        
        # Criar apps se não existirem
        if not App.query.filter_by(name='Email Validator').first():
            email_app = App(
                name='Email Validator',
                description='Validação e verificação de emails',
                route='/apps/email-validator'
            )
            db.session.add(email_app)
            db.session.commit()
            print('✅ Email Validator app registada!')
        
        if not App.query.filter_by(name='Text Transformer').first():
            text_app = App(
                name='Text Transformer',
                description='Transformação e análise de texto com múltiplas ferramentas',
                route='/apps/text-transformer'
            )
            db.session.add(text_app)
            db.session.commit()
            print('✅ Text Transformer app registada!')
        
        # Criar admin se não existir
        if not User.query.filter_by(email='admin@myxapp.com').first():
            admin = User(email='admin@myxapp.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin criado: admin@myxapp.com / admin123')

if __name__ == '__main__':
    # Apenas inicializa DB se estiver em desenvolvimento (local)
    if not os.environ.get('DATABASE_URL'):
        init_db()
    
    print('🚀 MyXAPP a correr em http://localhost:5000')
    app.run(debug=True)