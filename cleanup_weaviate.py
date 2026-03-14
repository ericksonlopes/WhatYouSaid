from src.infrastructure.repositories.vector.weaviate.weaviate_client import WeaviateClient
from src.config.settings import settings

client_wrapper = WeaviateClient(settings.vector)
collection_name = settings.vector.weaviate_collection_name_chunks

print(f"Connecting to Weaviate to delete collection: {collection_name}")

try:
    with client_wrapper as client:
        if client.collections.exists(collection_name):
            client.collections.delete(collection_name)
            print(f"Collection '{collection_name}' deleted successfully.")
        else:
            print(f"Collection '{collection_name}' does not exist.")
except Exception as e:
    print(f"Error: {e}")
