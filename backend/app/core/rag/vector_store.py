import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import VectorStoreException
import os


class VectorStore:
    """Vector database for storing and retrieving schema embeddings"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.VECTOR_DB_PATH,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="schema_embeddings",
                metadata={"description": "Database schema embeddings"}
            )
            
            logger.info("Vector store initialized successfully")
        
        except Exception as e:
            logger.error(f"Vector store initialization failed: {str(e)}")
            raise VectorStoreException(f"Failed to initialize vector store: {str(e)}")
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add documents with embeddings to vector store"""
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise VectorStoreException(f"Failed to add documents: {str(e)}")
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query vector store for similar documents"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"Retrieved {len(results['documents'][0])} results from vector store")
            return {
                "documents": results["documents"][0],
                "metadatas": results["metadatas"][0],
                "distances": results["distances"][0],
                "ids": results["ids"][0]
            }
        
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            raise VectorStoreException(f"Failed to query vector store: {str(e)}")
    
    def delete_by_database(self, database_name: str):
        """Delete all documents for a specific database"""
        try:
            self.collection.delete(
                where={"database_name": database_name}
            )
            logger.info(f"Deleted documents for database: {database_name}")
        
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            raise VectorStoreException(f"Failed to delete documents: {str(e)}")
    
    def get_collection_count(self) -> int:
        """Get total count of documents in collection"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to get count: {str(e)}")
            return 0


# Global instance
vector_store = VectorStore()
