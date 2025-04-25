async def search_docs(query: str) -> str:
    """Search the documentation for a given query."""
    with open("docs/api_reference.md", "r") as f:
        content = f.read()
        if query.lower() in content.lower():
            return f"Found '{query}' in the documentation."
        else:
            return f"'{query}' not found in the documentation."