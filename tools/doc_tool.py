import os
import json
from pathlib import Path
from typing import Dict
import ollama
import logging

logger = logging.getLogger(__name__)

def load_agent_config() -> Dict:
    """Load agent configuration from .agent.json"""
    config_path = Path('.agent.json')
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)

class DocSearchTool:
    def __init__(self):
        self.config = load_agent_config()
        self.model = "codellama" # Default model for documentation
        
    def search_with_ai(self, query: str) -> str:
        """Use local Ollama model to provide documentation and explanations"""
        try:
            print("🤖 Iniciando pesquisa com CodeLlama...")
            print("⏳ Buscando documentação, por favor aguarde...")
            
            # System message and query combined in the prompt
            prompt = f"""You are a documentation assistant specialized in programming and development. 
When asked about technologies, libraries, or programming concepts, provide clear, concise explanations with relevant code examples.
Focus on best practices and practical usage examples.

Query: {query}"""

            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                stream=False
            )
            
            print("✅ Pesquisa concluída!")
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Error using AI search: {e}")
            return f"Error searching documentation: {str(e)}"

async def search_docs(query: str) -> str:
    """Search for documentation using local AI model."""
    try:
        doc_tool = DocSearchTool()
        result = doc_tool.search_with_ai(query)
        return f"Documentation Results (using {doc_tool.model}):\n{result}"
            
    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        return f"Error searching documentation: {str(e)}"