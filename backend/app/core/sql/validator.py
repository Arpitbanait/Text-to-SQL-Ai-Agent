import sqlparse
from typing import Dict, Any, List
from app.utils.logger import logger
from app.utils.exceptions import ValidationException
import re


class SQLValidator:
    """Validate SQL queries for safety and correctness"""
    
    # Dangerous SQL keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
        'INSERT', 'UPDATE', 'GRANT', 'REVOKE', 'EXEC'
    ]
    
    def validate(self, sql: str) -> Dict[str, Any]:
        """Validate SQL query"""
        logger.info("Validating SQL query")
        # Normalize first: strip comments and leading helper keywords
        normalized = self._normalize_sql(sql)

        errors = []
        warnings = []
        
        # Check if query is empty
        if not normalized:
            errors.append("SQL query is empty")
            return {
                "is_valid": False,
                "errors": errors,
                "warnings": warnings
            }
        
        # Check for dangerous operations
        dangerous_check = self._check_dangerous_operations(normalized)
        if dangerous_check:
            errors.append(f"Dangerous operation detected: {dangerous_check}")
        
        # Check for SQL injection patterns
        injection_check = self._check_sql_injection(normalized)
        if injection_check:
            warnings.append(f"Potential SQL injection pattern: {injection_check}")
        
        # Validate syntax using sqlparse
        syntax_check = self._check_syntax(normalized)
        if syntax_check:
            errors.append(syntax_check)
        
        # Check for multiple statements
        if self._has_multiple_statements(normalized):
            errors.append("Multiple SQL statements not allowed")
        
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
    
    def _check_dangerous_operations(self, sql: str) -> str:
        """Check for dangerous SQL operations"""
        sql_upper = sql.upper()
        
        for keyword in self.DANGEROUS_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', sql_upper):
                return keyword
        
        return ""
    
    def _check_sql_injection(self, sql: str) -> str:
        """Check for common SQL injection patterns"""
        injection_patterns = [
            r"'\s*OR\s*'",
            r"'\s*OR\s+\d+\s*=\s*\d+",
            r"--",
            r"/\*.*\*/",
            r";\s*DROP",
            r"UNION\s+SELECT"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                return pattern
        
        return ""
    
    def _check_syntax(self, sql: str) -> str:
        """Basic syntax validation using sqlparse"""
        try:
            parsed = sqlparse.parse(sql)
            
            if not parsed:
                return "Invalid SQL syntax"
            
            # Check if it's a valid statement
            stmt = parsed[0]
            if stmt.get_type() == 'UNKNOWN':
                # Be lenient for dialect-specific SQL; accept common read queries
                if re.match(r"^\s*(SELECT|WITH)\b", sql, re.IGNORECASE):
                    return ""
                return "Unrecognized SQL statement"
            
            return ""
        
        except Exception as e:
            return f"Syntax error: {str(e)}"
    
    def _has_multiple_statements(self, sql: str) -> bool:
        """Check if SQL contains multiple statements"""
        parsed = sqlparse.parse(sql)
        return len(parsed) > 1
    
    def sanitize_query(self, sql: str) -> str:
        """Sanitize SQL query"""
        # Format the SQL for better readability
        formatted = sqlparse.format(
            sql,
            reindent=True,
            keyword_case='upper'
        )
        return formatted.strip()

    def _normalize_sql(self, sql: str) -> str:
        """Strip comments, leading helper keywords like EXPLAIN, and whitespace"""
        s = sql.strip()
        # Remove line comments
        s = re.sub(r"--.*?$", "", s, flags=re.MULTILINE)
        # Remove block comments
        s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
        s = s.strip()
        # Strip leading EXPLAIN if present
        s = re.sub(r"^EXPLAIN\s+", "", s, flags=re.IGNORECASE)
        # Collapse excessive whitespace
        s = re.sub(r"\s+", " ", s)
        return s


# Global instance
sql_validator = SQLValidator()
