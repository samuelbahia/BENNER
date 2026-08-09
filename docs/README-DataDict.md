# 📊 Explorador de Dicionário de Dados - Benner Legal

Este módulo fornece uma solução completa para documentação interativa do banco de dados Benner Legal.

## 📋 Visão Geral

O sistema transforma o arquivo de texto do dicionário de dados em uma interface web moderna e interativa, facilitando a consulta e navegação pela estrutura do banco de dados.

### Componentes

| Arquivo | Descrição |
|---------|-----------|
| `parser_datadict.py` | Parser Python que extrai tabelas, campos e relacionamentos |
| `datadict-explorer.html` | Dashboard HTML interativo para visualização |
| `datadict.json` | Dados estruturados gerados pelo parser |
| `../scripts/generate-datadict.sh` | Script de automação |

## 🚀 Como Usar

### Opção 1: Usando o Script de Automação (Recomendado)

```bash
# Na raiz do projeto
./scripts/generate-datadict.sh
```

### Opção 2: Execução Manual

```bash
# Gerar o JSON
cd docs
python3 parser_datadict.py

# Abrir no navegador
open datadict-explorer.html
```

### Opção 3: Com Servidor Local

Para melhor desempenho e compatibilidade CORS:

```bash
cd docs
python3 -m http.server 8080
```

Acesse: http://localhost:8080/datadict-explorer.html

## 🎨 Funcionalidades do Explorer

### Interface Principal

- **🔍 Busca em Tempo Real** - Filtra tabelas por nome, descrição ou campos
- **📁 Navegação por Módulos** - Agrupa tabelas por prefixo (GN_, PR_, EJ_, etc)
- **📊 Estatísticas** - Visualização de métricas do banco de dados

### Visualização de Tabelas

- Lista de todas as tabelas com cards informativos
- Detalhes completos de cada tabela:
  - Descrição
  - Lista de campos com tipo, nullable e descrição
  - Relacionamentos com outras tabelas
- Navegação entre tabelas relacionadas

### Estatísticas

- Total de tabelas, campos e relacionamentos
- Gráficos de distribuição por módulo
- Informações de geração

## 📊 Estrutura de Dados

O JSON gerado segue a seguinte estrutura:

```json
{
  "metadata": {
    "generated_at": "2025-01-01T00:00:00",
    "source_file": "Dicionario de Dados.txt",
    "total_tables": 550,
    "total_fields": 33000,
    "total_relationships": 500,
    "modules": ["Processos", "Financeiro", ...]
  },
  "module_stats": {
    "Processos": { "tables": 80, "fields": 3000 },
    ...
  },
  "tables": {
    "TABELA_EXEMPLO": {
      "name": "TABELA_EXEMPLO",
      "description": "Descrição da tabela",
      "module": "Processos",
      "fields": [
        {
          "name": "HANDLE",
          "type": "Integer",
          "nullable": false,
          "description": "Código identificador único",
          "references": null
        },
        ...
      ],
      "field_count": 10,
      "relationships": ["OUTRA_TABELA"]
    },
    ...
  },
  "relationships": [
    {
      "from_table": "TABELA_A",
      "from_field": "ID_B",
      "to_table": "TABELA_B",
      "type": "foreign_key"
    },
    ...
  ]
}
```

## 🏗️ Módulos Identificados

O parser identifica automaticamente os seguintes módulos baseado nos prefixos das tabelas:

| Prefixo | Módulo |
|---------|--------|
| `GN_` | Geral |
| `PR_` | Processos |
| `EJ_` | Escritórios Jurídicos |
| `FN_` | Financeiro |
| `FI_` | Financeiro Integrado |
| `CT_` | Contabilidade |
| `CA_` | Cálculo Trabalhista |
| `GE_` | Gestão de Documentos |
| `AG_` | Agenda |
| `BL_` | Biblioteca |
| `ES_` | eSocial |
| `CB_` | Conciliação Bancária |
| `CR_` | Circularização |
| `EX_` | Extrajudicial |
| `Z_` | Sistema |

## 🛠️ Desenvolvimento

### Requisitos

- Python 3.6+
- Navegador web moderno (Chrome, Firefox, Edge, Safari)

### Executando Testes

```bash
# Verificar geração do JSON
python3 parser_datadict.py
cat datadict.json | python3 -m json.tool | head -50
```

### Regenerando após alterações

Sempre que o arquivo `Dicionario de Dados.txt` for atualizado:

```bash
./scripts/generate-datadict.sh
```

## 🎯 Benefícios

1. **📖 Documentação Viva** - Sincronizada com a estrutura real do banco
2. **⚡ Acesso Rápido** - Consulta sem necessidade de IDE ou banco de dados
3. **📤 Compartilhável** - Um simples HTML para toda a equipe
4. **💼 Profissional** - Interface moderna e intuitiva
5. **🔧 Manutenção** - Facilita entender a arquitetura do sistema
6. **👥 Onboarding** - Novos desenvolvedores entendem rapidamente a modelagem

## 📝 Changelog

### v1.0.0
- Parser inicial com extração de tabelas, campos e relacionamentos
- Explorer HTML com busca, filtros e estatísticas
- Suporte a múltiplos módulos
- Script de automação

## 🤝 Contribuindo

Para melhorias ou correções:

1. Atualize o parser (`parser_datadict.py`) se necessário
2. Teste a geração do JSON
3. Verifique a visualização no explorer
4. Execute `./scripts/generate-datadict.sh` para validar

## 📄 Licença

Este projeto faz parte do sistema Benner Legal.
