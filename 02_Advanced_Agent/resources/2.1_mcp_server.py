# MCP concepts in this server (purpose + how to think about each):
#
# - Tool (@mcp.tool):
#   Purpose: give the assistant an “action” it can invoke on demand to get fresh data or perform work.
#   Tools are for functions that take arguments (e.g., a search query), run code or call an external API,
#   and return results to the model in a structured way. Use tools for operations you want the model to
#   decide to run at runtime (search, calculations, database lookups, etc.).
#
# - Resource (@mcp.resource("uri")):
#   Purpose: expose a specific, addressable piece of content (like a file/document) under a stable URI.
#   Resources are for “read this thing” access rather than “do an action.” In other words, calling a
#   resource should behave like fetching/reading content (similar to an HTTP GET): it returns text/data
#   and should not modify anything (no writes, no deletes, no state changes).

# - Prompt (@mcp.prompt):
#   Purpose: provide a reusable instruction/template that a client can load to set the assistant’s
#   behavior and boundaries for a task/session. Prompts are not actions and don’t fetch live data;
#   they define guidance like what the assistant should focus on, what tools/resources it may use,
#   and how it should respond in certain cases.

# https://modelcontextprotocol.io/docs/learn/server-concepts


from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict, Any
from requests import get


mcp = FastMCP("mcp_server")

tavily_client = TavilyClient()


# Tool for searching the web
@mcp.tool()
def search_web(query: str) -> Dict[str, Any]:
    """
    Search the web for information
    """

    results = tavily_client.search(query)

    return results


# Resources - provide access to langchain-ai repo files
@mcp.resource("github://langchain-ai/langchain-mcp-adapters/blob/main/README.md")
def github_file():
    """
    Resource for accessing langchain-ai/langchain-mcp-adapters/README.md file
    """

    url = f"https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/blob/main/README.md"
    try:
        resp = get(url)
        return resp.text
    except Exception as e:
        return f"Error: {str(e)}"


# Prompt template
@mcp.prompt()
def prompt():
    """
    Analyze data from a langchain-ai repo file with comprehensive insights
    """

    return """
        You are a helpful assistant that answers user questions about LangChain, LangGraph and LangSmith.

        You can use the following tools/resources to answer user questions:
        - search_web: Search the web for information
        - github_file: Access the langchain-ai repo files

        If the users asks a question that is not related to LangChain, LangGraph or LangSmith, you should say "I'm sorry, I can only answer questions about LangChain, LangGraph and LangSmith."

        You may try multiple tool and resource calls to answer the user's question.

        You may also ask clarifying questions to the user to better understand their question
    """


if __name__ == "__main__":
    mcp.run(transport="stdio")