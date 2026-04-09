from rest_framework.decorators import api_view
from rest_framework.response import Response
from services.langchain_chain import run_multi_agent_rag
from apps.memory.chat_memory import add_memory, clear_memory, get_memory_status


@api_view(['POST'])
def chat(request):
    """
    Enhanced RAG Chat Endpoint using Multi-Agent LangChain System
    
    Request:
        {
            "query": "user question"
        }
    
    Response:
        {
            "answer": "agent response"
        }
    """
    try:
        query = request.data.get("query")
        
        if not query or not query.strip():
            return Response({
                "error": "Query cannot be empty"
            }, status=400)
        
        # 🔥 RUN MULTI-AGENT RAG SYSTEM
        answer = run_multi_agent_rag(query)
        
        # 🔥 SAVE TO MEMORY
        add_memory(query, answer)
        
        return Response({
            "answer": answer,
            "source": "multi-agent-rag"
        }, status=200)
        
    except Exception as e:
        return Response({
            "error": str(e),
            "answer": f"An error occurred: {str(e)}"
        }, status=500)


@api_view(['POST'])
def reset_session(request):
    """
    Reset chat memory and session
    Useful when starting fresh conversation or memory gets polluted
    """
    try:
        clear_memory()
        return Response({
            "success": True,
            "message": "Session cleared successfully. Starting fresh!"
        }, status=200)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=500)


@api_view(['GET'])
def memory_status(request):
    """
    Check current memory status for debugging
    """
    try:
        status = get_memory_status()
        return Response({
            "memory_exchanges": status["exchange_count"],
            "memory_size_bytes": status["memory_size"],
            "status": "Health check - memory usage"
        }, status=200)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=500)