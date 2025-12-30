from anthropic import AsyncAnthropic
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import LLMException


class LLMClient:
    """Client for interacting with Large Language Models"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.MODEL_NAME
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion from LLM"""
        try:
            # Convert messages format for Anthropic
            system_message = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Call Anthropic API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_message,
                messages=anthropic_messages
            )
            
            content = response.content[0].text
            logger.info(f"LLM completion generated successfully")
            return content
        
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise LLMException(f"Failed to generate completion: {str(e)}")
    
    async def generate_sql(
        self,
        user_query: str,
        schema_context: str,
        few_shot_examples: Optional[str] = None
    ) -> str:
        """Generate SQL query from natural language"""
        system_prompt = self._build_system_prompt(schema_context, few_shot_examples)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        return await self.generate_completion(messages)
    
    def _build_system_prompt(
        self,
        schema_context: str,
        few_shot_examples: Optional[str] = None
    ) -> str:
        """Build system prompt for SQL generation"""
        prompt = f"""You are an expert SQL query generator. Your task is to convert natural language questions into accurate SQL queries.

Database Schema:
{schema_context}

Instructions:
1. Generate only valid SQL queries
2. Use proper SQL syntax and formatting
3. Consider table relationships and foreign keys
4. Use appropriate JOINs when needed
5. Add WHERE clauses for filtering
6. Use aggregate functions when appropriate
7. Return only the SQL query without explanation unless asked

"""
        
        if few_shot_examples:
            prompt += f"\nExamples:\n{few_shot_examples}\n"
        
        prompt += "\nGenerate the SQL query for the following question:"
        
        return prompt


# Global instance
llm_client = LLMClient()
