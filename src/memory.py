chat_history = []


def add_to_history(question, answer):
    """
    Save the conversation.
    """

    chat_history.append(
        {
            "question": question,
            "answer": answer
        }
    )


def get_chat_history():
    """
    Return the chat history as text.
    """

    history = ""

    for chat in chat_history:
        history += f"User: {chat['question']}\n"
        history += f"Assistant: {chat['answer']}\n\n"

    return history