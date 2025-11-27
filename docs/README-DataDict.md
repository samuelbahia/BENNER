# 📊 Explorador de Dicionário de Dados - Benner

## 🎯 Visão Geral

Esta ferramenta permite explorar o dicionário de dados do sistema Benner de forma interativa e visual, facilitando a compreensão da estrutura do banco de dados.

## 🚀 Início Rápido

### Opção 1: Usar diretamente (dados já gerados)

Basta abrir o arquivo `datadict-explorer.html` em qualquer navegador moderno:

```bash
# macOS
open docs/datadict-explorer.html

# Linux
xdg-open docs/datadict-explorer.html

# Windows
start docs\datadict-explorer.html
```

### Opção 2: Regenerar dados (após atualização do dicionário)

```bash
# Unix/macOS/Linux
chmod +x scripts/generate-datadict.sh
./scripts/generate-datadict.sh

# Windows
scripts\generate-datadict.bat
```

## 📁 Estrutura de Arquivos

```
docs/
├── datadict-explorer.html    ← Interface interativa (abra este!)
├── parser_datadict.py        ← Parser Python
├── datadict.json             ← Dados estruturados (gerado)
├── README-DataDict.md        ← Este arquivo
├── INSTALL.md                ← Guia de instalação
├── FEATURES.md               ← Lista de funcionalidades
└── EXAMPLES.md               ← Exemplos de uso

scripts/
├── generate-datadict.sh      ← Script Unix/macOS/Linux
└── generate-datadict.bat     ← Script Windows
```

## ✨ Funcionalidades

### Interface
- 🔍 **Busca em tempo real** - Filtre tabelas e campos instantaneamente
- 📦 **Navegação por módulos** - Agrupe tabelas por área funcional
- 📋 **Detalhes completos** - Veja todos os campos de cada tabela
- 🔗 **Relacionamentos** - Visualize FKs e navegue entre tabelas
- 📊 **Estatísticas** - Gráficos de distribuição de tipos

### Dados
- ✅ 1200+ tabelas mapeadas
- ✅ 17000+ campos estruturados
- ✅ 2400+ relacionamentos identificados
- ✅ 50+ módulos categorizados

## 🎨 Interface do Explorer

### Header
Exibe estatísticas gerais: total de tabelas, campos, relacionamentos e módulos.

### Sidebar
- **Busca**: Digite para filtrar tabelas por nome, campo ou descrição
- **Módulos**: Clique para filtrar tabelas por módulo
- **Lista de Tabelas**: Todas as tabelas do módulo selecionado

### Painel Principal
- **Campos**: Tabela com nome, tipo, tamanho, obrigatoriedade, FK e descrição
- **Relacionamentos**: Cards clicáveis para navegar entre tabelas relacionadas
- **Estatísticas**: Gráficos de distribuição de tipos de dados

## 🔧 Requisitos

- **Navegador moderno**: Chrome, Firefox, Safari, Edge
- **Python 3.7+** (apenas para regenerar dados)

## 📝 Módulos do Sistema

| Prefixo | Módulo | Descrição |
|---------|--------|-----------|
| PR | Processos | Gestão de processos jurídicos |
| TV | Tramitação | Visualização e tramitação |
| GN | Geral | Cadastros gerais (pessoas, empresas) |
| EJ | Extrajudicial | Contratos e acordos extrajudiciais |
| PI | Propriedade Intelectual | Marcas, patentes, direitos autorais |
| CA | Cálculos | Cálculos trabalhistas e financeiros |
| ES | eSocial | Integração com eSocial |
| FI | Financeiro | Gestão financeira |
| WF | Workflow | Fluxos de trabalho |
| GE | Gestão Eletrônica | Documentos eletrônicos |

## 🤝 Contribuindo

Para atualizar o dicionário:

1. Atualize o arquivo `Dicionario de Dados.txt` na raiz
2. Execute o script de geração
3. Verifique o resultado no explorer
4. Commit as mudanças

## 📄 Licença

Uso interno - Benner Sistemas

---

**Desenvolvido com ❤️ para a equipe Benner**
