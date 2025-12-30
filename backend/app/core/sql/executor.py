from typing import List, Dict, Any
import time
from app.core.database.connections import db_manager
from app.core.sql.validator import sql_validator
from app.utils.logger import logger
from app.utils.exceptions import DatabaseException, ValidationException


class SQLExecutor:
    """Execute SQL queries safely"""
    
    def __init__(self):
        self.db_manager = db_manager
        self.validator = sql_validator
    
    async def execute(
        self,
        sql: str,
        connection_string: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        logger.info("Executing SQL query")
        
        # Validate query
        validation_result = self.validator.validate(sql)
        
        if not validation_result["is_valid"]:
            raise ValidationException(
                f"SQL validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Add LIMIT if not present
        sql_to_execute = self._add_limit(sql, limit)
        
        try:
            # Get database engine
            engine = self.db_manager.get_engine(connection_string)
            
            # Execute query and measure time
            start_time = time.time()
            
            with engine.connect() as conn:
                result = conn.execute(sql_to_execute)
                rows = result.fetchall()
                columns = result.keys()
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Convert to list of dicts
            rows_dict = [
                {col: value for col, value in zip(columns, row)}
                for row in rows
            ]
            
            logger.info(f"Query executed successfully, returned {len(rows_dict)} rows")
            
            return {
                "rows": rows_dict,
                "row_count": len(rows_dict),
                "execution_time_ms": round(execution_time, 2),
                "columns": list(columns)
            }
        
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise DatabaseException(f"Failed to execute query: {str(e)}")
    
    def _add_limit(self, sql: str, limit: int) -> str:
        """Add LIMIT clause to query if not present"""
        sql_upper = sql.upper().strip()
        
        # Check if LIMIT already exists
        if 'LIMIT' in sql_upper:
            return sql
        
        # Add LIMIT
        return f"{sql} LIMIT {limit}"


# Global instance
sql_executor = SQLExecutor()
