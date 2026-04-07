from rest_framework.decorators import api_view
from rest_framework.response import Response
from services.ollama_llm import ask_llm
from apps.agents.sql_agent import get_all_students
from apps.memory.chat_memory import add_memory, get_memory


@api_view(['POST'])
def chat(request):
    query = request.data.get("query").lower()

    # 🔥 SQL ROUTER
    if "student" in query:
        context = get_all_students()
    else:
        context = ""

    # 🔥 MEMORY
    memory = get_memory()

    # 🔥 FINAL PROMPT
    prompt = f"""
Previous conversation:
{memory}

Context:
{context}

Question:
{query}
"""

    # 🔥 LLM
    answer = ask_llm(prompt)

    # 🔥 SAVE MEMORY
    add_memory(query, answer)

    return Response({
        "answer": answer
    })