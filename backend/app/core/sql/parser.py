import sqlparse
from typing import List, Dict, Any
from app.utils.logger import logger


class SQLParser:
    """Parse and analyze SQL queries"""
    
    def parse(self, sql: str) -> Dict[str, Any]:
        """Parse SQL query and extract information"""
        logger.info("Parsing SQL query")
        
        try:
            parsed = sqlparse.parse(sql)
            
            if not parsed:
                return {"error": "Failed to parse SQL"}
            
            stmt = parsed[0]
            
            return {
                "type": stmt.get_type(),
                "tables": self._extract_tables(stmt),
                "columns": self._extract_columns(stmt),
                "conditions": self._extract_conditions(stmt),
                "formatted": sqlparse.format(sql, reindent=True, keyword_case='upper')
            }
        
        except Exception as e:
            logger.error(f"SQL parsing failed: {str(e)}")
            return {"error": str(e)}
    
    def _extract_tables(self, stmt) -> List[str]:
        """Extract table names from SQL statement"""
        tables = []
        from_seen = False
        
        for token in stmt.tokens:
            if from_seen:
                if token.ttype is None and hasattr(token, 'get_real_name'):
                    table_name = token.get_real_name()
                    if table_name:
                        tables.append(table_name)
            
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                from_seen = True
        
        return tables
    
    def _extract_columns(self, stmt) -> List[str]:
        """Extract column names from SQL statement"""
        columns = []
        
        for token in stmt.tokens:
            if isinstance(token, sqlparse.sql.IdentifierList):
                for identifier in token.get_identifiers():
                    columns.append(str(identifier))
            elif isinstance(token, sqlparse.sql.Identifier):
                columns.append(str(token))
        
        return columns
    
    def _extract_conditions(self, stmt) -> List[str]:
        """Extract WHERE conditions from SQL statement"""
        conditions = []
        where_seen = False
        
        for token in stmt.tokens:
            if where_seen and not isinstance(token, sqlparse.sql.Where):
                condition = str(token).strip()
                if condition and condition.upper() not in ['WHERE', 'AND', 'OR']:
                    conditions.append(condition)
            
            if isinstance(token, sqlparse.sql.Where):
                where_seen = True
        
        return conditions


# Global instance
sql_parser = SQLParser()
