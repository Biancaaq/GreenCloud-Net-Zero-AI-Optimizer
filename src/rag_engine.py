import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer


KNOWLEDGE_BASE_PATH = "data/knowledge_base.json"


class RAGEngine:
    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = self.load_documents()
        self.index = self.build_index()

    def load_documents(self):
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    def build_index(self):
        texts = [
            f"{doc['label']} {doc['title']} {doc['content']}"
            for doc in self.documents
        ]

        embeddings = self.embedding_model.encode(texts)
        embeddings = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        return index

    def retrieve_solution(self, label: str, context: dict, top_k: int = 1):
        query = f"""
        Problem label: {label}

        Data center context:
        Timestamp_Hour: {context['Timestamp_Hour']}
        Operator: {context['Operator']}
        Location: {context['Location']}
        Ambient_Temp_C: {context['Ambient_Temp_C']}
        Ambient_Hum_Pct: {context['Ambient_Hum_Pct']}
        IT_Load_kW: {context['IT_Load_kW']}
        Fan_Speed_Pct: {context['Fan_Speed_Pct']}
        Chiller_Status: {context['Chiller_Status']}
        Cold_Aisle_Temp: {context['Cold_Aisle_Temp']}
        Hot_Aisle_Temp: {context['Hot_Aisle_Temp']}
        Rack_Inlet_Temp: {context['Rack_Inlet_Temp']}
        HVAC_Power_kW: {context['HVAC_Power_kW']}
        PUE: {context['PUE']}
        """

        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        return [self.documents[idx] for idx in indices[0]]