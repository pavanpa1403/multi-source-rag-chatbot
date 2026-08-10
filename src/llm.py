from langchain_ollama import ChatOllama


def get_llm():

    llm = ChatOllama(
        model="llama3.2",
        temperature=0
    )

    return llm