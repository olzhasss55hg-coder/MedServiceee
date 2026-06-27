import os
import meilisearch
from models import Service, Price
from database import SessionLocal

MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY", "masterKey123")

client = meilisearch.Client(MEILI_URL, MEILI_MASTER_KEY)

def init_meilisearch():
    try:
        client.create_index('services', {'primaryKey': 'id'})
        client.index('services').update_searchable_attributes(['name_raw', 'name_norm', 'category'])
        client.index('services').update_filterable_attributes(['category'])
        print("Meilisearch index initialized.")
    except Exception as e:
        print(f"Error initializing meilisearch: {e}")

def index_all_services():
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        documents = []
        for s in services:
            # We index service with a unified price string for basic display or we fetch price dynamically
            documents.append({
                "id": s.id,
                "name_raw": s.name_raw,
                "name_norm": s.name_norm or "",
                "category": s.category.value if hasattr(s.category, 'value') else s.category
            })
            
        if documents:
            client.index('services').add_documents(documents)
            print(f"Indexed {len(documents)} services.")
    except Exception as e:
        print(f"Error indexing services: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_meilisearch()
    index_all_services()
