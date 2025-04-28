from github import Github, GithubException
import os
from typing import Dict, List, Optional
from tree_sitter import Parser
import logging
import base64
import ollama
from datetime import datetime
from .memory_tool import add_memory

logger = logging.getLogger(__name__)

class GithubTool:
    def __init__(self):
        self.gh = Github(os.getenv('GITHUB_TOKEN'))
        self.parser = Parser()
        self.model = "codellama" # Default model for code-related tasks

    def analyze_code(self, content: str, language: str = 'python') -> Dict:
        """Analyze code content using basic parsing"""
        try:
            # Basic code analysis without tree-sitter language specifics
            lines = content.split('\n')
            analysis = {
                "functions": self._find_functions(lines, language),
                "classes": self._find_classes(lines, language),
                "imports": self._find_imports(lines, language)
            }
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {"error": str(e)}

    def _find_functions(self, lines: List[str], language: str) -> List[str]:
        """Find function definitions using basic text analysis"""
        functions = []
        if language == 'python':
            for line in lines:
                if line.strip().startswith('def '):
                    name = line.split('def ')[1].split('(')[0].strip()
                    functions.append(name)
        elif language in ['javascript', 'typescript']:
            for line in lines:
                line = line.strip()
                if 'function ' in line or '=>' in line:
                    if 'function ' in line:
                        name = line.split('function ')[1].split('(')[0].strip()
                        if name:
                            functions.append(name)
                    # Add basic support for arrow functions with names
                    elif '=' in line and '=>' in line:
                        name = line.split('=')[0].strip()
                        if name:
                            functions.append(name)
        return functions

    def _find_classes(self, lines: List[str], language: str) -> List[str]:
        """Find class definitions using basic text analysis"""
        classes = []
        if language == 'python':
            for line in lines:
                if line.strip().startswith('class '):
                    name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    classes.append(name)
        elif language in ['javascript', 'typescript']:
            for line in lines:
                if line.strip().startswith('class '):
                    name = line.split('class ')[1].split('{')[0].split('extends')[0].strip()
                    classes.append(name)
        return classes

    def _find_imports(self, lines: List[str], language: str) -> List[str]:
        """Find imports using basic text analysis"""
        imports = []
        if language == 'python':
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
        elif language in ['javascript', 'typescript']:
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('require('):
                    imports.append(line)
        return imports

    def summarize_text(self, text: str) -> str:
        """Use local Ollama model to summarize text content"""
        try:
            prompt = """You are a specialized assistant for summarizing GitHub issues. Create concise, relevant summaries that capture the main points, proposed solutions, and key decisions.

Issue to summarize:
"""
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt + text
                }],
                stream=False
            )
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return "Não foi possível gerar um resumo."

async def get_repo_details(repo_name: str) -> str:
    """Get detailed information about a GitHub repository"""
    try:
        tool = GithubTool()
        repo = tool.gh.get_repo(repo_name)

        # Coletar informações básicas
        info = {
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "language": repo.language,
            "topics": repo.get_topics()
        }

        return f"""Repository: {info['name']}
Description: {info['description']}
Stars: {info['stars']} | Forks: {info['forks']} | Open Issues: {info['open_issues']}
Main Language: {info['language']}
Topics: {', '.join(info['topics'])}"""
    except Exception as e:
        return f"Error getting repository details: {str(e)}"

async def get_repository_issues(repo_name: str, state: str = "open") -> str:
    """Get issues from a GitHub repository"""
    try:
        tool = GithubTool()
        repo = tool.gh.get_repo(repo_name)
        issues = repo.get_issues(state=state)

        result = []
        result.append(f"\nIssues do repositório {repo_name} ({state}):\n")
        
        for issue in issues[:10]:  # Limitar a 10 issues para não sobrecarregar
            result.append(f"""📎 Issue #{issue.number}
Título: {issue.title}
Status: {issue.state}
Criado em: {issue.created_at.strftime('%d/%m/%Y')}
Labels: {', '.join([label.name for label in issue.labels])}
URL: {issue.html_url}
""")

        if not result[1:]:  # Se não há issues (apenas o cabeçalho)
            return f"Nenhuma issue encontrada no repositório {repo_name} com status '{state}'"
            
        return "\n---\n".join(result)
    except Exception as e:
        return f"Erro ao buscar issues: {str(e)}"

async def analyze_file_content(content: str, language: str = "python") -> str:
    """Analyze code content and provide insights"""
    try:
        tool = GithubTool()
        analysis = tool.analyze_code(content, language)

        if "error" in analysis:
            return f"Error analyzing code: {analysis['error']}"

        return f"""Code Analysis:
Functions: {', '.join(analysis['functions'])}
Classes: {', '.join(analysis['classes'])}
Imports: {', '.join(analysis['imports'])}"""
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

async def search_github_code(query: str, language: Optional[str] = None) -> str:
    """Search for code in GitHub"""
    try:
        tool = GithubTool()
        query_str = query
        if language:
            query_str += f" language:{language}"

        results = tool.gh.search_code(query_str)
        found = []

        for item in results[:5]:  # Limitar a 5 resultados
            content = base64.b64decode(item.content).decode('utf-8')
            found.append(f"""File: {item.path}
Repository: {item.repository.full_name}
URL: {item.html_url}
Snippet:
{content[:300]}...
""")

        return "\n---\n".join(found) if found else "No code found"
    except Exception as e:
        return f"Error searching code: {str(e)}"

async def get_pull_requests(repo_name: str, state: str = "open") -> str:
    """Get pull requests from a GitHub repository"""
    try:
        tool = GithubTool()
        repo = tool.gh.get_repo(repo_name)
        prs = repo.get_pulls(state=state)

        result = []
        for pr in prs[:10]:  # Limitar a 10 PRs
            result.append(f"""#{pr.number} - {pr.title}
Status: {pr.state}
Autor: {pr.user.login}
Criado em: {pr.created_at}
Branch: {pr.head.ref} → {pr.base.ref}
Reviews: {pr.get_reviews().totalCount}
{pr.html_url}
""")

        return "\n---\n".join(result) if result else "Nenhum Pull Request encontrado"
    except Exception as e:
        return f"Erro ao buscar Pull Requests: {str(e)}"

async def get_project_info(org_name: str, project_number: int) -> str:
    """Get information about a GitHub Project (Project V2)"""
    try:
        tool = GithubTool()
        org = tool.gh.get_organization(org_name)
        projects = org.get_projects(state='open')

        for project in projects:
            if project.number == project_number:
                columns = project.get_columns()
                result = [f"Projeto: {project.name}\nDescrição: {project.body or 'N/A'}\n\nColunas:"]

                for column in columns:
                    cards = column.get_cards()
                    items = [f"- {card.get_content().title if card.get_content() else card.note}" 
                            for card in cards[:5]]  # Limitar a 5 cards por coluna
                    result.append(f"\n{column.name} ({cards.totalCount} items):")
                    result.extend(items)
                    if cards.totalCount > 5:
                        result.append("  ...")

                return "\n".join(result)

        return "Projeto não encontrado"
    except Exception as e:
        return f"Erro ao buscar informações do projeto: {str(e)}"

async def summarize_issue(repo_name: str, issue_number: int) -> str:
    """Get and summarize a GitHub issue"""
    try:
        tool = GithubTool()
        repo = tool.gh.get_repo(repo_name)
        
        try:
            issue = repo.get_issue(issue_number)
        except GithubException as e:
            if e.status == 404:
                return f"Issue #{issue_number} não encontrada no repositório {repo_name}"
            raise e

        # Preparar o contexto completo da issue
        comments = [comment.body for comment in issue.get_comments()]
        full_context = f"""Título: {issue.title}
Descrição: {issue.body}

Comentários:
{chr(10).join(f'- {comment}' for comment in comments)}"""

        # Gerar resumo usando modelo local
        summary = tool.summarize_text(full_context)

        # Salvar o resumo na memória
        metadata = {
            "issue_number": issue_number,
            "repo": repo_name,
            "timestamp": datetime.now().isoformat()
        }
        await add_memory(
            f"Resumo da issue #{issue_number} do repositório {repo_name}:\n{summary}",
            context_type="issue_summary",
            metadata=metadata
        )

        return f"""Issue #{issue_number}: {issue.title}

Resumo Automático:
{summary}

Status: {issue.state}
Autor: {issue.user.login}
Criado em: {issue.created_at}
Labels: {', '.join(label.name for label in issue.labels)}
URL: {issue.html_url}"""
        
    except Exception as e:
        return f"Erro ao resumir issue: {str(e)}"