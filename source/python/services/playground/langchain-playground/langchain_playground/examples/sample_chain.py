from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_playground.deps import Deps


def test():
    # - Simple call

    llm = ChatOpenAI(model_name="gpt-4o")
    print(llm.invoke("how can langsmith help with testing?"))

    # - Prompt

    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are a world class technical documentation writer."), ("user", "{input}")]
    )
    print(prompt)

    # - Chain

    chain = prompt | llm

    # - Invoke

    print(chain.invoke({"input": "how can langsmith help with testing?"}))

    # - Parse output

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    print(chain.invoke({"input": "how can langsmith help with testing?"}))


if __name__ == "__main__":
    deps = Deps.load()
    test()
