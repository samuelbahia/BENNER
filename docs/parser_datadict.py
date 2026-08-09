#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser de Dicionário de Dados - Benner

Este script extrai informações de tabelas, campos e relacionamentos
do arquivo 'Dicionario de Dados.txt' e gera um JSON estruturado.

Uso:
    python parser_datadict.py [input_file] [output_file]
    
    Argumentos opcionais:
    - input_file: Caminho para o arquivo de entrada (padrão: ../Dicionario de Dados.txt)
    - output_file: Caminho para o arquivo JSON de saída (padrão: datadict.json)
"""

import json
import re
import sys
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def detect_encoding(filepath: str) -> str:
    """Detecta a codificação do arquivo."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                f.read(1000)
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return 'latin-1'


def normalize_text(text: str) -> str:
    """Normaliza texto removendo caracteres problemáticos."""
    if not text:
        return ""
    # Remove caracteres de controle exceto quebras de linha
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text.strip()


def parse_type(type_str: str) -> Tuple[str, Optional[int]]:
    """Parseia o tipo de dado e extrai o tamanho se houver."""
    if not type_str:
        return ("Unknown", None)
    
    type_str = type_str.strip()
    
    # Detectar tipo com tamanho: Varchar (80), Char (1), etc
    match = re.match(r'^(\w+)\s*\((\d+)\)$', type_str)
    if match:
        return (match.group(1), int(match.group(2)))
    
    # Tipo simples: Integer, Number, Data, Blob
    return (type_str, None)


def extract_module(table_name: str) -> str:
    """Extrai o módulo/prefixo do nome da tabela."""
    match = re.match(r'^([A-Z]{2,3})_', table_name)
    if match:
        return match.group(1)
    return "OTHER"


def get_module_description(module: str) -> str:
    """Retorna a descrição do módulo."""
    modules = {
        'ADM': 'Administração',
        'AE': 'Avaliação de Escritórios',
        'AG': 'Agenda',
        'AU': 'Autenticação',
        'AV': 'Avaliação',
        'BI': 'Business Intelligence',
        'BL': 'Biblioteca',
        'CA': 'Cálculos',
        'CB': 'Cobrança',
        'CR': 'Crédito',
        'CS': 'Chamados/Suporte',
        'CT': 'Contabilidade',
        'EJ': 'Extrajudicial',
        'EP': 'Escritórios e Processos',
        'ES': 'eSocial',
        'EX': 'Extra Judicial',
        'FI': 'Financeiro',
        'FN': 'Contratos Financeiros',
        'FT': 'Faturamento',
        'GE': 'Gestão Eletrônica',
        'GI': 'Gestão de Indicadores',
        'GN': 'Geral',
        'GP': 'Gestão de Processos',
        'GR': 'Relatórios Gerenciais',
        'IA': 'Inteligência Artificial',
        'ID': 'Identificação',
        'IM': 'Importação',
        'IN': 'Interface',
        'IS': 'Integração de Sistemas',
        'LI': 'Licenças',
        'MB': 'Mobile',
        'ME': 'Mensagens',
        'MS': 'Mensageria',
        'NP': 'Materiais',
        'NT': 'Notas',
        'PI': 'Propriedade Intelectual',
        'PR': 'Processos',
        'PV': 'Previsão',
        'RE': 'Relatórios',
        'SE': 'Segurança',
        'SL': 'SLA',
        'SO': 'Solicitações',
        'ST': 'Status',
        'SX': 'Sistema Externo',
        'TA': 'Tarefas',
        'TMP': 'Temporário',
        'TS': 'Timesheet',
        'TV': 'Tramitação/Visualização',
        'UR': 'URLs',
        'VC': 'Versões/Controle',
        'WF': 'Workflow',
        'WG': 'Web/Geral',
        'WI': 'Web Interface',
        'Z_': 'Sistema (Interno)',
        'Z': 'Sistema (Interno)',
    }
    return modules.get(module, f'Módulo {module}')


def is_type_line(line: str) -> bool:
    """Verifica se a linha é um tipo de dado."""
    type_patterns = [
        r'^Integer$',
        r'^Number$',
        r'^Data$',
        r'^Blob$',
        r'^DateTime$',
        r'^SmallInt$',
        r'^BigInt$',
        r'^Varchar\s*\(\d+\)$',
        r'^Char\s*\(\d+\)$',
    ]
    for pattern in type_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    return False


def is_field_name(line: str) -> bool:
    """Verifica se a linha é um nome de campo válido."""
    # Nome de campo: letras maiúsculas, números e underscore
    # Não pode ser apenas N ou S (que são nullable flags)
    # Não pode ser um tipo de dado
    if not line or len(line) < 2:
        return False
    if line in ['N', 'S']:
        return False
    if is_type_line(line):
        return False
    if re.match(r'^[A-Z][A-Z0-9_]*$', line):
        return True
    return False


def is_table_reference(line: str) -> bool:
    """Verifica se a linha é uma referência a tabela (FK)."""
    if re.match(r'^[A-Z]{2,3}_[A-Z0-9_]+$', line):
        return True
    return False


def parse_dictionary(filepath: str) -> Dict:
    """
    Parseia o arquivo de dicionário de dados.
    
    Retorna um dicionário com:
    - metadata: estatísticas gerais
    - modules: lista de módulos
    - tables: dicionário de tabelas com seus campos e relacionamentos
    """
    
    encoding = detect_encoding(filepath)
    print(f"Usando codificação: {encoding}")
    
    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
        content = f.read()
    
    # Normalizar quebras de linha
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    lines = content.split('\n')
    
    tables = {}
    current_table = None
    current_description = ""
    fields = []
    
    # Padrão para identificar início de tabela
    table_pattern = re.compile(r'^([A-Z]{2,3}_[A-Z0-9_]+):\s*(.*?)$')
    
    # Buffer para o campo atual
    field_name = None
    field_type = None
    field_size = None
    field_nullable = True
    field_description = ""
    field_fk = None
    
    # Contador de posição no campo (0=nome, 1=tipo, 2=null, 3=desc, 4=fk)
    field_pos = -1
    
    def save_field():
        nonlocal field_name, field_type, field_size, field_nullable, field_description, field_fk, field_pos
        if field_name and field_type:
            fields.append({
                'name': field_name,
                'type': field_type,
                'size': field_size,
                'nullable': field_nullable,
                'description': field_description.strip(),
                'fk_table': field_fk
            })
        field_name = None
        field_type = None
        field_size = None
        field_nullable = True
        field_description = ""
        field_fk = None
        field_pos = -1
    
    def save_table():
        nonlocal current_table, current_description, fields
        if current_table:
            save_field()
            if fields:
                tables[current_table] = {
                    'name': current_table,
                    'module': extract_module(current_table),
                    'description': current_description,
                    'fields': fields,
                    'field_count': len(fields)
                }
            current_table = None
            current_description = ""
            fields = []
    
    in_header = False
    skip_header_lines = 0
    
    for line in lines:
        line = normalize_text(line)
        
        # Verificar se é início de nova tabela
        table_match = table_pattern.match(line)
        
        if table_match:
            save_table()
            current_table = table_match.group(1)
            current_description = table_match.group(2).strip() if table_match.group(2) else ""
            fields = []
            in_header = True
            skip_header_lines = 0
            continue
        
        if not current_table:
            continue
        
        # Pular linhas de cabeçalho (NOME, TIPO, NULL, DESCRIÇÃO, TABELA)
        if in_header:
            if line.upper() in ['NOME', 'TIPO', 'NULL', 'TABELA'] or 'DESCRI' in line.upper():
                skip_header_lines += 1
                continue
            if line == '':
                continue
            # Após encontrar o primeiro campo, sair do cabeçalho
            if is_field_name(line) or is_type_line(line):
                in_header = False
            else:
                continue
        
        # Ignorar linhas vazias dentro da tabela
        if not line:
            # Uma linha vazia pode indicar fim de um campo
            if field_pos >= 2:  # Já temos nome e tipo
                save_field()
            continue
        
        # Tentar identificar o que é esta linha
        
        # 1. É um nome de campo?
        if is_field_name(line) and not is_table_reference(line):
            # Se já temos um campo em andamento, salvar
            if field_name:
                save_field()
            field_name = line
            field_pos = 0
            continue
        
        # 2. É um tipo de dado?
        if is_type_line(line) and field_name:
            type_info = parse_type(line)
            field_type = type_info[0]
            field_size = type_info[1]
            field_pos = 1
            continue
        
        # 3. É indicador de nullable?
        if line in ['N', 'S'] and field_name and field_type:
            field_nullable = (line == 'S')
            field_pos = 2
            continue
        
        # 4. É uma referência a tabela (FK)?
        if is_table_reference(line) and field_name and field_type:
            field_fk = line
            field_pos = 4
            continue
        
        # 5. É descrição?
        if field_name and field_type and field_pos >= 2:
            if field_description:
                field_description += ' ' + line
            else:
                field_description = line
            field_pos = 3
    
    # Salvar última tabela
    save_table()
    
    return tables


def extract_relationships(tables: Dict) -> List[Dict]:
    """Extrai relacionamentos entre tabelas baseado em FKs."""
    relationships = []
    
    for table_name, table_data in tables.items():
        for field in table_data.get('fields', []):
            if field.get('fk_table'):
                fk_table = field['fk_table']
                # Verificar se a tabela referenciada existe
                if fk_table in tables:
                    relationships.append({
                        'from_table': table_name,
                        'to_table': fk_table,
                        'field': field['name'],
                        'type': 'FK'
                    })
    
    return relationships


def calculate_statistics(tables: Dict, relationships: List) -> Dict:
    """Calcula estatísticas do dicionário."""
    
    # Contadores
    total_tables = len(tables)
    total_fields = sum(t.get('field_count', 0) for t in tables.values())
    total_relationships = len(relationships)
    
    # Módulos
    modules = defaultdict(int)
    for table_data in tables.values():
        modules[table_data.get('module', 'OTHER')] += 1
    
    # Tipos de dados
    type_counts = defaultdict(int)
    nullable_count = 0
    required_count = 0
    
    for table_data in tables.values():
        for field in table_data.get('fields', []):
            type_counts[field.get('type', 'Unknown')] += 1
            if field.get('nullable'):
                nullable_count += 1
            else:
                required_count += 1
    
    return {
        'total_tables': total_tables,
        'total_fields': total_fields,
        'total_relationships': total_relationships,
        'total_modules': len(modules),
        'modules': dict(modules),
        'type_distribution': dict(type_counts),
        'nullable_fields': nullable_count,
        'required_fields': required_count
    }


def generate_json(tables: Dict, output_path: str) -> Dict:
    """Gera o arquivo JSON com o dicionário estruturado."""
    
    relationships = extract_relationships(tables)
    statistics = calculate_statistics(tables, relationships)
    
    # Adicionar descrições de módulos
    module_info = {}
    for module in statistics['modules'].keys():
        module_info[module] = {
            'name': module,
            'description': get_module_description(module),
            'table_count': statistics['modules'][module]
        }
    
    result = {
        'metadata': {
            'version': '1.0',
            'generated_by': 'parser_datadict.py',
            'statistics': statistics
        },
        'modules': module_info,
        'tables': tables,
        'relationships': relationships
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result


def main():
    """Função principal."""
    
    # Determinar caminhos de entrada e saída
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(script_dir, '..', 'Dicionario de Dados.txt')
    default_output = os.path.join(script_dir, 'datadict.json')
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_file = sys.argv[2] if len(sys.argv) > 2 else default_output
    
    print("=" * 60)
    print("Parser de Dicionário de Dados - Benner")
    print("=" * 60)
    
    if not os.path.exists(input_file):
        print(f"\n❌ Erro: Arquivo não encontrado: {input_file}")
        print("\nUso: python parser_datadict.py [input_file] [output_file]")
        sys.exit(1)
    
    print(f"\n📂 Arquivo de entrada: {input_file}")
    print(f"📂 Arquivo de saída: {output_file}")
    
    print("\n🔄 Parseando dicionário de dados...")
    tables = parse_dictionary(input_file)
    
    print(f"\n✅ Tabelas encontradas: {len(tables)}")
    
    print("\n🔄 Gerando JSON estruturado...")
    result = generate_json(tables, output_file)
    
    stats = result['metadata']['statistics']
    
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS")
    print("=" * 60)
    print(f"   📋 Total de Tabelas: {stats['total_tables']}")
    print(f"   📝 Total de Campos: {stats['total_fields']}")
    print(f"   🔗 Total de Relacionamentos: {stats['total_relationships']}")
    print(f"   📦 Total de Módulos: {stats['total_modules']}")
    print(f"   ✅ Campos Obrigatórios: {stats['required_fields']}")
    print(f"   ⭕ Campos Opcionais: {stats['nullable_fields']}")
    
    print("\n📦 MÓDULOS:")
    for module, count in sorted(stats['modules'].items(), key=lambda x: -x[1]):
        desc = get_module_description(module)
        print(f"   • {module}: {count} tabelas ({desc})")
    
    print("\n📊 TIPOS DE DADOS:")
    for type_name, count in sorted(stats['type_distribution'].items(), key=lambda x: -x[1])[:10]:
        print(f"   • {type_name}: {count} campos")
    
    print("\n" + "=" * 60)
    print(f"✅ JSON gerado com sucesso: {output_file}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
