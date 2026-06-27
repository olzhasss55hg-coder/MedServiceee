from database import engine, Base
import models
import seed_real_data
import search

def reset():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Seeding database...")
    seed_real_data.seed_db()
    print("Re-indexing meilisearch...")
    search.init_meilisearch()
    search.index_all_services()
    print("Done!")

if __name__ == "__main__":
    reset()
