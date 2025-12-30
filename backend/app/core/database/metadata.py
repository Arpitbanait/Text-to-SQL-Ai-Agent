from typing import Dict, Any, List
import json
import os
from datetime import datetime
from app.utils.logger import logger


class SchemaMetadataStore:
    """Store and retrieve schema metadata"""
    
    def __init__(self, storage_path: str = "./data/schemas"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def save_metadata(
        self,
        database_name: str,
        metadata: Dict[str, Any]
    ):
        """Save schema metadata to file"""
        try:
            metadata['last_updated'] = datetime.now().isoformat()
            
            file_path = os.path.join(self.storage_path, f"{database_name}.json")
            
            with open(file_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Saved metadata for database: {database_name}")
        
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")
    
    def load_metadata(
        self,
        database_name: str
    ) -> Dict[str, Any]:
        """Load schema metadata from file"""
        try:
            file_path = os.path.join(self.storage_path, f"{database_name}.json")
            
            if not os.path.exists(file_path):
                logger.warning(f"No metadata found for database: {database_name}")
                return {}
            
            with open(file_path, 'r') as f:
                metadata = json.load(f)
            
            logger.info(f"Loaded metadata for database: {database_name}")
            return metadata
        
        except Exception as e:
            logger.error(f"Failed to load metadata: {str(e)}")
            return {}
    
    def list_databases(self) -> List[str]:
        """List all databases with stored metadata"""
        try:
            files = os.listdir(self.storage_path)
            databases = [f.replace('.json', '') for f in files if f.endswith('.json')]
            return databases
        
        except Exception as e:
            logger.error(f"Failed to list databases: {str(e)}")
            return []
    
    def delete_metadata(self, database_name: str):
        """Delete metadata for a database"""
        try:
            file_path = os.path.join(self.storage_path, f"{database_name}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted metadata for database: {database_name}")
        
        except Exception as e:
            logger.error(f"Failed to delete metadata: {str(e)}")


# Global instance
metadata_store = SchemaMetadataStore()
