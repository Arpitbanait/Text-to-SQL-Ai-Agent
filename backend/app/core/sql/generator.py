from typing import Dict, Any, Optional
from app.core.llm.chains import sql_generation_chain
from app.core.rag.retriever import schema_retriever
from app.utils.logger import logger
from app.utils.exceptions import SQLGenerationException


class SQLGenerator:
    """Generate SQL queries from natural language"""
    
    def __init__(self):
        self.chain = sql_generation_chain
        self.retriever = schema_retriever
    
    async def generate(
        self,
        user_query: str,
        database_name: str,
        include_explanation: bool = True
    ) -> Dict[str, Any]:
        """Generate SQL query from natural language query"""
        logger.info(f"Generating SQL for query: {user_query}")
        
        try:
            # Retrieve relevant schema context
            context_result = await self.retriever.retrieve_context(
                user_query=user_query,
                database_name=database_name,
                top_k=5
            )
            
            schema_context = context_result["context"]
            
            # Generate SQL
            result = await self.chain.generate(
                user_query=user_query,
                schema_context=schema_context,
                few_shot_examples=None
            )
            
            sql_query = result["sql"]
            
            # Extract tables used
            tables_used = self._extract_tables_from_metadata(
                context_result["metadata"]
            )
            
            # Generate explanation if requested
            explanation = None
            if include_explanation:
                explanation = await self.chain.explain_sql(
                    sql=sql_query,
                    schema_context=schema_context
                )
            
            # Calculate confidence score (simplified)
            confidence = self._calculate_confidence(context_result)
            
            return {
                "sql_query": sql_query,
                "explanation": explanation,
                "confidence": confidence,
                "tables_used": tables_used,
                "schema_context": schema_context
            }
        
        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise SQLGenerationException(f"Failed to generate SQL: {str(e)}")
    
    def _extract_tables_from_metadata(
        self,
        metadatas: list
    ) -> list:
        """Extract unique table names from metadata"""
        tables = set()
        for meta in metadatas:
            table_name = meta.get("table_name")
            if table_name:
                tables.add(table_name)
        return list(tables)
    
    def _calculate_confidence(
        self,
        context_result: Dict[str, Any]
    ) -> float:
        """Calculate confidence score based on retrieval results"""
        # Simple confidence calculation based on number of results
        num_results = len(context_result.get("retrieved_documents", []))
        
        if num_results >= 3:
            return 0.9
        elif num_results >= 2:
            return 0.75
        elif num_results >= 1:
            return 0.6
        else:
            return 0.4


# Global instance
sql_generator = SQLGenerator()
