#!/bin/bash
# =============================================================================
# Script para gerar o Dicionário de Dados Benner
# =============================================================================
#
# Uso:
#   chmod +x generate-datadict.sh
#   ./generate-datadict.sh
#
# Este script:
#   1. Verifica pré-requisitos (Python 3)
#   2. Executa o parser para gerar o JSON
#   3. Exibe instruções para visualização
#
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$ROOT_DIR/docs"

echo ""
echo "============================================================"
echo -e "${BLUE}  Gerador de Dicionário de Dados - Benner${NC}"
echo "============================================================"
echo ""

# Verificar Python
echo -e "${YELLOW}🔍 Verificando pré-requisitos...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Verificar se é Python 3
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)
    if [ "$PYTHON_VERSION" = "3" ]; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python 3 não encontrado.${NC}"
        echo ""
        echo "Por favor, instale o Python 3:"
        echo "  - Windows: https://www.python.org/downloads/"
        echo "  - macOS: brew install python3"
        echo "  - Linux: sudo apt install python3"
        exit 1
    fi
else
    echo -e "${RED}❌ Python não encontrado.${NC}"
    echo ""
    echo "Por favor, instale o Python 3:"
    echo "  - Windows: https://www.python.org/downloads/"
    echo "  - macOS: brew install python3"
    echo "  - Linux: sudo apt install python3"
    exit 1
fi

echo -e "${GREEN}✅ Python encontrado: $($PYTHON_CMD --version)${NC}"

# Verificar arquivo de entrada
INPUT_FILE="$ROOT_DIR/Dicionario de Dados.txt"
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}❌ Arquivo de entrada não encontrado:${NC}"
    echo "   $INPUT_FILE"
    exit 1
fi

echo -e "${GREEN}✅ Arquivo de entrada encontrado${NC}"

# Verificar parser
PARSER_FILE="$DOCS_DIR/parser_datadict.py"
if [ ! -f "$PARSER_FILE" ]; then
    echo -e "${RED}❌ Parser não encontrado:${NC}"
    echo "   $PARSER_FILE"
    exit 1
fi

echo -e "${GREEN}✅ Parser encontrado${NC}"

# Executar parser
echo ""
echo -e "${YELLOW}🔄 Executando parser...${NC}"
echo ""

cd "$DOCS_DIR"
$PYTHON_CMD parser_datadict.py "$INPUT_FILE" "datadict.json"

# Verificar se JSON foi gerado
OUTPUT_FILE="$DOCS_DIR/datadict.json"
if [ ! -f "$OUTPUT_FILE" ]; then
    echo -e "${RED}❌ Erro: JSON não foi gerado${NC}"
    exit 1
fi

# Resultado
echo ""
echo "============================================================"
echo -e "${GREEN}  ✅ Dicionário de Dados gerado com sucesso!${NC}"
echo "============================================================"
echo ""
echo -e "${BLUE}📁 Arquivos gerados:${NC}"
echo "   • docs/datadict.json"
echo ""
echo -e "${BLUE}🚀 Para visualizar:${NC}"
echo "   Abra o arquivo no navegador:"
echo "   ${GREEN}docs/datadict-explorer.html${NC}"
echo ""
echo "   Comandos úteis:"
echo "   • macOS:  open docs/datadict-explorer.html"
echo "   • Linux:  xdg-open docs/datadict-explorer.html"
echo "   • WSL:    explorer.exe docs/datadict-explorer.html"
echo ""
echo "============================================================"
