from langchain_openai import ChatOpenAI


def test():
    llm = ChatOpenAI()
    print(llm.invoke("how can langsmith help with testing?"))

    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are a world class technical documentation writer."), ("user", "{input}")]
    )
    print(prompt)


if __name__ == "__main__":
    test()
