from typing import Dict, Any, List, Optional, Set, Tuple
from app.utils.logger import logger
from app.utils.exceptions import ValidationException
import re
import json
from pathlib import Path

try:
    import sqlparse
except ModuleNotFoundError:
    sqlparse = None


class SQLValidator:
    """Validate SQL queries for safety and correctness"""
    
    # Dangerous SQL keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
        'INSERT', 'UPDATE', 'GRANT', 'REVOKE', 'EXEC'
    ]

    SQL_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'FULL', 'INNER', 'OUTER',
        'ON', 'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'AS', 'AND', 'OR',
        'NOT', 'IN', 'IS', 'NULL', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT',
        'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'WITH', 'UNION', 'ALL', 'DESC', 'ASC'
    }

    def __init__(self):
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
    
    def validate(self, sql: str, database_name: Optional[str] = None) -> Dict[str, Any]:
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

        # Validate table/column references against selected database schema
        schema_result = self._check_schema_references(normalized, database_name)
        errors.extend(schema_result["errors"])
        warnings.extend(schema_result["warnings"])
        
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
            if sqlparse is None:
                # Fallback when optional dependency is not installed in runtime env.
                if not re.match(r"^\s*(SELECT|WITH)\b", sql, re.IGNORECASE):
                    return "Only SELECT/WITH statements are supported"
                return ""

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
        if sqlparse is None:
            # Conservative fallback: reject explicit semicolon-separated statements.
            return ";" in sql.strip().rstrip(";")

        parsed = sqlparse.parse(sql)
        return len(parsed) > 1
    
    def sanitize_query(self, sql: str) -> str:
        """Sanitize SQL query"""
        if sqlparse is None:
            return sql.strip()

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

    def _check_schema_references(
        self,
        sql: str,
        database_name: Optional[str]
    ) -> Dict[str, List[str]]:
        """Validate table and qualified-column references against stored schema."""
        errors: List[str] = []
        warnings: List[str] = []

        if not database_name:
            warnings.append("Schema validation skipped: database name not provided")
            return {"errors": errors, "warnings": warnings}

        schema = self._load_database_schema(database_name)
        known_tables: Set[str] = schema.get("tables", set())
        columns_by_table: Dict[str, Set[str]] = schema.get("columns_by_table", {})

        if not known_tables:
            warnings.append(
                f"Schema validation skipped: no schema metadata found for database '{database_name}'"
            )
            return {"errors": errors, "warnings": warnings}

        cte_names = self._extract_cte_names(sql)
        referenced_tables, alias_map = self._extract_tables_and_aliases(sql)

        unknown_tables = sorted(
            table for table in referenced_tables
            if table not in known_tables and table not in cte_names
        )

        if unknown_tables:
            suggestion = ", ".join(sorted(list(known_tables))[:10])
            errors.append(
                f"Unknown table(s) referenced: {', '.join(unknown_tables)}. "
                f"Available tables include: {suggestion}"
            )

        checked_missing_column_support: Set[str] = set()
        for alias_or_table, column in self._extract_qualified_columns(sql):
            resolved_table = alias_map.get(alias_or_table, alias_or_table)

            if resolved_table in cte_names or resolved_table not in known_tables:
                continue

            known_columns = columns_by_table.get(resolved_table, set())
            if not known_columns:
                if resolved_table not in checked_missing_column_support:
                    warnings.append(
                        f"Column-level validation unavailable for table '{resolved_table}' "
                        "because stored schema has no column details"
                    )
                    checked_missing_column_support.add(resolved_table)
                continue

            if column != "*" and column not in known_columns:
                errors.append(
                    f"Unknown column '{column}' on table '{resolved_table}'"
                )

        return {
            "errors": sorted(list(set(errors))),
            "warnings": sorted(list(set(warnings)))
        }

    def _load_database_schema(self, database_name: str) -> Dict[str, Any]:
        """Load schema file from disk and normalize to lookup structures."""
        key = database_name.lower()
        if key in self._schema_cache:
            return self._schema_cache[key]

        backend_root = Path(__file__).resolve().parents[3]
        schema_path = backend_root / "data" / "schemas" / f"{database_name}.json"

        if not schema_path.exists():
            self._schema_cache[key] = {"tables": set(), "columns_by_table": {}}
            return self._schema_cache[key]

        try:
            with schema_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load schema '{schema_path}': {str(e)}")
            self._schema_cache[key] = {"tables": set(), "columns_by_table": {}}
            return self._schema_cache[key]

        tables: Set[str] = set()
        columns_by_table: Dict[str, Set[str]] = {}

        for table_entry in payload.get("tables", []):
            if isinstance(table_entry, str):
                table_name = self._normalize_identifier(table_entry)
                if table_name:
                    tables.add(table_name)
                    columns_by_table.setdefault(table_name, set())
                continue

            if isinstance(table_entry, dict):
                table_name = self._normalize_identifier(table_entry.get("name", ""))
                if not table_name:
                    continue
                tables.add(table_name)

                columns = set()
                for col in table_entry.get("columns", []):
                    col_name = self._normalize_identifier((col or {}).get("name", ""))
                    if col_name:
                        columns.add(col_name)
                columns_by_table[table_name] = columns

        self._schema_cache[key] = {
            "tables": tables,
            "columns_by_table": columns_by_table
        }
        return self._schema_cache[key]

    def _extract_tables_and_aliases(self, sql: str) -> Tuple[Set[str], Dict[str, str]]:
        """Extract table names and aliases from FROM/JOIN clauses."""
        tables: Set[str] = set()
        alias_map: Dict[str, str] = {}

        pattern = re.compile(
            r"\b(?:FROM|JOIN)\s+([`\"\[]?[\w\.]+[`\"\]]?)(?:\s+(?:AS\s+)?([`\"\[]?[\w]+[`\"\]]?))?",
            flags=re.IGNORECASE,
        )

        for match in pattern.finditer(sql):
            raw_table = match.group(1) or ""
            raw_alias = match.group(2) or ""

            if raw_table.startswith("("):
                continue

            table_name = self._normalize_identifier(raw_table)
            if not table_name:
                continue

            tables.add(table_name)

            alias = self._normalize_identifier(raw_alias)
            if alias and alias.upper() not in self.SQL_KEYWORDS:
                alias_map[alias] = table_name

            alias_map[table_name] = table_name

        return tables, alias_map

    def _extract_qualified_columns(self, sql: str) -> List[Tuple[str, str]]:
        """Extract qualified columns like alias.column or table.column."""
        columns: List[Tuple[str, str]] = []
        pattern = re.compile(
            r"([`\"\[]?[A-Za-z_][\w$]*[`\"\]]?)\s*\.\s*([`\"\[]?[A-Za-z_*][\w$*]*[`\"\]]?)",
            flags=re.IGNORECASE,
        )

        for match in pattern.finditer(sql):
            left = self._normalize_identifier(match.group(1))
            right = self._normalize_identifier(match.group(2), allow_star=True)
            if left and right:
                columns.append((left, right))

        return columns

    def _extract_cte_names(self, sql: str) -> Set[str]:
        """Extract CTE names to avoid false unknown-table errors."""
        ctes: Set[str] = set()

        with_match = re.search(r"\bWITH\b", sql, flags=re.IGNORECASE)
        if not with_match:
            return ctes

        i = with_match.end()
        n = len(sql)

        # Support optional WITH RECURSIVE prefix.
        recursive_match = re.match(r"\s*RECURSIVE\b", sql[i:], flags=re.IGNORECASE)
        if recursive_match:
            i += recursive_match.end()

        while i < n:
            ws = re.match(r"\s*", sql[i:])
            if ws:
                i += ws.end()

            name_match = re.match(r"([A-Za-z_][\w$]*)", sql[i:])
            if not name_match:
                break

            cte_name = self._normalize_identifier(name_match.group(1))
            if cte_name:
                ctes.add(cte_name)
            i += name_match.end()

            # Optional CTE column list: cte_name(col1, col2)
            ws = re.match(r"\s*", sql[i:])
            if ws:
                i += ws.end()
            if i < n and sql[i] == "(":
                depth = 1
                i += 1
                while i < n and depth > 0:
                    if sql[i] == "(":
                        depth += 1
                    elif sql[i] == ")":
                        depth -= 1
                    i += 1

            as_match = re.match(r"\s*AS\s*\(", sql[i:], flags=re.IGNORECASE)
            if not as_match:
                break
            i += as_match.end()

            # Consume full CTE query body using balanced parentheses.
            depth = 1
            while i < n and depth > 0:
                if sql[i] == "(":
                    depth += 1
                elif sql[i] == ")":
                    depth -= 1
                i += 1

            ws = re.match(r"\s*", sql[i:])
            if ws:
                i += ws.end()

            # Multiple CTEs are comma-separated; main query starts otherwise.
            if i < n and sql[i] == ",":
                i += 1
                continue
            break

        return ctes

    def _normalize_identifier(self, token: str, allow_star: bool = False) -> str:
        """Normalize SQL identifier for case-insensitive comparison."""
        if not token:
            return ""

        token = token.strip()
        if allow_star and token == "*":
            return "*"

        if "." in token:
            token = token.split(".")[-1]

        token = token.strip('`"[]').strip()
        return token.lower()


# Global instance
sql_validator = SQLValidator()
