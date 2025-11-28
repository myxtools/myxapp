# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from models import db, User, Permission, App
from functools import wraps

email_validator_bp = Blueprint('email_validator', __name__)

def app_permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login.', 'warning')
            return redirect(url_for('auth.login'))
        
        # CORRIGIDO: Usar db.session.get() em vez de User.query.get()
        user = db.session.get(User, session['user_id'])
        app = App.query.filter_by(route='/apps/email-validator').first()
        
        if not app:
            flash('App não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        if user.role != 'admin' and not user.has_permission(app.id):
            flash('Não tem permissão para aceder a esta app.', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@email_validator_bp.route('/')
@app_permission_required
def index():
    return render_template('apps/email_validator.html')

@email_validator_bp.route('/validate', methods=['POST'])
@app_permission_required
def validate():
    data = request.get_json()
    email = data.get('email', '')
    
    # Validação básica
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    is_valid = bool(re.match(email_regex, email))
    
    return jsonify({
        'valid': is_valid,
        'email': email,
        'message': 'Email válido!' if is_valid else 'Email inválido.'
    })