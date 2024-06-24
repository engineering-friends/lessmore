from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import create_retriever_tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_playground.deps import Deps
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.prebuilt import chat_agent_executor


def test():
    # - Prompt

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a world class technical documentation writer."),
            ("user", "{input}"),
        ]
    )

    # - Retreiver tool

    retriever_tool = create_retriever_tool(
        retriever=FAISS.from_documents(
            documents=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(
                WebBaseLoader("https://docs.smith.langchain.com/overview").load()
            ),
            embedding=OpenAIEmbeddings(),
        ).as_retriever(),
        name="langsmith_search",
        description="Search for information about LangSmith. For any questions about LangSmith, you must use this tool!",
    )

    model_with_tools = ChatOpenAI(model_name="gpt-4o").bind_tools([retriever_tool])

    # - Run basic one

    response = model_with_tools.invoke([HumanMessage(content="Hi!")])

    print(f"ContentString: {response.content}")
    print(f"ToolCalls: {response.tool_calls}")
    """
    ContentString: Hello! How can I assist you today?
    ToolCalls: []
    """

    response = model_with_tools.invoke([HumanMessage(content="What's the weather in SF?")])

    print(f"ContentString: {response.content}")
    print(f"ToolCalls: {response.tool_calls}")

    """
    ContentString: 
    ToolCalls: [{'name': 'tavily_search_results_json', 'args': {'query': 'current weather in SF'}}]
    """

    # - Create agent

    agent_executor = chat_agent_executor.create_tool_calling_executor(ChatOpenAI(model_name="gpt-4o"), [retriever_tool])

    response = agent_executor.invoke({"messages": [HumanMessage(content="hi!")]})
    print(response["messages"])


if __name__ == "__main__":
    deps = Deps.load()
    test()
