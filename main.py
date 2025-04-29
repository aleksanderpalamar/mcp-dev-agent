from datetime import datetime
from mcp.server.fastmcp import FastMCP
from tools.memory_tool import add_memory, get_memory, add_repo_memory, get_repo_memory
from tools.doc_tool import search_docs
from tools.git_tool import get_commit_history, get_issues, get_repo_info, get_diffs
from tools.github_tool import (
    get_repo_details, get_repository_issues, analyze_file_content, search_github_code,
    get_pull_requests, get_project_info, summarize_issue
)
import argparse
import asyncio
import json
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import uuid
import git
from rich.console import Console
from rich.panel import Panel
from rich.box import SQUARE
from rich.text import Text

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

console = Console()

def print_result(result):
    """Print command result with border"""
    if result:
        if isinstance(result, (list, dict)):
            result = json.dumps(result, indent=2, ensure_ascii=False)
        console.print(Panel(str(result), box=SQUARE))
    console.print()

def get_git_info():
    """Get git branch and status"""
    try:
        repo = git.Repo(os.getcwd())
        branch = repo.active_branch.name
        changes = len(repo.index.diff(None)) + len(repo.untracked_files)
        return f"git:({branch})±{changes}" if changes > 0 else f"git:({branch})"
    except:
        return ""

def print_cli_header():
    """Print CLI header with rich formatting"""
    # Get virtual env name
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        venv = os.path.basename(venv)
    
    # Get current directory
    current_dir = os.path.basename(os.getcwd())
    
    # Get git info
    git_info = get_git_info()
    
    # Print header line with dim style
    if venv:
        console.print(f"{venv} ~/{current_dir} {git_info}", style="dim")
    
    # Print title in box using rich Panel
    title = Text("MCP Dev Agent (research preview) v0.1.0", style="white")
    console.print(Panel(title, box=SQUARE))
    console.print()
    
    # Session info with proper formatting
    session_id = str(uuid.uuid4())[:8] + "-" + str(uuid.uuid4())[:4] + "-" + str(uuid.uuid4())[:4] + "-" + str(uuid.uuid4())[:4] + "-"
    workdir = os.getcwd()
    console.print(f"localhost session: {session_id}")
    
    # Print info with proper indentation using dim style for the L symbols
    console.print(Text("└", style="dim") + f" workdir: {workdir}")
    console.print(Text("└", style="dim") + " model: codellama")
    console.print()

def print_help():
    """Print help information about available commands"""
    help_text = """
🔥 MCP Dev Agent - Comandos Disponíveis

🧠 Comandos de Memória:
  /memory add <conteúdo>         - Adicionar nova memória geral
  /memory get <consulta>         - Buscar memórias existentes
  /memory repo add <conteúdo>    - Adicionar memória específica do repositório
  /memory repo get <consulta>    - Buscar memórias do repositório

🔄 Comandos Git:
  /git commits [número]          - Mostrar histórico de commits (padrão: últimos 5)
  /git issues                    - Listar issues do repositório local
  /git info                      - Mostrar informações detalhadas do repositório
  /git diff                      - Mostrar mudanças pendentes (staged e unstaged)

🌐 Comandos GitHub:
  /github repo <owner/repo>      - Mostrar detalhes do repositório
  /github issues <owner/repo>    - Listar issues (state: open/closed)
  /github prs <owner/repo>       - Listar pull requests (state: open/closed)
  /github project <org> <number> - Mostrar informações do projeto
  /github summarize <owner/repo> - Gerar resumo da issue usando GPT
  /github search <query>         - Buscar código no GitHub

💻 Análise de Código e Documentação:
  /code analyze <file>           - Analisar estrutura do código
  /docs <query>                  - Buscar documentação

⚡ Outros Comandos:
  /help                          - Mostrar esta mensagem de ajuda
  exit                           - Sair do CLI
"""
    print(help_text)

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

def setup_logging():
    """Configure logging to use current directory"""
    current_dir = Path.cwd()
    log_file = current_dir / 'logs' / 'agent.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
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

# Registro das ferramentas Git e GitHub
mcp.add_tool(get_commit_history)
mcp.add_tool(get_issues)
mcp.add_tool(get_repo_info)
mcp.add_tool(get_diffs)
mcp.add_tool(get_repo_details)
mcp.add_tool(get_repository_issues)
mcp.add_tool(analyze_file_content)
mcp.add_tool(search_github_code)
mcp.add_tool(get_pull_requests)
mcp.add_tool(get_project_info)
mcp.add_tool(summarize_issue)

async def cli_interaction():
    """Interactive CLI with modern UI"""
    print_cli_header()
    
    while True:
        try:
            command = input("> ").strip()
            
            if command.lower() == 'exit':
                break
            
            if command.startswith('/'):
                parts = command[1:].split()
                if not parts:
                    continue

                if parts[0] == 'help':
                    print_help()
                    continue

                if parts[0] == 'docs':
                    if len(parts) < 2:
                        print("Uso: /docs <consulta>")
                        continue
                    query = ' '.join(parts[1:])
                    result = await search_docs(query)
                    print_result(result)
                    continue
                
                elif parts[0] == 'git':
                    if len(parts) < 2:
                        print("Uso: /git [commits|issues|info|diff]")
                        continue
                    if parts[1] == 'commits':
                        limit = int(parts[2]) if len(parts) > 2 else 5
                        result = await get_commit_history(limit)
                        print_result(result)
                        continue
                    elif parts[1] == 'issues':
                        result = await get_issues()
                        print_result(result)
                        continue
                    elif parts[1] == 'info':
                        result = await get_repo_info()
                        print_result(result)
                        continue
                    elif parts[1] == 'diff':
                        result = await get_diffs()
                        print_result(result)
                        continue

                elif parts[0] == 'memory':
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
                            print_result(result)
                            continue
                        elif parts[2] == 'get':
                            query = ' '.join(parts[3:])
                            result = await get_repo_memory(query)
                            print_result(result)
                            continue
                    elif parts[1] == 'add':
                        content = ' '.join(parts[2:])
                        result = await add_memory(content)
                        print_result(result)
                        continue
                    elif parts[1] == 'get':
                        query = ' '.join(parts[2:])
                        result = await get_memory(query)
                        print_result(result)
                        continue

                elif parts[0] == 'github':
                    if len(parts) < 3:
                        print("Uso: /github [repo|issues|prs|project|summarize|search] <args>")
                        continue
                        
                    if parts[1] == 'repo':
                        result = await get_repo_details(parts[2])
                        print_result(result)
                        continue
                    elif parts[1] == 'issues':
                        state = parts[3] if len(parts) > 3 else 'open'
                        result = await get_repository_issues(parts[2], state)
                        print_result(result)
                        continue
                    elif parts[1] == 'prs':
                        state = parts[3] if len(parts) > 3 else 'open'
                        result = await get_pull_requests(parts[2], state)
                        print_result(result)
                        continue
                    elif parts[1] == 'project':
                        if len(parts) < 4:
                            print("Uso: /github project <org> <number>")
                            continue
                        result = await get_project_info(parts[2], int(parts[3]))
                        print_result(result)
                        continue
                    elif parts[1] == 'summarize':
                        if len(parts) < 4:
                            print("Uso: /github summarize <owner/repo> <issue_number>")
                            continue
                        result = await summarize_issue(parts[2], int(parts[3]))
                        print_result(result)
                        continue
                    elif parts[1] == 'search':
                        query = ' '.join(parts[2:])
                        language = None
                        if ' in:' in query:
                            query, language = query.split(' in:', 1)
                        result = await search_github_code(query, language)
                    
                    # Salvar automaticamente na memória resultados relevantes
                    if parts[1] in ['summarize', 'project']:
                        await add_memory(
                            result,
                            context_type=f"github_{parts[1]}",
                            metadata={"command": command, "timestamp": datetime.now().isoformat()}
                        )

                elif parts[0] == 'code':
                    if len(parts) < 3:
                        print("Uso: /code analyze <file> [language]")
                        continue
                    
                    if parts[1] == 'analyze':
                        file_path = parts[2]
                        language = parts[3] if len(parts) > 3 else None
                        
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                            
                            # Inferir linguagem do arquivo se não especificada
                            if not language:
                                if file_path.endswith('.py'):
                                    language = 'python'
                                elif file_path.endswith('.js'):
                                    language = 'javascript'
                                elif file_path.endswith('.ts'):
                                    language = 'typescript'
                                else:
                                    language = 'python'  # default
                            
                            result = await analyze_file_content(content, language)
                        except FileNotFoundError:
                            result = f"Erro: Arquivo '{file_path}' não encontrado"
                        except Exception as e:
                            result = f"Erro ao analisar arquivo: {str(e)}"
                        print_result(result)
                        continue
                    else:
                        result = "Subcomando desconhecido. Use: /code analyze <file> [language]"
                        print_result(result)
                        continue
                else:
                    print("Comando desconhecido. Use /help para ver os comandos disponíveis.")
            else:
                print("Por favor, use comandos que começam com /")
                
            # Ask if user wants to continue
            continue_response = input("Continue to iterate? (y/n): ").strip().lower()
            if continue_response != 'y':
                break
                
        except Exception as e:
            print(f"Erro: {str(e)}")

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser(description='MCP Development Agent')
    parser.add_argument('--mode', choices=['cli', 'server'], default='server',
                      help='Modo de operação (cli ou server)')
    args = parser.parse_args()
    
    if args.mode == 'cli':
        asyncio.run(cli_interaction())
    else:
        mcp.run(transport="sse")  # Server-Sent Events for HTTP transport