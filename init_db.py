# -*- coding: utf-8 -*-
"""Script para inicializar base de dados no Render"""
from app import app, db
from models import User, App

def init_database():
    with app.app_context():
        print("🔧 Criando tabelas...")
        db.create_all()
        
        # Criar apps
        if not App.query.filter_by(name='Email Validator').first():
            email_app = App(
                name='Email Validator',
                description='Validação e verificação de emails',
                icon='fa-envelope',
                route='/apps/email-validator'
            )
            db.session.add(email_app)
            print('✅ Email Validator criada')
        
        if not App.query.filter_by(name='Text Transformer').first():
            text_app = App(
                name='Text Transformer',
                description='Transforme textos com 18 ferramentas profissionais',
                icon='fa-magic',
                route='/apps/text-transformer'
            )
            db.session.add(text_app)
            print('✅ Text Transformer criada')
        
        # Criar admin
        if not User.query.filter_by(email='admin@myxapp.com').first():
            admin = User(email='admin@myxapp.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print('✅ Admin criado: admin@myxapp.com / admin123')
        
        db.session.commit()
        print("✅ Base de dados inicializada!")

if __name__ == '__main__':
    init_database()