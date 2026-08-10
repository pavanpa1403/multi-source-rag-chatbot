from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_history_aware_retriever(llm, retriever):

    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
Given a chat history and the latest user question,
rewrite the question so that it can be understood
without the previous conversation.

Do NOT answer the question.

Only rewrite it if necessary.
Otherwise return it unchanged.
"""
            ),

            MessagesPlaceholder("chat_history"),

            (
                "human",
                "{input}"
            )
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_prompt
    )

    return history_aware_retriever