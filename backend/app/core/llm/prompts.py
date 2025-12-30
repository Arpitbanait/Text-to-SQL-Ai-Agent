from typing import List, Dict, Any


class PromptTemplates:
    """Collection of prompt templates for LLM"""
    
    @staticmethod
    def sql_generation_system_prompt(schema: str, examples: str = "") -> str:
        """System prompt for SQL generation"""
        prompt = f"""You are an expert SQL query generator. Convert natural language questions into SQL queries.

Database Schema:
{schema}

Guidelines:
- Generate syntactically correct SQL
- Use table aliases for readability
- Include appropriate JOINs for multi-table queries
- Add WHERE clauses for filtering
- Use aggregate functions (COUNT, SUM, AVG) when needed
- Format dates properly
- Handle NULL values appropriately
- Return ONLY the SQL query in a code block

"""
        if examples:
            prompt += f"Examples:\n{examples}\n\n"
        
        return prompt
    
    @staticmethod
    def sql_explanation_prompt(sql: str, schema: str) -> str:
        """Prompt for explaining SQL query"""
        return f"""Explain the following SQL query in simple terms:

SQL Query:
{sql}

Database Schema:
{schema}

Provide a clear, concise explanation of what this query does.
"""
    
    @staticmethod
    def schema_description_prompt(table_info: Dict[str, Any]) -> str:
        """Generate natural language description of schema"""
        return f"""Generate a concise description of this database table:

Table Name: {table_info.get('name')}
Columns: {', '.join(table_info.get('columns', []))}
Primary Keys: {', '.join(table_info.get('primary_keys', []))}
Foreign Keys: {table_info.get('foreign_keys', {})}

Description (1-2 sentences):"""
    
    @staticmethod
    def format_few_shot_examples(examples: List[Dict[str, str]]) -> str:
        """Format few-shot examples for prompt"""
        formatted = []
        for i, example in enumerate(examples, 1):
            formatted.append(
                f"Example {i}:\n"
                f"Question: {example.get('question')}\n"
                f"SQL: {example.get('sql')}\n"
            )
        return "\n".join(formatted)
    
    @staticmethod
    def format_schema_context(tables: List[Dict[str, Any]]) -> str:
        """Format schema information for context"""
        formatted = []
        for table in tables:
            table_info = [f"Table: {table.get('name')}"]
            
            # Add columns
            columns = table.get('columns', [])
            if columns:
                table_info.append("Columns:")
                for col in columns:
                    col_str = f"  - {col.get('name')} ({col.get('data_type')})"
                    if col.get('is_primary_key'):
                        col_str += " [PRIMARY KEY]"
                    if col.get('is_foreign_key'):
                        col_str += f" [FOREIGN KEY -> {col.get('foreign_key_table')}]"
                    table_info.append(col_str)
            
            formatted.append("\n".join(table_info))
        
        return "\n\n".join(formatted)


prompt_templates = PromptTemplates()
