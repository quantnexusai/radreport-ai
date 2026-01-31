import pytest
import os
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("SUPABASE_URL", "https://test-project.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("CLAUDE_API_KEY", "test-claude-key")
    monkeypatch.setenv("ADMIN_PASSWORD", "test-admin-password")


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    with patch("utils.supabase_client.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_facilities():
    """Sample facility data for testing."""
    return [
        {
            "id": 1,
            "name": "Test Hospital",
            "technique_template_chest": "CT chest without contrast technique.",
            "technique_template_abdomen": "CT abdomen without contrast technique."
        },
        {
            "id": 2,
            "name": "Medical Center",
            "technique_template_chest": "Chest CT technique template.",
            "technique_template_abdomen": "Abdomen CT technique template."
        }
    ]


@pytest.fixture
def sample_report_template():
    """Sample report template for testing."""
    return {
        "section_name": "chest",
        "default_findings": {
            "Heart": "Normal size",
            "Lungs": "Clear",
            "Mediastinum": "Unremarkable"
        }
    }
