from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import pathlib


paths = list(pathlib.Path("./data").glob("**/*.pdf"))

docs = []
for path in paths:
    loader = PyPDFLoader(path)
    docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
chunks = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db"
)