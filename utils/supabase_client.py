"""Supabase client for database operations.

This module provides a client for interacting with the Supabase database,
including CRUD operations for facilities, impression patterns, and findings.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class SupabaseClient:
    """Client for interacting with the Supabase database.

    This class provides methods for managing facilities, report templates,
    impression patterns, and unmatched findings in the database.

    Attributes:
        client: The underlying Supabase client instance.

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
        Exception: If connection to Supabase fails.
    """

    def __init__(self) -> None:
        """Initialize the Supabase client.

        Raises:
            ValueError: If required environment variables are missing.
            Exception: If connection test fails.
        """
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            logger.error("Supabase URL or key is missing in environment variables")
            raise ValueError("Supabase URL or key is missing")

        try:
            self.client: Client = create_client(url, key)
            # Test connection by fetching a simple query
            self.client.table("facilities").select("count", count="exact").execute()
            logger.info("Successfully connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def get_facilities(self) -> list[dict[str, Any]]:
        """Retrieve all facilities from the database.

        Returns:
            A list of facility dictionaries containing id, name, and template fields.

        Raises:
            Exception: If the database query fails.
        """
        try:
            response = self.client.table("facilities").select("*").execute()
            logger.info(f"Retrieved {len(response.data)} facilities")
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving facilities: {e}")
            raise

    def add_facility(
        self,
        name: str,
        technique_template_chest: str,
        technique_template_abdomen: str
    ) -> bool:
        """Add a new facility to the database.

        Args:
            name: The name of the facility.
            technique_template_chest: The chest technique template text.
            technique_template_abdomen: The abdomen technique template text.

        Returns:
            True if the facility was added successfully, False otherwise.
        """
        try:
            response = self.client.table("facilities").insert({
                "name": name,
                "technique_template_chest": technique_template_chest,
                "technique_template_abdomen": technique_template_abdomen
            }).execute()
            logger.info(f"Added new facility: {name}")
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error adding facility: {e}")
            return False

    def delete_facility(self, facility_id: int) -> bool:
        """Delete a facility from the database.

        Args:
            facility_id: The unique identifier of the facility to delete.

        Returns:
            True if the facility was deleted successfully, False otherwise.
        """
        try:
            response = self.client.table("facilities").delete().eq("id", facility_id).execute()
            logger.info(f"Deleted facility with ID: {facility_id}")
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error deleting facility: {e}")
            return False

    def update_facility_templates(
        self,
        facility_id: int,
        technique_template_chest: str,
        technique_template_abdomen: str
    ) -> bool:
        """Update a facility's technique templates.

        Args:
            facility_id: The unique identifier of the facility.
            technique_template_chest: The new chest technique template text.
            technique_template_abdomen: The new abdomen technique template text.

        Returns:
            True if the templates were updated successfully, False otherwise.
        """
        try:
            response = self.client.table("facilities").update({
                "technique_template_chest": technique_template_chest,
                "technique_template_abdomen": technique_template_abdomen,
                "updated_at": "now()"
            }).eq("id", facility_id).execute()
            logger.info(f"Updated templates for facility with ID: {facility_id}")
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error updating facility templates: {e}")
            return False

    def get_report_template(self, section_name: str) -> Optional[dict[str, Any]]:
        """Retrieve a report template for a specific section.

        Args:
            section_name: The name of the section (e.g., "chest", "abdomen_pelvis").

        Returns:
            A dictionary containing the template data, or None if not found.

        Raises:
            Exception: If the database query fails.
        """
        try:
            response = self.client.table("report_templates") \
                .select("*") \
                .eq("section_name", section_name) \
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting report template: {e}")
            raise

    def get_impression(self, finding: str, section_name: str) -> Optional[str]:
        """Match a finding to an appropriate impression using pattern matching.

        This method attempts to find a matching impression for a given finding
        using the following strategy:
        1. Exact match on finding pattern
        2. Partial match with scoring based on pattern length
        3. Word-based matching as a fallback

        Args:
            finding: The finding text to match.
            section_name: The section name to filter patterns by.

        Returns:
            The matched impression text, or None if no match is found.
        """
        try:
            response = self.client.table("impression_lookup") \
                .select("*") \
                .eq("section_name", section_name) \
                .execute()

            if not response.data:
                return None

            finding_lower = finding.lower()

            # Try exact matches first
            for record in response.data:
                if record["finding_pattern"].lower() == finding_lower:
                    return record["impression_text"]

            # Try partial matches with scoring
            matches: list[tuple[int, str]] = []
            for record in response.data:
                pattern = record["finding_pattern"].lower()
                if pattern in finding_lower:
                    score = len(pattern)
                    if finding_lower.startswith(pattern):
                        score += 5
                    matches.append((score, record["impression_text"]))

            if matches:
                matches.sort(reverse=True, key=lambda x: x[0])
                return matches[0][1]

            # Try partial word matching as fallback
            words = finding_lower.split()
            for record in response.data:
                pattern_words = record["finding_pattern"].lower().split()
                common_words = set(words).intersection(set(pattern_words))
                if len(common_words) >= min(2, len(pattern_words)):
                    matches.append((len(common_words), record["impression_text"]))

            if matches:
                matches.sort(reverse=True, key=lambda x: x[0])
                return matches[0][1]

            return None
        except Exception as e:
            logger.error(f"Error matching impression: {e}")
            return None

    def log_unmatched_finding(self, finding: str, section_name: str) -> bool:
        """Log a finding that didn't match any pattern for future review.

        Args:
            finding: The unmatched finding text.
            section_name: The section where the finding was entered.

        Returns:
            True if the finding was logged successfully, False otherwise.
        """
        try:
            response = self.client.table("unmatched_findings").insert({
                "finding": finding,
                "section_name": section_name
            }).execute()
            logger.info(f"Logged unmatched finding in section {section_name}")
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error logging unmatched finding: {e}")
            return False

    def delete_unmatched_finding(self, finding_id: int) -> bool:
        """Delete an unmatched finding from the database.

        Args:
            finding_id: The unique identifier of the finding to delete.

        Returns:
            True if the finding was deleted successfully, False otherwise.
        """
        try:
            response = self.client.table("unmatched_findings").delete().eq("id", finding_id).execute()
            logger.info(f"Deleted unmatched finding with ID: {finding_id}")
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error deleting unmatched finding: {e}")
            return False

    def add_impression_pattern(
        self,
        finding_pattern: str,
        section_name: str,
        impression_text: str
    ) -> bool:
        """Add a new impression pattern to the database.

        Args:
            finding_pattern: The pattern to match against findings.
            section_name: The section this pattern applies to.
            impression_text: The impression text to generate when matched.

        Returns:
            True if the pattern was added successfully, False otherwise.
        """
        try:
            response = self.client.table("impression_lookup").insert({
                "finding_pattern": finding_pattern,
                "section_name": section_name,
                "impression_text": impression_text
            }).execute()
            logger.info(f"Added new impression pattern: {finding_pattern}")
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error adding impression pattern: {e}")
            return False

    def delete_impression_pattern(self, pattern_id: int) -> bool:
        """Delete an impression pattern from the database.

        Args:
            pattern_id: The unique identifier of the pattern to delete.

        Returns:
            True if the pattern was deleted successfully, False otherwise.
        """
        try:
            response = self.client.table("impression_lookup").delete().eq("id", pattern_id).execute()
            logger.info(f"Deleted impression pattern with ID: {pattern_id}")
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error deleting impression pattern: {e}")
            return False

    def get_all_impression_patterns(self) -> list[dict[str, Any]]:
        """Retrieve all impression patterns from the database.

        Returns:
            A list of impression pattern dictionaries.

        Raises:
            Exception: If the database query fails.
        """
        try:
            response = self.client.table("impression_lookup").select("*").execute()
            logger.info(f"Retrieved {len(response.data)} impression patterns")
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving impression patterns: {e}")
            raise

    def get_unmatched_findings(self, limit: int = 100) -> list[dict[str, Any]]:
        """Retrieve unmatched findings for review.

        Args:
            limit: Maximum number of findings to retrieve (default: 100).

        Returns:
            A list of unmatched finding dictionaries, ordered by creation date.

        Raises:
            Exception: If the database query fails.
        """
        try:
            response = self.client.table("unmatched_findings") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            logger.info(f"Retrieved {len(response.data)} unmatched findings")
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving unmatched findings: {e}")
            raise
