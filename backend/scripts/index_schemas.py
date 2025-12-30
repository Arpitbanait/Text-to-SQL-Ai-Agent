#!/usr/bin/env python3
"""
Script for indexing database schemas.
Use this to index a new database or re-index an existing one.
"""

import sys
import os
import asyncio
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.schema_service import schema_service
from app.models.request import SchemaIndexRequest
from app.utils.logger import logger


async def index_database(
    connection_string: str,
    database_name: str,
    description: str = None
):
    """Index a database schema"""
    logger.info(f"Starting schema indexing for: {database_name}")
    
    try:
        request = SchemaIndexRequest(
            connection_string=connection_string,
            database_name=database_name,
            description=description
        )
        
        response = await schema_service.index_schema(request)
        
        print("\n✅ Schema indexed successfully!")
        print(f"📊 Database: {response.database_name}")
        print(f"📋 Tables indexed: {response.tables_indexed}")
        print(f"📝 Columns indexed: {response.columns_indexed}")
        print(f"⏰ Indexed at: {response.indexed_at}")
        
    except Exception as e:
        logger.error(f"Schema indexing failed: {str(e)}")
        print(f"\n❌ Indexing failed: {str(e)}")
        sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Index database schema into vector store"
    )
    
    parser.add_argument(
        "--connection-string",
        required=True,
        help="Database connection string"
    )
    
    parser.add_argument(
        "--database-name",
        required=True,
        help="Name of the database"
    )
    
    parser.add_argument(
        "--description",
        default=None,
        help="Optional description of the database"
    )
    
    args = parser.parse_args()
    
    # Run async function
    asyncio.run(index_database(
        connection_string=args.connection_string,
        database_name=args.database_name,
        description=args.description
    ))


if __name__ == "__main__":
    main()
