class Text2SQLException(Exception):
    """Base exception for Text2SQL application"""
    pass


class LLMException(Text2SQLException):
    """Exception raised when LLM operations fail"""
    pass


class VectorStoreException(Text2SQLException):
    """Exception raised when vector store operations fail"""
    pass


class DatabaseException(Text2SQLException):
    """Exception raised when database operations fail"""
    pass


class ValidationException(Text2SQLException):
    """Exception raised when validation fails"""
    pass


class SchemaNotFoundException(Text2SQLException):
    """Exception raised when schema is not found"""
    pass


class SQLGenerationException(Text2SQLException):
    """Exception raised when SQL generation fails"""
    pass
