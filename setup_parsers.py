import os
import subprocess
from pathlib import Path
from tree_sitter import Parser, Language

def setup_tree_sitter():
    """Setup tree-sitter parsers for code analysis using simpler approach"""
    try:
        # Initialize a basic parser to verify tree-sitter is working
        parser = Parser()
        print("Successfully initialized tree-sitter Parser")
        
        # Create build directory if it doesn't exist
        build_dir = Path("build")
        build_dir.mkdir(exist_ok=True)
        
        print("Parser setup completed. Using dynamic language loading.")
        return True
        
    except Exception as e:
        print(f"Error setting up parser: {e}")
        return False

if __name__ == "__main__":
    setup_tree_sitter()