from typing import Dict, Any
from datetime import datetime
from app.core.database.schema_extractor import schema_extractor
from app.core.database.metadata import metadata_store
from app.core.rag.indexer import schema_indexer
from app.models.request import SchemaIndexRequest
from app.models.response import SchemaIndexResponse
from app.utils.logger import logger
from app.utils.exceptions import DatabaseException


class SchemaService:
    """Service for managing database schemas"""
    
    def __init__(self):
        self.extractor = schema_extractor
        self.indexer = schema_indexer
        self.metadata_store = metadata_store
    
    async def index_schema(
        self,
        request: SchemaIndexRequest
    ) -> SchemaIndexResponse:
        """Index database schema into vector store"""
        logger.info(f"Indexing schema for database: {request.database_name}")
        
        try:
            # Extract schema from database
            database_schema = self.extractor.extract_schema(
                connection_string=request.connection_string,
                database_name=request.database_name
            )
            
            # Add description if provided
            if request.description:
                database_schema.description = request.description
            
            # Index schema into vector store
            stats = await self.indexer.index_database_schema(database_schema)
            
            # Save metadata
            metadata = {
                "database_name": request.database_name,
                "connection_string": request.connection_string,  # In production, encrypt this
                "description": request.description,
                "tables": [t.name for t in database_schema.tables],
                "table_count": len(database_schema.tables),
                "indexed_at": datetime.now().isoformat()
            }
            
            self.metadata_store.save_metadata(
                database_name=request.database_name,
                metadata=metadata
            )
            
            return SchemaIndexResponse(
                database_name=request.database_name,
                tables_indexed=stats["tables_indexed"],
                columns_indexed=stats["columns_indexed"],
                status="success",
                indexed_at=datetime.now()
            )
        
        except Exception as e:
            logger.error(f"Schema indexing failed: {str(e)}")
            raise DatabaseException(f"Failed to index schema: {str(e)}")
    
    def get_schema_info(
        self,
        database_name: str
    ) -> Dict[str, Any]:
        """Get schema information for a database"""
        logger.info(f"Retrieving schema info for database: {database_name}")
        
        metadata = self.metadata_store.load_metadata(database_name)
        
        if not metadata:
            raise DatabaseException(f"No schema found for database: {database_name}")
        
        return metadata
    
    def list_databases(self) -> list:
        """List all indexed databases"""
        return self.metadata_store.list_databases()


# Global instance
schema_service = SchemaService()
