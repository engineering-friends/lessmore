from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_playground.deps.init_deps import init_deps
from langchain_text_splitters import RecursiveCharacterTextSplitter


def test():
    # - Simple call
    pass


if __name__ == "__main__":
    deps = init_deps()
    test()
