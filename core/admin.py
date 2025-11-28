from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User, App, Permission
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Acesso negado. Apenas administradores.', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_apps = App.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_apps=total_apps,
                         active_users=active_users,
                         recent_users=recent_users)

@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/<int:user_id>/permissions', methods=['GET', 'POST'])
@admin_required
def user_permissions(user_id):
    user = User.query.get_or_404(user_id)
    all_apps = App.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        # Remove todas as permissões existentes
        Permission.query.filter_by(user_id=user_id).delete()
        
        # Adiciona novas permissões
        app_ids = request.form.getlist('apps')
        for app_id in app_ids:
            permission = Permission(user_id=user_id, app_id=int(app_id))
            db.session.add(permission)
        
        db.session.commit()
        flash(f'Permissões atualizadas para {user.email}', 'success')
        return redirect(url_for('admin.users'))
    
    user_app_ids = [p.app_id for p in user.permissions]
    
    return render_template('admin/permissions.html', 
                         user=user, 
                         all_apps=all_apps,
                         user_app_ids=user_app_ids)

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == session['user_id']:
        flash('Não pode desativar a sua própria conta.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'ativado' if user.is_active else 'desativado'
    flash(f'Utilizador {user.email} foi {status}.', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == session['user_id']:
        flash('Não pode apagar a sua própria conta.', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Utilizador {user.email} foi apagado.', 'success')
    return redirect(url_for('admin.users'))