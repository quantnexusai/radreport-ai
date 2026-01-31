import pytest
from unittest.mock import MagicMock, patch


class TestReportGenerator:
    """Tests for the ReportGenerator class."""

    @patch("utils.report_generator.SupabaseClient")
    @patch("utils.report_generator.ClaudeClient")
    def test_generate_report_basic(self, mock_claude, mock_supabase, sample_facilities, sample_report_template):
        """Test basic report generation."""
        # Set up mocks
        mock_supabase_instance = MagicMock()
        mock_supabase.return_value = mock_supabase_instance
        mock_supabase_instance.get_facilities.return_value = sample_facilities
        mock_supabase_instance.get_report_template.return_value = sample_report_template
        mock_supabase_instance.get_impression.return_value = "Normal cardiac silhouette."
        
        mock_claude_instance = MagicMock()
        mock_claude.return_value = mock_claude_instance
        mock_claude_instance.process_findings.return_value = "Heart: Normal size"
        mock_claude_instance.categorize_findings.return_value = {}
        
        from utils.report_generator import ReportGenerator
        generator = ReportGenerator()
        
        report = generator.generate_report(
            "Test Hospital",
            "Chest",
            {"chest": "heart normal size"}
        )
        
        assert "CT CHEST" in report
        assert "TECHNIQUE:" in report
        assert "FINDINGS:" in report
        assert "IMPRESSION:" in report

    @patch("utils.report_generator.SupabaseClient")
    @patch("utils.report_generator.ClaudeClient")
    def test_generate_report_facility_not_found(self, mock_claude, mock_supabase, sample_facilities):
        """Test report generation with non-existent facility."""
        mock_supabase_instance = MagicMock()
        mock_supabase.return_value = mock_supabase_instance
        mock_supabase_instance.get_facilities.return_value = sample_facilities
        
        mock_claude_instance = MagicMock()
        mock_claude.return_value = mock_claude_instance
        
        from utils.report_generator import ReportGenerator
        generator = ReportGenerator()
        
        report = generator.generate_report(
            "Non-existent Hospital",
            "Chest",
            {"chest": "test findings"}
        )
        
        assert "Error: Facility not found" in report

    @patch("utils.report_generator.SupabaseClient")
    @patch("utils.report_generator.ClaudeClient")
    def test_generate_report_empty_findings(self, mock_claude, mock_supabase, sample_facilities):
        """Test report generation with empty findings."""
        mock_supabase_instance = MagicMock()
        mock_supabase.return_value = mock_supabase_instance
        mock_supabase_instance.get_facilities.return_value = sample_facilities
        
        mock_claude_instance = MagicMock()
        mock_claude.return_value = mock_claude_instance
        
        from utils.report_generator import ReportGenerator
        generator = ReportGenerator()
        
        report = generator.generate_report(
            "Test Hospital",
            "Chest",
            {"chest": ""}
        )
        
        assert "Unremarkable exam" in report

    @patch("utils.report_generator.SupabaseClient")
    @patch("utils.report_generator.ClaudeClient")
    def test_generate_report_with_image(self, mock_claude, mock_supabase, sample_facilities, sample_report_template):
        """Test report generation with image analysis."""
        mock_supabase_instance = MagicMock()
        mock_supabase.return_value = mock_supabase_instance
        mock_supabase_instance.get_facilities.return_value = sample_facilities
        mock_supabase_instance.get_report_template.return_value = sample_report_template
        mock_supabase_instance.get_impression.return_value = None
        
        mock_claude_instance = MagicMock()
        mock_claude.return_value = mock_claude_instance
        mock_claude_instance.process_findings.return_value = "Heart: Normal"
        mock_claude_instance.categorize_findings.return_value = {}
        mock_claude_instance.generate_impression.return_value = "Normal study."
        mock_claude_instance.analyze_image.return_value = "Small nodule identified in right lower lobe."
        
        from utils.report_generator import ReportGenerator
        generator = ReportGenerator()
        
        report = generator.generate_report(
            "Test Hospital",
            "Chest",
            {"chest": "heart normal"},
            image_data="base64encodedimage"
        )
        
        assert "IMAGE ANALYSIS NOTES:" in report
        assert "nodule" in report.lower()
