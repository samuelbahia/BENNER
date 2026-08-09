#!/bin/bash
#
# generate-datadict.sh - Script de automação para geração do dicionário de dados interativo
#
# Uso: ./generate-datadict.sh [arquivo_entrada]
#
# Se nenhum arquivo de entrada for especificado, usa 'Dicionario de Dados.txt' na raiz do projeto
#

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$PROJECT_ROOT/docs"

# Arquivos
DEFAULT_INPUT="$PROJECT_ROOT/Dicionario de Dados.txt"
PARSER_SCRIPT="$DOCS_DIR/parser_datadict.py"
OUTPUT_JSON="$DOCS_DIR/datadict.json"
EXPLORER_HTML="$DOCS_DIR/datadict-explorer.html"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Benner Legal - Gerador de Dicionário de Dados           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verifica arquivo de entrada
INPUT_FILE="${1:-$DEFAULT_INPUT}"

if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}✗ Erro: Arquivo de entrada não encontrado: $INPUT_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Arquivo de entrada: $INPUT_FILE${NC}"

# Verifica se Python está instalado e versão mínima
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Erro: Python 3 não encontrado. Por favor, instale o Python 3.6+${NC}"
    exit 1
fi

# Verifica versão do Python (requer 3.6+)
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
    echo -e "${RED}✗ Erro: Python 3.6+ é necessário (encontrado: $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION encontrado${NC}"

# Verifica se o parser existe
if [ ! -f "$PARSER_SCRIPT" ]; then
    echo -e "${RED}✗ Erro: Script do parser não encontrado: $PARSER_SCRIPT${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Parser encontrado: $PARSER_SCRIPT${NC}"

# Verifica se o explorer HTML existe
if [ ! -f "$EXPLORER_HTML" ]; then
    echo -e "${YELLOW}⚠ Aviso: Explorer HTML não encontrado: $EXPLORER_HTML${NC}"
fi

echo ""
echo -e "${BLUE}► Executando parser...${NC}"
echo "─────────────────────────────────────────────────────────────────"

# Executa o parser
python3 "$PARSER_SCRIPT" "$INPUT_FILE" "$OUTPUT_JSON"

echo "─────────────────────────────────────────────────────────────────"

# Verifica se o JSON foi gerado
if [ ! -f "$OUTPUT_JSON" ]; then
    echo -e "${RED}✗ Erro: Falha ao gerar o arquivo JSON${NC}"
    exit 1
fi

# Mostra tamanho do arquivo
JSON_SIZE=$(du -h "$OUTPUT_JSON" | cut -f1)
echo ""
echo -e "${GREEN}✓ Arquivo JSON gerado: $OUTPUT_JSON ($JSON_SIZE)${NC}"

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✓ Geração concluída!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Como usar:${NC}"
echo ""
echo "  1. Abra o explorer no navegador:"
echo -e "     ${GREEN}open $EXPLORER_HTML${NC}"
echo ""
echo "  2. Ou inicie um servidor local:"
echo -e "     ${GREEN}cd $DOCS_DIR && python3 -m http.server 8080${NC}"
echo "     Acesse: http://localhost:8080/datadict-explorer.html"
echo ""
echo "  3. Para regenerar após alterações no dicionário:"
echo -e "     ${GREEN}./scripts/generate-datadict.sh${NC}"
echo ""
