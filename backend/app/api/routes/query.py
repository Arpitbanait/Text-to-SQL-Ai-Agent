from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
import asyncio
import json
from app.models.request import TextToSQLRequest, QueryExecutionRequest
from app.models.response import TextToSQLResponse, QueryExecutionResponse, ErrorResponse
from app.services.query_service import query_service
from app.services.cache_service import cache_service
from app.utils.logger import logger
from app.utils.exceptions import Text2SQLException

router = APIRouter(prefix="/query", tags=["Query"])


@router.post(
    "/text-to-sql",
    response_model=TextToSQLResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert natural language to SQL"
)
async def text_to_sql(request: TextToSQLRequest):
    """
    Convert a natural language query to SQL.
    
    - **query**: Natural language question
    - **database_name**: Name of the indexed database
    - **include_explanation**: Include explanation of the SQL query
    - **execute_query**: Execute the generated SQL query
    """
    try:
        logger.info(f"Received text-to-SQL request: {request.query}")
        
        # Check cache
        cache_key = cache_service.generate_query_key(
            query=request.query,
            database_name=request.database_name
        )
        
        cached_result = cache_service.get(cache_key)
        if cached_result:
            logger.info("Returning cached result")
            return TextToSQLResponse(**cached_result)
        
        # Process request
        response = await query_service.text_to_sql(request)
        
        # Cache result
        cache_service.set(cache_key, response.dict())
        
        return response
    
    except Text2SQLException as e:
        logger.error(f"Text2SQL error: {str(e)}")
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


@router.post(
    "/text-to-sql/stream",
    summary="Convert natural language to SQL with streaming explanation"
)
async def text_to_sql_stream(request: TextToSQLRequest):
    """
    Stream the response so the client can visualize word-by-word explanation.
    Emits SSE events: sql, explanation, done, and error.
    """
    try:
        logger.info(f"Streaming text-to-SQL for: {request.query}")
        response = await query_service.text_to_sql(request)

        def sse_event(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        async def event_generator():
            yield sse_event("sql", {
                "sql_query": response.sql_query,
                "confidence": response.confidence,
                "tables_used": response.tables_used,
            })

            if request.include_explanation and response.explanation:
                words = response.explanation.split()
                for w in words:
                    yield sse_event("explanation", {"chunk": w + " "})
                    await asyncio.sleep(0.03)

            yield sse_event("done", {})

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Text2SQLException as e:
        logger.error(f"Streaming error: {str(e)}")
        async def error_gen():
            yield f"event: error\ndata: {json.dumps({"detail": str(e)})}\n\n"
            yield "event: done\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream", status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected streaming error: {str(e)}")
        async def error_gen():
            yield f"event: error\ndata: {json.dumps({"detail": "Internal server error"})}\n\n"
            yield "event: done\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post(
    "/execute",
    response_model=QueryExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute SQL query"
)
async def execute_query(request: QueryExecutionRequest):
    """
    Execute a SQL query.
    
    - **sql_query**: SQL query to execute
    - **database_name**: Name of the database
    - **limit**: Maximum number of rows to return
    """
    try:
        logger.info(f"Executing query for database: {request.database_name}")
        
        # In production, retrieve connection string from secure storage
        # For now, return error
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Query execution requires database connection configuration"
        )
    
    except Text2SQLException as e:
        logger.error(f"Query execution error: {str(e)}")
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
