# -*- coding: utf-8 -*-
"""
Script para integrar o Email Validator completo no MyXAPP
"""
import os

# Criar diretórios se não existirem
os.makedirs('apps/email_validator', exist_ok=True)
os.makedirs('templates/apps', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

print("🚀 Integrando Email Validator completo...")

# 1. ROUTES.PY
routes_content = '''# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from models import db, User, Permission, App
from functools import wraps
import re
import dns.resolver
import csv
import json
import io
from datetime import datetime
from werkzeug.utils import secure_filename
import openpyxl

email_validator_bp = Blueprint('email_validator', __name__)

# Lista de domínios descartáveis conhecidos
DISPOSABLE_DOMAINS = {
    'tempmail.com', 'guerrillamail.com', '10minutemail.com', 'throwaway.email',
    'mailinator.com', 'trashmail.com', 'temp-mail.org', 'fakeinbox.com',
    'maildrop.cc', 'yopmail.com', 'getnada.com', 'mohmal.com', 'sharklasers.com',
    'spam4.me', 'getairmail.com', 'dispostable.com', 'mintemail.com'
}

def app_permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login.', 'warning')
            return redirect(url_for('auth.login'))
        
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

def validate_single_email(email):
    """Valida um único email com todas as verificações"""
    email = email.strip().lower()
    
    result = {
        'email': email,
        'valid': False,
        'score': 0,
        'checks': {
            'format': False,
            'syntax': False,
            'domain': False,
            'mx_records': False,
            'disposable': False
        },
        'details': [],
        'warnings': []
    }
    
    # 1. Validação de formato básico
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        result['details'].append('Formato inválido')
        return result
    
    result['checks']['format'] = True
    result['score'] += 20
    
    # 2. Extrair domínio
    try:
        local, domain = email.rsplit('@', 1)
    except:
        result['details'].append('Erro ao processar domínio')
        return result
    
    result['checks']['domain'] = True
    result['score'] += 10
    
    # 3. Verificações de sintaxe avançada
    syntax_valid = True
    
    if '..' in email or '__' in email or '--' in email:
        syntax_valid = False
        result['warnings'].append('Caracteres consecutivos detectados')
    
    if local.startswith('.') or local.endswith('.'):
        syntax_valid = False
        result['warnings'].append('Local parte não pode começar/terminar com ponto')
    
    if len(local) > 64 or len(domain) > 255:
        syntax_valid = False
        result['warnings'].append('Comprimento excede limites RFC')
    
    result['checks']['syntax'] = syntax_valid
    if syntax_valid:
        result['score'] += 20
    
    # 4. Verificar se é descartável
    is_disposable = domain in DISPOSABLE_DOMAINS
    result['checks']['disposable'] = not is_disposable
    
    if is_disposable:
        result['warnings'].append('Email descartável/temporário')
    else:
        result['score'] += 20
    
    # 5. Verificar registos MX
    mx_valid = False
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        if len(mx_records) > 0:
            mx_valid = True
            result['details'].append(f'{len(mx_records)} servidor(es) de email encontrado(s)')
            result['score'] += 30
    except dns.resolver.NXDOMAIN:
        result['details'].append('Domínio não existe')
    except dns.resolver.NoAnswer:
        result['warnings'].append('Sem registos MX')
    except Exception as e:
        result['warnings'].append('Erro ao verificar MX')
    
    result['checks']['mx_records'] = mx_valid
    
    # 6. Determinar validade final
    result['valid'] = (
        result['checks']['format'] and
        result['checks']['syntax'] and
        result['checks']['mx_records'] and
        result['checks']['disposable']
    )
    
    return result

@email_validator_bp.route('/')
@app_permission_required
def index():
    return render_template('apps/email_validator.html')

@email_validator_bp.route('/validate', methods=['POST'])
@app_permission_required
def validate():
    """Validar um único email"""
    data = request.get_json()
    email = data.get('email', '')
    
    if not email:
        return jsonify({'error': 'Email não fornecido'}), 400
    
    result = validate_single_email(email)
    return jsonify(result)

@email_validator_bp.route('/upload', methods=['POST'])
@app_permission_required
def upload():
    """Processar upload de ficheiro"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum ficheiro enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum ficheiro selecionado'}), 400
    
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    emails = []
    
    try:
        if file_ext == 'csv':
            stream = io.StringIO(file.stream.read().decode('utf-8-sig'), newline=None)
            csv_reader = csv.reader(stream)
            for row in csv_reader:
                if row and row[0].strip():
                    emails.append(row[0].strip())
        
        elif file_ext == 'txt':
            content = file.stream.read().decode('utf-8-sig')
            emails = [line.strip() for line in content.split('\\n') if line.strip()]
        
        elif file_ext in ['xlsx', 'xls']:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            for row in sheet.iter_rows(values_only=True):
                if row and row[0]:
                    email = str(row[0]).strip()
                    if email:
                        emails.append(email)
        
        else:
            return jsonify({'error': 'Formato de ficheiro não suportado'}), 400
        
        seen = set()
        unique_emails = []
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                unique_emails.append(email)
        
        return jsonify({
            'success': True,
            'total': len(unique_emails),
            'emails': unique_emails[:1000]
        })
    
    except Exception as e:
        return jsonify({'error': f'Erro ao processar ficheiro: {str(e)}'}), 500

@email_validator_bp.route('/validate-bulk', methods=['POST'])
@app_permission_required
def validate_bulk():
    """Validar lista de emails"""
    data = request.get_json()
    emails = data.get('emails', [])
    
    if not emails:
        return jsonify({'error': 'Nenhum email para validar'}), 400
    
    results = []
    for email in emails:
        result = validate_single_email(email)
        results.append(result)
    
    valid_count = sum(1 for r in results if r['valid'])
    invalid_count = len(results) - valid_count
    
    return jsonify({
        'results': results,
        'stats': {
            'total': len(results),
            'valid': valid_count,
            'invalid': invalid_count,
            'success_rate': round((valid_count / len(results)) * 100, 2) if results else 0
        }
    })

@email_validator_bp.route('/export/<format>')
@app_permission_required
def export(format):
    """Exportar resultados"""
    results_json = request.args.get('data')
    
    if not results_json:
        return jsonify({'error': 'Sem dados para exportar'}), 400
    
    try:
        results = json.loads(results_json)
    except:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Email', 'Válido', 'Score', 'Formato', 'Sintaxe', 'Domínio', 'MX Records', 'Não Descartável', 'Detalhes'])
        
        for result in results:
            checks = result.get('checks', {})
            writer.writerow([
                result['email'],
                'Sim' if result['valid'] else 'Não',
                result.get('score', 0),
                'Sim' if checks.get('format') else 'Não',
                'Sim' if checks.get('syntax') else 'Não',
                'Sim' if checks.get('domain') else 'Não',
                'Sim' if checks.get('mx_records') else 'Não',
                'Sim' if checks.get('disposable') else 'Não',
                '; '.join(result.get('details', []) + result.get('warnings', []))
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'email_validation_{timestamp}.csv'
        )
    
    elif format == 'json':
        output = json.dumps(results, indent=2, ensure_ascii=False)
        return send_file(
            io.BytesIO(output.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'email_validation_{timestamp}.json'
        )
    
    elif format == 'txt':
        output = io.StringIO()
        output.write(f'Email Validation Results - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\\n')
        output.write('=' * 80 + '\\n\\n')
        
        for i, result in enumerate(results, 1):
            output.write(f'{i}. {result["email"]}\\n')
            output.write(f'   Status: {"✓ VÁLIDO" if result["valid"] else "✗ INVÁLIDO"}\\n')
            output.write(f'   Score: {result.get("score", 0)}/100\\n')
            
            if result.get('details'):
                output.write(f'   Detalhes: {", ".join(result["details"])}\\n')
            if result.get('warnings'):
                output.write(f'   Avisos: {", ".join(result["warnings"])}\\n')
            
            output.write('\\n')
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'email_validation_{timestamp}.txt'
        )
    
    else:
        return jsonify({'error': 'Formato não suportado'}), 400
'''

with open('apps/email_validator/routes.py', 'w', encoding='utf-8') as f:
    f.write(routes_content)

print("✅ routes.py criado")

# 2. ATUALIZAR REQUIREMENTS.TXT
requirements_content = '''Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Bcrypt==1.0.1
python-dotenv==1.0.0
dnspython==2.4.2
openpyxl==3.1.2
'''

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_content)

print("✅ requirements.txt atualizado")

print("\n🎉 Integração completa!")
print("\n📋 Próximos passos:")
print("1. pip install dnspython openpyxl --break-system-packages")
print("2. Copia o HTML manualmente (é muito extenso)")
print("3. python app.py")