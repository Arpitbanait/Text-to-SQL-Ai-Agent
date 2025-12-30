from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.models.request import SchemaIndexRequest
from app.models.response import SchemaIndexResponse
from app.services.schema_service import schema_service
from app.utils.logger import logger
from app.utils.exceptions import Text2SQLException

router = APIRouter(prefix="/schema", tags=["Schema"])


@router.post(
    "/index",
    response_model=SchemaIndexResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Index database schema"
)
async def index_schema(request: SchemaIndexRequest):
    """
    Index a database schema into the vector store.
    
    - **connection_string**: Database connection string
    - **database_name**: Name of the database
    - **description**: Optional description of the database
    """
    try:
        logger.info(f"Indexing schema for database: {request.database_name}")
        
        response = await schema_service.index_schema(request)
        
        return response
    
    except Text2SQLException as e:
        logger.error(f"Schema indexing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{database_name}",
    response_model=Dict[str, Any],
    summary="Get schema information"
)
async def get_schema(database_name: str):
    """
    Get schema information for a database.
    
    - **database_name**: Name of the database
    """
    try:
        logger.info(f"Retrieving schema info for: {database_name}")
        
        schema_info = schema_service.get_schema_info(database_name)
        
        return schema_info
    
    except Text2SQLException as e:
        logger.error(f"Schema retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=List[str],
    summary="List indexed databases"
)
async def list_databases():
    """
    List all indexed databases.
    """
    try:
        logger.info("Listing all indexed databases")
        
        databases = schema_service.list_databases()
        
        return databases
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
