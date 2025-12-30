from pydantic import BaseModel, Field
from typing import Optional


class TextToSQLRequest(BaseModel):
    """Request model for text to SQL conversion"""
    query: str = Field(..., description="Natural language query", min_length=1, max_length=500)
    database_name: str = Field(..., description="Name of the database to query")
    include_explanation: bool = Field(default=True, description="Include explanation in response")
    execute_query: bool = Field(default=False, description="Execute the generated SQL query")


class SchemaIndexRequest(BaseModel):
    """Request model for indexing database schema"""
    connection_string: str = Field(..., description="Database connection string")
    database_name: str = Field(..., description="Name of the database")
    description: Optional[str] = Field(None, description="Optional description of the database")


class QueryExecutionRequest(BaseModel):
    """Request model for executing SQL query"""
    sql_query: str = Field(..., description="SQL query to execute")
    database_name: str = Field(..., description="Name of the database")
    limit: int = Field(default=100, description="Maximum number of rows to return")
