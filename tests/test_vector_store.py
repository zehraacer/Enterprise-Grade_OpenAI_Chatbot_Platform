# tests/test_vector_store.py
import pytest
import numpy as np
import faiss
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def vector_store(dimension=1536):
    index = faiss.IndexFlatL2(dimension)
    return index

def test_vector_addition(vector_store):
    """Test adding vectors to FAISS index"""
    test_vector = np.random.rand(1, vector_store.d).astype('float32')
    vector_store.add(test_vector)
    assert vector_store.ntotal == 1

def test_vector_search(vector_store):
    """Test vector similarity search"""
    # Add test vectors
    vectors = np.random.rand(5, vector_store.d).astype('float32')
    vector_store.add(vectors)
    
    # Search
    query = vectors[0].reshape(1, -1)
    D, I = vector_store.search(query, k=1)
    
    assert I[0][0] == 0  # Should find the first vector
    assert D[0][0] <= 1e-5  # Distance should be very small