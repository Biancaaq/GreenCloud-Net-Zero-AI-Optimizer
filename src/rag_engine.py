import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, "data", "knowledge_base.json")

class RAGEngine:
    def __init__(self):
        # We don't even need FAISS or SentenceTransformer anymore for this specific logic
        # but we keep the structure so you don't have to change other files
        self.documents = self.load_documents()

    def load_documents(self):
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    def retrieve_solution(self, label: str, context: dict = None):
        """
        Direct mapping: We take the label from AI 1 and fetch 
        the exact instructions from our JSON knowledge base.
        """
        # We search through our documents for the matching label
        for doc in self.documents:
            if doc.get("label") == label:
                return [doc] # Returning as list to keep compatibility with your main.py
        
        # Fallback if label is not found
        return []