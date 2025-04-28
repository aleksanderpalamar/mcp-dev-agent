#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import subprocess

def is_git_repo(path):
    """Check if the current directory is a git repository"""
    try:
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                      cwd=path, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except:
        return False

def setup_project_directory(current_dir):
    """Setup required directories in the project"""
    # Criar pasta logs se não existir
    logs_dir = current_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    return True

def main():
    # Get the installation directory (where mcp-dev-agent is installed)
    install_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    
    # Get the current working directory
    current_dir = Path.cwd()
    
    if not is_git_repo(current_dir):
        print("❌ Error: O MCP Dev Agent CLI deve ser executado dentro de um repositório Git.")
        sys.exit(1)
    
    # Setup project directory structure
    setup_project_directory(current_dir)
    
    # Activate virtual environment and run the CLI
    if sys.platform == 'win32':
        python_path = install_dir / "venv" / "Scripts" / "python.exe"
        main_script = install_dir / "main.py"
    else:
        python_path = install_dir / "venv" / "bin" / "python"
        main_script = install_dir / "main.py"
    
    if not python_path.exists():
        print("❌ Error: Ambiente virtual não encontrado. Execute o script de instalação primeiro.")
        sys.exit(1)
    
    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(install_dir)
    
    try:
        # Execute o CLI no diretório atual
        process = subprocess.run([str(python_path), str(main_script), "--mode", "cli"],
                               cwd=current_dir,
                               env=env)
        sys.exit(process.returncode)
    except KeyboardInterrupt:
        print("\nEncerrando MCP Dev Agent CLI...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()