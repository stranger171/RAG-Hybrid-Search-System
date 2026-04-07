chat_history = []

def add_memory(query, answer):
    chat_history.append({"q": query, "a": answer})

def get_memory():
    return chat_history[-3:]  # last 3 chats