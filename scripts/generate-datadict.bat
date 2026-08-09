@echo off
REM =============================================================================
REM Script para gerar o Dicionário de Dados Benner (Windows)
REM =============================================================================
REM
REM Uso:
REM   scripts\generate-datadict.bat
REM
REM Este script:
REM   1. Verifica pré-requisitos (Python 3)
REM   2. Executa o parser para gerar o JSON
REM   3. Exibe instruções para visualização
REM
REM =============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Gerador de Dicionario de Dados - Benner
echo ============================================================
echo.

REM Diretórios
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
set "DOCS_DIR=%ROOT_DIR%\docs"

REM Verificar Python
echo [INFO] Verificando pre-requisitos...

where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERRO] Python nao encontrado.
        echo.
        echo Por favor, instale o Python 3:
        echo   https://www.python.org/downloads/
        echo.
        echo Certifique-se de marcar "Add Python to PATH" durante a instalacao.
        exit /b 1
    ) else (
        set "PYTHON_CMD=python3"
    )
) else (
    set "PYTHON_CMD=python"
)

echo [OK] Python encontrado
%PYTHON_CMD% --version

REM Verificar arquivo de entrada
set "INPUT_FILE=%ROOT_DIR%\Dicionario de Dados.txt"
if not exist "%INPUT_FILE%" (
    echo [ERRO] Arquivo de entrada nao encontrado:
    echo   %INPUT_FILE%
    exit /b 1
)

echo [OK] Arquivo de entrada encontrado

REM Verificar parser
set "PARSER_FILE=%DOCS_DIR%\parser_datadict.py"
if not exist "%PARSER_FILE%" (
    echo [ERRO] Parser nao encontrado:
    echo   %PARSER_FILE%
    exit /b 1
)

echo [OK] Parser encontrado

REM Executar parser
echo.
echo [INFO] Executando parser...
echo.

cd /d "%DOCS_DIR%"
%PYTHON_CMD% parser_datadict.py "%INPUT_FILE%" "datadict.json"

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao executar o parser
    exit /b 1
)

REM Verificar se JSON foi gerado
set "OUTPUT_FILE=%DOCS_DIR%\datadict.json"
if not exist "%OUTPUT_FILE%" (
    echo [ERRO] JSON nao foi gerado
    exit /b 1
)

REM Resultado
echo.
echo ============================================================
echo   Dicionario de Dados gerado com sucesso!
echo ============================================================
echo.
echo Arquivos gerados:
echo   * docs\datadict.json
echo.
echo Para visualizar:
echo   Abra o arquivo no navegador:
echo   docs\datadict-explorer.html
echo.
echo   Comando:
echo   start docs\datadict-explorer.html
echo.
echo ============================================================

REM Perguntar se deseja abrir
echo.
set /p OPEN_NOW="Deseja abrir o explorador agora? (S/N): "
if /i "%OPEN_NOW%"=="S" (
    start "" "%DOCS_DIR%\datadict-explorer.html"
)

endlocal
