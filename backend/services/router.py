"""
Query Router - Decides which agent/tool to use based on query intent
"""

import re
from typing import Literal


def detect_query_intent(query: str) -> Literal["semantic_search", "sql_search", "hybrid_search"]:
    """
    Analyze the query and determine the best agent(s) to use.
    
    Returns:
        - "sql_search": Use SQL database queries (for student data queries)
        - "semantic_search": Use vector similarity search (for general knowledge)
        - "hybrid_search": Combine both approaches
    """
    
    query_lower = query.lower()
    
    # SQL Search Keywords (STUDENT DATA QUERIES - HIGHEST PRIORITY)
    sql_keywords = [
        r"\bwho\s+(?:is|are)\s+(?:the\s+)?[a-z\s]+",  # "who is Anthony Hall" - HIGHEST PRIORITY
        r"tell\s+(?:me\s+)?about\s+(?:the\s+)?[a-z\s]+",  # "tell me about Anthony Hall"
        r"information\s+about\s+(?:the\s+)?[a-z\s]+",  # "information about Anthony Hall"
        r"student.*named\s+[\w\s]+",  # "student named John"
        r"find.*(?:student|person)",  # "find student"
        r"which.*student",  # "which student"
        r"marks.*of.*student|student.*marks",  # "marks of student"
        r"blood.*group.*of|blood.*group.*student",  # "blood group of student"
        r"age.*of.*student|student.*age",  # "age of student"
        r"height.*of.*student|student.*height",  # "height of student"
        r"weight.*of.*student|student.*weight",  # "weight of student"
        r"attendance.*of.*student|student.*attendance",  # "attendance of student"
        r"fees.*of.*student|student.*fees|fees.*status",  # "fees of student"
        r"class\s+\d+[a-z]?",  # "class 10" or "class 10A"
        r"students.*in.*class",  # "students in class"
        r"students.*with.*\d+.*marks",  # "students with 80 marks"
        r"grades|marks|scores",  # grade/marks related
        r"(?:what|who|which)\s+(?:is|are)\s+(?:the\s+)?(blood|age|height|weight|attendance|section|class|marks)",  # "what is the blood group"
    ]
    
    # Semantic Search Keywords (GENERAL KNOWLEDGE - LOWER PRIORITY)
    semantic_keywords = [
        r"what.*about|tell.*about",  # "what about students" (general)
        r"general.*info|describe|explain",  # "explain" or "describe"
        r"information.*about.*education|knowledge.*about",  # "information about education"
        r"(?:how|why|what)\s+(?:does|is|are)\s+(?:it|this)",  # "what does this mean"
    ]
    
    # Hybrid Search Keywords (COMBINATION INDICATORS)
    hybrid_keywords = [
        r"top.*students|best.*students",  # "top students"
        r"performance",  # "performance"
        r"find.*students.*with",  # "find students with"
    ]
    
    # Check for SQL search FIRST (most specific for student data)
    for pattern in sql_keywords:
        if re.search(pattern, query_lower):
            return "sql_search"
    
    # Check for hybrid search next
    for pattern in hybrid_keywords:
        if re.search(pattern, query_lower):
            return "hybrid_search"
    
    # Check for semantic search
    for pattern in semantic_keywords:
        if re.search(pattern, query_lower):
            return "semantic_search"
    
    # If no clear pattern matched, default to sql_search
    # (student assistant should prioritize database queries)
    return "sql_search"


def extract_entities(query: str) -> dict:
    """
    Extract named entities from the query for SQL search.
    
    Returns:
        Dictionary with extracted entities like student_name, class, subject, marks, student_id, column
    """
    query_lower = query.lower()
    entities = {}
    
    # Extract column name if asking about specific attribute
    columns = {
        "age": r"age",
        "class": r"class(?:_name)?",
        "section": r"section",
        "math": r"math(?:_marks)?",
        "science": r"science(?:_marks)?",
        "english": r"english(?:_marks)?",
        "attendance": r"attendance(?:_percentage)?",
        "fees_paid": r"fees(?:_)?paid",
        "fees_pending": r"fees(?:_)?pending|pending fees",
        "height": r"height",
        "weight": r"weight",
        "blood_group": r"blood(?:_)?group",
    }
    
    for col_name, col_pattern in columns.items():
        if re.search(col_pattern, query_lower):
            entities["column"] = col_name
            break
    
    # Extract student ID (pattern: "student 5" or "student id 5" or "id: 5")
    id_patterns = [
        r"student\s+(\d+)(?:\s|$|\?)",
        r"(?:student\s+)?id\s*(?::|=)?\s*(\d+)",
        r"(?:(?:student\s+)?id|marks?)\s+of\s+(?:student\s+)?(\d+)",
    ]
    
    for pattern in id_patterns:
        match = re.search(pattern, query_lower)
        if match:
            entities["student_id"] = int(match.group(1))
            break
    
    # Extract student name (pattern: "blood group of X" or "marks of X" or "details of X")
    name_patterns = [
        # Priority 1: "who is the Anthony Hall" or "who is Anthony Hall" - Capture full name (2+ words)
        r"\bwho\s+(?:is|are)\s+(?:the\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s|$|\?)",
        r"\bwho\s+(?:is|are)\s+(?:the\s+)?([A-Za-z\s]{3,})(?:\s|$|\?)",  # Fallback for lowercase
        # Priority 2: "tell me about Anthony Hall" - Capture full name
        r"tell\s+(?:me\s+)?about\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s|$|\?)",
        r"information\s+about\s+(?:the\s+)?(?:student\s+)?([A-Za-z\s]+?)(?:\s|$|\?)",
        # Priority 3: Specific attribute queries
        r"blood\s+group\s+of\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+in|$|\?)",
        r"marks\s+of\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+in|$|\?)",
        r"details?\s+(?:of|about)\s+(?:the\s+)?(?:student\s+)?([A-Za-z\s]+?)(?:\s+in|$|\?)",
        r"(?:age|height|weight|section|class|attendance|fees|blood\s+group)\s+of\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+in|$|\?)",
        r"(?:of|about)\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+in\s+class|$|\?)",
        # Priority 4: Explicit student references
        r"student\s+named\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+(?:in|from)|$|\?)",
        r"find\s+(?:the\s+)?(?:student\s+)?([A-Za-z\s]+?)(?:\s+(?:in|from)|$|\?)",
        r"search\s+for\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s|$|\?)",
        r"student\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+in\s+class|\s+marks|$|\?)",
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, query_lower)
        if match:
            name = match.group(1).strip()
            # Clean up name - remove articles
            name = re.sub(r"^(the|a|an)\s+", "", name, flags=re.IGNORECASE).strip()
            name = re.sub(r"\s+(the|a|an)$", "", name, flags=re.IGNORECASE).strip()
            
            # Validate name (must have letters, not just numbers or common words)
            if name and len(name) > 1 and not name.isdigit():
                # Check if it's a valid name (not just filter words)
                if name.lower() not in ['marks', 'class', 'in', 'student', 'students', 'the', 'a', 'an']:
                    entities["student_name"] = name
                    break
    
    # Extract class (pattern: "class 10" or "in class 10")
    class_pattern = r"(?:class|in)\s+(\d+[A-Za-z]?)"
    match = re.search(class_pattern, query_lower)
    if match:
        entities["class"] = match.group(1)
    
    # Extract subject (math, science, english, hindi, social)
    subjects = ["math", "science", "english", "hindi", "social"]
    for subject in subjects:
        if subject in query_lower:
            entities["subject"] = subject
            break
    
    # Extract marks requirement (pattern: "80 marks" or "above 75" or "over 80")
    marks_pattern = r"(?:above|over|more\s+than|>|>=)?\s*(\d+)\s*(?:marks|%)?|(\d+)\s*(?:\+|plus)"
    match = re.search(marks_pattern, query_lower)
    if match:
        marks = match.group(1) or match.group(2)
        if marks:
            entities["marks"] = int(marks)
    
    # Extract attendance requirement
    attendance_pattern = r"(?:above|over|more\s+than|>|>=)?\s*(\d+)%?\s*(?:attendance|attend)"
    match = re.search(attendance_pattern, query_lower)
    if match:
        entities["attendance"] = int(match.group(1))
    
    return entities


def route_query(query: str) -> dict:
    """
    Main routing function that analyzes a query and returns routing info.
    """
    intent = detect_query_intent(query)
    entities = extract_entities(query)
    
    return {
        "intent": intent,
        "entities": entities,
        "use_semantic_search": intent in ["semantic_search", "hybrid_search"],
        "use_sql_search": intent in ["sql_search", "hybrid_search"],
    }


# Example usage
if __name__ == "__main__":
    test_queries = [
        "Tell me about student John",
        "Find students in class 10A",
        "What are the marks of student 5?",
        "Which students have good performance?",
        "Show me students with 80+ marks in math",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = route_query(query)
        print(f"Intent: {result['intent']}")
        print(f"Entities: {result['entities']}")
        print(f"Use Semantic: {result['use_semantic_search']}")
        print(f"Use SQL: {result['use_sql_search']}")
