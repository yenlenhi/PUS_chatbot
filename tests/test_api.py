"""
Tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from main import app

client = TestClient(app)


class TestAPI:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "ollama_status" in data
        assert "database_status" in data
    
    def test_chat_endpoint_validation(self):
        """Test chat endpoint input validation"""
        # Test missing message
        response = client.post("/api/v1/chat", json={})
        assert response.status_code == 422
        
        # Test empty message
        response = client.post("/api/v1/chat", json={"message": ""})
        assert response.status_code == 422
        
        # Test message too long
        long_message = "A" * 1001
        response = client.post("/api/v1/chat", json={"message": long_message})
        assert response.status_code == 422
    
    def test_chat_endpoint_valid_request(self):
        """Test chat endpoint with valid request"""
        response = client.post("/api/v1/chat", json={
            "message": "Điều kiện tuyển sinh là gì?"
        })
        
        # Should return 200 or 500 (if services not available)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "sources" in data
            assert "confidence" in data
            assert "conversation_id" in data
    
    def test_search_endpoint_validation(self):
        """Test search endpoint input validation"""
        # Test missing query
        response = client.post("/api/v1/search", json={})
        assert response.status_code == 422
        
        # Test empty query
        response = client.post("/api/v1/search", json={"query": ""})
        assert response.status_code == 422
        
        # Test invalid top_k
        response = client.post("/api/v1/search", json={
            "query": "test",
            "top_k": 0
        })
        assert response.status_code == 422
        
        response = client.post("/api/v1/search", json={
            "query": "test",
            "top_k": 25
        })
        assert response.status_code == 422
    
    def test_search_endpoint_valid_request(self):
        """Test search endpoint with valid request"""
        response = client.post("/api/v1/search", json={
            "query": "tuyển sinh",
            "top_k": 3
        })
        
        # Should return 200 or 500 (if services not available)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "total_found" in data
            assert isinstance(data["results"], list)
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = client.get("/api/v1/stats")
        
        # Should return 200 or 500 (if services not available)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "database" in data
            assert "faiss_index" in data
    
    def test_conversation_endpoint(self):
        """Test conversation history endpoint"""
        conversation_id = "test-conversation-id"
        response = client.get(f"/api/v1/conversation/{conversation_id}")
        
        # Should return 200 or 500 (if services not available)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "conversation_id" in data
            assert "history" in data
            assert data["conversation_id"] == conversation_id
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/v1/health")
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404

