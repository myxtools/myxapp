# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from models import db, User, Permission, App, TextTransformation
from functools import wraps
from apps.text_transformer.transformer import TextTransformer
from datetime import datetime, timedelta

# Criar Blueprint
text_transformer_bp = Blueprint('text_transformer', __name__)

# ====================================
# CONFIGURAÇÕES DE LIMITAÇÕES
# ====================================
PUBLIC_CHAR_LIMIT = 500
PUBLIC_TRANSFORMATIONS_PER_HOUR = 3
LOGGED_CHAR_LIMIT = 50000

# Lista completa de transformações disponíveis
ALL_TRANSFORMATIONS = [
    'uppercase', 'lowercase', 'capitalize', 'title_case',
    'alternating_case', 'reverse', 'snake_case', 'kebab_case',
    'camel_case', 'pascal_case', 'remove_accents', 'remove_extra_spaces',
    'remove_duplicate_lines', 'sort_lines_asc', 'sort_lines_desc',
    'add_line_numbers', 'extract_emails', 'extract_urls'
]

# Transformações disponíveis para público (4 básicas)
PUBLIC_TRANSFORMATIONS = ['uppercase', 'lowercase', 'capitalize', 'title_case']

# ====================================
# DECORADORES
# ====================================

def app_permission_required(f):
    """Decorador para área privada - requer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para aceder à versão completa.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            flash('Sessão inválida.', 'warning')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def check_public_limits():
    """Verificar limites para utilizadores não autenticados"""
    if 'text_transformer_count' not in session:
        session['text_transformer_count'] = 0
        session['text_transformer_reset'] = datetime.now().isoformat()
    
    reset_time = datetime.fromisoformat(session['text_transformer_reset'])
    if datetime.now() - reset_time > timedelta(hours=1):
        session['text_transformer_count'] = 0
        session['text_transformer_reset'] = datetime.now().isoformat()
    
    if session['text_transformer_count'] >= PUBLIC_TRANSFORMATIONS_PER_HOUR:
        return False, f"Limite de {PUBLIC_TRANSFORMATIONS_PER_HOUR} transformações/hora atingido."
    
    return True, None

# ====================================
# FUNÇÕES AUXILIARES
# ====================================

def get_transformation_info():
    """Retorna informações de todas as transformações organizadas"""
    return TextTransformer.get_all_transformations()

def is_public_transformation(trans_type):
    """Verifica se a transformação está disponível na versão pública"""
    return trans_type in PUBLIC_TRANSFORMATIONS

# ====================================
# ROTAS - HUB (Index)
# ====================================

@text_transformer_bp.route('/public')
def public_hub():
    """Hub público - 4 transformações básicas"""
    transformations = get_transformation_info()
    
    # Filtrar apenas as 4 básicas
    public_trans = {k: v for k, v in transformations.items() if k in PUBLIC_TRANSFORMATIONS}
    
    # Organizar por categoria
    categories = {}
    for key, trans in public_trans.items():
        category = trans['category']
        if category not in categories:
            categories[category] = []
        categories[category].append({
            'key': key,
            'name': trans['name'],
            'description': trans['description'],
            'example': trans['example'],
            'icon': get_icon_for_transformation(key)
        })
    
    # Calcular transformações restantes
    remaining = PUBLIC_TRANSFORMATIONS_PER_HOUR
    if 'text_transformer_count' in session:
        remaining = PUBLIC_TRANSFORMATIONS_PER_HOUR - session['text_transformer_count']
    
    return render_template('text_transformer_public_hub.html',
                         categories=categories,
                         transformations_remaining=remaining,
                         total_transformations=PUBLIC_TRANSFORMATIONS_PER_HOUR)

@text_transformer_bp.route('/')
@app_permission_required
def hub():
    """Hub cliente - 18 transformações"""
    user = db.session.get(User, session['user_id'])
    transformations = get_transformation_info()
    
    # Organizar por categoria
    categories = {}
    for key, trans in transformations.items():
        category = trans['category']
        if category not in categories:
            categories[category] = []
        categories[category].append({
            'key': key,
            'name': trans['name'],
            'description': trans['description'],
            'example': trans['example'],
            'icon': get_icon_for_transformation(key)
        })
    
    return render_template('text_transformer_hub.html',
                         user=user,
                         categories=categories)

def get_icon_for_transformation(trans_type):
    """Retorna ícone FontAwesome para cada tipo de transformação"""
    icons = {
        'uppercase': 'fa-font',
        'lowercase': 'fa-text-height',
        'capitalize': 'fa-heading',
        'title_case': 'fa-text-width',
        'alternating_case': 'fa-wave-square',
        'reverse': 'fa-exchange-alt',
        'snake_case': 'fab fa-python',
        'kebab_case': 'fa-minus',
        'camel_case': 'fab fa-js',
        'pascal_case': 'fa-code',
        'remove_accents': 'fa-eraser',
        'remove_extra_spaces': 'fa-compress',
        'remove_duplicate_lines': 'fa-copy',
        'sort_lines_asc': 'fa-sort-alpha-down',
        'sort_lines_desc': 'fa-sort-alpha-up',
        'add_line_numbers': 'fa-list-ol',
        'extract_emails': 'fa-at',
        'extract_urls': 'fa-link'
    }
    return icons.get(trans_type, 'fa-magic')

# ====================================
# ROTAS - PÁGINAS INDIVIDUAIS (Público)
# ====================================

@text_transformer_bp.route('/public/<transformation_type>')
def public_transformation(transformation_type):
    """Página individual de transformação (versão pública)"""
    
    # Verificar se a transformação existe e é pública
    if transformation_type not in PUBLIC_TRANSFORMATIONS:
        flash('Esta transformação não está disponível na versão pública.', 'warning')
        return redirect(url_for('text_transformer.public_hub'))
    
    transformations = get_transformation_info()
    current_trans = transformations.get(transformation_type)
    
    if not current_trans:
        flash('Transformação não encontrada.', 'danger')
        return redirect(url_for('text_transformer.public_hub'))
    
    # Calcular transformações restantes
    remaining = PUBLIC_TRANSFORMATIONS_PER_HOUR
    if 'text_transformer_count' in session:
        remaining = PUBLIC_TRANSFORMATIONS_PER_HOUR - session['text_transformer_count']
    
    # Lista de transformações para dropdown (só as 4 públicas)
    available_trans = {k: v for k, v in transformations.items() if k in PUBLIC_TRANSFORMATIONS}
    
    return render_template('text_transformer_public_page.html',
                         transformation_type=transformation_type,
                         current_transformation=current_trans,
                         available_transformations=available_trans,
                         char_limit=PUBLIC_CHAR_LIMIT,
                         transformations_remaining=remaining,
                         total_transformations=PUBLIC_TRANSFORMATIONS_PER_HOUR,
                         icon=get_icon_for_transformation(transformation_type))

# ====================================
# ROTAS - PÁGINAS INDIVIDUAIS (Cliente)
# ====================================

@text_transformer_bp.route('/<transformation_type>')
@app_permission_required
def transformation(transformation_type):
    """Página individual de transformação (versão cliente)"""
    
    user = db.session.get(User, session['user_id'])
    
    # Verificar se a transformação existe
    if transformation_type not in ALL_TRANSFORMATIONS:
        flash('Transformação não encontrada.', 'danger')
        return redirect(url_for('text_transformer.hub'))
    
    transformations = get_transformation_info()
    current_trans = transformations.get(transformation_type)
    
    if not current_trans:
        flash('Transformação não encontrada.', 'danger')
        return redirect(url_for('text_transformer.hub'))
    
    return render_template('text_transformer_page.html',
                         user=user,
                         transformation_type=transformation_type,
                         current_transformation=current_trans,
                         available_transformations=transformations,
                         char_limit=LOGGED_CHAR_LIMIT,
                         icon=get_icon_for_transformation(transformation_type))

# ====================================
# API - TRANSFORMAÇÃO (Público)
# ====================================

@text_transformer_bp.route('/api/public/transform', methods=['POST'])
def api_public_transform():
    """API pública para transformar texto"""
    data = request.get_json()
    
    # Verificar limites
    allowed, error_message = check_public_limits()
    if not allowed:
        return jsonify({'success': False, 'error': error_message}), 429
    
    text = data.get('text', '')
    transformation = data.get('transformation', '')
    
    # Validação
    if not text:
        return jsonify({'success': False, 'error': 'Texto não pode estar vazio'}), 400
    
    if transformation not in PUBLIC_TRANSFORMATIONS:
        return jsonify({'success': False, 'error': 'Transformação não disponível na versão pública'}), 400
    
    if len(text) > PUBLIC_CHAR_LIMIT:
        return jsonify({
            'success': False, 
            'error': f'Limite de {PUBLIC_CHAR_LIMIT} caracteres excedido.'
        }), 400
    
    # Executar transformação
    try:
        transformer = TextTransformer()
        result = execute_transformation(transformer, transformation, text)
        
        # Incrementar contador
        session['text_transformer_count'] = session.get('text_transformer_count', 0) + 1
        remaining = PUBLIC_TRANSFORMATIONS_PER_HOUR - session['text_transformer_count']
        
        # Adicionar watermark
        watermark = "\n\n---\n✨ Processado com MyXAPP Text Transformer"
        result_with_watermark = result + watermark
        
        # Estatísticas
        stats = transformer.count_stats(result)
        
        return jsonify({
            'success': True,
            'result': result_with_watermark,
            'stats': stats,
            'remaining_transformations': remaining,
            'is_public': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro ao processar: {str(e)}'}), 500

# ====================================
# API - TRANSFORMAÇÃO (Cliente)
# ====================================

@text_transformer_bp.route('/api/transform', methods=['POST'])
@app_permission_required
def api_transform():
    """API privada para transformar texto"""
    user = db.session.get(User, session['user_id'])
    data = request.get_json()
    
    text = data.get('text', '')
    transformation = data.get('transformation', '')
    prefix = data.get('prefix', '')
    suffix = data.get('suffix', '')
    
    # Validação
    if not text:
        return jsonify({'success': False, 'error': 'Texto não pode estar vazio'}), 400
    
    if transformation not in ALL_TRANSFORMATIONS:
        return jsonify({'success': False, 'error': 'Transformação inválida'}), 400
    
    if len(text) > LOGGED_CHAR_LIMIT:
        return jsonify({
            'success': False, 
            'error': f'Limite de {LOGGED_CHAR_LIMIT} caracteres excedido'
        }), 400
    
    # Executar transformação
    try:
        transformer = TextTransformer()
        
        # Transformações que precisam de parâmetros extras
        if transformation == 'add_prefix':
            result = transformer.add_prefix(text, prefix)
        elif transformation == 'add_suffix':
            result = transformer.add_suffix(text, suffix)
        else:
            result = execute_transformation(transformer, transformation, text)
        
        # Estatísticas
        stats = transformer.count_stats(result)
        
        # Salvar no histórico AUTOMATICAMENTE
        history_entry = TextTransformation(
            user_id=user.id,
            transformation_type=transformation,
            original_text=text[:1000],
            result_text=result[:1000],
            char_count=len(text)
        )
        db.session.add(history_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'result': result,
            'stats': stats,
            'is_public': False,
            'history_id': history_entry.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao processar: {str(e)}'}), 500

def execute_transformation(transformer, trans_type, text):
    """Executa a transformação apropriada"""
    transformations_map = {
        'uppercase': transformer.to_uppercase,
        'lowercase': transformer.to_lowercase,
        'capitalize': transformer.to_capitalize,
        'title_case': transformer.to_title_case,
        'alternating_case': transformer.to_alternating_case,
        'reverse': transformer.to_reverse,
        'snake_case': transformer.to_snake_case,
        'kebab_case': transformer.to_kebab_case,
        'camel_case': transformer.to_camel_case,
        'pascal_case': transformer.to_pascal_case,
        'remove_accents': transformer.remove_accents,
        'remove_extra_spaces': transformer.remove_extra_spaces,
        'remove_duplicate_lines': transformer.remove_duplicate_lines,
        'sort_lines_asc': transformer.sort_lines_asc,
        'sort_lines_desc': transformer.sort_lines_desc,
        'add_line_numbers': transformer.add_line_numbers,
        'extract_emails': transformer.extract_emails,
        'extract_urls': transformer.extract_urls
    }
    
    if trans_type in transformations_map:
        return transformations_map[trans_type](text)
    else:
        raise ValueError(f'Transformação desconhecida: {trans_type}')

# ====================================
# API - ESTATÍSTICAS
# ====================================

@text_transformer_bp.route('/api/public/stats', methods=['POST'])
def api_public_stats():
    """API pública para estatísticas"""
    data = request.get_json()
    text = data.get('text', '')
    
    if len(text) > PUBLIC_CHAR_LIMIT:
        return jsonify({
            'success': False, 
            'error': f'Limite de {PUBLIC_CHAR_LIMIT} caracteres excedido'
        }), 400
    
    stats = TextTransformer.count_stats(text)
    return jsonify({'success': True, 'stats': stats})

@text_transformer_bp.route('/api/stats', methods=['POST'])
@app_permission_required
def api_stats():
    """API privada para estatísticas"""
    data = request.get_json()
    text = data.get('text', '')
    
    if len(text) > LOGGED_CHAR_LIMIT:
        return jsonify({
            'success': False, 
            'error': f'Limite de {LOGGED_CHAR_LIMIT} caracteres excedido'
        }), 400
    
    stats = TextTransformer.count_stats(text)
    return jsonify({'success': True, 'stats': stats})

# ====================================
# ROTAS - HISTÓRICO
# ====================================

@text_transformer_bp.route('/history')
@app_permission_required
def history():
    """Página de histórico completo"""
    user = db.session.get(User, session['user_id'])
    
    # Parâmetros de paginação e ordenação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'date')  # 'date' ou 'type'
    
    # Limitar per_page entre 10 e 100
    per_page = max(10, min(per_page, 100))
    
    # Query base
    query = TextTransformation.query.filter_by(user_id=user.id)
    
    # Ordenação
    if sort_by == 'type':
        query = query.order_by(TextTransformation.transformation_type.asc(), 
                              TextTransformation.created_at.desc())
    else:  # sort_by == 'date'
        query = query.order_by(TextTransformation.created_at.desc())
    
    # Paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('text_transformer_history.html',
                         user=user,
                         pagination=pagination,
                         sort_by=sort_by,
                         per_page=per_page)

@text_transformer_bp.route('/api/history/<int:id>/view', methods=['GET'])
@app_permission_required
def api_view_history(id):
    """Ver detalhes de um item do histórico"""
    user = db.session.get(User, session['user_id'])
    entry = TextTransformation.query.filter_by(id=id, user_id=user.id).first()
    
    if not entry:
        return jsonify({'success': False, 'error': 'Entrada não encontrada'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': entry.id,
            'transformation_type': entry.transformation_type,
            'original_text': entry.original_text,
            'result_text': entry.result_text,
            'char_count': entry.char_count,
            'created_at': entry.created_at.strftime('%d/%m/%Y %H:%M:%S')
        }
    })

@text_transformer_bp.route('/api/history/<int:id>/delete', methods=['DELETE'])
@app_permission_required
def api_delete_history(id):
    """Apagar entrada do histórico"""
    user = db.session.get(User, session['user_id'])
    entry = TextTransformation.query.filter_by(id=id, user_id=user.id).first()
    
    if not entry:
        return jsonify({'success': False, 'error': 'Entrada não encontrada'}), 404
    
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Entrada eliminada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao eliminar: {str(e)}'}), 500

@text_transformer_bp.route('/api/history/<int:id>/download', methods=['GET'])
@app_permission_required
def api_download_history(id):
    """Download de um item do histórico"""
    user = db.session.get(User, session['user_id'])
    entry = TextTransformation.query.filter_by(id=id, user_id=user.id).first()
    
    if not entry:
        return jsonify({'success': False, 'error': 'Entrada não encontrada'}), 404
    
    format_type = request.args.get('format', 'txt')
    
    if format_type == 'txt':
        content = f"""TEXT TRANSFORMER - HISTÓRICO
================================
Data: {entry.created_at.strftime('%d/%m/%Y %H:%M:%S')}
Tipo: {entry.transformation_type.replace('_', ' ').title()}
Caracteres: {entry.char_count}

TEXTO ORIGINAL:
{entry.original_text}

RESULTADO:
{entry.result_text}
"""
        return jsonify({
            'success': True,
            'content': content,
            'filename': f'text_transformer_{entry.id}_{entry.created_at.strftime("%Y%m%d_%H%M%S")}.txt',
            'mime_type': 'text/plain'
        })
    
    elif format_type == 'json':
        import json
        export_data = {
            'id': entry.id,
            'transformation_type': entry.transformation_type,
            'original_text': entry.original_text,
            'result_text': entry.result_text,
            'char_count': entry.char_count,
            'created_at': entry.created_at.isoformat(),
            'exported_at': datetime.now().isoformat()
        }
        return jsonify({
            'success': True,
            'content': json.dumps(export_data, indent=2, ensure_ascii=False),
            'filename': f'text_transformer_{entry.id}_{entry.created_at.strftime("%Y%m%d_%H%M%S")}.json',
            'mime_type': 'application/json'
        })
    
    else:
        return jsonify({'success': False, 'error': 'Formato inválido'}), 400

# ====================================
# API - EXPORTAÇÃO (de resultados atuais)
# ====================================

@text_transformer_bp.route('/api/export', methods=['POST'])
@app_permission_required
def api_export():
    """Exportar resultado atual"""
    data = request.get_json()
    text = data.get('text', '')
    format_type = data.get('format', 'txt')
    transformation_type = data.get('transformation_type', 'unknown')
    
    if format_type == 'txt':
        return jsonify({
            'success': True,
            'content': text,
            'filename': f'text_transformer_{transformation_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            'mime_type': 'text/plain'
        })
    elif format_type == 'json':
        import json
        stats = TextTransformer.count_stats(text)
        export_data = {
            'text': text,
            'transformation_type': transformation_type,
            'stats': stats,
            'exported_at': datetime.now().isoformat()
        }
        return jsonify({
            'success': True,
            'content': json.dumps(export_data, indent=2, ensure_ascii=False),
            'filename': f'text_transformer_{transformation_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'mime_type': 'application/json'
        })
    else:
        return jsonify({'success': False, 'error': 'Formato inválido'}), 400

# ====================================
# ROTAS - ADMIN
# ====================================

@text_transformer_bp.route('/admin')
def admin_dashboard():
    """Painel administrativo - estatísticas de uso"""
    if 'user_id' not in session:
        flash('Por favor, faça login.', 'warning')
        return redirect(url_for('auth.login'))
    
    user = db.session.get(User, session['user_id'])
    if not user or user.role != 'admin':
        flash('Acesso negado. Apenas administradores.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Estatísticas globais
    total_transformations = TextTransformation.query.count()
    total_users = db.session.query(TextTransformation.user_id).distinct().count()
    
    # Transformações por tipo
    from sqlalchemy import func
    transformations_by_type = db.session.query(
        TextTransformation.transformation_type,
        func.count(TextTransformation.id).label('count')
    ).group_by(TextTransformation.transformation_type).all()
    
    # Top 10 utilizadores mais ativos
    top_users = db.session.query(
        User.email,
        func.count(TextTransformation.id).label('count')
    ).join(TextTransformation).group_by(User.id).order_by(func.count(TextTransformation.id).desc()).limit(10).all()
    
    # Transformações recentes (últimas 50)
    recent_transformations = TextTransformation.query.order_by(
        TextTransformation.created_at.desc()
    ).limit(50).all()
    
    # Transformações por dia (últimos 7 dias)
    seven_days_ago = datetime.now() - timedelta(days=7)
    transformations_by_day = db.session.query(
        func.date(TextTransformation.created_at).label('date'),
        func.count(TextTransformation.id).label('count')
    ).filter(TextTransformation.created_at >= seven_days_ago)\
     .group_by(func.date(TextTransformation.created_at))\
     .order_by('date').all()
    
    return render_template('apps/text_transformer_admin.html',
                         user=user,
                         total_transformations=total_transformations,
                         total_users=total_users,
                         transformations_by_type=transformations_by_type,
                         top_users=top_users,
                         recent_transformations=recent_transformations,
                         transformations_by_day=transformations_by_day)

