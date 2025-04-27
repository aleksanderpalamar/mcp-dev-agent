import os
import json
from pathlib import Path
from typing import Dict
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
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

    def search_with_ai(self, query: str) -> str:
        """Use AI to provide documentation and explanations"""
        try:
            response = client.chat.completions.create(model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """You are a documentation assistant specialized in programming and development. 
When asked about technologies, libraries, or programming concepts, provide clear, concise explanations with relevant code examples.
Focus on best practices and practical usage examples."""},
                {"role": "user", "content": f"I need documentation/explanation about: {query}"}
            ],
            max_tokens=500,
            temperature=0.3)
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error using AI search: {e}")
            return f"Error searching documentation: {str(e)}"

async def search_docs(query: str) -> str:
    """Search for documentation using AI."""
    try:
        doc_tool = DocSearchTool()
        result = doc_tool.search_with_ai(query)
        return f"Documentation Results:\n{result}"

    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        return f"Error searching documentation: {str(e)}"