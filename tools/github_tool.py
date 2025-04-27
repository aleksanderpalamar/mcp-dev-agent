from github import Github
import os
from typing import Dict, List, Optional
from tree_sitter import Language, Parser
import logging
import base64
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
from datetime import datetime
from .memory_tool import add_memory

logger = logging.getLogger(__name__)

class GithubTool:
    def __init__(self):
        self.gh = Github(os.getenv('GITHUB_TOKEN'))
        self._setup_parser()

    def _setup_parser(self):
        """Setup tree-sitter parser for code analysis"""
        try:
            Language.build_library(
                'build/languages.so',
                [
                    'vendor/tree-sitter-python',
                    'vendor/tree-sitter-javascript',
                    'vendor/tree-sitter-typescript'
                ]
            )
            self.PY_LANGUAGE = Language('build/languages.so', 'python')
            self.JS_LANGUAGE = Language('build/languages.so', 'javascript')
            self.TS_LANGUAGE = Language('build/languages.so', 'typescript')
            self.parser = Parser()
        except Exception as e:
            logger.warning(f"Could not setup tree-sitter: {e}")
            self.parser = None

    def analyze_code(self, content: str, language: str = 'python') -> Dict:
        """Analyze code content using tree-sitter"""
        if not self.parser:
            return {"error": "Code analysis not available"}

        try:
            if language == 'python':
                self.parser.set_language(self.PY_LANGUAGE)
            elif language == 'javascript':
                self.parser.set_language(self.JS_LANGUAGE)
            elif language == 'typescript':
                self.parser.set_language(self.TS_LANGUAGE)
            else:
                return {"error": f"Language {language} not supported"}

            tree = self.parser.parse(bytes(content, "utf8"))
            return {
                "functions": self._extract_functions(tree),
                "classes": self._extract_classes(tree),
                "imports": self._extract_imports(tree)
            }
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {"error": str(e)}

    def _extract_functions(self, tree) -> List[str]:
        """Extract function definitions from AST"""
        functions = []
        cursor = tree.walk()

        def visit_function():
            node = cursor.node
            if node.type == "function_definition":
                for child in node.children:
                    if child.type == "identifier":
                        functions.append(child.text.decode('utf8'))
                return True
            return False

        while cursor.goto_first_child() or cursor.goto_next_sibling():
            visit_function()

        return functions

    def _extract_classes(self, tree) -> List[str]:
        """Extract class definitions from AST"""
        classes = []
        cursor = tree.walk()

        def visit_class():
            node = cursor.node
            if node.type == "class_definition":
                for child in node.children:
                    if child.type == "identifier":
                        classes.append(child.text.decode('utf8'))
                return True
            return False

        while cursor.goto_first_child() or cursor.goto_next_sibling():
            visit_class()

        return classes

    def _extract_imports(self, tree) -> List[str]:
        """Extract imports from AST"""
        imports = []
        cursor = tree.walk()

        def visit_import():
            node = cursor.node
            if node.type in ["import_statement", "import_from_statement"]:
                imports.append(node.text.decode('utf8'))
                return True
            return False

        while cursor.goto_first_child() or cursor.goto_next_sibling():
            visit_import()

        return imports

    def summarize_text(self, text: str) -> str:
        """Use GPT to summarize text content"""
        try:
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em resumir issues do GitHub. Mantenha os resumos concisos e relevantes."},
                {"role": "user", "content": f"Resuma esta issue de forma concisa:\n\n{text}"}
            ],
            max_tokens=150)
            return response.choices[0].message.content
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
        for issue in issues[:10]:  # Limitar a 10 issues para não sobrecarregar
            result.append(f"""#{issue.number} - {issue.title}
State: {issue.state}
Created: {issue.created_at}
Labels: {', '.join([label.name for label in issue.labels])}
""")

        return "\n---\n".join(result) if result else "No issues found"
    except Exception as e:
        return f"Error getting issues: {str(e)}"

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
        issue = repo.get_issue(issue_number)

        # Preparar o contexto completo da issue
        comments = [comment.body for comment in issue.get_comments()]
        full_context = f"""Título: {issue.title}
Descrição: {issue.body}

Comentários:
{chr(10).join(f'- {comment}' for comment in comments)}"""

        # Gerar resumo usando GPT
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