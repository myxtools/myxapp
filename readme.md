# MyXAPP

Sistema modular de aplicações com autenticação centralizada e gestão de permissões.

## 🚀 Funcionalidades

- ✅ Sistema de autenticação completo (registo, login, logout)
- ✅ Painel de administração com gestão de utilizadores
- ✅ Sistema de permissões por aplicação
- ✅ Apps modulares independentes
- ✅ Email Validator integrado
- ✅ Base de dados preparada para sistema de afiliados
- ✅ Interface responsiva com Bootstrap 5

## 📦 Instalação

### Requisitos
- Python 3.8+
- pip

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/myxtools/myxapp.git
cd myxapp
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python app.py
```

4. Aceda no browser:
```
http://localhost:5000
```

## 🔐 Credenciais de Teste

**Admin:**
- Email: `admin@myxapp.com`
- Password: `admin123`

## 📁 Estrutura do Projeto
```
myxapp/
├── app.py                 # Aplicação principal
├── config.py             # Configurações
├── models.py             # Modelos da base de dados
├── requirements.txt      # Dependências
├── core/                 # Sistema central
│   ├── auth.py          # Autenticação
│   └── admin.py         # Painel admin
├── apps/                # Apps modulares
│   └── email_validator/
├── templates/           # Templates HTML
└── static/             # CSS, JS, imagens
```

## 🎯 Como Adicionar Nova App

1. Crie pasta em `apps/nome_app/`
2. Crie `routes.py` com as rotas
3. Registe no `app.py`
4. Adicione à base de dados (tabela `apps`)
5. Configure permissões no painel admin

## 🚀 Deploy

### Render.com (Recomendado)

1. Faça push do código para o GitHub
2. Crie conta no Render.com
3. Conecte o repositório
4. Configure PostgreSQL
5. Defina variáveis de ambiente

## 📝 Licença

MIT License

## 👨‍💻 Autor

MyXTools - 2024
```

---

### **1️⃣7️⃣ Criar `.gitignore`**

**Caminho:** `D:\Software\myxapp\.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local