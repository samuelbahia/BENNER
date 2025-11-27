#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser de Dicionário de Dados - Benner Legal
Extrai tabelas, campos, tipos e relacionamentos do arquivo de texto
e gera um JSON estruturado.

Autor: Gerado automaticamente
Versão: 1.0.0
"""

import re
import json
import os
from collections import defaultdict
from datetime import datetime

# Caminho padrão do arquivo de entrada (relativo ao diretório do script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT_FILE = os.path.join(SCRIPT_DIR, "..", "Dicionario de Dados.txt")
DEFAULT_OUTPUT_FILE = os.path.join(SCRIPT_DIR, "datadict.json")

# Padrões regex para extração
TABLE_PATTERN = r'^([A-Z][A-Z0-9_]+):\s*(.*)$'
FIELD_PATTERN = r'([A-Z][A-Z0-9_]+)\s*(Integer|Number|Varchar\s*\(\s*\d+\s*\)|Char\s*\(\s*\d+\s*\)|Data|Blob|Arquivos?|S?)\s*([NS]?)\s*(.*?)(?=[A-Z][A-Z0-9_]+(?:Integer|Number|Varchar|Char|Data|Blob|Arquivos?)|$)'

# Tipos de dados conhecidos
DATA_TYPES = ['Integer', 'Number', 'Varchar', 'Char', 'Data', 'Blob', 'Arquivo', 'Arquivos']

# Prefixos de módulos conhecidos
MODULE_PREFIXES = {
    'ADM_': 'Administração',
    'ADMW_': 'Administração Web',
    'AE_': 'Avaliação de Escritórios',
    'AG_': 'Agenda',
    'AU_': 'Autenticação',
    'AV_': 'Avaliação',
    'BI_': 'Business Intelligence',
    'BL_': 'Biblioteca',
    'CA_': 'Cálculo Trabalhista',
    'CB_': 'Conciliação Bancária',
    'CR_': 'Circularização',
    'CS_': 'Consultivo Smart',
    'CT_': 'Contabilidade',
    'EJ_': 'Escritórios Jurídicos',
    'ES_': 'eSocial',
    'EX_': 'Extrajudicial',
    'FI_': 'Financeiro Integrado',
    'FN_': 'Financeiro',
    'GE_': 'Gestão de Documentos',
    'GI_': 'Gestão de Informações',
    'GN_': 'Geral',
    'GR_': 'Gestão de Risco',
    'IN_': 'Integração',
    'K9_': 'K9',
    'MS_': 'Mensageria',
    'PD_': 'Pedidos',
    'PR_': 'Processos',
    'PT_': 'Portal',
    'RP_': 'Relatórios',
    'SO_': 'Sociedades',
    'TR_': 'Trabalhista',
    'WK_': 'Workflow',
    'Z_': 'Sistema',
    'BAIRROS': 'Localização',
    'ESTADOS': 'Localização',
    'MUNICIPIOS': 'Localização',
    'PAISES': 'Localização',
    'FILIAIS': 'Empresas',
    'EMPRESAS': 'Empresas'
}


def detect_encoding(file_path):
    """Detecta a codificação do arquivo."""
    encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1000)
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return 'utf-8'


def get_module(table_name):
    """Determina o módulo de uma tabela baseado no prefixo."""
    for prefix, module in MODULE_PREFIXES.items():
        if table_name.startswith(prefix):
            return module
    # Tenta identificar por nome completo
    if table_name in MODULE_PREFIXES:
        return MODULE_PREFIXES[table_name]
    # Extrai prefixo se tiver underscore
    if '_' in table_name:
        prefix = table_name.split('_')[0] + '_'
        return prefix[:-1]  # Remove o underscore
    return 'Outros'


def parse_type(type_str):
    """Normaliza o tipo de dado."""
    if not type_str:
        return 'Unknown'
    
    type_str = type_str.strip()
    
    # Extrai tamanho se existir
    size_match = re.search(r'\((\d+)\)', type_str)
    size = int(size_match.group(1)) if size_match else None
    
    # Normaliza o tipo
    type_lower = type_str.lower()
    if 'varchar' in type_lower:
        return f'Varchar({size})' if size else 'Varchar'
    elif 'char' in type_lower:
        return f'Char({size})' if size else 'Char(1)'
    elif 'integer' in type_lower:
        return 'Integer'
    elif 'number' in type_lower:
        return 'Number'
    elif 'data' in type_lower:
        return 'Data'
    elif 'blob' in type_lower:
        return 'Blob'
    elif 'arquivo' in type_lower:
        return 'Arquivo'
    
    return type_str if type_str else 'Unknown'


def parse_nullable(nullable_str):
    """Determina se o campo permite nulos."""
    if not nullable_str:
        return True
    return nullable_str.strip().upper() == 'S'


def extract_table_reference(description):
    """Extrai referência para outra tabela da descrição."""
    if not description:
        return None
    
    # Padrões comuns de referência
    patterns = [
        r'([A-Z][A-Z0-9_]+)$',  # Nome da tabela no final
        r'->([A-Z][A-Z0-9_]+)',  # Após seta
    ]
    
    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            table_ref = match.group(1)
            # Verifica se parece ser uma tabela válida
            if len(table_ref) >= 3 and table_ref.isupper():
                return table_ref
    return None


def parse_datadict(file_path):
    """
    Faz o parse do arquivo de dicionário de dados.
    
    Args:
        file_path: Caminho para o arquivo de entrada
        
    Returns:
        dict: Estrutura de dados com tabelas, campos e metadados
    """
    encoding = detect_encoding(file_path)
    print(f"Detectada codificação: {encoding}")
    
    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
        content = f.read()
    
    # Remove linhas vazias excessivas e normaliza
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r'ESTRUTURA DAS TABELAS', '', content)
    
    tables = {}
    relationships = []
    current_table = None
    current_description = ""
    
    # Regex melhorado para encontrar tabelas
    # Formato: NOME_TABELA:  Descrição...NOMETIPONULLDESCRIÇÃOTABELA...campos...
    table_regex = re.compile(r'([A-Z][A-Z0-9_]+):\s+([^\n]*?)(?=NOME\s*TIPO|$)', re.MULTILINE)
    
    # Processa o conteúdo linha por linha
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Verifica se é uma definição de tabela (termina com :)
        table_match = re.match(r'^([A-Z][A-Z0-9_]+):\s*(.*)', line)
        
        if table_match:
            table_name = table_match.group(1)
            remaining = table_match.group(2)
            
            # Pega a descrição (texto antes do padrão NOME)
            desc_match = re.match(r'^(.*?)(?:NOME\s*TIPO|NOME\t|$)', remaining)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Limpa a descrição
            description = re.sub(r'[NS]$', '', description).strip()
            description = re.sub(r'(?:Integer|Number|Varchar|Char|Data|Blob).*$', '', description).strip()
            
            # Cria entrada da tabela
            tables[table_name] = {
                'name': table_name,
                'description': description,
                'module': get_module(table_name),
                'fields': [],
                'field_count': 0,
                'relationships': []
            }
            current_table = table_name
            
            # Processa campos na mesma linha
            field_content = remaining
            
            # Adiciona linhas subsequentes até encontrar nova tabela
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if re.match(r'^[A-Z][A-Z0-9_]+:\s+', next_line):
                    break
                field_content += next_line
                j += 1
            
            # Extrai campos
            fields = extract_fields(field_content, table_name)
            tables[table_name]['fields'] = fields
            tables[table_name]['field_count'] = len(fields)
            
            # Extrai relacionamentos
            for field in fields:
                if field.get('references'):
                    rel = {
                        'from_table': table_name,
                        'from_field': field['name'],
                        'to_table': field['references'],
                        'type': 'foreign_key'
                    }
                    relationships.append(rel)
                    tables[table_name]['relationships'].append(field['references'])
            
            i = j - 1
        
        i += 1
    
    # Gera metadados
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'source_file': os.path.basename(file_path),
        'total_tables': len(tables),
        'total_fields': sum(t['field_count'] for t in tables.values()),
        'total_relationships': len(relationships),
        'modules': list(set(t['module'] for t in tables.values()))
    }
    
    # Estatísticas por módulo
    module_stats = defaultdict(lambda: {'tables': 0, 'fields': 0})
    for table in tables.values():
        module_stats[table['module']]['tables'] += 1
        module_stats[table['module']]['fields'] += table['field_count']
    
    return {
        'metadata': metadata,
        'module_stats': dict(module_stats),
        'tables': tables,
        'relationships': relationships
    }


def extract_fields(content, table_name):
    """
    Extrai campos de uma string de conteúdo.
    
    Args:
        content: String com definição dos campos
        table_name: Nome da tabela (para referência)
        
    Returns:
        list: Lista de campos
    """
    fields = []
    
    # Remove o cabeçalho NOME TIPO NULL DESCRIÇÃO TABELA se existir
    content = re.sub(r'NOME\s*TIPO\s*NULL\s*DESCRI[CÇ][AÃ]O\s*TABELA\s*', '', content, flags=re.IGNORECASE)
    
    # Padrão para capturar campos
    # Formato típico: CAMPO_NOME Integer/Number/Varchar(N)/Data/Blob N/S Descrição TABELA_REFERENCIA
    
    # Tipos de dados possíveis
    type_pattern = r'(?:Integer|Number|Varchar\s*\(\s*\d+\s*\)|Char\s*\(\s*\d+\s*\)|Data|Blob|Arquivos?)'
    
    # Padrão mais flexível
    field_regex = re.compile(
        r'([A-Z][A-Z0-9_]+)\s*'  # Nome do campo
        r'(' + type_pattern + r')?\s*'  # Tipo (opcional)
        r'([NS])?\s*'  # Nullable (opcional)
        r'([^A-Z]*?)(?=[A-Z][A-Z0-9_]+\s*(?:' + type_pattern + r'|[NS])|$)',  # Descrição
        re.IGNORECASE
    )
    
    # Tenta extrair usando regex
    matches = list(field_regex.finditer(content))
    
    # Se não encontrou matches, tenta abordagem mais simples
    if not matches:
        # Tenta split por tipos conhecidos
        parts = re.split(r'(Integer|Number|Varchar\s*\(\s*\d+\s*\)|Char\s*\(\s*\d+\s*\)|Data|Blob)', content)
        
        i = 0
        while i < len(parts) - 1:
            # Procura nome do campo antes do tipo
            name_match = re.search(r'([A-Z][A-Z0-9_]+)\s*$', parts[i])
            if name_match and i + 1 < len(parts):
                field_name = name_match.group(1)
                field_type = parts[i + 1] if i + 1 < len(parts) else 'Unknown'
                
                # Procura nullable e descrição
                desc_part = parts[i + 2] if i + 2 < len(parts) else ''
                nullable_match = re.match(r'^\s*([NS])\s*(.*)', desc_part)
                
                nullable = True
                description = ''
                references = None
                
                if nullable_match:
                    nullable = nullable_match.group(1) == 'S'
                    desc_text = nullable_match.group(2)
                    # Extrai descrição e possível referência
                    ref_match = re.match(r'^(.*?)([A-Z][A-Z0-9_]+)\s*$', desc_text)
                    if ref_match:
                        description = ref_match.group(1).strip()
                        potential_ref = ref_match.group(2)
                        # Verifica se parece uma tabela
                        if len(potential_ref) >= 3 and potential_ref != field_name:
                            references = potential_ref
                    else:
                        description = desc_text.strip()
                
                # Evita duplicatas
                if field_name not in ['NOME', 'TIPO', 'NULL', 'TABELA'] and not any(f['name'] == field_name for f in fields):
                    fields.append({
                        'name': field_name,
                        'type': parse_type(field_type),
                        'nullable': nullable,
                        'description': description,
                        'references': references
                    })
            i += 2
    else:
        for match in matches:
            field_name = match.group(1)
            field_type = match.group(2) or 'Unknown'
            nullable = match.group(3) == 'S' if match.group(3) else True
            desc_text = match.group(4) or ''
            
            # Extrai possível referência
            references = None
            ref_match = re.search(r'([A-Z][A-Z0-9_]+)\s*$', desc_text.strip())
            if ref_match:
                potential_ref = ref_match.group(1)
                if len(potential_ref) >= 3 and potential_ref != field_name:
                    references = potential_ref
                    desc_text = desc_text[:ref_match.start()].strip()
            
            # Evita campos inválidos
            if field_name not in ['NOME', 'TIPO', 'NULL', 'TABELA', 'DESCRI', 'DESCRIÇÃO']:
                fields.append({
                    'name': field_name,
                    'type': parse_type(field_type),
                    'nullable': nullable,
                    'description': desc_text.strip(),
                    'references': references
                })
    
    # Adiciona campos padrão se não existirem
    # NOTA: HANDLE e Z_GRUPO são campos padrão do Benner Legal presentes em todas as tabelas.
    # HANDLE é a chave primária única, e Z_GRUPO define o grupo de segurança.
    # Estes campos podem não aparecer explicitamente no arquivo de texto, mas são
    # sempre criados pelo framework Benner. Esta lógica garante sua inclusão.
    has_handle = any(f['name'] == 'HANDLE' for f in fields)
    has_zgrupo = any(f['name'] == 'Z_GRUPO' for f in fields)
    
    if not has_handle:
        fields.insert(0, {
            'name': 'HANDLE',
            'type': 'Integer',
            'nullable': False,
            'description': 'Código identificador único',
            'references': None
        })
    
    if not has_zgrupo:
        fields.insert(1 if has_handle else 0, {
            'name': 'Z_GRUPO',
            'type': 'Integer',
            'nullable': False,
            'description': 'Grupo',
            'references': 'Z_GRUPOS'
        })
    
    return fields


def generate_json(data, output_file):
    """
    Gera o arquivo JSON de saída.
    
    Args:
        data: Dados estruturados
        output_file: Caminho do arquivo de saída
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Arquivo JSON gerado: {output_file}")
    print(f"Total de tabelas: {data['metadata']['total_tables']}")
    print(f"Total de campos: {data['metadata']['total_fields']}")
    print(f"Total de relacionamentos: {data['metadata']['total_relationships']}")
    print(f"Módulos identificados: {len(data['metadata']['modules'])}")


def main():
    """Função principal."""
    import sys
    
    # Determina caminhos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Arquivo de entrada
    input_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(script_dir, DEFAULT_INPUT_FILE)
    
    # Arquivo de saída
    output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(script_dir, DEFAULT_OUTPUT_FILE)
    
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo não encontrado: {input_file}")
        sys.exit(1)
    
    print(f"Processando: {input_file}")
    print("-" * 50)
    
    # Processa o arquivo
    data = parse_datadict(input_file)
    
    # Gera JSON
    generate_json(data, output_file)
    
    print("-" * 50)
    print("Processamento concluído com sucesso!")
    
    return data


if __name__ == '__main__':
    main()
