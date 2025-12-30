from sqlalchemy import inspect, MetaData
from typing import List, Dict, Any
from app.core.database.connections import db_manager
from app.models.schema import DatabaseSchema, TableSchema, ColumnSchema
from app.utils.logger import logger
from app.utils.exceptions import DatabaseException


class SchemaExtractor:
    """Extract database schema metadata"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def extract_schema(
        self,
        connection_string: str,
        database_name: str
    ) -> DatabaseSchema:
        """Extract complete database schema"""
        logger.info(f"Extracting schema for database: {database_name}")
        
        try:
            engine = self.db_manager.get_engine(connection_string)
            inspector = inspect(engine)
            
            # Get all table names
            table_names = inspector.get_table_names()
            logger.info(f"Found {len(table_names)} tables")
            
            # Extract schema for each table
            tables = []
            for table_name in table_names:
                table_schema = self._extract_table_schema(inspector, table_name)
                tables.append(table_schema)
            
            database_schema = DatabaseSchema(
                name=database_name,
                tables=tables
            )
            
            logger.info(f"Successfully extracted schema for {len(tables)} tables")
            return database_schema
        
        except Exception as e:
            logger.error(f"Schema extraction failed: {str(e)}")
            raise DatabaseException(f"Failed to extract schema: {str(e)}")
    
    def _extract_table_schema(
        self,
        inspector,
        table_name: str
    ) -> TableSchema:
        """Extract schema for a single table"""
        # Get columns
        columns = []
        column_info = inspector.get_columns(table_name)
        
        # Get primary keys
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get('constrained_columns', [])
        
        # Get foreign keys
        fk_constraints = inspector.get_foreign_keys(table_name)
        foreign_key_map = {}
        
        for fk in fk_constraints:
            for col in fk.get('constrained_columns', []):
                ref_table = fk.get('referred_table')
                ref_cols = fk.get('referred_columns', [])
                if ref_cols:
                    foreign_key_map[col] = {
                        'table': ref_table,
                        'column': ref_cols[0]
                    }
        
        # Process each column
        for col in column_info:
            col_name = col['name']
            
            column_schema = ColumnSchema(
                name=col_name,
                data_type=str(col['type']),
                is_nullable=col.get('nullable', True),
                is_primary_key=col_name in primary_keys,
                is_foreign_key=col_name in foreign_key_map,
                foreign_key_table=foreign_key_map.get(col_name, {}).get('table'),
                foreign_key_column=foreign_key_map.get(col_name, {}).get('column')
            )
            
            columns.append(column_schema)
        
        return TableSchema(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_key_map
        )


# Global instance
schema_extractor = SchemaExtractor()
