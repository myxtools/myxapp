import re
import dns.resolver
from datetime import datetime

# Lista de domínios temporários/descartáveis
DISPOSABLE_DOMAINS = [
    'tempmail.com', 'guerrillamail.com', '10minutemail.com', 'throwaway.email',
    'mailinator.com', 'trashmail.com', 'temp-mail.org', 'fakeinbox.com',
    'maildrop.cc', 'yopmail.com', 'getnada.com', 'mohmal.com', 'sharklasers.com'
]

def validate_email(email, check_mx=True):
    """
    Valida um email - CÓDIGO EXATO DO ORIGINAL
    
    Returns:
        tuple: (is_valid, reason)
    """
    email = email.strip().lower()
    
    # 1. Validar formato básico
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, 'Formato inválido'
    
    # 2. Extrair domínio
    try:
        domain = email.split('@')[1]
    except IndexError:
        return False, 'Formato inválido'
    
    # 3. Verificar caracteres inválidos
    if '..' in email:
        return False, 'Uso de acentos inválido'
    
    local = email.split('@')[0]
    if local.startswith('.') or local.endswith('.'):
        return False, 'Formato de local inválido'
    
    # 4. Verificar se é email descartável
    if domain in DISPOSABLE_DOMAINS:
        return False, 'Email descartável/temporário'
    
    # 5. Verificar MX records (se solicitado)
    if check_mx:
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return False, 'Sem registos MX'
            return True, '—'
        except dns.resolver.NXDOMAIN:
            return False, 'Domínio não existe'
        except dns.resolver.NoAnswer:
            return False, 'Domínio válido mas não registado'
        except dns.resolver.Timeout:
            return False, 'Timeout ao verificar DNS'
        except Exception as e:
            return False, f'Erro ao verificar DNS: {str(e)}'
    
    return True, '—'