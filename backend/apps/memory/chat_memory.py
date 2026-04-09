chat_history = []
MAX_MEMORY_LENGTH = 3  # Only keep last 3 queries (not 5)
MAX_MEMORY_TOKENS = 800  # Maximum tokens for memory in prompt

def add_memory(query, answer):
    """Add query-answer pair to memory with size limits"""
    chat_history.append({
        "q": query,
        "a": answer
    })

    # Keep only last 3 exchanges (reduced from 5)
    if len(chat_history) > MAX_MEMORY_LENGTH:
        chat_history.pop(0)


def get_memory_compact():
    """Return ONLY highly relevant memory - remove noise"""
    if not chat_history:
        return ""
    
    # Only include the LAST query, not all history
    # This prevents context pollution from previous conversations
    last_chat = chat_history[-1]
    
    # Keep response short to save tokens
    memory_text = f"Recent context:\nPrevious: {last_chat['q'][:100]}\n"
    
    return memory_text


def get_memory():
    """Get full memory for reference - but limited to recent exchanges"""
    if not chat_history:
        return ""
    
    # Return ONLY last 2 exchanges to avoid context overload
    recent = chat_history[-2:] if len(chat_history) >= 2 else chat_history
    formatted = ""
    
    for chat in recent:
        # Truncate long responses to save tokens
        short_answer = chat['a'][:200] + "..." if len(chat['a']) > 200 else chat['a']
        formatted += f"Previous Q: {chat['q'][:150]}\nPrevious A: {short_answer}\n\n"
    
    return formatted


def clear_memory():
    """Clear chat history - use after user session ends"""
    global chat_history
    chat_history = []


def get_memory_status():
    """Debug: Get memory status"""
    return {
        "exchange_count": len(chat_history),
        "memory_size": sum(len(c['q']) + len(c['a']) for c in chat_history)
    }