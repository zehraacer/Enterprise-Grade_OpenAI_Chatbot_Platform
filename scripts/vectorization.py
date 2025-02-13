# scripts/vectorization.py
import json
import numpy as np
import faiss
import openai
from typing import List, Dict
import os
import logging
from tqdm import tqdm
import asyncio
from app.exceptions import DatabaseException

# Suppress FAISS logs
logging.getLogger('faiss').disabled = True

# Logger configuration
logger = logging.getLogger('app.vectorization')

class VectorDatabase:
    def __init__(self):
        self.dimension = 1536  # OpenAI embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.embeddings = []
        self.batch_size = 100

    def create_embedding(self, text: str) -> np.ndarray:
        """Synchronous embedding creation"""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return np.array(response['data'][0]['embedding'], dtype=np.float32)
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise

    def add_documents(self, documents: List[Dict[str, str]]):
        """Synchronous version"""
        try:
            for doc in tqdm(documents, desc="Processing documents"):
                full_text = f"{doc['title']} {doc['content']}"
                try:
                    embedding = self.create_embedding(full_text)
                    self.embeddings.append(embedding)
                    self.documents.append(doc)
                    
                    # Batch processing
                    if len(self.embeddings) >= self.batch_size:
                        self._add_batch_to_index()
                        
                except Exception as e:
                    logger.error(f"Error processing document: {str(e)}")
                    continue

            # Add remaining embeddings
            if self.embeddings:
                self._add_batch_to_index()
                
        except Exception as e:
            raise DatabaseException(f"Database error: {str(e)}")

    async def create_embedding_async(self, text: str) -> np.ndarray:
        """Asynchronous embedding creation"""
        try:
            response = await openai.Embedding.acreate(
                input=text,
                model="text-embedding-ada-002"
            )
            return np.array(response['data'][0]['embedding'], dtype=np.float32)
        except Exception as e:
            logger.error(f"Error creating asynchronous embedding: {str(e)}")
            raise

    def _add_batch_to_index(self):
        """Batch embedding addition"""
        if not self.embeddings:
            return
            
        embeddings_array = np.array(self.embeddings)
        self.index.add(embeddings_array)
        logger.info(f"{len(self.embeddings)} documents added to the database")
        self.embeddings = []  # Reset embeddings list

    async def add_documents_async(self, documents: List[Dict[str, str]]):
        """Asynchronous version"""
        try:
            tasks = []
            for doc in documents:
                full_text = f"{doc['title']} {doc['content']}"
                task = asyncio.create_task(self.create_embedding_async(full_text))
                tasks.append((task, doc))

            for i, (task, doc) in enumerate(tqdm(tasks, desc="Processing documents")):
                try:
                    embedding = await task
                    self.embeddings.append(embedding)
                    self.documents.append(doc)

                    # Batch processing
                    if len(self.embeddings) >= self.batch_size:
                        self._add_batch_to_index()

                except Exception as e:
                    logger.error(f"Error processing document: {str(e)}")
                    continue

            # Add remaining embeddings
            if self.embeddings:
                self._add_batch_to_index()

        except Exception as e:
            raise DatabaseException(f"Database error: {str(e)}")

    def save(self, index_file: str = "models/vector_index.faiss",
            docs_file: str = "models/documents.pkl"):
        """Save the database"""
        try:
            os.makedirs(os.path.dirname(index_file), exist_ok=True)
            faiss.write_index(self.index, index_file)
            
            import pickle
            with open(docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            logger.info(f"Database saved: {index_file} and {docs_file}")
            
        except Exception as e:
            raise DatabaseException(f"Save error: {str(e)}")

async def main_async():
    try:
        # Load the knowledge base
        with open("data/knowledge_base.json", 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # Create and save the database
        db = VectorDatabase()
        await db.add_documents_async(documents)
        db.save()
        
    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main_async())