#!/usr/bin/env python3
"""
Setup script for initializing the vector database.
Run this script before using the Text2SQL API for the first time.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.rag.vector_store import vector_store
from app.config import settings
from app.utils.logger import logger


def main():
    """Initialize vector database"""
    logger.info("Initializing vector database...")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        # Initialize vector store (already done in constructor)
        count = vector_store.get_collection_count()
        
        logger.info(f"Vector database initialized successfully")
        logger.info(f"Current document count: {count}")
        logger.info(f"Vector DB path: {settings.VECTOR_DB_PATH}")
        
        print("\n✅ Vector database setup complete!")
        print(f"📊 Current documents: {count}")
        print(f"📁 Storage path: {settings.VECTOR_DB_PATH}")
        
    except Exception as e:
        logger.error(f"Vector database setup failed: {str(e)}")
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
