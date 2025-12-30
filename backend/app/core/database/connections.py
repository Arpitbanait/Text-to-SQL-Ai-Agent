from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any
from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import DatabaseException


class DatabaseConnectionManager:
    """Manage database connections"""
    
    def __init__(self):
        self.engines: Dict[str, Any] = {}
        self.sessions: Dict[str, Any] = {}
    
    def get_engine(self, connection_string: str, pool_size: int = 5):
        """Get or create database engine"""
        if connection_string not in self.engines:
            try:
                engine = create_engine(
                    connection_string,
                    poolclass=pool.QueuePool,
                    pool_size=pool_size,
                    max_overflow=10,
                    pool_pre_ping=True
                )
                self.engines[connection_string] = engine
                logger.info(f"Created database engine for connection")
            
            except Exception as e:
                logger.error(f"Failed to create database engine: {str(e)}")
                raise DatabaseException(f"Failed to connect to database: {str(e)}")
        
        return self.engines[connection_string]
    
    def get_session(self, connection_string: str):
        """Get database session"""
        engine = self.get_engine(connection_string)
        
        if connection_string not in self.sessions:
            SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
            self.sessions[connection_string] = SessionLocal
        
        return self.sessions[connection_string]()
    
    def test_connection(self, connection_string: str) -> bool:
        """Test database connection"""
        try:
            engine = self.get_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def close_all(self):
        """Close all database connections"""
        for engine in self.engines.values():
            engine.dispose()
        self.engines.clear()
        self.sessions.clear()
        logger.info("All database connections closed")


# Global instance
db_manager = DatabaseConnectionManager()
