# 📚 MyXAPP - Guia de Desenvolvimento

> Sistema modular de gestão de aplicações web com autenticação centralizada

---

## 🏗️ Arquitetura do Projeto
```
myxapp/
├── app.py                      # Aplicação principal Flask
├── config.py                   # Configurações
├── models.py                   # Modelos de Base de Dados
├── requirements.txt            # Dependências Python
│
├── core/                       # Funcionalidades core
│   ├── auth.py                # Sistema de autenticação
│   └── admin.py               # Painel administrativo
│
├── apps/                      # Apps modulares (adiciona aqui novas apps)
│   └── email_validator/
│       ├── __init__.py
│       ├── routes.py
│       └── validator.py
│
├── templates/                 # Templates HTML
│   ├── base.html             # Template base (todas as páginas extendem este)
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin/                # Templates admin
│   └── apps/                 # Templates de apps
│
├── static/                   # Ficheiros estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│
└── instance/                 # Base de dados SQLite (NÃO commitar)
    └── myxapp.db
```

---

## 🚀 Como Criar uma Nova App

### **Passo 1: Criar Estrutura de Pastas**
```bash
cd D:\Software\myxapp\apps
mkdir nova_app
cd nova_app
type nul > __init__.py
type nul > routes.py
```

### **Passo 2: Criar `routes.py`**

**Template Base:** `apps/nova_app/routes.py`
```python
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from models import db, User, Permission, App
from functools import wraps

# Criar Blueprint
nova_app_bp = Blueprint('nova_app', __name__)

# Decorador de Permissões (OBRIGATÓRIO para proteger rotas)
def app_permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            flash('Sessão inválida.', 'warning')
            return redirect(url_for('auth.login'))
        
        app = App.query.filter_by(route='/apps/nova-app').first()
        
        if not app:
            flash('App não encontrada.', 'danger')
            return redirect(url_for('dashboard'))
        
        if user.role != 'admin' and not user.has_permission(app.id):
            flash('Não tem permissão para aceder a esta app.', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Rota Principal
@nova_app_bp.route('/')
@app_permission_required
def index():
    """Página principal da app"""
    return render_template('apps/nova_app.html')

# Exemplo: API endpoint
@nova_app_bp.route('/api/exemplo', methods=['POST'])
@app_permission_required
def api_exemplo():
    """Endpoint de API exemplo"""
    data = request.get_json()
    
    # Tua lógica aqui
    
    return jsonify({'success': True, 'data': data})
```

### **Passo 3: Criar Template HTML**

**Caminho:** `templates/apps/nova_app.html`
```html
{% extends "base.html" %}

{% block title %}Nova App - MyXAPP{% endblock %}

{% block extra_css %}
<style>
/* CSS específico da tua app */
.custom-class {
    /* teus estilos */
}
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Nova App</h1>
    <p>Conteúdo da tua aplicação aqui</p>
    
    <!-- Exemplo: Formulário -->
    <div class="card">
        <div class="card-body">
            <input type="text" id="inputExemplo" class="form-control" placeholder="Digite algo...">
            <button class="btn btn-primary mt-2" onclick="executarAcao()">Executar</button>
        </div>
    </div>
    
    <!-- Resultado -->
    <div id="resultado" class="mt-3"></div>
    
    <!-- Link voltar -->
    <a href="{{ url_for('dashboard') }}" class="btn btn-secondary mt-3">
        ← Voltar ao Dashboard
    </a>
</div>
{% endblock %}

{% block extra_js %}
<script>
// JavaScript específico da tua app

async function executarAcao() {
    const valor = document.getElementById('inputExemplo').value;
    
    try {
        const response = await fetch('{{ url_for("nova_app.api_exemplo") }}', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ valor: valor })
        });
        
        const data = await response.json();
        
        document.getElementById('resultado').innerHTML = 
            `<div class="alert alert-success">Sucesso! ${JSON.stringify(data)}</div>`;
    } catch (error) {
        document.getElementById('resultado').innerHTML = 
            `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}
</script>
{% endblock %}
```

### **Passo 4: Registar App no `app.py`**

Abre `app.py` e adiciona:
```python
# ANTES da linha "if __name__ == '__main__':"

# Importar blueprint
from apps.nova_app.routes import nova_app_bp

# Registar blueprint
app.register_blueprint(nova_app_bp, url_prefix='/apps/nova-app')
```

### **Passo 5: Adicionar App à Base de Dados**

Executa Python interativo:
```bash
python
```
```python
from app import app, db
from models import App

with app.app_context():
    # Criar app na BD
    nova_app = App(
        name='Nova App',
        description='Descrição da tua app',
        route='/apps/nova-app',
        is_active=True
    )
    db.session.add(nova_app)
    db.session.commit()
    print(f"✅ App criada com ID: {nova_app.id}")
```

Ou adiciona em `app.py` na função `init_db()`:
```python
# Adicionar após a criação do Email Validator
nova_app = App.query.filter_by(route='/apps/nova-app').first()
if not nova_app:
    nova_app = App(
        name='Nova App',
        description='Descrição da tua app',
        route='/apps/nova-app'
    )
    db.session.add(nova_app)
    db.session.commit()
    print('✅ Nova App registada!')
```

### **Passo 6: Testar!**
```bash
python app.py
```

1. Login como admin
2. Vai a `/admin/users`
3. Dá permissão a um utilizador para "Nova App"
4. Login como esse utilizador
5. Acede `/apps/nova-app`
6. **FUNCIONA!** ✅

---

## 🔐 Sistema de Permissões

### **Como Funciona:**
```
Admin → Acede a TUDO (sem verificação de permissões)
User → Só acede às apps com permissão explícita
```

### **Dar Permissões:**

1. Login como admin
2. `/admin/users`
3. Clicar "🔑 Permissões" ao lado do utilizador
4. Marcar checkbox da app
5. Guardar

### **Verificar Permissões no Código:**
```python
# No template (Jinja2)
{% if current_user.has_permission(app_id) %}
    <!-- Mostrar conteúdo -->
{% endif %}

# No Python
if user.has_permission(app_id):
    # Executar ação
```

---

## 📊 Modelos de Base de Dados

### **User** (Utilizadores)
```python
{
    'id': int,
    'email': str,
    'password_hash': str,
    'role': 'admin' | 'user',
    'is_active': bool,
    'created_at': datetime,
    'referred_by': int (FK para User)
}
```

### **App** (Aplicações)
```python
{
    'id': int,
    'name': str,
    'description': str,
    'route': str,  # Ex: '/apps/email-validator'
    'is_active': bool,
    'created_at': datetime
}
```

### **Permission** (Permissões)
```python
{
    'id': int,
    'user_id': int (FK),
    'app_id': int (FK),
    'granted_at': datetime
}
```

---

## 🛠️ Stack Tecnológica

### **Backend:**
- Python 3.11
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Bcrypt 1.0.1 (passwords)
- SQLite (desenvolvimento)
- PostgreSQL (produção - recomendado)

### **Frontend:**
- HTML5
- Bootstrap 5.3
- JavaScript Vanilla
- Font Awesome (ícones)

### **Outras:**
- dnspython (Email Validator)
- openpyxl (Excel export)

---

## 📝 Convenções de Código

### **Python:**
```python
# SEMPRE adicionar encoding UTF-8 no início
# -*- coding: utf-8 -*-

# Imports organizados
from flask import (
    Blueprint, render_template, request,
    jsonify, session, redirect, url_for, flash
)
from models import db, User, App
from functools import wraps

# Nomes descritivos
def validate_email(email):
    """Valida formato de email"""
    pass

# Usar f-strings
message = f"Bem-vindo, {user.email}!"
```

### **HTML/Jinja2:**
```html
<!-- SEMPRE extender base.html -->
{% extends "base.html" %}

<!-- Usar blocos corretos -->
{% block title %}Título{% endblock %}
{% block extra_css %}<!-- CSS -->{% endblock %}
{% block content %}<!-- Conteúdo -->{% endblock %}
{% block extra_js %}<!-- JS -->{% endblock %}

<!-- Usar url_for para URLs -->
<a href="{{ url_for('dashboard') }}">Dashboard</a>

<!-- Escapar HTML automaticamente (Jinja faz isto) -->
<p>{{ user_input }}</p>
```

### **Git:**
```bash
# Commits descritivos
git commit -m "Add password reset feature"
git commit -m "Fix email validation bug"
git commit -m "Update dashboard UI"

# Branches por feature
git checkout -b feature/nova-app
git checkout -b fix/email-bug
```

---

## 🔥 Comandos Úteis

### **Desenvolvimento:**
```bash
# Iniciar servidor
python app.py

# Criar base de dados
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()

# Instalar dependências
pip install -r requirements.txt --break-system-packages

# Ver logs
# Os logs aparecem no terminal onde corre o servidor
```

### **Git:**
```bash
# Status
git status

# Adicionar tudo
git add .

# Commit
git commit -m "Mensagem"

# Push
git push origin main

# Ver histórico
git log --oneline

# Criar tag
git tag -a v1.1 -m "Descrição"
git push origin main --tags
```

### **Base de Dados:**
```bash
# Backup SQLite
copy instance\myxapp.db instance\myxapp_backup.db

# Reset completo (CUIDADO!)
del instance\myxapp.db
python app.py  # Cria BD nova
```

---

## 🐛 Troubleshooting

### **Erro: "User não encontrado" após criar BD nova**
**Solução:**
```bash
1. Vai ao browser → Limpar cookies do localhost:5000
2. Ou acede /logout
3. Faz login novamente com admin@myxapp.com / admin123
```

### **Erro: "App não encontrada"**
**Solução:** Verifica se adicionaste a app à BD (Passo 5)

### **Erro: "Sem permissão"**
**Solução:** 
1. Login como admin
2. `/admin/users`
3. Dar permissão ao utilizador

### **Imports não funcionam**
**Solução:**
```python
# Em routes.py, usa imports relativos
from models import db  # ✅ Correto
# ou
from ..models import db  # ✅ Também correto
```

### **CSS/JS não carrega**
**Solução:**
1. Ficheiros em `static/css/` e `static/js/`
2. No HTML: `<link href="{{ url_for('static', filename='css/style.css') }}">`
3. Hard refresh: CTRL + F5

---

## 📦 Estrutura de uma App Completa
```
apps/
  minha_app/
    __init__.py           # Vazio ou com __all__
    routes.py             # Rotas Flask
    logic.py              # Lógica de negócio (opcional)
    models.py             # Modelos específicos (opcional)
    utils.py              # Funções auxiliares (opcional)

templates/
  apps/
    minha_app.html        # Template principal
    minha_app_*.html      # Outros templates

static/
  css/
    minha_app.css         # CSS específico (opcional)
  js/
    minha_app.js          # JS específico (opcional)
```

---

## 🚀 Deploy em Produção (Futuro)

### **Opção 1: Render.com** (Recomendado - Grátis)
1. Criar `render.yaml`
2. Mudar SQLite → PostgreSQL
3. Push para GitHub
4. Deploy automático

### **Opção 2: Heroku**
1. Criar `Procfile`
2. Adicionar PostgreSQL addon
3. `git push heroku main`

### **Opção 3: VPS (DigitalOcean, etc.)**
1. Ubuntu Server
2. Nginx + Gunicorn
3. PostgreSQL
4. SSL com Let's Encrypt

---

## 📚 Recursos Úteis

### **Documentação:**
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Bootstrap: https://getbootstrap.com/
- Jinja2: https://jinja.palletsprojects.com/

### **Este Projeto:**
- GitHub: https://github.com/myxtools/myxapp
- Versão: v1.0

---

## 💡 Dicas de Boas Práticas

### **Segurança:**
```python
# ✅ SEMPRE usar @app_permission_required em rotas protegidas
# ✅ SEMPRE usar db.session.get() em vez de Query.get()
# ✅ NUNCA commitar instance/myxapp.db
# ✅ NUNCA commitar senhas/secrets no código
```

### **Performance:**
```python
# ✅ Usar pagination em listas grandes
# ✅ Adicionar índices na BD se necessário
# ✅ Fazer queries eficientes (evitar N+1)
```

### **UX:**
```python
# ✅ SEMPRE dar feedback ao utilizador (flash messages)
# ✅ Loading spinners em operações demoradas
# ✅ Validação no frontend E backend
```

---

## 🎯 Roadmap Futuro

- [ ] Sistema de afiliados completo
- [ ] Subscriptions/Pagamentos (Stripe)
- [ ] 2FA (Two-Factor Authentication)
- [ ] Recuperação de password por email
- [ ] Rate limiting
- [ ] Logs de atividade
- [ ] API pública com tokens
- [ ] Testes automatizados
- [ ] CI/CD pipeline

---

## 📞 Suporte

Para questões sobre o MyXAPP:
1. Consulta este GUIDE.md
2. Verifica issues no GitHub
3. Cria nova issue no repositório

---

**Última atualização:** 28 Novembro 2025  
**Versão:** 1.0  
**Autor:** MyXTools Team