"""Report generator for radiology reports.

This module provides the main report generation logic, combining
findings processing, impression matching, and image analysis.
"""

from __future__ import annotations

from typing import Any, Optional

from .supabase_client import SupabaseClient
from .claude_client import ClaudeClient


class ReportGenerator:
    """Generator for structured radiology reports.

    This class orchestrates the generation of complete radiology reports
    by combining user-provided findings with database templates and
    AI-powered processing.

    Attributes:
        supabase: The Supabase client for database operations.
        claude: The Claude client for AI-powered processing.
        use_claude_for_unmatched: Whether to use Claude for generating
            impressions when no database match is found.
    """

    def __init__(self) -> None:
        """Initialize the report generator with database and AI clients."""
        self.supabase = SupabaseClient()
        self.claude = ClaudeClient()
        self.use_claude_for_unmatched: bool = True

    def generate_report(
        self,
        facility_name: str,
        study_type: str,
        sections_data: dict[str, str],
        image_data: Optional[str] = None
    ) -> str:
        """Generate a complete radiology report.

        This method creates a structured radiology report with findings
        and impressions based on the provided inputs.

        Args:
            facility_name: Name of the imaging facility.
            study_type: Type of study (e.g., "Full Body", "Chest", "Abdomen and Pelvis").
            sections_data: Dictionary mapping section names to findings text.
            image_data: Optional base64-encoded image data for analysis.

        Returns:
            The complete formatted radiology report as a string.
        """
        facilities = self.supabase.get_facilities()

        facility = next((f for f in facilities if f["name"] == facility_name), None)
        if not facility:
            return "Error: Facility not found"

        report_sections: list[str] = []
        impressions: list[str] = []
        matched_findings: list[str] = []

        for section_name, findings in sections_data.items():
            if not findings or findings.strip() == "":
                continue

            template = self.supabase.get_report_template(section_name)
            if not template:
                continue

            section_content = self._process_section(
                section_name,
                findings,
                facility,
                template,
                impressions,
                matched_findings
            )
            report_sections.extend(section_content)

        report_sections.extend(self._generate_impressions_section(impressions))

        if image_data:
            image_analysis = self._analyze_image(image_data, study_type)
            if image_analysis:
                report_sections.extend(image_analysis)

        return "\n".join(report_sections)

    def _process_section(
        self,
        section_name: str,
        findings: str,
        facility: dict[str, Any],
        template: dict[str, Any],
        impressions: list[str],
        matched_findings: list[str]
    ) -> list[str]:
        """Process a single report section.

        Args:
            section_name: The name of the section being processed.
            findings: The raw findings text for this section.
            facility: The facility dictionary with template information.
            template: The report template for this section.
            impressions: List to append generated impressions to.
            matched_findings: List to append matched findings to.

        Returns:
            A list of formatted section lines.
        """
        section_content: list[str] = []

        if section_name == "chest":
            section_content.append("CT CHEST WITHOUT CONTRAST:")
            technique = facility["technique_template_chest"]
        else:
            section_content.append("CT ABDOMEN AND PELVIS WITHOUT CONTRAST")
            technique = facility["technique_template_abdomen"]

        section_content.append("TECHNIQUE:")
        section_content.append(technique)
        section_content.append("")
        section_content.append("FINDINGS:")

        default_findings: dict[str, str] = template["default_findings"]
        modified_findings = dict(default_findings)

        processed_findings = self.claude.process_findings(findings, section_name)
        finding_lines = processed_findings.strip().split('\n')

        processed_finding_indexes: set[int] = set()

        # First pass: categorize findings by direct category match
        for idx, finding in enumerate(finding_lines):
            for category in default_findings.keys():
                if category.lower() in finding.lower():
                    modified_findings[category] = finding
                    processed_finding_indexes.add(idx)
                    self._process_finding_impression(
                        finding,
                        section_name,
                        impressions,
                        matched_findings
                    )
                    break

        # Second pass: use Claude to categorize remaining findings
        if len(processed_finding_indexes) < len(finding_lines):
            uncategorized_findings = [
                f for idx, f in enumerate(finding_lines)
                if idx not in processed_finding_indexes
            ]

            categories = self.claude.categorize_findings(
                uncategorized_findings,
                list(default_findings.keys()),
                section_name
            )

            for finding, suggested_category in categories.items():
                if suggested_category in modified_findings:
                    modified_findings[suggested_category] = finding
                    self._process_finding_impression(
                        finding,
                        section_name,
                        impressions,
                        matched_findings
                    )

        for category, text in modified_findings.items():
            section_content.append(f"{category}: {text}")

        section_content.append("")
        return section_content

    def _process_finding_impression(
        self,
        finding: str,
        section_name: str,
        impressions: list[str],
        matched_findings: list[str]
    ) -> None:
        """Process a finding to generate its impression.

        This method looks up the impression in the database first,
        then falls back to Claude if enabled and no match is found.

        Args:
            finding: The finding text to process.
            section_name: The section name for context.
            impressions: List to append generated impressions to.
            matched_findings: List to append matched findings to.
        """
        impression = self.supabase.get_impression(finding, section_name)

        if impression:
            impressions.append(impression)
            matched_findings.append(finding)
        else:
            self.supabase.log_unmatched_finding(finding, section_name)

            if self.use_claude_for_unmatched:
                claude_impression = self.claude.generate_impression(finding, section_name)
                if claude_impression:
                    impressions.append(claude_impression)
                    matched_findings.append(finding)

    def _generate_impressions_section(self, impressions: list[str]) -> list[str]:
        """Generate the impressions section of the report.

        Args:
            impressions: List of impression texts.

        Returns:
            A list of formatted impression lines.
        """
        section: list[str] = ["IMPRESSION:"]

        if impressions:
            for i, impression in enumerate(impressions, 1):
                section.append(f"{i}. {impression}")
        else:
            section.append("Unremarkable exam.")

        return section

    def _analyze_image(
        self,
        image_data: str,
        study_type: str
    ) -> Optional[list[str]]:
        """Analyze an image and return the findings section.

        Args:
            image_data: Base64-encoded image data.
            study_type: The type of study for context.

        Returns:
            A list of image analysis lines, or None if no significant findings.
        """
        image_findings = self.claude.analyze_image(image_data, study_type)

        if image_findings and not image_findings.lower().startswith("no significant"):
            return ["", "IMAGE ANALYSIS NOTES:", image_findings]

        return None
