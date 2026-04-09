from sentence_transformers import SentenceTransformer
import numpy as np
import csv
import os
from pathlib import Path


class VectorStore:
    def __init__(self):
        try:
            # Try to load with local files only first (if already cached)
            self.model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=os.path.expanduser("~/.cache/huggingface/hub"))
        except Exception as e:
            try:
                # Try again with offline mode
                import transformers
                transformers.utils.hub.HF_HUB_OFFLINE = True
                self.model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=os.path.expanduser("~/.cache/huggingface/hub"))
                transformers.utils.hub.HF_HUB_OFFLINE = False
            except Exception as e2:
                print(f"Warning: Could not load SentenceTransformer: {e2}")
                print("Vector store will operate in limited mode")
                self.model = None
                
        self.documents = []
        self.embeddings = []
        self.metadata = []  # Store metadata for each document
        
    def load_csv_data(self, csv_path: str):
        """Load student data from CSV file into vector store"""
        if not os.path.exists(csv_path):
            print(f"CSV file not found at {csv_path}, using dummy data")
            return False
        
        try:
            documents = []
            metadata = []
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Create a document from CSV row
                    doc = f"Student {row.get('name', 'Unknown')}: Class {row.get('class', 'N/A')}, " \
                          f"Math marks: {row.get('math_marks', 'N/A')}, " \
                          f"Science marks: {row.get('science_marks', 'N/A')}, " \
                          f"English marks: {row.get('english_marks', 'N/A')}, " \
                          f"Attendance: {row.get('attendance_percentage', 'N/A')}%"
                    
                    documents.append(doc)
                    metadata.append(row)
            
            if documents:
                self.add_documents(documents, metadata)
                print(f"✅ Loaded {len(documents)} documents from CSV")
                return True
            else:
                print("CSV file is empty, using dummy data")
                return False
                
        except Exception as e:
            print(f"Error loading CSV: {e}, using dummy data")
            return False

    def add_documents(self, docs: list, metadata: list = None):
        """Add documents to the vector store with optional metadata"""
        self.documents = docs
        if self.model:
            self.embeddings = self.model.encode(docs)
        else:
            # Fallback: use simple length-based embeddings if model unavailable
            self.embeddings = [np.array([float(len(doc))] * 10) for doc in docs]
        self.metadata = metadata if metadata else [{} for _ in docs]

    def search(self, query: str, top_k: int = 3) -> list:
        """
        Search for documents using semantic similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of most relevant documents
        """
        if not self.documents:
            return ["No documents in vector store"]
        
        if self.model:
            query_embedding = self.model.encode(query)
        else:
            # Fallback: simple length-based search
            query_embedding = np.array([float(len(query))] * 10)
            
        scores = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [self.documents[i] for i in top_indices]
    
    def search_with_metadata(self, query: str, top_k: int = 3) -> list:
        """
        Search for documents and return both content and metadata
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of tuples (document, metadata)
        """
        if not self.documents:
            return []
        
        query_embedding = self.model.encode(query)
        scores = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [
            (self.documents[i], self.metadata[i]) 
            for i in top_indices
        ]
    
    def filter_and_search(self, query: str, filter_key: str, filter_value: str, top_k: int = 3) -> list:
        """
        Search with metadata filtering (hybrid search)
        
        Args:
            query: Search query
            filter_key: Metadata field to filter by (e.g., 'class')
            filter_value: Value to match
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        if not self.documents:
            return ["No documents in vector store"]
        
        # Filter documents first
        filtered_indices = [
            i for i, meta in enumerate(self.metadata) 
            if meta.get(filter_key) == filter_value
        ]
        
        if not filtered_indices:
            return [f"No documents found with {filter_key}={filter_value}"]
        
        # Search within filtered set
        query_embedding = self.model.encode(query)
        
        scores = []
        for idx in filtered_indices:
            score = np.dot(self.embeddings[idx], query_embedding)
            scores.append((idx, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in scores[:top_k]]
        
        return [self.documents[i] for i in top_indices]
    
    def get_all_documents(self) -> list:
        """Get all documents in the store"""
        return self.documents
    
    def clear(self):
        """Clear all documents"""
        self.documents = []
        self.embeddings = []
        self.metadata = []


# Initialize vector store
vector_store = VectorStore()

# 🔥 Try loading from CSV first, fallback to dummy data
csv_path = Path(__file__).parent.parent.parent / "data" / "data.csv"
if not vector_store.load_csv_data(str(csv_path)):
    # Fallback to dummy data if CSV loading fails
    vector_store.add_documents([
        "Rahul is a student of class 10 and good in math. His math marks are 85%",
        "Priya is topper in science and studies in class 10. Her science marks are 92%",
        "Aman is average student from class 9. His overall performance is 65%",
        "Neha has good attendance (95%) and studies in class 8. She is performing well",
    ])