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

    def document_to_text(self, doc: dict):
        symptoms = " ".join(doc.get("symptoms", []))
        actions = " ".join(doc.get("recommended_actions", []))

        return f"""
        Label: {doc.get("label", "")}
        Title: {doc.get("title", "")}
        Content: {doc.get("content", "")}
        Symptoms: {symptoms}
        Recommended actions: {actions}
        Expected impact: {doc.get("expected_impact", "")}
        Risk level: {doc.get("risk_level", "")}
        Estimated saving percent: {doc.get("estimated_saving_pct", 0)}
        """

    def build_index(self):
        texts = [self.document_to_text(doc) for doc in self.documents]

        embeddings = self.embedding_model.encode(texts)
        embeddings = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        return index

    def retrieve_solution(self, label: str, context: dict, top_k: int = 1):
        query = f"""
        Problem label: {label}

        Data center context:
        Timestamp_Hour: {context.get("Timestamp_Hour")}
        Operator: {context.get("Operator")}
        Location: {context.get("Location")}
        Ambient_Temp_C: {context.get("Ambient_Temp_C")}
        Ambient_Hum_Pct: {context.get("Ambient_Hum_Pct")}
        IT_Load_kW: {context.get("IT_Load_kW")}
        Fan_Speed_Pct: {context.get("Fan_Speed_Pct")}
        Chiller_Status: {context.get("Chiller_Status")}
        Cold_Aisle_Temp: {context.get("Cold_Aisle_Temp")}
        Hot_Aisle_Temp: {context.get("Hot_Aisle_Temp")}
        Rack_Inlet_Temp: {context.get("Rack_Inlet_Temp")}
        HVAC_Power_kW: {context.get("HVAC_Power_kW")}
        PUE: {context.get("PUE")}
        """

        query_embedding = self.embedding_model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            results.append(self.documents[idx])

        return results