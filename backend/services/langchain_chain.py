"""
Multi-Agent RAG System (Simplified Version)
Uses direct LLM API calls for maximum compatibility
"""

import re
import requests
from services.vector_store import vector_store
from services.router import route_query
from apps.agents.sql_agent import (
    search_students_by_name,
    get_full_student_by_name,
    get_student_by_id,
    get_marks_for_student,
    search_students_by_class,
    get_students_with_high_marks,
    get_students_by_attendance,
    get_all_students,
    get_random_students,
    get_student_field,
)
from apps.memory.chat_memory import get_memory


# ============================================================
# LLM INTERFACE
# ============================================================

def ask_ollama(prompt: str) -> str:
    """
    Call Ollama API directly for text generation
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        return response.json().get("response", "No response from Ollama")
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure it's running on localhost:11434"
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"


# ============================================================
# AGENT FUNCTIONS (Simplified Tools)
# ============================================================

def semantic_search_agent(query: str) -> str:
    """
    Semantic search agent - searches documents using vector embeddings
    """
    try:
        results = vector_store.search(query, top_k=3)
        if not results or all(r == "No documents in vector store" for r in results):
            return "No relevant documents found for your query."
        return "Found relevant information:\n" + "\n".join(results)
    except Exception as e:
        return f"Error in semantic search: {str(e)}"


def sql_search_agent(query: str, entities: dict) -> str:
    """
    SQL search agent - queries database for structured information
    Returns accurate data from Neon database based on extracted entities
    """
    try:
        results = []
        query_lower = query.lower()
        
        # Handle specific column queries (e.g., "blood group of Ricardo Freeman", "age of student 5")
        if "column" in entities and ("student_id" in entities or "student_name" in entities):
            student_identifier = entities.get("student_id") or entities.get("student_name")
            result = get_student_field(student_identifier, entities["column"])
            results.append(result)
            return "\n".join(results) if results else "No data found."
        
        # Search by student ID
        if "student_id" in entities:
            result = get_student_by_id(entities["student_id"])
            results.append(result)
            return "\n".join(results)
        
        # Search by student name
        if "student_name" in entities:
            result = get_full_student_by_name(entities["student_name"])
            results.append(result)
            return "\n".join(results)
        
        # Search by class
        if "class" in entities:
            result = search_students_by_class(entities["class"])
            results.append(result)
            return "\n".join(results)
        
        # Search by marks threshold
        if "subject" in entities and "marks" in entities:
            result = get_students_with_high_marks(entities["subject"], entities["marks"])
            results.append(result)
            return "\n".join(results)
        
        # Search by attendance
        if "attendance" in entities:
            result = get_students_by_attendance(entities["attendance"])
            results.append(result)
            return "\n".join(results)
        
        # Only show all students if explicitly requested
        if any(keyword in query_lower for keyword in ["all students", "list all", "show all", "show everyone", "list every"]):
            result = get_all_students()
            results.append(result)
            return "\n".join(results)
        
        # If query has database-related keywords but no specific entities, return helpful message
        database_keywords = ["student", "find", "search", "information", "data", "marks", "class", "blood", "age", "height", "weight", "attendance", "fees"]
        if any(keyword in query_lower for keyword in database_keywords):
            return "🔍 I found database-related keywords in your query, but I need more specific information. Please try asking about:\n- A specific student (by name or ID)\n- Students in a specific class\n- Students with certain marks\n- Any specific student attribute (blood group, age, height, etc.)\n\nExample: 'What is the blood group of Ricardo Freeman?'"
        
        # Default: Not a database query
        return "Sorry, I don't have enough information to query the database. Please ask about specific students or their information."
            
    except Exception as e:
        print(f"Error in SQL search agent: {str(e)}")
        return f"❌ Error querying database: {str(e)}"


def hybrid_search_agent(query: str, entities: dict) -> str:
    """
    Hybrid search agent - combines semantic and SQL search
    """
    try:
        semantic_result = semantic_search_agent(query)
        sql_result = sql_search_agent(query, entities)
        
        combined = f"""
**Vector Search Results:**
{semantic_result}

**Database Search Results:**
{sql_result}
"""
        return combined
    except Exception as e:
        return f"Error in hybrid search: {str(e)}"


# ============================================================
# MAIN MULTI-AGENT ORCHESTRATOR
# ============================================================

def is_greeting_or_general(query: str) -> bool:
    """
    Check if query is a greeting or general conversation, not a data request
    """
    query_lower = query.lower().strip()
    
    greeting_patterns = [
        r"^(hello|hi|hey|greetings|good morning|good afternoon|good evening|howdy)[\s!?]*$",
        r"^(what|who|how|when|where)\s+(are\s+you|is\s+this|do\s+you\s+work)[\s!?]*$",
        r"^(thanks|thank you|ok|okay|sure|got it|understood)[\s!?]*$",
        r"^(bye|goodbye|see you|take care)[\s!?]*$",
        r"^(help|can you help|what can you do)[\s!?]*$",
    ]
    
    for pattern in greeting_patterns:
        if re.match(pattern, query_lower):
            return True
    
    return False


def handle_greeting(query: str) -> str:
    """
    Handle greeting or general questions with appropriate responses
    """
    query_lower = query.lower().strip()
    
    if re.match(r"^(hello|hi|hey|greetings|good morning|good afternoon|good evening|howdy)", query_lower):
        return "👋 Hello! I'm your Student AI Assistant. I can help you find information about students from our database. You can ask me things like:\n- Blood group of Ricardo Freeman\n- Age of student 5\n- Math marks of student 10\n- Height of Alexandra Berry\n- Or any other student information!\n\nWhat would you like to know?"
    
    elif re.match(r"^(what|who|how|when|where)\s+(are\s+you|is\s+this|do\s+you\s+work)", query_lower):
        return "🤖 I'm an RAG-based AI chatbot that can search a Neon PostgreSQL database with 5,000 student records. I use:\n- **SQL Search**: For direct database queries\n- **Semantic Search**: For document similarity\n- **Hybrid Search**: Combining both approaches\n\nI'm designed to give you accurate student information. Try asking me about any student!"
    
    elif re.match(r"^(help|can you help|what can you do)", query_lower):
        return "📚 I can help you find information about students including:\n- Blood groups\n- Age\n- Class & Section\n- Marks (Math, Science, English)\n- Attendance percentage\n- Fees status\n- Height & Weight\n\nJust ask me about any student by name or ID!"
    
    elif re.match(r"^(thanks|thank you|ok|okay|sure|got it|understood)", query_lower):
        return "✅ You're welcome! Feel free to ask me anything about the student database."
    
    elif re.match(r"^(bye|goodbye|see you|take care)", query_lower):
        return "👋 Goodbye! Have a great day!"
    
    return "👋 How can I assist you with student information today?"


def run_multi_agent_rag(query: str) -> str:
    """
    Main entry point for multi-agent RAG system.
    
    Flow:
    1. Check if greeting/general conversation
    2. Route the query (detect intent)
    3. Extract entities
    4. Choose appropriate agent(s)
    5. Enhance with memory
    6. Pass to LLM for final response
    
    Args:
        query: User input query
        
    Returns:
        Final response from the agent
    """
    try:
        # Step 0: Check if this is a greeting or general conversation
        if is_greeting_or_general(query):
            return handle_greeting(query)
        
        # Step 1: Route the query
        routing = route_query(query)
        intent = routing["intent"]
        entities = routing["entities"]
        
        # Step 2: Get search results based on intent - ONLY FOR RELEVANT QUERIES
        if intent == "semantic_search":
            search_results = semantic_search_agent(query)
        elif intent == "sql_search":
            search_results = sql_search_agent(query, entities)
        else:  # hybrid
            search_results = hybrid_search_agent(query, entities)
        
        # If search results are just random data, don't use LLM
        if "Sample Students" in search_results or search_results.startswith("Database query error"):
            return search_results
        
        # Step 3: Get conversation memory - BUT DON'T USE IT FOR STUDENT QUERIES
        # To prevent memory pollution, only use memory for non-student queries
        memory = get_memory()
        
        # Step 4: Create comprehensive prompt for LLM
        # Special handling for student queries - MINIMAL MEMORY
        is_student_query = "student" in query.lower() or any(name in query.lower() for name in ["who is", "tell me about", "information about", "age of", "blood group", "marks", "height", "weight"])
        
        if is_student_query and ("📋" in search_results or "✅" in search_results):
            # This is a student info query with actual database results
            # ⚠️ IMPORTANT: NO memory included here to prevent confusion between students
            prompt = f"""You are a helpful student assistant AI. A student database query has been performed.

STUDENT INFORMATION RETRIEVED FROM DATABASE:
{search_results}

USER QUESTION: {query}

TASK: Present ONLY the retrieved student information clearly and accurately.

INSTRUCTIONS:
- Present the student information exactly as provided from the database
- Use friendly language but keep it factual
- If asking "who is [name]", provide a summary of their key information
- Always include specific details like class, section, blood group, marks, etc.
- Do NOT make up any information
- Do NOT reference previous queries or other students
- Format the response to be easy to read
- Keep response focused ONLY on the current student being asked about

Provide your response now:"""
        else:
            # General query - use minimal memory only
            prompt = f"""You are a helpful student assistant AI with access to a Neon database.

RETRIEVED DATABASE INFORMATION:
{search_results}

USER QUESTION: {query}

INSTRUCTIONS:
- Provide accurate information based on the retrieved database data ONLY
- Do NOT make up student information
- If the retrieved data doesn't answer the question, be honest and ask for clarification
- Keep responses concise and friendly
- Focus ONLY on the current question

Provide your response now:"""
        
        # Step 5: Get LLM response
        response = ask_ollama(prompt)
        
        return response if response else "I'm unable to provide an answer at the moment."
        
    except Exception as e:
        error_msg = f"Agent error: {str(e)}"
        print(f"Error in run_multi_agent_rag: {error_msg}")
        return f"❌ Error processing your query. Please try again. Details: {error_msg}"


# ============================================================
# AGENT DETAILS (for debugging/logging)
# ============================================================

AGENT_DESCRIPTIONS = {
    "semantic_search": {
        "name": "Vector Similarity Search",
        "description": "Searches documents using semantic embeddings",
        "use_cases": ["General information queries", "What about questions", "Definition requests"]
    },
    "sql_search": {
        "name": "Database Query Agent",
        "description": "Queries structured database for student records",
        "use_cases": ["Find specific students", "Get marks", "Class information", "Academic data"]
    },
    "hybrid_search": {
        "name": "Hybrid Search Agent",
        "description": "Combines vector and database searches",
        "use_cases": ["Complex queries", "Combining semantic + structured data", "Comprehensive searches"]
    }
}


if __name__ == "__main__":
    # Test the system
    test_queries = [
        "Tell me about students in the system",
        "Find student John",
        "What are the marks for student 5",
        "Show me students in class 10A",
    ]
    
    print("=" * 60)
    print("MULTI-AGENT RAG SYSTEM TEST")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        try:
            response = run_multi_agent_rag(query)
            print(f"✅ Response: {response}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
