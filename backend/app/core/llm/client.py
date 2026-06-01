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
        self.fallback_models = self._parse_fallback_models(settings.FALLBACK_MODELS)
        self.excluded_model_keywords = self._parse_model_keywords(
            settings.EXCLUDED_MODEL_KEYWORDS
        )
        self.auto_discover_models = settings.AUTO_DISCOVER_MODELS
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        self._cached_available_models: Optional[List[str]] = None

    @staticmethod
    def _parse_fallback_models(raw_fallbacks: str) -> List[str]:
        """Parse comma-separated fallback models from settings."""
        return [model.strip() for model in raw_fallbacks.split(",") if model.strip()]

    @staticmethod
    def _parse_model_keywords(raw_keywords: str) -> List[str]:
        """Parse comma-separated model filter keywords."""
        return [keyword.strip().lower() for keyword in raw_keywords.split(",") if keyword.strip()]

    @staticmethod
    def _unique_preserve_order(items: List[str]) -> List[str]:
        """Return unique items while preserving their first-seen order."""
        return list(dict.fromkeys(items))

    def _filter_excluded_models(self, models: List[str]) -> List[str]:
        """Exclude model IDs containing configured blocked keywords."""
        if not self.excluded_model_keywords:
            return models

        filtered: List[str] = []
        for model in models:
            model_lower = model.lower()
            if any(keyword in model_lower for keyword in self.excluded_model_keywords):
                continue
            filtered.append(model)
        return filtered

    async def _get_available_models(self) -> List[str]:
        """Fetch model IDs available for the configured Anthropic API key."""
        if self._cached_available_models is not None:
            return self._cached_available_models

        discovered: List[str] = []
        try:
            response = await self.client.models.list(limit=100)
            data = getattr(response, "data", None)
            if data:
                discovered = [m.id for m in data if getattr(m, "id", None)]
            else:
                # Fallback for SDK response shapes that return an iterable directly.
                discovered = [m.id for m in response if getattr(m, "id", None)]
        except Exception as e:
            logger.warning(f"Unable to discover Anthropic models automatically: {e}")

        self._cached_available_models = self._unique_preserve_order(discovered)
        return self._cached_available_models

    async def _build_candidate_models(self) -> List[str]:
        """Build ordered candidate list, preferring configured and available models."""
        configured = self._filter_excluded_models(
            self._unique_preserve_order([self.model] + self.fallback_models)
        )

        if not self.auto_discover_models:
            return configured

        available = self._filter_excluded_models(await self._get_available_models())
        if not available:
            return configured

        configured_available = [m for m in configured if m in available]
        extra_available = [m for m in available if m not in configured_available]

        if configured_available:
            return configured_available + extra_available

        logger.warning(
            "None of the configured models are available for this API key. "
            "Falling back to discovered available models."
        )
        return available
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion from LLM"""
        try:
            
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
            
            
            candidate_models = await self._build_candidate_models()

            last_error: Optional[Exception] = None
            attempted_models: List[str] = []

            for model_name in candidate_models:
                attempted_models.append(model_name)
                try:
                    selected_temperature = (
                        temperature if temperature is not None else self.temperature
                    )
                    response = await self.client.messages.create(
                        model=model_name,
                        max_tokens=max_tokens or self.max_tokens,
                        temperature=selected_temperature,
                        system=system_message,
                        messages=anthropic_messages
                    )

                    if model_name != self.model:
                        logger.warning(
                            f"Configured model '{self.model}' unavailable; "
                            f"used fallback model '{model_name}'"
                        )

                    content = response.content[0].text
                    logger.info("LLM completion generated successfully")
                    return content
                except Exception as model_error:
                    last_error = model_error
                    error_text = str(model_error).lower()

                    if "temperature" in error_text and "deprecated" in error_text:
                        logger.warning(
                            f"Model '{model_name}' does not support temperature; retrying without it."
                        )
                        try:
                            response = await self.client.messages.create(
                                model=model_name,
                                max_tokens=max_tokens or self.max_tokens,
                                system=system_message,
                                messages=anthropic_messages
                            )

                            if model_name != self.model:
                                logger.warning(
                                    f"Configured model '{self.model}' unavailable; "
                                    f"used fallback model '{model_name}'"
                                )

                            content = response.content[0].text
                            logger.info("LLM completion generated successfully")
                            return content
                        except Exception as retry_error:
                            last_error = retry_error
                            error_text = str(retry_error).lower()

                    if "not_found_error" in error_text or "model:" in error_text:
                        logger.warning(
                            f"Model '{model_name}' not found. Trying next fallback model."
                        )
                        continue
                    raise

            if last_error:
                raise LLMException(
                    "No configured Anthropic model is available. "
                    f"Attempted models: {', '.join(attempted_models)}. "
                    "Set MODEL_NAME and FALLBACK_MODELS to model IDs enabled for your API key. "
                    f"Last error: {last_error}"
                )

            raise LLMException("No LLM models available")
        
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


llm_client = LLMClient()
