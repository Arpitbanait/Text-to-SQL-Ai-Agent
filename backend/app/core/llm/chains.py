from typing import Dict, Any, Optional
from app.core.llm.client import llm_client
from app.core.llm.prompts import prompt_templates
from app.utils.logger import logger
from app.utils.helpers import clean_sql_query


class SQLGenerationChain:
    """Chain for SQL generation workflow"""
    
    def __init__(self):
        self.llm = llm_client
    
    async def generate(
        self,
        user_query: str,
        schema_context: str,
        few_shot_examples: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate SQL from user query"""
        logger.info(f"Generating SQL for query: {user_query}")
        
        # Build prompt
        system_prompt = prompt_templates.sql_generation_system_prompt(
            schema_context,
            few_shot_examples or ""
        )
        
        # Generate SQL
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        response = await self.llm.generate_completion(messages)
        
        # Clean and extract SQL
        sql = clean_sql_query(response)
        
        return {
            "sql": sql,
            "raw_response": response
        }
    
    async def explain_sql(
        self,
        sql: str,
        schema_context: str
    ) -> str:
        """Generate explanation for SQL query"""
        logger.info(f"Generating explanation for SQL")
        
        prompt = prompt_templates.sql_explanation_prompt(sql, schema_context)
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        explanation = await self.llm.generate_completion(messages)
        return explanation


class SchemaDescriptionChain:
    """Chain for generating schema descriptions"""
    
    def __init__(self):
        self.llm = llm_client
    
    async def generate_description(
        self,
        table_info: Dict[str, Any]
    ) -> str:
        """Generate natural language description of table"""
        prompt = prompt_templates.schema_description_prompt(table_info)
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        description = await self.llm.generate_completion(messages, temperature=0.3)
        return description.strip()


# Global instances
sql_generation_chain = SQLGenerationChain()
schema_description_chain = SchemaDescriptionChain()
