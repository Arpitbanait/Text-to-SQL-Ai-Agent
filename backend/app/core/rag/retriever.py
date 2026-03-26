from typing import List, Dict, Any
from app.core.rag.vector_store import get_vector_store
from app.core.rag.embeddings import get_embedding_generator
from app.utils.logger import logger


class SchemaRetriever:
    """Retrieve relevant schema context using RAG"""
    
    def __init__(self):
        self.vector_store = None
        self.embedding_generator = None

    def _get_vector_store(self):
        if self.vector_store is None:
            self.vector_store = get_vector_store()
        return self.vector_store

    def _get_embedding_generator(self):
        if self.embedding_generator is None:
            self.embedding_generator = get_embedding_generator()
        return self.embedding_generator
    
    async def retrieve_context(
        self,
        user_query: str,
        database_name: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Retrieve relevant schema context for user query"""
        logger.info(f"Retrieving context for query: {user_query}")
        embedding_generator = self._get_embedding_generator()
        vector_store = self._get_vector_store()
        
        # Generate query embedding
        query_embedding = await embedding_generator.generate_embedding(user_query)
        
        # Query vector store
        results = vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k,
            where={"database_name": database_name}
        )
        
        # Format context
        context = self._format_context(results)
        
        logger.info(f"Retrieved {len(results['documents'])} relevant schema elements")
        
        return {
            "context": context,
            "retrieved_documents": results["documents"],
            "metadata": results["metadatas"]
        }
    
    def _format_context(self, results: Dict[str, Any]) -> str:
        """Format retrieved documents into context string"""
        documents = results["documents"]
        metadatas = results["metadatas"]
        
        context_parts = []
        
        for doc, meta in zip(documents, metadatas):
            table_name = meta.get("table_name", "Unknown")
            context_parts.append(f"Table: {table_name}\n{doc}\n")
        
        return "\n".join(context_parts)
    
    async def retrieve_table_schemas(
        self,
        table_names: List[str],
        database_name: str
    ) -> str:
        """Retrieve specific table schemas by name"""
        logger.info(f"Retrieving schemas for tables: {table_names}")
        
        # This would query the vector store for specific tables
        # For now, we'll use a simple implementation
        context_parts = []
        
        for table_name in table_names:
            # In production, query vector store with table name filter
            context_parts.append(f"Table: {table_name}")
        
        return "\n\n".join(context_parts)


# Global instance
schema_retriever = SchemaRetriever()
