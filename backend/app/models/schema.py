from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ColumnType(str, Enum):
    """Database column types"""
    INTEGER = "integer"
    STRING = "string"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TEXT = "text"
    JSON = "json"
    UNKNOWN = "unknown"


class ColumnSchema(BaseModel):
    """Schema model for a database column"""
    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Column data type")
    is_nullable: bool = Field(default=True, description="Whether column allows NULL")
    is_primary_key: bool = Field(default=False, description="Whether column is primary key")
    is_foreign_key: bool = Field(default=False, description="Whether column is foreign key")
    foreign_key_table: Optional[str] = Field(None, description="Referenced table for foreign key")
    foreign_key_column: Optional[str] = Field(None, description="Referenced column for foreign key")
    description: Optional[str] = Field(None, description="Column description")


class TableSchema(BaseModel):
    """Schema model for a database table"""
    name: str = Field(..., description="Table name")
    columns: List[ColumnSchema] = Field(default_factory=list, description="List of columns")
    primary_keys: List[str] = Field(default_factory=list, description="List of primary key columns")
    foreign_keys: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="Foreign key relationships")
    description: Optional[str] = Field(None, description="Table description")
    row_count: Optional[int] = Field(None, description="Approximate number of rows")


class DatabaseSchema(BaseModel):
    """Schema model for entire database"""
    name: str = Field(..., description="Database name")
    tables: List[TableSchema] = Field(default_factory=list, description="List of tables")
    description: Optional[str] = Field(None, description="Database description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SchemaDocument(BaseModel):
    """Document model for vector store"""
    id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
