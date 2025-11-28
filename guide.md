# MyXAPP - Guia de Desenvolvimento

## Estrutura do Projeto
- `app.py` - Aplicação principal Flask
- `models.py` - Modelos de BD (User, App, Permission, etc.)
- `apps/` - Apps modulares
- `templates/` - Templates HTML

## Como Criar Nova App

### Passo 1: Criar Estrutura
```
apps/
  nova_app/
    __init__.py
    routes.py
```

### Passo 2: routes.py Template
```python
from flask import Blueprint, render_template
from functools import wraps

nova_app_bp = Blueprint('nova_app', __name__)

@nova_app_bp.route('/')
def index():
    return render_template('apps/nova_app.html')
```

### Passo 3: Registar em app.py
```python
from apps.nova_app.routes import nova_app_bp
app.register_blueprint(nova_app_bp, url_prefix='/apps/nova-app')
```

### Passo 4: Adicionar à BD
```python
app = App(name='Nova App', route='/apps/nova-app')
db.session.add(app)
```

## Stack Tecnológica
- Python 3.11
- Flask 3.0.0
- SQLAlchemy
- Bootstrap 5
- SQLite (dev) / PostgreSQL (prod)

## Convenções
- UTF-8 encoding: `# -*- coding: utf-8 -*-`
- Decorador de permissões: `@app_permission_required`
- Templates extendem `base.html`