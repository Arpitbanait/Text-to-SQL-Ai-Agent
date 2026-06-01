from typing import Dict, Any
from app.core.sql.generator import sql_generator
from app.core.sql.validator import sql_validator
from app.core.sql.executor import sql_executor
from app.models.request import TextToSQLRequest, QueryExecutionRequest
from app.models.response import TextToSQLResponse, QueryExecutionResponse
from app.utils.logger import logger
from app.utils.exceptions import ValidationException, SQLGenerationException


class QueryService:
    """Service for handling text-to-SQL queries"""
    
    def __init__(self):
        self.generator = sql_generator
        self.validator = sql_validator
        self.executor = sql_executor
    
    async def text_to_sql(
        self,
        request: TextToSQLRequest
    ) -> TextToSQLResponse:
        """Convert natural language to SQL"""
        logger.info(f"Processing text-to-SQL request for database: {request.database_name}")
        
        try:
            max_attempts = 3
            generation_result: Dict[str, Any] = {}
            sql_query = ""
            validation_result: Dict[str, Any] = {
                "is_valid": False,
                "errors": ["Validation not executed"],
                "warnings": [],
            }
            feedback: str | None = None

            for attempt in range(1, max_attempts + 1):
                generation_result = await self.generator.generate(
                    user_query=request.query,
                    database_name=request.database_name,
                    include_explanation=request.include_explanation,
                    validation_feedback=feedback,
                )

                sql_query_raw = generation_result["sql_query"]
                logger.info(f"Generated SQL candidate (attempt {attempt}/{max_attempts}): {sql_query_raw}")

                sql_query = self._extract_sql(sql_query_raw)
                validation_result = self.validator.validate(
                    sql_query,
                    database_name=request.database_name,
                )

                if validation_result["is_valid"]:
                    logger.info(f"SQL validation passed on attempt {attempt}")
                    break

                logger.warning(
                    "SQL validation failed on attempt %s: %s",
                    attempt,
                    ", ".join(validation_result["errors"]),
                )

                if attempt < max_attempts:
                    warning_text = ", ".join(validation_result["warnings"]) or "none"
                    feedback = (
                        f"Database: {request.database_name}. "
                        f"Errors: {', '.join(validation_result['errors'])}. "
                        f"Warnings: {warning_text}."
                    )
                else:
                    raise ValidationException(
                        f"Generated SQL is invalid after {max_attempts} attempts: "
                        f"{', '.join(validation_result['errors'])}"
                    )
            
            # Sanitize query
            sql_query = self.validator.sanitize_query(sql_query)
            
            # Execute if requested
            execution_result = None
            if request.execute_query:
                # Note: Would need connection string from database registry
                logger.info("Query execution requested but connection string not provided")
            
            return TextToSQLResponse(
                sql_query=sql_query,
                explanation=generation_result.get("explanation"),
                confidence=generation_result["confidence"],
                tables_used=generation_result["tables_used"],
                execution_result=execution_result
            )
        
        except Exception as e:
            logger.error(f"Text-to-SQL conversion failed: {str(e)}")
            raise SQLGenerationException(f"Failed to convert text to SQL: {str(e)}")

    def _extract_sql(self, text: str) -> str:
        """Extract SQL statement from LLM output possibly containing markdown fences and prose."""
        import re

        s = text.strip()

        # Prefer fenced code block content
        m = re.search(r"```\s*sql\s*([\s\S]*?)```", s, flags=re.IGNORECASE)
        if not m:
            m = re.search(r"```\s*([\s\S]*?)```", s, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()

        # Else, take from first SELECT/WITH onward
        start = None
        sel = re.search(r"\bSELECT\b", s, flags=re.IGNORECASE)
        cte = re.search(r"\bWITH\b", s, flags=re.IGNORECASE)
        if sel and cte:
            start = min(sel.start(), cte.start())
        elif sel:
            start = sel.start()
        elif cte:
            start = cte.start()
        else:
            return s

        candidate = s[start:].strip()
        # Stop before any trailing fenced block or Explanation:
        end_fence = candidate.find("```")
        end_expl = re.search(r"\bExplanation\s*:", candidate, flags=re.IGNORECASE)
        cut = None
        if end_fence != -1:
            cut = end_fence
        if end_expl:
            cut = min(cut, end_expl.start()) if cut is not None else end_expl.start()
        if cut is not None:
            candidate = candidate[:cut].strip()

        return candidate
    
    async def execute_query(
        self,
        request: QueryExecutionRequest,
        connection_string: str
    ) -> QueryExecutionResponse:
        """Execute SQL query"""
        logger.info(f"Executing query for database: {request.database_name}")
        
        try:
            result = await self.executor.execute(
                sql=request.sql_query,
                connection_string=connection_string,
                limit=request.limit
            )
            
            return QueryExecutionResponse(
                rows=result["rows"],
                row_count=result["row_count"],
                execution_time_ms=result["execution_time_ms"]
            )
        
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise


# Global instance
query_service = QueryService()
