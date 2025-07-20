#!/usr/bin/env python3
"""
Tests for TNEClient

Comprehensive test suite for the TNEClient class with mocked HTTP responses.
Tests all methods and error handling scenarios.
"""

import pytest
import responses
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the TNEClient
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from integrations.tne_client import TNEClient


class TestTNEClient:
    """Test suite for TNEClient class."""
    
    @pytest.fixture
    def client(self):
        """Create a TNEClient instance for testing."""
        return TNEClient(base_url="http://localhost:5002", campaign_id="test_campaign")
    
    @pytest.fixture
    def mock_responses(self):
        """Set up mock responses for HTTP requests."""
        with responses.RequestsMock() as rsps:
            yield rsps
    
    def test_init_default_values(self):
        """Test TNEClient initialization with default values."""
        client = TNEClient()
        assert client.base_url == "http://localhost:5002"
        assert client.campaign_id == "default"
        assert client.session.headers['Content-Type'] == 'application/json'
        assert client.session.headers['User-Agent'] == 'SoloHeart-TNE-Client/1.0'
    
    def test_init_custom_values(self):
        """Test TNEClient initialization with custom values."""
        client = TNEClient(base_url="http://test-server:8080", campaign_id="custom_campaign")
        assert client.base_url == "http://test-server:8080"
        assert client.campaign_id == "custom_campaign"
    
    def test_init_strips_trailing_slash(self):
        """Test that base_url trailing slash is stripped."""
        client = TNEClient(base_url="http://localhost:5002/")
        assert client.base_url == "http://localhost:5002"
    
    @responses.activate
    def test_add_memory_entry_success(self, client):
        """Test successful memory entry addition."""
        # Mock the API response
        mock_response = {
            "result": {
                "success": True,
                "message": "Memory entry added successfully",
                "campaign_id": "test_campaign",
                "timestamp": "2024-01-01T12:00:00"
            }
        }
        
        responses.add(
            responses.POST,
            "http://localhost:5002/memory/add",
            json=mock_response,
            status=200
        )
        
        # Test the method
        entry = {"text": "Test memory entry"}
        result = client.add_memory_entry(entry)
        
        # Verify the request
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == 'POST'
        assert request.url == "http://localhost:5002/memory/add"
        
        # Verify the request body
        request_body = json.loads(request.body)
        assert request_body["text"] == "Test memory entry"
        assert request_body["campaign_id"] == "test_campaign"
        
        # Verify the response
        assert result == mock_response
    
    @responses.activate
    def test_add_memory_entry_error(self, client):
        """Test memory entry addition with error."""
        # Mock an error response
        responses.add(
            responses.POST,
            "http://localhost:5002/memory/add",
            json={"error": "Server error"},
            status=500
        )
        
        # Test the method
        entry = {"text": "Test memory entry"}
        result = client.add_memory_entry(entry)
        
        # Verify error handling
        assert "error" in result
        assert "HTTP request failed" in result["error"]
    
    @responses.activate
    def test_query_concepts_success(self, client):
        """Test successful concept query."""
        # Mock the API response
        mock_response = {
            "result": {
                "concepts": {"test_concept": {"confidence": 0.8}},
                "conflicts": [],
                "summary": {
                    "total_concepts": 1,
                    "total_conflicts": 0
                }
            }
        }
        
        responses.add(
            responses.GET,
            "http://localhost:5002/memory/query_concepts",
            json=mock_response,
            status=200
        )
        
        # Test the method
        result = client.query_concepts()
        
        # Verify the request
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == 'GET'
        assert "campaign_id=test_campaign" in request.url
        
        # Verify the response
        assert result == mock_response
    
    @responses.activate
    def test_query_concepts_with_query(self, client):
        """Test concept query with specific query parameter."""
        # Mock the API response
        mock_response = {"result": {"concepts": {}}}
        
        responses.add(
            responses.GET,
            "http://localhost:5002/memory/query_concepts",
            json=mock_response,
            status=200
        )
        
        # Test the method with query
        result = client.query_concepts("test query")
        
        # Verify the request includes query parameter
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "query=test+query" in request.url
    
    @responses.activate
    def test_query_identity_success(self, client):
        """Test successful identity query."""
        # Mock the API response
        mock_response = {
            "result": {
                "identity_profile": ["I am a test character"],
                "contradictions": [],
                "alignment_score": 0.9
            }
        }
        
        responses.add(
            responses.GET,
            "http://localhost:5002/memory/query_identity",
            json=mock_response,
            status=200
        )
        
        # Test the method
        result = client.query_identity()
        
        # Verify the request
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == 'GET'
        assert "campaign_id=test_campaign" in request.url
        
        # Verify the response
        assert result == mock_response
    
    @responses.activate
    def test_add_scene_success(self, client):
        """Test successful scene addition."""
        # Mock the API response
        mock_response = {
            "result": {
                "scene_id": "scene_123",
                "scene_text": "Test scene",
                "identity_facts": [],
                "contradictions": [],
                "timestamp": "2024-01-01T12:00:00"
            }
        }
        
        responses.add(
            responses.POST,
            "http://localhost:5002/scene/add",
            json=mock_response,
            status=200
        )
        
        # Test the method
        scene = {"text": "Test scene"}
        result = client.add_scene(scene)
        
        # Verify the request
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == 'POST'
        assert request.url == "http://localhost:5002/scene/add"
        
        # Verify the request body
        request_body = json.loads(request.body)
        assert request_body["text"] == "Test scene"
        assert request_body["campaign_id"] == "test_campaign"
        
        # Verify the response
        assert result == mock_response
    
    @responses.activate
    def test_get_scene_stats_success(self, client):
        """Test successful scene statistics retrieval."""
        # Mock the API response
        mock_response = {
            "result": {
                "total_scenes": 5,
                "total_identity_facts": 25,
                "total_contradictions": 2,
                "average_facts_per_scene": 5.0,
                "scenes_with_contradictions": 1,
                "most_recent_scene_id": "scene_123"
            }
        }
        
        responses.add(
            responses.GET,
            "http://localhost:5002/scene/stats",
            json=mock_response,
            status=200
        )
        
        # Test the method
        result = client.get_scene_stats()
        
        # Verify the request
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == 'GET'
        assert "campaign_id=test_campaign" in request.url
        
        # Verify the response
        assert result == mock_response
    
    @responses.activate
    def test_get_symbolic_summary_success(self, client):
        """Test successful symbolic summary retrieval."""
        # Mock the API response
        mock_response = {
            "result": {
                "identity_profile": {
                    "total_facts": 25,
                    "fact_categories": {
                        "roles": ["hero", "wizard"],
                        "values": ["bravery", "wisdom"],
                        "beliefs": ["good triumphs over evil"],
                        "emotions": ["determination"],
                        "goals": ["save the world"]
                    },
                    "confidence_score": 0.85
                },
                "contradictions": [],
                "fact_count": 25,
                "scene_count": 5
            }
        }
        
        responses.add(
            responses.GET,
            "http://localhost:5002/symbolic/summary",
            json=mock_response,
            status=200
        )
        
        # Test the method
        result = client.get_symbolic_summary()
        
        # Verify the request
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == 'GET'
        assert "campaign_id=test_campaign" in request.url
        
        # Verify the response
        assert result == mock_response
    
    @responses.activate
    def test_is_healthy_success(self, client):
        """Test successful health check."""
        # Mock the API response
        mock_response = {
            "result": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00",
                "active_campaigns": 1,
                "campaign_ids": ["test_campaign"]
            }
        }
        
        responses.add(
            responses.GET,
            "http://localhost:5002/health",
            json=mock_response,
            status=200
        )
        
        # Test the method
        result = client.is_healthy()
        
        # Verify the result
        assert result is True
    
    @responses.activate
    def test_is_healthy_failure(self, client):
        """Test health check failure."""
        # Mock an error response
        responses.add(
            responses.GET,
            "http://localhost:5002/health",
            json={"error": "Server error"},
            status=500
        )
        
        # Test the method
        result = client.is_healthy()
        
        # Verify the result
        assert result is False
    
    @responses.activate
    def test_get_server_info_success(self, client):
        """Test successful server info retrieval."""
        # Mock the API response
        mock_response = {
            "result": {
                "name": "The Narrative Engine API",
                "version": "1.0.0",
                "description": "HTTP API for narrative processing",
                "documentation": "/docs",
                "health_check": "/health",
                "timestamp": "2024-01-01T12:00:00"
            }
        }
        
        responses.add(
            responses.GET,
            "http://localhost:5002/",
            json=mock_response,
            status=200
        )
        
        # Test the method
        result = client.get_server_info()
        
        # Verify the request
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == 'GET'
        assert request.url == "http://localhost:5002/"
        
        # Verify the response
        assert result == mock_response
    
    def test_set_campaign_id(self, client):
        """Test setting campaign ID."""
        # Test initial value
        assert client.campaign_id == "test_campaign"
        
        # Set new campaign ID
        client.set_campaign_id("new_campaign")
        assert client.campaign_id == "new_campaign"
    
    def test_get_campaign_id(self, client):
        """Test getting campaign ID."""
        assert client.get_campaign_id() == "test_campaign"
    
    @responses.activate
    def test_test_connection_success(self, client):
        """Test successful connection test."""
        # Mock health endpoint
        responses.add(
            responses.GET,
            "http://localhost:5002/health",
            json={"result": {"status": "healthy"}},
            status=200
        )
        
        # Mock server info endpoint
        responses.add(
            responses.GET,
            "http://localhost:5002/",
            json={"result": {"name": "TNE API"}},
            status=200
        )
        
        # Test the method
        result = client.test_connection()
        
        # Verify the result structure
        assert "base_url" in result
        assert "campaign_id" in result
        assert "timestamp" in result
        assert "tests" in result
        assert "overall_status" in result
        
        # Verify test results
        assert result["overall_status"] == "connected"
        assert result["tests"]["health"]["status"] == "passed"
        assert result["tests"]["server_info"]["status"] == "passed"
    
    @responses.activate
    def test_test_connection_failure(self, client):
        """Test connection test with failures."""
        # Mock health endpoint failure
        responses.add(
            responses.GET,
            "http://localhost:5002/health",
            json={"error": "Server error"},
            status=500
        )
        
        # Mock server info endpoint failure
        responses.add(
            responses.GET,
            "http://localhost:5002/",
            json={"error": "Server error"},
            status=500
        )
        
        # Test the method
        result = client.test_connection()
        
        # Verify the result
        assert result["overall_status"] == "disconnected"
        assert result["tests"]["health"]["status"] == "failed"
        assert result["tests"]["server_info"]["status"] == "failed"
    
    @responses.activate
    def test_timeout_handling(self, client):
        """Test timeout handling."""
        # Mock a timeout scenario
        responses.add(
            responses.GET,
            "http://localhost:5002/health",
            body=requests.exceptions.Timeout("Request timed out")
        )
        
        # Test the method
        result = client.is_healthy()
        
        # Verify timeout is handled
        assert result is False
    
    @responses.activate
    def test_connection_error_handling(self, client):
        """Test connection error handling."""
        # Mock a connection error
        responses.add(
            responses.GET,
            "http://localhost:5002/health",
            body=requests.exceptions.ConnectionError("Connection failed")
        )
        
        # Test the method
        result = client.is_healthy()
        
        # Verify connection error is handled
        assert result is False
    
    def test_make_request_unsupported_method(self, client):
        """Test handling of unsupported HTTP methods."""
        with pytest.raises(ValueError, match="Unsupported HTTP method"):
            client._make_request("PUT", "/test")
    
    @responses.activate
    def test_make_request_json_decode_error(self, client):
        """Test handling of JSON decode errors."""
        # Mock a response with invalid JSON
        responses.add(
            responses.GET,
            "http://localhost:5002/health",
            body="Invalid JSON",
            status=200
        )
        
        # Test the method
        result = client.is_healthy()
        
        # Verify JSON decode error is handled
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__]) 