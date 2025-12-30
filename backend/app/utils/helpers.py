import re
from typing import Dict, Any


def clean_sql_query(sql: str) -> str:
    """Clean and format SQL query"""
    sql = sql.strip()
    # Remove markdown code blocks if present
    sql = re.sub(r'^```sql\s*', '', sql)
    sql = re.sub(r'^```\s*', '', sql)
    sql = re.sub(r'\s*```$', '', sql)
    return sql.strip()


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text that may contain markdown or other formatting"""
    import json
    
    # Try to find JSON in code blocks
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))
    
    # Try to find raw JSON
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    
    return {}


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
