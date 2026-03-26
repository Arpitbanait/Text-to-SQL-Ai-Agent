from typing import List, Dict, Any
from app.core.rag.vector_store import get_vector_store
from app.core.rag.embeddings import get_embedding_generator
from app.models.schema import TableSchema, DatabaseSchema
from app.utils.logger import logger
import uuid


class SchemaIndexer:
    """Index database schemas into vector store"""
    
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
    
    async def index_database_schema(
        self,
        database_schema: DatabaseSchema
    ) -> Dict[str, int]:
        """Index entire database schema"""
        logger.info(f"Indexing schema for database: {database_schema.name}")
        vector_store = self._get_vector_store()
        embedding_generator = self._get_embedding_generator()
        
        documents = []
        metadatas = []
        ids = []
        
        # Delete existing documents for this database
        vector_store.delete_by_database(database_schema.name)
        
        # Process each table
        for table in database_schema.tables:
            doc_data = self._create_table_document(table, database_schema.name)
            documents.append(doc_data["document"])
            metadatas.append(doc_data["metadata"])
            ids.append(doc_data["id"])
        

        # Generate embeddings
        embeddings = await embedding_generator.generate_embeddings(documents)
        
        
        # Add to vector store
        vector_store.add_documents(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        stats = {
            "tables_indexed": len(database_schema.tables),
            "columns_indexed": sum(len(t.columns) for t in database_schema.tables)
        }
        
        logger.info(f"Indexed {stats['tables_indexed']} tables with {stats['columns_indexed']} columns")
        
        return stats
    
    def _create_table_document(
        self,
        table: TableSchema,
        database_name: str
    ) -> Dict[str, Any]:
        """Create searchable document from table schema"""
        # Build document content
        content_parts = [f"Table: {table.name}"]
        
        if table.description:
            content_parts.append(f"Description: {table.description}")
        
        # Add columns
        content_parts.append("\nColumns:")
        for col in table.columns:
            col_desc = f"- {col.name} ({col.data_type})"
            if col.is_primary_key:
                col_desc += " [PRIMARY KEY]"
            if col.is_foreign_key:
                col_desc += f" [FOREIGN KEY -> {col.foreign_key_table}.{col.foreign_key_column}]"
            if not col.is_nullable:
                col_desc += " [NOT NULL]"
            if col.description:
                col_desc += f" - {col.description}"
            content_parts.append(col_desc)
        
        # Add relationships
        if table.foreign_keys:
            content_parts.append("\nRelationships:")
            for fk, ref in table.foreign_keys.items():
                content_parts.append(f"- {fk} references {ref}")
        
        document = "\n".join(content_parts)
        
        # Create metadata
        metadata = {
            "database_name": database_name,
            "table_name": table.name,
            "column_count": len(table.columns),
            "has_foreign_keys": len(table.foreign_keys) > 0
        }
        
        # Generate unique ID
        doc_id = f"{database_name}_{table.name}_{uuid.uuid4().hex[:8]}"
        
        return {
            "document": document,
            "metadata": metadata,
            "id": doc_id
        }


# Global instance
schema_indexer = SchemaIndexer()
