# 📝 Text Transformer - Guia de Instalação

## 🎯 O que foi criado?

Uma aplicação completa de transformação e análise de texto com:
- ✅ **Versão Pública** (Frontend) - Com limitações
- ✅ **Versão Premium** (Área Reservada) - Sem limitações
- ✅ **18 Ferramentas de Transformação**
- ✅ **Histórico de Transformações**
- ✅ **Export TXT e JSON**
- ✅ **Design Moderno e Responsivo**

---

## 📦 Ficheiros Criados

```
D:\Software\myxapp\
├── apps/
│   └── text_transformer/
│       ├── __init__.py          ✅ NOVO
│       ├── routes.py            ✅ NOVO
│       └── transformer.py       ✅ NOVO
│
├── templates/
│   ├── text_transformer_public.html     ✅ NOVO (Frontend público)
│   └── apps/
│       └── text_transformer.html        ✅ NOVO (Área reservada)
│
├── models.py                    ✅ ATUALIZADO (novo modelo)
└── app.py                       ✅ ATUALIZADO (blueprint registado)
```

---

## 🚀 Instalação Passo a Passo

### **Passo 1: Substituir Ficheiros**

1. **Substituir `models.py`:**
   ```bash
   # Backup do original
   copy D:\Software\myxapp\models.py D:\Software\myxapp\models_backup.py
   
   # Copiar novo models.py (o que te enviei)
   copy models.py D:\Software\myxapp\models.py
   ```

2. **Substituir `app.py`:**
   ```bash
   # Backup do original
   copy D:\Software\myxapp\app.py D:\Software\myxapp\app_backup.py
   
   # Copiar novo app.py (o que te enviei)
   copy app.py D:\Software\myxapp\app.py
   ```

### **Passo 2: Criar Estrutura de Pastas**

```bash
cd D:\Software\myxapp\apps
mkdir text_transformer
cd text_transformer
```

### **Passo 3: Adicionar Ficheiros da App**

Copiar os 3 ficheiros para `apps/text_transformer/`:
- `__init__.py`
- `routes.py`
- `transformer.py`

### **Passo 4: Adicionar Templates**

1. **Template Público:**
   ```bash
   # Copiar para D:\Software\myxapp\templates\
   text_transformer_public.html
   ```

2. **Template Área Reservada:**
   ```bash
   # Copiar para D:\Software\myxapp\templates\apps\
   text_transformer.html
   ```

### **Passo 5: Atualizar Base de Dados**

```bash
cd D:\Software\myxapp
python
```

```python
from app import app, db
from models import TextTransformation

# Criar nova tabela
with app.app_context():
    db.create_all()
    print("✅ Tabela text_transformations criada!")
exit()
```

### **Passo 6: Iniciar Servidor**

```bash
python app.py
```

Deverás ver:
```
✅ Email Validator app registada!
✅ Text Transformer app registada!
✅ Admin criado: admin@myxapp.com / admin123
🚀 MyXAPP a correr em http://localhost:5000
```

---

## 🔗 URLs de Acesso

### **Frontend Público (Sem Login):**
```
http://localhost:5000/apps/text-transformer/public
```

**Características:**
- ❌ Limite de 500 caracteres
- ❌ Máximo 10 transformações por hora
- ❌ Apenas 4 transformações básicas
- ❌ Com watermark nos resultados

### **Área Reservada (Com Login):**
```
http://localhost:5000/apps/text-transformer
```

**Características:**
- ✅ Limite de 50.000 caracteres
- ✅ Transformações ilimitadas
- ✅ Todas as 18 ferramentas
- ✅ Histórico completo
- ✅ Export TXT/JSON
- ✅ Sem watermark

---

## 🛠️ Funcionalidades Disponíveis

### **Transformações Básicas (4):**
1. **MAIÚSCULAS** - Converter todo o texto
2. **minúsculas** - Converter todo o texto
3. **Capitalizar** - Primeira letra maiúscula
4. **Title Case** - Primeira Letra De Cada Palavra

### **Transformações Avançadas (2):**
5. **Alternado** - aLtErNaR MaIúScUlAs/MiNúScUlAs
6. **Inverter** - Escrever ao contrário

### **Programação (4):**
7. **snake_case** - para_programacao_python
8. **kebab-case** - para-urls-e-css
9. **camelCase** - paraProgramacaoJavaScript
10. **PascalCase** - ParaClassesEmProgramacao

### **Utilidades (6):**
11. **Remover Acentos** - José → Jose
12. **Remover Espaços Extras** - Limpar formatação
13. **Remover Linhas Duplicadas** - Eliminar repetições
14. **Ordenar Linhas (A-Z)** - Ordem alfabética
15. **Ordenar Linhas (Z-A)** - Ordem inversa
16. **Numerar Linhas** - Adicionar números

### **Extração (2):**
17. **Extrair Emails** - Encontrar emails no texto
18. **Extrair URLs** - Encontrar links no texto

---

## 📊 Estatísticas em Tempo Real

Ambas as versões mostram:
- 📝 Contagem de caracteres
- 📝 Contagem de caracteres sem espaços
- 📝 Contagem de palavras
- 📝 Contagem de linhas
- 📝 Contagem de frases
- ⏱️ Tempo estimado de leitura

---

## 🔒 Sistema de Limitações

### **Frontend Público:**
```python
PUBLIC_CHAR_LIMIT = 500
PUBLIC_TRANSFORMATIONS_PER_HOUR = 10
```

- Limite resetado a cada hora automaticamente
- Contador visível para o utilizador
- Mensagens incentivando registo

### **Área Reservada:**
```python
LOGGED_CHAR_LIMIT = 50000
TRANSFORMATIONS = ILIMITADAS
```

- Sem restrições de tempo
- Todas as funcionalidades ativas
- Histórico permanente

---

## 💾 Histórico de Transformações

**Apenas para utilizadores registados:**

Cada transformação guarda:
- Tipo de transformação
- Texto original (primeiros 1000 chars)
- Texto resultado (primeiros 1000 chars)
- Número de caracteres
- Data e hora

**Ver histórico:**
```
http://localhost:5000/apps/text-transformer/history
```

---

## 📤 Export de Resultados

**Formatos disponíveis (apenas área reservada):**

### **TXT:**
```
texto_transformado.txt
```

### **JSON:**
```json
{
  "text": "resultado...",
  "stats": {
    "characters": 150,
    "words": 25,
    "lines": 5,
    ...
  },
  "exported_at": "2025-11-29T12:30:00"
}
```

---

## 🎨 Design e UX

### **Frontend Público:**
- 🎨 Gradiente roxo vibrante
- 🌟 Cards com sombras
- 📱 Totalmente responsivo
- ⚡ Contadores em tempo real
- 💡 CTAs para registo

### **Área Reservada:**
- 🎨 Design clean e profissional
- 👑 Badge "PREMIUM"
- 📊 Grid de estatísticas
- 📜 Sidebar com histórico
- 💾 Botões de export

---

## 🧪 Testar a Instalação

### **1. Testar Frontend Público:**

1. Abrir: `http://localhost:5000/apps/text-transformer/public`
2. Colar texto (máx. 500 chars)
3. Escolher "MAIÚSCULAS"
4. Clicar "Transformar"
5. Verificar watermark no resultado
6. Tentar 10 transformações → Ver limite

### **2. Testar Área Reservada:**

1. Login como admin: `admin@myxapp.com / admin123`
2. Aceder: `http://localhost:5000/apps/text-transformer`
3. Colar texto longo (testar até 50k chars)
4. Testar todas as transformações
5. Verificar estatísticas em tempo real
6. Exportar TXT e JSON
7. Ver histórico

---

## ⚙️ Configuração Avançada

### **Alterar Limites:**

Em `apps/text_transformer/routes.py`:

```python
# Linha 11-13
PUBLIC_CHAR_LIMIT = 500          # Mudar para outro valor
PUBLIC_TRANSFORMATIONS_PER_HOUR = 10
LOGGED_CHAR_LIMIT = 50000
```

### **Adicionar Transformações:**

1. **Criar função em `transformer.py`:**
```python
@staticmethod
def minha_transformacao(text):
    """Descrição"""
    # Lógica aqui
    return resultado
```

2. **Adicionar ao dicionário:**
```python
'minha_key': {
    'name': 'Meu Nome',
    'description': 'O que faz',
    'example': 'antes → depois',
    'category': 'Categoria'
}
```

3. **Mapear em `routes.py`:**
```python
transformations_map = {
    'minha_key': transformer.minha_transformacao,
    ...
}
```

---

## 🐛 Troubleshooting

### **Erro: "No module named 'apps.text_transformer'"**
```bash
# Verificar estrutura de pastas
dir D:\Software\myxapp\apps\text_transformer
# Deve mostrar: __init__.py, routes.py, transformer.py
```

### **Erro: "text_transformations table doesn't exist"**
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

### **Erro 404 na rota pública**
```bash
# Verificar se blueprint está registado em app.py
grep "text_transformer_bp" app.py
# Deve aparecer: from apps.text_transformer.routes import text_transformer_bp
```

### **Sessão não guarda contador**
```bash
# Verificar SECRET_KEY em config.py
# Limpar cookies do browser
```

---

## 📈 Próximos Passos (Opcional)

### **Funcionalidades Futuras:**

1. **Processar Ficheiros:**
   - Upload de .txt
   - Transformar ficheiros completos

2. **Batch Processing:**
   - Múltiplas transformações sequenciais
   - Pipelines de transformação

3. **Partilha:**
   - Gerar links partilháveis
   - Copiar transformação via URL

4. **API Pública:**
   - Endpoints REST
   - Autenticação por token

---

## 📞 Suporte

**Testaste e funciona?**
- ✅ Frontend público acessível
- ✅ Área reservada acessível
- ✅ Transformações funcionam
- ✅ Histórico a gravar
- ✅ Export funciona

**Encontraste problemas?**
- Verifica logs no terminal
- Consulta este guia
- Envia screenshots dos erros

---

## 🎉 Conclusão

Criámos uma aplicação **completa** e **profissional** de transformação de texto!

**Destaques:**
- 💪 Robusta e escalável
- 🎨 Design moderno
- 📱 Responsiva
- 🔒 Sistema de limitações inteligente
- 💾 Histórico persistente
- 📤 Export múltiplos formatos

**Testa agora e qualquer dúvida, avisa!** 🚀

---

**Última atualização:** 29 Novembro 2025  
**Versão:** Text Transformer v1.0