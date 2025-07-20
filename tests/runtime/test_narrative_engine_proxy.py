"""
Unit tests for NarrativeEngineProxy class.

Tests the high-level proxy wrapper around TNEClient for SoloHeart runtime integration.
"""

import pytest
from unittest.mock import Mock, patch
from runtime.narrative_engine_proxy import NarrativeEngineProxy


class TestNarrativeEngineProxy:
    """Test suite for NarrativeEngineProxy class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.campaign_id = "test_campaign_123"
        self.base_url = "http://localhost:5002"
        self.proxy = NarrativeEngineProxy(self.campaign_id, self.base_url)
    
    def test_initialization(self):
        """Test proxy initialization with valid parameters."""
        proxy = NarrativeEngineProxy("test_campaign", "http://test:5002")
        
        assert proxy.campaign_id == "test_campaign"
        assert proxy.base_url == "http://test:5002"
        assert proxy._client is not None
    
    def test_initialization_with_default_url(self):
        """Test proxy initialization with default base URL."""
        proxy = NarrativeEngineProxy("test_campaign")
        
        assert proxy.campaign_id == "test_campaign"
        assert proxy.base_url == "http://localhost:5002"
    
    def test_record_scene_success(self):
        """Test successful scene recording."""
        # Mock the TNEClient.add_scene method
        with patch.object(self.proxy._client, 'add_scene') as mock_add_scene:
            mock_add_scene.return_value = {'status': 'success', 'scene_id': 'scene_123'}
            
            result = self.proxy.record_scene("A dark forest scene", {'location': 'forest'})
            
            mock_add_scene.assert_called_once_with("A dark forest scene", {'location': 'forest'})
            assert result['status'] == 'success'
            assert result['scene_id'] == 'scene_123'
    
    
    def test_record_scene_failure(self):
        """Test scene recording failure handling."""
        with patch.object(self.proxy._client, 'add_scene') as mock_add_scene:
            mock_add_scene.side_effect = Exception("Connection failed")
            
            result = self.proxy.record_scene("A scene")
            
            assert result['error'] == "Connection failed"
            assert result['status'] == 'failed'
    
    
    def test_add_memory_success(self):
        """Test successful memory addition."""
        with patch.object(self.proxy._client, 'add_memory_entry') as mock_add_memory:
            mock_add_memory.return_value = {'status': 'success', 'memory_id': 'mem_123'}
            
            memory_entry = {'type': 'combat', 'description': 'Fought a dragon'}
            result = self.proxy.add_memory(memory_entry)
            
            mock_add_memory.assert_called_once_with(memory_entry)
            assert result['status'] == 'success'
            assert result['memory_id'] == 'mem_123'
    
    
    def test_add_memory_failure(self):
        """Test memory addition failure handling."""
        with patch.object(self.proxy._client, 'add_memory_entry') as mock_add_memory:
            mock_add_memory.side_effect = Exception("Memory storage failed")
            
            result = self.proxy.add_memory({'type': 'test'})
            
            assert result['error'] == "Memory storage failed"
            assert result['status'] == 'failed'
    
    
    def test_get_summary_success(self):
        """Test successful summary retrieval."""
        with patch.object(self.proxy._client, 'get_symbolic_summary') as mock_get_summary:
            mock_get_summary.return_value = {
                'status': 'success',
                'summary': 'The hero has completed three quests and gained experience.'
            }
            
            result = self.proxy.get_summary()
            
            mock_get_summary.assert_called_once()
            assert result == 'The hero has completed three quests and gained experience.'
    
    
    def test_get_summary_failure(self):
        """Test summary retrieval failure handling."""
        with patch.object(self.proxy._client, 'get_symbolic_summary') as mock_get_summary:
            mock_get_summary.side_effect = Exception("Summary generation failed")
            
            result = self.proxy.get_summary()
            
            assert result == "Error retrieving summary: Summary generation failed"
    
    
    def test_get_summary_no_summary_field(self):
        """Test summary retrieval when response lacks summary field."""
        with patch.object(self.proxy._client, 'get_symbolic_summary') as mock_get_summary:
            mock_get_summary.return_value = {'status': 'success'}
            
            result = self.proxy.get_summary()
            
            assert result == 'No summary available'
    
    
    def test_get_identity_profile_success(self):
        """Test successful identity profile retrieval."""
        with patch.object(self.proxy._client, 'query_identity') as mock_query_identity:
            mock_query_identity.return_value = {
                'status': 'success',
                'identity': {
                    'name': 'Hero',
                    'background': 'Warrior',
                    'level': 5
                }
            }
            
            result = self.proxy.get_identity_profile()
            
            mock_query_identity.assert_called_once()
            assert result['status'] == 'success'
            assert result['identity']['name'] == 'Hero'
    
    
    def test_get_identity_profile_failure(self):
        """Test identity profile retrieval failure handling."""
        with patch.object(self.proxy._client, 'query_identity') as mock_query_identity:
            mock_query_identity.side_effect = Exception("Identity query failed")
            
            result = self.proxy.get_identity_profile()
            
            assert result['error'] == "Identity query failed"
            assert result['status'] == 'failed'
    
    
    def test_search_memory_success(self):
        """Test successful memory search."""
        with patch.object(self.proxy._client, 'query_concepts') as mock_query_concepts:
            mock_query_concepts.return_value = {
                'status': 'success',
                'results': [
                    {'memory_id': 'mem_1', 'relevance': 0.9},
                    {'memory_id': 'mem_2', 'relevance': 0.7}
                ]
            }
            
            result = self.proxy.search_memory("dragon fight")
            
            mock_query_concepts.assert_called_once_with("dragon fight")
            assert result['status'] == 'success'
            assert len(result['results']) == 2
    
    
    def test_search_memory_failure(self):
        """Test memory search failure handling."""
        with patch.object(self.proxy._client, 'query_concepts') as mock_query_concepts:
            mock_query_concepts.side_effect = Exception("Memory search failed")
            
            result = self.proxy.search_memory("dragon fight")
            
            assert result['error'] == "Memory search failed"
            assert result['status'] == 'failed'
            assert result['results'] == []
    
    
    def test_get_scene_stats_success(self):
        """Test successful scene stats retrieval."""
        with patch.object(self.proxy._client, 'get_scene_stats') as mock_get_stats:
            mock_get_stats.return_value = {
                'status': 'success',
                'stats': {
                    'total_scenes': 15,
                    'avg_scene_length': 250,
                    'last_scene_time': '2024-01-15T10:30:00Z'
                }
            }
            
            result = self.proxy.get_scene_stats()
            
            mock_get_stats.assert_called_once()
            assert result['status'] == 'success'
            assert result['stats']['total_scenes'] == 15
    
    
    def test_get_scene_stats_failure(self):
        """Test scene stats retrieval failure handling."""
        with patch.object(self.proxy._client, 'get_scene_stats') as mock_get_stats:
            mock_get_stats.side_effect = Exception("Stats retrieval failed")
            
            result = self.proxy.get_scene_stats()
            
            assert result['error'] == "Stats retrieval failed"
            assert result['status'] == 'failed'
    
    
    def test_is_online_success(self):
        """Test successful health check."""
        with patch.object(self.proxy._client, 'is_healthy') as mock_is_healthy:
            mock_is_healthy.return_value = {'status': 'healthy'}
            
            result = self.proxy.is_online()
            
            mock_is_healthy.assert_called_once()
            assert result is True
    
    
    def test_is_online_unhealthy(self):
        """Test health check when TNE is unhealthy."""
        with patch.object(self.proxy._client, 'is_healthy') as mock_is_healthy:
            mock_is_healthy.return_value = {'status': 'unhealthy'}
            
            result = self.proxy.is_online()
            
            assert result is False
    
    
    def test_is_online_failure(self):
        """Test health check failure handling."""
        with patch.object(self.proxy._client, 'is_healthy') as mock_is_healthy:
            mock_is_healthy.side_effect = Exception("Health check failed")
            
            result = self.proxy.is_online()
            
            assert result is False
    
    def test_get_campaign_id(self):
        """Test campaign ID retrieval."""
        result = self.proxy.get_campaign_id()
        assert result == self.campaign_id
    
    def test_reset_campaign(self):
        """Test campaign reset functionality."""
        new_campaign_id = "new_campaign_456"
        
        with patch('runtime.narrative_engine_proxy.TNEClient') as mock_tne_client:
            self.proxy.reset_campaign(new_campaign_id)
            
            assert self.proxy.campaign_id == new_campaign_id
            mock_tne_client.assert_called_once_with(
                base_url=self.base_url,
                campaign_id=new_campaign_id
            )
    
    def test_record_scene_without_metadata(self):
        """Test scene recording without metadata."""
        with patch.object(self.proxy._client, 'add_scene') as mock_add_scene:
            mock_add_scene.return_value = {'status': 'success'}
            
            result = self.proxy.record_scene("A simple scene")
            
            mock_add_scene.assert_called_once_with("A simple scene", {})
            assert result['status'] == 'success'
    
    
    def test_integration_with_tne_client(self):
        """Test that proxy properly wraps TNEClient methods."""
        # Test that all proxy methods call their corresponding TNEClient methods
        methods_to_test = [
            ('record_scene', 'add_scene', ["test scene"], {}),
            ('add_memory', 'add_memory_entry', [{'type': 'test'}], {}),
            ('get_summary', 'get_symbolic_summary', [], {}),
            ('get_identity_profile', 'query_identity', [], {}),
            ('search_memory', 'query_concepts', ["test query"], {}),
            ('get_scene_stats', 'get_scene_stats', [], {}),
            ('is_online', 'is_healthy', [], {})
        ]
        
        for proxy_method, client_method, args, kwargs in methods_to_test:
            with patch.object(self.proxy._client, client_method) as mock_client_method:
                mock_client_method.return_value = {'status': 'success'}
                
                getattr(self.proxy, proxy_method)(*args, **kwargs)
                
                mock_client_method.assert_called_once() 