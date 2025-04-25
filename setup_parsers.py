import os
import subprocess
from pathlib import Path

def setup_tree_sitter():
    """Setup tree-sitter parsers for code analysis"""
    # Create vendor directory
    vendor_dir = Path("vendor")
    vendor_dir.mkdir(exist_ok=True)
    
    # Define repositories to clone
    repos = {
        "tree-sitter-python": "https://github.com/tree-sitter/tree-sitter-python",
        "tree-sitter-javascript": "https://github.com/tree-sitter/tree-sitter-javascript",
        "tree-sitter-typescript": "https://github.com/tree-sitter/tree-sitter-typescript"
    }
    
    # Clone repositories
    os.chdir(vendor_dir)
    for name, url in repos.items():
        if not Path(name).exists():
            subprocess.run(["git", "clone", url, name], check=True)
    
    # Return to original directory
    os.chdir("..")
    
    # Create build directory
    Path("build").mkdir(exist_ok=True)

if __name__ == "__main__":
    setup_tree_sitter()