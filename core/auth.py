from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para aceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not email or not password:
            flash('Email e password são obrigatórios.', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('As passwords não coincidem.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Este email já está registado.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registo efetuado com sucesso! Por favor, faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Esta conta está desativada.', 'danger')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            session.permanent = True
            
            flash(f'Bem-vindo, {user.email}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou password incorretos.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout efetuado com sucesso.', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.get(session['user_id'])
        
        # Verificar password atual
        if not user.check_password(current_password):
            flash('Password atual incorreta.', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Verificar se as novas passwords coincidem
        if new_password != confirm_password:
            flash('As novas passwords não coincidem.', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Verificar comprimento mínimo
        if len(new_password) < 6:
            flash('A password deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Atualizar password
        user.set_password(new_password)
        db.session.commit()
        
        flash('Password alterada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')