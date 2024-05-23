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

    llm = ChatOpenAI(model_name="gpt-4o")

    #  - Test run

    document_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            """Answer the following question based only on the provided context:

    <context>
    {context}
    </context>

    Question: {input}"""
        ),
    )

    print(
        document_chain.invoke(
            {
                "input": "how can langsmith help with testing?",
                "context": [Document(page_content="langsmith can let you visualize test results")],
            }
        )
    )

    response = create_retrieval_chain(
        FAISS.from_documents(
            documents=RecursiveCharacterTextSplitter().split_documents(
                WebBaseLoader("https://docs.smith.langchain.com/user_guide").load()
            ),
            embedding=OpenAIEmbeddings(),
        ).as_retriever(),
        document_chain,
    ).invoke({"input": "how can langsmith help with testing?"})

    print(response["answer"])


if __name__ == "__main__":
    deps = init_deps()
    test()
