from typing import List, Optional
import asyncio
import os
from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import VectorStoreException


class EmbeddingGenerator:
    """Generate embeddings for text using HuggingFace models"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.model = None
        
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            hf_token = settings.HUGGINGFACE_API_KEY or os.getenv("HF_TOKEN", "")
            if hf_token and not os.getenv("HF_TOKEN"):
                os.environ["HF_TOKEN"] = hf_token

            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise VectorStoreException(f"Failed to load embedding model: {str(e)}")

    def _ensure_model_loaded(self):
        """Load model on first use to reduce startup memory usage."""
        if self.model is None:
            self._load_model()
    

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            self._ensure_model_loaded()
            
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
            self._ensure_model_loaded()
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


_embedding_generator_instance: Optional[EmbeddingGenerator] = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Lazily initialize and return the embedding generator singleton."""
    global _embedding_generator_instance

    if _embedding_generator_instance is None:
        _embedding_generator_instance = EmbeddingGenerator()

    return _embedding_generator_instance
