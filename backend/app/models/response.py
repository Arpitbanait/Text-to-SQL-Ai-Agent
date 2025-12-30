from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class TextToSQLResponse(BaseModel):
    """Response model for text to SQL conversion"""
    sql_query: str = Field(..., description="Generated SQL query")
    explanation: Optional[str] = Field(None, description="Explanation of the query")
    confidence: float = Field(..., description="Confidence score (0-1)")
    tables_used: List[str] = Field(default_factory=list, description="List of tables used")
    execution_result: Optional[Dict[str, Any]] = Field(None, description="Query execution results if executed")


class SchemaIndexResponse(BaseModel):
    """Response model for schema indexing"""
    database_name: str = Field(..., description="Name of the database")
    tables_indexed: int = Field(..., description="Number of tables indexed")
    columns_indexed: int = Field(..., description="Number of columns indexed")
    status: str = Field(..., description="Indexing status")
    indexed_at: datetime = Field(default_factory=datetime.now, description="Timestamp of indexing")


class QueryExecutionResponse(BaseModel):
    """Response model for query execution"""
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="Query result rows")
    row_count: int = Field(..., description="Number of rows returned")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Current timestamp")


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
