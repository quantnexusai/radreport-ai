import pytest
from unittest.mock import MagicMock, patch


class TestClaudeClient:
    """Tests for the ClaudeClient class."""

    @patch("utils.claude_client.requests.post")
    def test_process_findings(self, mock_post, mock_env_vars):
        """Test processing findings with Claude."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "The heart is normal in size."}]
        }
        mock_post.return_value = mock_response
        
        from utils.claude_client import ClaudeClient
        client = ClaudeClient()
        
        result = client.process_findings("heart normal size", "chest")
        
        assert "heart" in result.lower()
        mock_post.assert_called_once()

    @patch("utils.claude_client.requests.post")
    def test_generate_impression(self, mock_post, mock_env_vars):
        """Test generating impression for a finding."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "Hepatomegaly. Clinical correlation recommended."}]
        }
        mock_post.return_value = mock_response
        
        from utils.claude_client import ClaudeClient
        client = ClaudeClient()
        
        result = client.generate_impression("liver is enlarged", "abdomen_pelvis")
        
        assert len(result) > 0
        mock_post.assert_called_once()

    @patch("utils.claude_client.requests.post")
    def test_api_retry_on_rate_limit(self, mock_post, mock_env_vars):
        """Test that API retries on rate limit."""
        # First call returns 429, second succeeds
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.text = "Rate limited"
        
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "content": [{"text": "Test response"}]
        }
        
        mock_post.side_effect = [rate_limit_response, success_response]
        
        from utils.claude_client import ClaudeClient
        client = ClaudeClient()
        
        result = client.process_findings("test", "chest")
        
        assert result == "Test response"
        assert mock_post.call_count == 2

    @patch("utils.claude_client.requests.post")
    def test_categorize_findings(self, mock_post, mock_env_vars):
        """Test categorizing findings into sections."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{
                "text": "Finding: enlarged heart\nCategory: Heart\n\nFinding: nodule in lung\nCategory: Lungs"
            }]
        }
        mock_post.return_value = mock_response
        
        from utils.claude_client import ClaudeClient
        client = ClaudeClient()
        
        findings = ["enlarged heart", "nodule in lung"]
        categories = ["Heart", "Lungs", "Mediastinum"]
        
        result = client.categorize_findings(findings, categories, "chest")
        
        assert "enlarged heart" in result
        assert result["enlarged heart"] == "Heart"
