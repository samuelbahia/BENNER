# 🔧 Guia de Instalação

## Requisitos

### Para Visualização (Explorer)
- Navegador moderno (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- Nenhuma instalação necessária!

### Para Regeneração de Dados
- Python 3.7 ou superior
- Nenhuma dependência externa necessária

## Instalação do Python

### Windows

1. Acesse [python.org/downloads](https://www.python.org/downloads/)
2. Baixe o instalador para Windows
3. **IMPORTANTE**: Marque "Add Python to PATH" durante a instalação
4. Clique em "Install Now"
5. Verifique a instalação:
   ```cmd
   python --version
   ```

### macOS

**Usando Homebrew (recomendado):**
```bash
brew install python3
```

**Ou baixe do site oficial:**
1. Acesse [python.org/downloads](https://www.python.org/downloads/)
2. Baixe o instalador para macOS
3. Execute o instalador

Verifique:
```bash
python3 --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip
```

Verifique:
```bash
python3 --version
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3
```

## Verificação da Instalação

Execute o seguinte comando para verificar se tudo está correto:

```bash
# Unix/macOS/Linux
python3 --version

# Windows
python --version
```

Deve exibir algo como: `Python 3.x.x`

## Estrutura de Diretórios

Certifique-se de que a estrutura do projeto está correta:

```
BENNER/
├── Dicionario de Dados.txt    ← Arquivo fonte
├── docs/
│   ├── parser_datadict.py     ← Parser
│   ├── datadict-explorer.html ← Interface
│   ├── datadict.json          ← Será gerado
│   └── ...
└── scripts/
    ├── generate-datadict.sh   ← Script Unix
    └── generate-datadict.bat  ← Script Windows
```

## Execução

### Unix/macOS/Linux

```bash
# Dar permissão de execução (primeira vez)
chmod +x scripts/generate-datadict.sh

# Executar
./scripts/generate-datadict.sh
```

### Windows

```cmd
scripts\generate-datadict.bat
```

## Troubleshooting

### "Python não encontrado"

**Windows:**
- Reinstale o Python marcando "Add Python to PATH"
- Ou adicione manualmente ao PATH:
  1. Abra "Configurações do Sistema"
  2. Variáveis de Ambiente
  3. PATH → Editar → Adicionar `C:\Python3x\` e `C:\Python3x\Scripts\`

**macOS/Linux:**
- Use `python3` ao invés de `python`
- Instale via gerenciador de pacotes

### "Arquivo não encontrado"

Verifique se você está no diretório correto:
```bash
cd /caminho/para/BENNER
ls "Dicionario de Dados.txt"
```

### "Erro de codificação"

O parser detecta automaticamente a codificação. Se houver problemas:
1. Verifique se o arquivo está em Latin-1 ou UTF-8
2. O parser tentará múltiplas codificações automaticamente

### "JSON não foi gerado"

1. Verifique as mensagens de erro no console
2. Certifique-se de que o arquivo de entrada existe
3. Verifique permissões de escrita no diretório `docs/`

## Suporte

Em caso de dúvidas ou problemas, consulte:
- `docs/README-DataDict.md` - Documentação geral
- `docs/EXAMPLES.md` - Exemplos de uso
- `docs/FEATURES.md` - Lista de funcionalidades
