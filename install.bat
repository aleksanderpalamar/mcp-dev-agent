@echo off
echo Instalando MCP Dev Agent...

REM Verificar se Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado! Por favor, instale Python 3.x
    exit /b 1
)

REM Verificar se pip está instalado
pip --version > nul 2>&1
if errorlevel 1 (
    echo pip nao encontrado! Por favor, instale pip
    exit /b 1
)

REM Verificar se Ollama está instalado
ollama --version > nul 2>&1
if errorlevel 1 (
    echo Ollama nao encontrado! Por favor, instale Ollama de https://ollama.ai
    exit /b 1
)

REM Obter diretório atual
set INSTALL_DIR=%CD%

REM Criar ambiente virtual
python -m venv venv
call venv\Scripts\activate.bat

REM Instalar dependências
pip install -r requirements.txt

REM Criar arquivo .env se não existir
if not exist .env (
    echo Criando arquivo .env...
    echo GITHUB_TOKEN=seu_token_aqui > .env
    echo LOG_LEVEL=INFO >> .env
)

REM Criar diretório de logs se não existir
if not exist logs (
    mkdir logs
)

REM Criar comando global
echo @echo off > "%USERPROFILE%\mcp-dev-agent-cli.bat"
echo python "%INSTALL_DIR%\mcp_cli.py" %%* >> "%USERPROFILE%\mcp-dev-agent-cli.bat"

REM Adicionar ao PATH se não existir
set "PATH_ENTRY=%USERPROFILE%"
echo %PATH% | find /i "%PATH_ENTRY%" > nul
if errorlevel 1 (
    setx PATH "%PATH%;%PATH_ENTRY%"
    set "PATH=%PATH%;%PATH_ENTRY%"
)

REM Dar permissão de execução ao mcp_cli.py
copy NUL > "%INSTALL_DIR%\mcp_cli.py.executable"

echo.
echo Instalacao concluida! O comando 'mcp-dev-agent-cli' esta disponivel globalmente.
echo.
echo Para usar:
echo 1. Configure seu token do GitHub no arquivo .env
echo 2. Entre em qualquer repositório git
echo 3. Execute: mcp-dev-agent-cli
echo.
echo IMPORTANTE: Execute sempre dentro de um repositorio git!