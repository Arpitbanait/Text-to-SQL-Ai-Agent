from sentence_transformers import SentenceTransformer
from typing import List
import asyncio
from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import VectorStoreException


class EmbeddingGenerator:
    """Generate embeddings for text using HuggingFace models"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise VectorStoreException(f"Failed to load embedding model: {str(e)}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.model.encode(text, convert_to_numpy=True).tolist()
            )
            logger.info(f"Generated embedding for text of length {len(text)}")
            return embedding
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise VectorStoreException(f"Failed to generate embedding: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, convert_to_numpy=True).tolist()
            )
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {str(e)}")
            raise VectorStoreException(f"Failed to generate embeddings: {str(e)}")


# Global instance
embedding_generator = EmbeddingGenerator()
