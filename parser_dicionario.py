#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser para o Dicionário de Dados BENNER
Extrai automaticamente tabelas e campos do arquivo de texto
e gera estrutura JSON para visualização HTML
"""

import re
import json
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Prefixos de módulos conhecidos
MODULE_PREFIXES = {
    'ADM': 'Administração do Sistema',
    'ADMW': 'Administração Workflow',
    'AE': 'Avaliação de Escritórios',
    'AG': 'Agenda',
    'AU': 'Autenticação',
    'AV': 'Avaliação',
    'BAIRROS': 'Localização',
    'BI': 'Business Intelligence',
    'BL': 'Biblioteca',
    'CA': 'Cálculo Trabalhista',
    'CB': 'Conciliação Bancária',
    'CR': 'Circularização',
    'CS': 'Consultivo Smart',
    'CT': 'Contabilidade',
    'EJ': 'Execução Judicial',
    'EMPRESAS': 'Empresas',
    'ESTADOS': 'Estados',
    'FI': 'Financeiro',
    'FILIAIS': 'Filiais',
    'FN': 'Financeiro',
    'GE': 'Gestão de Documentos',
    'GI': 'Gestão de Informações',
    'GN': 'Geral',
    'GP': 'Gestão de Processos',
    'IN': 'Integração',
    'K9': 'Integração K9',
    'LG': 'Legal',
    'MN': 'Manutenção',
    'MUNICIPIOS': 'Localização',
    'PAISES': 'Localização',
    'PR': 'Processos',
    'RE': 'Relatórios',
    'SO': 'Sociedade',
    'WF': 'Workflow',
    'Z': 'Sistema/Framework'
}

def get_module_name(table_name: str) -> Tuple[str, str]:
    """Retorna o prefixo do módulo e o nome do módulo para uma tabela"""
    for prefix, module_name in sorted(MODULE_PREFIXES.items(), key=lambda x: -len(x[0])):
        if table_name.startswith(prefix + '_') or table_name == prefix:
            return prefix, module_name
    return 'OUTROS', 'Outros'

def identify_fk_relationship(field_name: str, fk_table: str) -> Optional[Dict]:
    """Identifica se um campo é uma FK e retorna informações do relacionamento"""
    if fk_table and fk_table.strip():
        return {
            'field': field_name,
            'references_table': fk_table.strip(),
            'references_field': 'HANDLE'  # Assumindo que a PK é sempre HANDLE
        }
    return None

def parse_field_definition(field_text: str) -> Dict:
    """Parse de uma definição de campo individual"""
    # Padrões para tipos de dados
    type_patterns = [
        (r'Integer', 'Integer'),
        (r'Varchar\s*\((\d+)\)', 'Varchar'),
        (r'Char\s*\((\d+)\)', 'Char'),
        (r'Number', 'Number'),
        (r'Blob', 'Blob'),
        (r'Data', 'Date'),
    ]
    
    field_info = {
        'name': '',
        'type': 'Unknown',
        'size': None,
        'nullable': None,
        'description': '',
        'fk_table': None
    }
    
    for pattern, type_name in type_patterns:
        match = re.search(pattern, field_text, re.IGNORECASE)
        if match:
            field_info['type'] = type_name
            if type_name in ['Varchar', 'Char'] and match.groups():
                field_info['size'] = int(match.group(1))
            break
    
    return field_info

def parse_data_dictionary(file_path: str) -> Dict:
    """
    Parse do arquivo de dicionário de dados e extração de tabelas e campos
    """
    tables = {}
    
    with open(file_path, 'r', encoding='latin-1', errors='replace') as f:
        content = f.read()
    
    # Limpar e normalizar o conteúdo
    lines = content.split('\n')
    
    current_table = None
    current_description = ''
    current_fields = []
    
    # Padrão para identificar nome de tabela (começa com número. NOME_TABELA:)
    table_pattern = re.compile(r'^\d+\.\s*([A-Z_][A-Z0-9_]*)\s*:\s*(.*?)$', re.IGNORECASE)
    
    # Também procurar por tabelas que podem não ter número no início
    table_pattern2 = re.compile(r'^([A-Z][A-Z0-9_]+)\s*:\s*(.*?)$')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Ignorar linhas vazias e cabeçalhos
        if not line or 'ESTRUTURA DAS TABELAS' in line:
            i += 1
            continue
        
        # Procurar por definição de tabela
        table_match = table_pattern.match(line) or table_pattern2.match(line)
        
        if table_match:
            table_name = table_match.group(1).strip()
            rest = table_match.group(2).strip() if table_match.group(2) else ''
            
            # Verificar se é realmente um nome de tabela válido
            if table_name and len(table_name) > 1 and table_name[0].isalpha():
                # Salvar tabela anterior se existir
                if current_table:
                    tables[current_table['name']] = current_table
                
                # Iniciar nova tabela
                current_table = {
                    'name': table_name,
                    'description': rest,
                    'fields': [],
                    'relationships': [],
                    'module': get_module_name(table_name)[0],
                    'module_name': get_module_name(table_name)[1]
                }
                
                # Processar o resto da linha e linhas subsequentes para campos
                field_text = rest
                i += 1
                
                # Continuar lendo linhas que fazem parte desta tabela
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    # Parar se encontrar nova tabela ou linha vazia significativa
                    if table_pattern.match(next_line) or table_pattern2.match(next_line):
                        break
                    
                    if 'ESTRUTURA DAS TABELAS' in next_line:
                        i += 1
                        continue
                    
                    field_text += ' ' + next_line
                    i += 1
                
                # Extrair campos do texto
                fields = extract_fields_from_text(field_text)
                current_table['fields'] = fields
                
                # Identificar relacionamentos baseados em FKs
                for field in fields:
                    if field.get('fk_table'):
                        rel = identify_fk_relationship(field['name'], field['fk_table'])
                        if rel:
                            current_table['relationships'].append(rel)
                
                continue
        
        i += 1
    
    # Salvar última tabela
    if current_table:
        tables[current_table['name']] = current_table
    
    return tables

def extract_fields_from_text(text: str) -> List[Dict]:
    """
    Extrai campos de um bloco de texto
    """
    fields = []
    
    # Padrão mais robusto para capturar campos
    # NOME_CAMPO Tipo (tamanho) N/S Descrição TABELA_FK
    
    # Primeiro, normalizar o texto
    text = re.sub(r'\s+', ' ', text)
    
    # Procurar por padrões de campo
    # Padrão: NOME seguido de tipo (Integer, Varchar, Number, Blob, Data, Char)
    field_pattern = re.compile(
        r'([A-Z][A-Z0-9_]*)\s*'  # Nome do campo
        r'(Integer|Varchar\s*\(\s*\d+\s*\)|Char\s*\(\s*\d+\s*\)|Number|Blob|Data)\s*'  # Tipo
        r'([NS])\s*'  # Nullable
        r'([^A-Z]*?(?=[A-Z][A-Z0-9_]*\s*(?:Integer|Varchar|Char|Number|Blob|Data)|$))',  # Descrição até próximo campo
        re.IGNORECASE
    )
    
    # Tentar um padrão mais simples se o complexo não funcionar
    simple_pattern = re.compile(
        r'([A-Z][A-Z0-9_]+)\s+'  # Nome do campo
        r'(Integer|Varchar\s*\(\s*\d+\s*\)|Char\s*\(\s*\d+\s*\)|Number|Blob|Data)',  # Tipo
        re.IGNORECASE
    )
    
    # Encontrar todos os campos usando o padrão simples primeiro
    matches = list(simple_pattern.finditer(text))
    
    for i, match in enumerate(matches):
        field_name = match.group(1).strip()
        field_type = match.group(2).strip()
        
        # Ignorar campos de sistema duplicados ou inválidos
        if field_name in ['NOME', 'TIPO', 'NULL', 'DESCRICAO', 'TABELA']:
            continue
        
        # Extrair tamanho se for Varchar ou Char
        size = None
        size_match = re.search(r'\((\d+)\)', field_type)
        if size_match:
            size = int(size_match.group(1))
            field_type = re.sub(r'\s*\(\s*\d+\s*\)', '', field_type).strip()
        
        # Tentar extrair descrição e FK
        description = ''
        fk_table = None
        
        # Olhar texto após o tipo até o próximo campo
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        between_text = text[start_pos:end_pos].strip()
        
        # Extrair nullable (N ou S logo após o tipo)
        nullable_match = re.match(r'^\s*([NS])\s*', between_text)
        nullable = nullable_match.group(1) == 'S' if nullable_match else None
        
        # O resto é descrição + possível FK
        if nullable_match:
            rest = between_text[nullable_match.end():].strip()
        else:
            rest = between_text
        
        # Procurar por nome de tabela FK (padrão de nome de tabela no final)
        fk_match = re.search(r'([A-Z][A-Z0-9_]+)\s*$', rest)
        if fk_match:
            potential_fk = fk_match.group(1)
            # Verificar se parece ser uma tabela (tem prefixo conhecido ou termina com S)
            if any(potential_fk.startswith(p + '_') for p in MODULE_PREFIXES.keys()) or potential_fk.endswith('S'):
                fk_table = potential_fk
                description = rest[:fk_match.start()].strip()
            else:
                description = rest
        else:
            description = rest
        
        # Limpar descrição
        description = re.sub(r'[|].*$', '', description).strip()
        
        fields.append({
            'name': field_name,
            'type': field_type,
            'size': size,
            'nullable': nullable,
            'description': description,
            'fk_table': fk_table
        })
    
    return fields

def build_statistics(tables: Dict) -> Dict:
    """Constrói estatísticas sobre as tabelas"""
    stats = {
        'total_tables': len(tables),
        'total_fields': 0,
        'total_relationships': 0,
        'tables_by_module': defaultdict(int),
        'fields_by_type': defaultdict(int),
        'tables_with_most_fields': [],
        'most_referenced_tables': defaultdict(int)
    }
    
    field_counts = []
    
    for table_name, table in tables.items():
        num_fields = len(table['fields'])
        stats['total_fields'] += num_fields
        stats['total_relationships'] += len(table['relationships'])
        stats['tables_by_module'][table['module']] += 1
        field_counts.append((table_name, num_fields))
        
        for field in table['fields']:
            stats['fields_by_type'][field['type']] += 1
            if field.get('fk_table'):
                stats['most_referenced_tables'][field['fk_table']] += 1
    
    # Top 10 tabelas com mais campos
    field_counts.sort(key=lambda x: -x[1])
    stats['tables_with_most_fields'] = field_counts[:10]
    
    # Top 10 tabelas mais referenciadas
    most_ref = sorted(stats['most_referenced_tables'].items(), key=lambda x: -x[1])[:10]
    stats['most_referenced_tables'] = dict(most_ref)
    
    # Converter defaultdicts para dicts normais para JSON
    stats['tables_by_module'] = dict(stats['tables_by_module'])
    stats['fields_by_type'] = dict(stats['fields_by_type'])
    
    return stats

def generate_json_output(tables: Dict, output_path: str):
    """Gera arquivo JSON com os dados estruturados"""
    output = {
        'tables': tables,
        'statistics': build_statistics(tables),
        'modules': MODULE_PREFIXES
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"JSON gerado: {output_path}")

def generate_dbml(tables: Dict, output_path: str):
    """Gera arquivo DBML para diagrama ER"""
    dbml_lines = ['// DBML - Database Markup Language', 
                  '// Gerado automaticamente do Dicionário de Dados BENNER', '']
    
    for table_name, table in sorted(tables.items()):
        dbml_lines.append(f'Table {table_name} {{')
        
        for field in table['fields']:
            type_str = field['type']
            if field.get('size'):
                type_str = f"varchar({field['size']})"
            elif field['type'] == 'Integer':
                type_str = 'integer'
            elif field['type'] == 'Number':
                type_str = 'decimal'
            elif field['type'] == 'Date':
                type_str = 'datetime'
            elif field['type'] == 'Blob':
                type_str = 'text'
            
            nullable = '' if field.get('nullable') else 'not null'
            pk = 'pk' if field['name'] == 'HANDLE' else ''
            ref = f"[ref: > {field['fk_table']}.HANDLE]" if field.get('fk_table') else ''
            
            modifiers = ' '.join(filter(None, [pk, nullable, ref]))
            if modifiers:
                modifiers = f' [{modifiers}]'
            
            desc = f" // {field['description']}" if field.get('description') else ''
            dbml_lines.append(f"  {field['name']} {type_str}{modifiers}{desc}")
        
        dbml_lines.append('}')
        dbml_lines.append('')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dbml_lines))
    
    print(f"DBML gerado: {output_path}")

def main():
    """Função principal"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'Dicionario de Dados.txt')
    json_output = os.path.join(script_dir, 'dicionario_dados.json')
    dbml_output = os.path.join(script_dir, 'dicionario_dados.dbml')
    
    print(f"Processando: {input_file}")
    
    tables = parse_data_dictionary(input_file)
    print(f"Tabelas encontradas: {len(tables)}")
    
    generate_json_output(tables, json_output)
    generate_dbml(tables, dbml_output)
    
    # Retornar dados para uso pelo gerador HTML
    return tables

if __name__ == '__main__':
    main()
