from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from .rag import vectorstore

web_search = TavilySearchResults()


@tool
def pdf_search(question: str) -> str:
    """
    Search inside PDF documents and return relevant information.
    """
    docs = vectorstore.similarity_search(question)

    if not docs:
        return "No relevant information found in PDF."

    return "\n".join([doc.page_content for doc in docs])