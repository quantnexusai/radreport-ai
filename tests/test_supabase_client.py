import pytest
from unittest.mock import MagicMock, patch


class TestSupabaseClient:
    """Tests for the SupabaseClient class."""

    def test_init_missing_url(self, monkeypatch):
        """Test that initialization fails without SUPABASE_URL."""
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        
        with pytest.raises(ValueError, match="Supabase URL or key is missing"):
            from utils.supabase_client import SupabaseClient
            SupabaseClient()

    def test_init_missing_key(self, monkeypatch):
        """Test that initialization fails without SUPABASE_KEY."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.delenv("SUPABASE_KEY", raising=False)
        
        with pytest.raises(ValueError, match="Supabase URL or key is missing"):
            from utils.supabase_client import SupabaseClient
            SupabaseClient()

    @patch("utils.supabase_client.create_client")
    def test_get_facilities(self, mock_create, mock_env_vars, sample_facilities):
        """Test getting facilities from database."""
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = sample_facilities
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        
        from utils.supabase_client import SupabaseClient
        client = SupabaseClient()
        
        facilities = client.get_facilities()
        
        assert len(facilities) == 2
        assert facilities[0]["name"] == "Test Hospital"

    @patch("utils.supabase_client.create_client")
    def test_add_facility(self, mock_create, mock_env_vars):
        """Test adding a new facility."""
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [{"id": 1}]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        from utils.supabase_client import SupabaseClient
        client = SupabaseClient()
        
        result = client.add_facility(
            "New Hospital",
            "Chest template",
            "Abdomen template"
        )
        
        assert result is True

    @patch("utils.supabase_client.create_client")
    def test_get_impression_exact_match(self, mock_create, mock_env_vars):
        """Test getting impression with exact match."""
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [
            {
                "finding_pattern": "enlarged liver",
                "impression_text": "Hepatomegaly noted.",
                "section_name": "abdomen_pelvis"
            }
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        from utils.supabase_client import SupabaseClient
        client = SupabaseClient()
        
        impression = client.get_impression("enlarged liver", "abdomen_pelvis")
        
        assert impression == "Hepatomegaly noted."
