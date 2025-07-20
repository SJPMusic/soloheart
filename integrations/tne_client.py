#!/usr/bin/env python3
"""
TNE Client for SoloHeart

HTTP client wrapper for The Narrative Engine API Server.
Allows SoloHeart to interact with TNE without importing any TNE modules directly.

This client provides a clean interface to all TNE functionality via HTTP requests.
"""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TNEClient:
    """
    HTTP client for The Narrative Engine API Server.
    
    Provides methods to interact with TNE functionality without direct imports.
    All communication is done via HTTP requests to the TNE API server.
    """
    
    def __init__(self, base_url: str = "http://localhost:5002", campaign_id: str = None):
        """
        Initialize the TNE client.
        
        Args:
            base_url: URL to the TNE API server (default: localhost:5002)
            campaign_id: Optional identifier to tag requests
        """
        self.base_url = base_url.rstrip('/')
        self.campaign_id = campaign_id or "default"
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SoloHeart-TNE-Client/1.0'
        })
        
        logger.info(f"🔌 Initialized TNE Client for {self.base_url} (campaign: {self.campaign_id})")
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, 
                     params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the TNE API server.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data (for POST requests)
            params: Query parameters (for GET requests)
            
        Returns:
            Parsed JSON response or error dict
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"🌐 {method} {url}")
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request failed: {str(e)}"
            logger.warning(f"❌ {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.warning(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def add_memory_entry(self, entry: dict) -> dict:
        """
        Add a memory entry to the narrative engine.
        
        Args:
            entry: Memory entry data
            
        Returns:
            Parsed response as a dictionary
        """
        logger.info(f"📝 Adding memory entry for campaign: {self.campaign_id}")
        
        data = {
            "text": entry.get("text", ""),
            "campaign_id": self.campaign_id
        }
        
        return self._make_request("POST", "/memory/add", data=data)
    
    def query_concepts(self, query: str = "") -> dict:
        """
        Query symbolic concepts from current memory.
        
        Args:
            query: Optional query string for concept filtering
            
        Returns:
            Parsed JSON result of symbolic reasoning
        """
        logger.info(f"🔍 Querying concepts for campaign: {self.campaign_id}")
        
        params = {
            "campaign_id": self.campaign_id
        }
        
        if query:
            params["query"] = query
        
        return self._make_request("GET", "/memory/query_concepts", params=params)
    
    def query_identity(self) -> dict:
        """
        Query identity information from memory.
        
        Returns:
            Symbolic identity analysis result
        """
        logger.info(f"🔍 Querying identity for campaign: {self.campaign_id}")
        
        params = {
            "campaign_id": self.campaign_id
        }
        
        return self._make_request("GET", "/memory/query_identity", params=params)
    
    def add_scene(self, scene: dict) -> dict:
        """
        Add a scene entry with symbolic identity analysis.
        
        Args:
            scene: Scene data to add
            
        Returns:
            Confirmation and indexing result
        """
        logger.info(f"📝 Adding scene for campaign: {self.campaign_id}")
        
        data = {
            "text": scene.get("text", ""),
            "campaign_id": self.campaign_id
        }
        
        return self._make_request("POST", "/scene/add", data=data)
    
    def get_scene_stats(self) -> dict:
        """
        Get statistics about stored scenes.
        
        Returns:
            Metadata about scenes stored
        """
        logger.info(f"📊 Getting scene stats for campaign: {self.campaign_id}")
        
        params = {
            "campaign_id": self.campaign_id
        }
        
        return self._make_request("GET", "/scene/stats", params=params)
    
    def get_symbolic_summary(self) -> dict:
        """
        Get symbolic summary of all stored scenes.
        
        Returns:
            Symbolic layer abstraction for narrative state
        """
        logger.info(f"🔍 Getting symbolic summary for campaign: {self.campaign_id}")
        
        params = {
            "campaign_id": self.campaign_id
        }
        
        return self._make_request("GET", "/symbolic/summary", params=params)
    
    def is_healthy(self) -> bool:
        """
        Check if the TNE API server is healthy.
        
        Returns:
            True if HTTP 200, else False
        """
        try:
            response = self._make_request("GET", "/health")
            return "error" not in response and response.get("result", {}).get("status") == "healthy"
        except Exception as e:
            logger.warning(f"❌ Health check failed: {e}")
            return False
    
    def get_server_info(self) -> dict:
        """
        Get server information and status.
        
        Returns:
            Server information including version and status
        """
        logger.info("ℹ️ Getting server info")
        
        return self._make_request("GET", "/")
    
    def set_campaign_id(self, campaign_id: str) -> None:
        """
        Set the campaign ID for subsequent requests.
        
        Args:
            campaign_id: New campaign identifier
        """
        self.campaign_id = campaign_id
        logger.info(f"🔄 Campaign ID set to: {self.campaign_id}")
    
    def get_campaign_id(self) -> str:
        """
        Get the current campaign ID.
        
        Returns:
            Current campaign identifier
        """
        return self.campaign_id
    
    def test_connection(self) -> dict:
        """
        Test the connection to the TNE API server.
        
        Returns:
            Connection test result with details
        """
        logger.info("🧪 Testing connection to TNE API server")
        
        result = {
            "base_url": self.base_url,
            "campaign_id": self.campaign_id,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test health endpoint
        health_result = self.is_healthy()
        result["tests"]["health"] = {
            "status": "passed" if health_result else "failed",
            "endpoint": f"{self.base_url}/health"
        }
        
        # Test server info
        server_info = self.get_server_info()
        result["tests"]["server_info"] = {
            "status": "passed" if "error" not in server_info else "failed",
            "endpoint": f"{self.base_url}/",
            "response": server_info
        }
        
        # Overall status
        all_passed = all(test["status"] == "passed" for test in result["tests"].values())
        result["overall_status"] = "connected" if all_passed else "disconnected"
        
        logger.info(f"✅ Connection test completed: {result['overall_status']}")
        return result 