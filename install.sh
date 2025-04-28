#!/bin/bash

echo "Instalando MCP Dev Agent..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python não encontrado! Por favor, instale Python 3.x"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "pip não encontrado! Por favor, instale pip"
    exit 1
fi

# Verificar se Ollama está instalado
if ! command -v ollama &> /dev/null; then
    echo "Ollama não encontrado! Por favor, instale Ollama de https://ollama.ai"
    exit 1
fi

# Obter diretório absoluto de instalação
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "Criando arquivo .env..."
    echo "GITHUB_TOKEN=seu_token_aqui" > .env
    echo "LOG_LEVEL=INFO" >> .env
fi

# Criar diretório de logs se não existir
mkdir -p logs

# Dar permissão de execução aos scripts
chmod +x mcp_cli.py
chmod +x main.py

# Criar link simbólico global
if [[ "$OSTYPE" == "darwin"* ]]; then
    # MacOS
    INSTALL_PATH="/usr/local/bin/mcp-dev-agent-cli"
else
    # Linux
    INSTALL_PATH="/usr/local/bin/mcp-dev-agent-cli"
fi

# Criar wrapper script
cat > "$INSTALL_DIR/mcp-dev-agent-cli-wrapper" << EOF
#!/bin/bash
INSTALL_DIR="$INSTALL_DIR"
"\$INSTALL_DIR/venv/bin/python" "\$INSTALL_DIR/mcp_cli.py" "\$@"
EOF

chmod +x "$INSTALL_DIR/mcp-dev-agent-cli-wrapper"

# Instalar globalmente (requer sudo)
echo "Criando comando global (requer senha de administrador)..."
sudo ln -sf "$INSTALL_DIR/mcp-dev-agent-cli-wrapper" "$INSTALL_PATH"

echo
echo "Instalação concluída! O comando 'mcp-dev-agent-cli' está disponível globalmente."
echo
echo "Para usar:"
echo "1. Configure seu token do GitHub no arquivo .env"
echo "2. Entre em qualquer repositório git"
echo "3. Execute: mcp-dev-agent-cli"
echo
echo "IMPORTANTE: Execute sempre dentro de um repositório git!"