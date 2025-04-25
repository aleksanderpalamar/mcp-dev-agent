from mcp.server.fastmcp import FastMCP
from tools.memory_tool import add_memory, get_memory, add_repo_memory, get_repo_memory
from tools.doc_tool import search_docs
from tools.git_tool import get_commit_history, get_issues, get_repo_info, get_diffs
import argparse
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def load_agent_config():
    """Load agent configuration from .agent.json"""
    config_path = Path('.agent.json')
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Resolve environment variables
    if config.get('security', {}).get('use_env_variables'):
        required_vars = config.get('security', {}).get('required_env_vars', [])
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Required environment variables not found: {', '.join(missing_vars)}")
    
    return config

# Configurar logging
import logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)

config = load_agent_config()
mcp = FastMCP("pair_programming_agent", config=config)
# Registro das ferramentas de memória
mcp.add_tool(add_memory)
mcp.add_tool(get_memory)
mcp.add_tool(add_repo_memory)
mcp.add_tool(get_repo_memory)

# Registro das ferramentas de documentação
mcp.add_tool(search_docs)

# Registro das ferramentas Git
mcp.add_tool(get_commit_history)
mcp.add_tool(get_issues)
mcp.add_tool(get_repo_info)
mcp.add_tool(get_diffs)

async def cli_interaction():
    print("CLI Mode - Digite 'exit' para sair")
    print("Comandos disponíveis:")
    print("  /memory add <conteúdo> - Adicionar memória")
    print("  /memory get <consulta> - Buscar memória")
    print("  /memory repo add <conteúdo> - Adicionar memória do repositório")
    print("  /memory repo get <consulta> - Buscar memória do repositório")
    print("  /docs <consulta> - Buscar documentação")
    print("  /git commits [número] - Ver histórico de commits")
    print("  /git issues - Ver issues")
    print("  /git info - Ver informações do repositório")
    print("  /git diff - Ver alterações pendentes")
    
    while True:
        try:
            command = input("\nDigite seu comando: ").strip()
            
            if command.lower() == 'exit':
                break
                
            if command.startswith('/'):
                parts = command[1:].split()
                if not parts:
                    continue
                    
                if parts[0] == 'memory':
                    if len(parts) < 2:
                        print("Uso: /memory [add|get|repo] <conteúdo>")
                        continue
                        
                    if parts[1] == 'repo':
                        if len(parts) < 3:
                            print("Uso: /memory repo [add|get] <conteúdo>")
                            continue
                            
                        if parts[2] == 'add':
                            content = ' '.join(parts[3:])
                            # Obter contexto do git antes de adicionar memória
                            git_info = await get_repo_info()
                            git_context = {}
                            for line in git_info.split('\n'):
                                if line.startswith('Branch:'):
                                    git_context['branch'] = line.split(': ')[1]
                                elif line.startswith('Last Commit:'):
                                    git_context['last_commit'] = line.split(': ')[1].split(' ')[0]
                            result = await add_repo_memory(content, git_context)
                        elif parts[2] == 'get':
                            query = ' '.join(parts[3:])
                            result = await get_repo_memory(query)
                    elif parts[1] == 'add':
                        content = ' '.join(parts[2:])
                        result = await add_memory(content)
                    elif parts[1] == 'get':
                        query = ' '.join(parts[2:])
                        result = await get_memory(query)
                
                elif parts[0] == 'docs':
                    if len(parts) < 2:
                        print("Uso: /docs <consulta>")
                        continue
                    query = ' '.join(parts[1:])
                    result = await search_docs(query)
                
                elif parts[0] == 'git':
                    if len(parts) < 2:
                        print("Uso: /git [commits|issues|info|diff]")
                        continue
                    if parts[1] == 'commits':
                        limit = int(parts[2]) if len(parts) > 2 else 5
                        result = await get_commit_history(limit)
                    elif parts[1] == 'issues':
                        result = await get_issues()
                    elif parts[1] == 'info':
                        result = await get_repo_info()
                    elif parts[1] == 'diff':
                        result = await get_diffs()
                
                else:
                    result = "Comando desconhecido"
                
                print(result)
                
                # Se houver alterações no git, salvar automaticamente na memória
                if parts[0] == 'git' and parts[1] in ['info', 'diff']:
                    git_info = await get_repo_info()
                    if 'modified files' in git_info or 'staged changes' in git_info:
                        diff_info = await get_diffs()
                        await add_repo_memory(
                            f"Estado do repositório:\n{git_info}\n\nMudanças:\n{diff_info}",
                            {}
                        )
            else:
                print("Comandos devem começar com '/'")
                
        except Exception as e:
            print(f"Erro: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MCP Development Agent')
    parser.add_argument('--mode', choices=['cli', 'server'], default='server',
                      help='Modo de operação (cli ou server)')
    args = parser.parse_args()
    
    if args.mode == 'cli':
        asyncio.run(cli_interaction())
    else:
        mcp.run(transport="sse")  # Server-Sent Events for HTTP transport