from fastapi import FastAPI
import chromadb

app = FastAPI()
client = chromadb.PersistentClient(path=".")
COLLECTIONS = [c.name for c in client.list_collections()]

@app.get("/collections")
def list_collections():
    out = []
    for name in COLLECTIONS:
        col = client.get_collection(name)
        # Safely determine embedding dimension; fall back to 0 if unavailable
        try:
            sample = col.get(where={}, include=["embeddings"], limit=1)
            if sample["embeddings"]:
                dimension = len(sample["embeddings"][0])
            else:
                dimension = 0
        except Exception:
            dimension = 0

        out.append({
            "name": name,
            "count": col.count(),
            "dimension": dimension
        })
    return out

@app.get("/collection/{name}")
def fetch_items(name: str, offset: int = 0, limit: int = 50):
    col = client.get_collection(name)
    # ChromaDB v0.4+ doesn't accept empty where={}, use None instead
    res = col.get(include=["metadatas"], limit=limit, offset=offset)
    return res     # ids + metadatas
