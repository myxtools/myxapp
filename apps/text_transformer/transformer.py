# -*- coding: utf-8 -*-
"""
Text Transformer - Lógica de transformação de texto
Todas as funcionalidades de manipulação e análise de texto
"""
import re
import unicodedata
from datetime import datetime

class TextTransformer:
    """Classe principal para transformações de texto"""
    
    @staticmethod
    def to_uppercase(text):
        """Converter para MAIÚSCULAS"""
        return text.upper()
    
    @staticmethod
    def to_lowercase(text):
        """Converter para minúsculas"""
        return text.lower()
    
    @staticmethod
    def to_capitalize(text):
        """Primeira letra maiúscula"""
        return text.capitalize()
    
    @staticmethod
    def to_title_case(text):
        """Primeira Letra De Cada Palavra Maiúscula"""
        return text.title()
    
    @staticmethod
    def to_alternating_case(text):
        """aLtErNaR eNtRe MaIúScUlAs E mInÚsCuLaS"""
        result = []
        uppercase = True
        for char in text:
            if char.isalpha():
                result.append(char.upper() if uppercase else char.lower())
                uppercase = not uppercase
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def to_reverse(text):
        """Inverter texto"""
        return text[::-1]
    
    @staticmethod
    def to_snake_case(text):
        """Converter para snake_case"""
        # Remover acentos
        text = TextTransformer.remove_accents(text)
        # Substituir espaços e caracteres especiais por underscore
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', '_', text.strip())
        return text.lower()
    
    @staticmethod
    def to_kebab_case(text):
        """Converter para kebab-case"""
        # Remover acentos
        text = TextTransformer.remove_accents(text)
        # Substituir espaços e caracteres especiais por hífen
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', '-', text.strip())
        return text.lower()
    
    @staticmethod
    def to_camel_case(text):
        """Converter para camelCase"""
        # Remover acentos
        text = TextTransformer.remove_accents(text)
        # Remover caracteres especiais
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        if not words:
            return ''
        # Primeira palavra minúscula, resto com primeira letra maiúscula
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    @staticmethod
    def to_pascal_case(text):
        """Converter para PascalCase"""
        # Remover acentos
        text = TextTransformer.remove_accents(text)
        # Remover caracteres especiais
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        return ''.join(word.capitalize() for word in words)
    
    @staticmethod
    def remove_accents(text):
        """Remover todos os acentos do texto"""
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    @staticmethod
    def remove_extra_spaces(text):
        """Remover espaços extras"""
        # Substituir múltiplos espaços por um único
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def remove_duplicate_lines(text):
        """Remover linhas duplicadas"""
        lines = text.split('\n')
        seen = set()
        result = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                result.append(line)
        return '\n'.join(result)
    
    @staticmethod
    def sort_lines_asc(text):
        """Ordenar linhas A-Z"""
        lines = text.split('\n')
        return '\n'.join(sorted(lines))
    
    @staticmethod
    def sort_lines_desc(text):
        """Ordenar linhas Z-A"""
        lines = text.split('\n')
        return '\n'.join(sorted(lines, reverse=True))
    
    @staticmethod
    def add_line_numbers(text):
        """Adicionar números às linhas"""
        lines = text.split('\n')
        return '\n'.join(f"{i+1}. {line}" for i, line in enumerate(lines))
    
    @staticmethod
    def add_prefix(text, prefix):
        """Adicionar prefixo a cada linha"""
        lines = text.split('\n')
        return '\n'.join(f"{prefix}{line}" for line in lines)
    
    @staticmethod
    def add_suffix(text, suffix):
        """Adicionar sufixo a cada linha"""
        lines = text.split('\n')
        return '\n'.join(f"{line}{suffix}" for line in lines)
    
    @staticmethod
    def extract_emails(text):
        """Extrair emails do texto"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return '\n'.join(emails) if emails else 'Nenhum email encontrado'
    
    @staticmethod
    def extract_urls(text):
        """Extrair URLs do texto"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return '\n'.join(urls) if urls else 'Nenhuma URL encontrada'
    
    @staticmethod
    def count_stats(text):
        """Contar estatísticas do texto"""
        # Caracteres
        char_count = len(text)
        char_no_spaces = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
        
        # Palavras
        words = text.split()
        word_count = len(words)
        
        # Linhas
        lines = text.split('\n')
        line_count = len(lines)
        
        # Frases (aproximado - termina com . ! ?)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Tempo de leitura (média de 200 palavras por minuto)
        reading_time = round(word_count / 200, 1) if word_count > 0 else 0
        
        return {
            'characters': char_count,
            'characters_no_spaces': char_no_spaces,
            'words': word_count,
            'lines': line_count,
            'sentences': sentence_count,
            'reading_time': reading_time
        }
    
    @staticmethod
    def get_all_transformations():
        """Retorna todas as transformações disponíveis"""
        return {
            'uppercase': {
                'name': 'MAIÚSCULAS',
                'description': 'Converter todo o texto para MAIÚSCULAS',
                'example': 'olá mundo → OLÁ MUNDO',
                'category': 'Básico'
            },
            'lowercase': {
                'name': 'minúsculas',
                'description': 'Converter todo o texto para minúsculas',
                'example': 'OLÁ MUNDO → olá mundo',
                'category': 'Básico'
            },
            'capitalize': {
                'name': 'Capitalizar',
                'description': 'Primeira letra maiúscula, resto minúsculas',
                'example': 'olá mundo → Olá mundo',
                'category': 'Básico'
            },
            'title_case': {
                'name': 'Title Case',
                'description': 'Primeira Letra De Cada Palavra Maiúscula',
                'example': 'olá mundo bonito → Olá Mundo Bonito',
                'category': 'Básico'
            },
            'alternating_case': {
                'name': 'Alternado',
                'description': 'aLtErNaR eNtRe MaIúScUlAs E mInÚsCuLaS',
                'example': 'olá mundo → OlÁ mUnDo',
                'category': 'Avançado'
            },
            'reverse': {
                'name': 'Inverter',
                'description': 'Escrever o texto ao contrário',
                'example': 'olá mundo → odnum álO',
                'category': 'Avançado'
            },
            'snake_case': {
                'name': 'snake_case',
                'description': 'Converter para snake_case (programação)',
                'example': 'Olá Mundo Bonito → ola_mundo_bonito',
                'category': 'Programação'
            },
            'kebab_case': {
                'name': 'kebab-case',
                'description': 'Converter para kebab-case (URLs)',
                'example': 'Olá Mundo Bonito → ola-mundo-bonito',
                'category': 'Programação'
            },
            'camel_case': {
                'name': 'camelCase',
                'description': 'Converter para camelCase (JavaScript)',
                'example': 'Olá Mundo Bonito → olaMundoBonito',
                'category': 'Programação'
            },
            'pascal_case': {
                'name': 'PascalCase',
                'description': 'Converter para PascalCase (Classes)',
                'example': 'Olá Mundo Bonito → OlaMundoBonito',
                'category': 'Programação'
            },
            'remove_accents': {
                'name': 'Remover Acentos',
                'description': 'Remover todos os acentos do texto',
                'example': 'Olá José → Ola Jose',
                'category': 'Utilidades'
            },
            'remove_extra_spaces': {
                'name': 'Remover Espaços Extras',
                'description': 'Remover espaços duplicados',
                'example': 'olá    mundo → olá mundo',
                'category': 'Utilidades'
            },
            'remove_duplicate_lines': {
                'name': 'Remover Linhas Duplicadas',
                'description': 'Remover linhas repetidas',
                'example': 'linha1\\nlinha1\\nlinha2 → linha1\\nlinha2',
                'category': 'Utilidades'
            },
            'sort_lines_asc': {
                'name': 'Ordenar Linhas (A-Z)',
                'description': 'Ordenar linhas alfabeticamente',
                'example': 'c\\nb\\na → a\\nb\\nc',
                'category': 'Utilidades'
            },
            'sort_lines_desc': {
                'name': 'Ordenar Linhas (Z-A)',
                'description': 'Ordenar linhas inversamente',
                'example': 'a\\nb\\nc → c\\nb\\na',
                'category': 'Utilidades'
            },
            'add_line_numbers': {
                'name': 'Numerar Linhas',
                'description': 'Adicionar números a cada linha',
                'example': 'linha → 1. linha',
                'category': 'Utilidades'
            },
            'extract_emails': {
                'name': 'Extrair Emails',
                'description': 'Extrair todos os emails do texto',
                'example': 'Contacte joao@email.com → joao@email.com',
                'category': 'Extração'
            },
            'extract_urls': {
                'name': 'Extrair URLs',
                'description': 'Extrair todos os links do texto',
                'example': 'Visite https://site.com → https://site.com',
                'category': 'Extração'
            }
        }