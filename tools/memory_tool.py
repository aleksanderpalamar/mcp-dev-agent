import chromadb
import json
from datetime import datetime
from typing import Dict, Optional

client = chromadb.Client()
collection = client.get_or_create_collection("memory")

async def add_memory(content: str, context_type: str = "general", metadata: Optional[Dict] = None) -> str:
    """Add a memory to the database with context type and metadata."""
    if metadata is None:
        metadata = {}
    
    # Adiciona metadados padrão
    metadata.update({
        "timestamp": datetime.now().isoformat(),
        "context_type": context_type
    })
    
    memory_id = f"mem-{hash(content)}-{context_type}"
    collection.add(
        documents=[content],
        ids=[memory_id],
        metadatas=[metadata]
    )
    
    return f"Memory added [{context_type}]: {content[:100]}..."

async def get_memory(query: str, context_type: Optional[str] = None) -> str:
    """Retrieve memories from the database with optional context type filter."""
    where_filter = {"context_type": context_type} if context_type else None
    
    results = collection.query(
        query_texts=[query],
        n_results=3,
        where=where_filter
    )
    
    if not results['documents'][0]:
        return "No memory found."
        
    memories = []
    for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
        context = metadata.get('context_type', 'general')
        timestamp = metadata.get('timestamp', 'Unknown time')
        memories.append(f"[{context} - {timestamp}] {doc}")
    
    return "\n\n".join(memories)

async def add_repo_memory(content: str, git_context: Dict) -> str:
    """Add a memory specifically about the repository state."""
    metadata = {
        "branch": git_context.get("branch", "unknown"),
        "commit": git_context.get("last_commit", "unknown"),
        "files_changed": git_context.get("modified", 0) + git_context.get("staged", 0)
    }
    
    return await add_memory(content, context_type="repository", metadata=metadata)

async def get_repo_memory(query: str) -> str:
    """Retrieve repository-specific memories."""
    return await get_memory(query, context_type="repository")