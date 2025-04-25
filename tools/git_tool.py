from git import Repo
import os
from typing import List, Dict

class GitTool:
    def __init__(self):
        self.repo = None
        try:
            self.repo = Repo(os.getcwd())
        except:
            print("Not a git repository")

    def get_repo_info(self) -> Dict:
        """Get repository information."""
        if not self.repo:
            return {}
        
        active_branch = self.repo.active_branch
        remotes = [remote.url for remote in self.repo.remotes]
        return {
            "branch": str(active_branch),
            "remotes": remotes,
            "last_commit": str(self.repo.head.commit.hexsha[:7]),
            "author": str(self.repo.head.commit.author),
            "untracked": len(self.repo.untracked_files),
            "modified": len([item.a_path for item in self.repo.index.diff(None)]),
            "staged": len([item.a_path for item in self.repo.index.diff("HEAD")])
        }

    def get_file_diffs(self) -> List[Dict]:
        """Get diffs of modified files."""
        if not self.repo:
            return []
        
        diffs = []
        # Unstaged changes
        for diff in self.repo.index.diff(None):
            diffs.append({
                "file": diff.a_path,
                "status": "modified",
                "staged": False,
                "diff": diff.diff.decode('utf-8')
            })
        
        # Staged changes
        for diff in self.repo.index.diff("HEAD"):
            diffs.append({
                "file": diff.a_path,
                "status": "staged",
                "staged": True,
                "diff": diff.diff.decode('utf-8')
            })
        
        return diffs

async def get_commit_history(limit: int = 5) -> str:
    """Get the recent commit history."""
    tool = GitTool()
    if not tool.repo:
        return "No git repository found"
    
    commits = []
    for commit in tool.repo.iter_commits(max_count=limit):
        commits.append(f"Commit: {commit.hexsha[:7]}\nAuthor: {commit.author}\nMessage: {commit.message}")
    
    return "\n\n".join(commits)

async def get_issues() -> str:
    """Get open issues from the repository."""
    # Nota: Isso requer configuração adicional com GitHub/GitLab API
    return "Para acessar issues, é necessário configurar a integração com GitHub/GitLab API"

async def get_repo_info() -> str:
    """Get formatted repository information."""
    tool = GitTool()
    info = tool.get_repo_info()
    if not info:
        return "No git repository found"
    
    return f"""Repository Info:
Branch: {info['branch']}
Last Commit: {info['last_commit']} by {info['author']}
Remotes: {', '.join(info['remotes']) if info['remotes'] else 'No remotes'}
Status:
- {info['untracked']} untracked files
- {info['modified']} modified files
- {info['staged']} staged changes"""

async def get_diffs() -> str:
    """Get formatted diff information."""
    tool = GitTool()
    diffs = tool.get_file_diffs()
    if not diffs:
        return "No changes found"
    
    result = []
    for diff in diffs:
        result.append(f"""File: {diff['file']}
Status: {diff['status']} ({'staged' if diff['staged'] else 'unstaged'})
Changes:
{diff['diff']}
---""")
    
    return "\n\n".join(result)