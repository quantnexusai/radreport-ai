"""Claude API client for AI-powered text processing.

This module provides a client for interacting with the Claude API,
including finding processing, image analysis, and impression generation.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Optional

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class ClaudeClient:
    """Client for interacting with the Claude API.

    This class provides methods for processing radiology findings,
    analyzing images, and generating impressions using Claude.

    Attributes:
        api_key: The Anthropic API key.
        base_url: The base URL for the Claude API.
        model: The Claude model to use for requests.
    """

    def __init__(self) -> None:
        """Initialize the Claude client.

        The API key is read from the CLAUDE_API_KEY environment variable.
        """
        self.api_key: Optional[str] = os.environ.get("CLAUDE_API_KEY")
        self.base_url: str = "https://api.anthropic.com/v1/messages"
        self.model: str = "claude-3-7-sonnet-20250219"
        logger.info(f"Initialized Claude client with model: {self.model}")

    def _make_api_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Make an API request to Claude with retry logic.

        Args:
            payload: The request payload to send to the API.

        Returns:
            The JSON response from the API.

        Raises:
            Exception: If the request fails after all retries.
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        timeout = 60
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )

                if response.status_code == 200:
                    return response.json()

                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                logger.error(error_msg)

                if response.status_code == 429:
                    retry_count += 1
                    wait_time = min(2 ** retry_count, 60)
                    logger.info(f"Rate limited. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                raise Exception(error_msg)
            except requests.exceptions.Timeout:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"Request timed out. Retrying ({retry_count}/{max_retries})...")
                    time.sleep(2)
                else:
                    raise Exception("Request timed out after multiple retries")
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"Error during request: {str(e)}. Retrying ({retry_count}/{max_retries})...")
                    time.sleep(2)
                else:
                    raise

        raise Exception("Failed to get a successful response after multiple retries")

    def process_findings(self, findings: str, section: str) -> str:
        """Process findings text to correct grammar and format.

        Args:
            findings: The raw findings text to process.
            section: The section name (e.g., "chest", "abdomen_pelvis").

        Returns:
            The formatted findings text with proper grammar.

        Raises:
            Exception: If the API request fails.
        """
        try:
            prompt = f"""
            Please convert these radiology findings into properly formatted, grammatically
            correct complete sentences for a {section} CT report:

            {findings}

            Return only the formatted findings with no additional commentary. Each finding should
            be on its own line. Maintain all medical details exactly as provided.
            """

            payload = {
                "model": self.model,
                "max_tokens": 1000,
                "temperature": 0,
                "system": "You are a radiology report assistant that helps format findings into proper medical terminology and grammar. You never change measurements or clinical observations.",
                "messages": [{"role": "user", "content": prompt}]
            }

            response = self._make_api_request(payload)
            return response["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error processing findings: {e}")
            raise

    def analyze_image(self, image_data: str, study_type: str) -> str:
        """Analyze a radiology image using Claude's vision capabilities.

        Args:
            image_data: Base64-encoded image data.
            study_type: The type of study (e.g., "Full Body", "Chest").

        Returns:
            The image analysis text describing any findings.
        """
        try:
            prompt = f"""
            Please analyze this {study_type} CT scan image and provide any notable observations
            that might complement the radiologist's findings. Focus only on obvious abnormalities
            visible in this single image. Be conservative and specific in your assessment.

            If you identify any clear abnormalities, describe them in detail including:
            1. Location (which anatomical structure/region)
            2. Size (if measurable)
            3. Characteristics (density, shape, borders)
            4. Significance (normal variant, potentially concerning, etc.)

            If no significant abnormalities are evident, state that clearly.
            """

            # Ensure image_data is properly encoded
            if not image_data.startswith("data:image"):
                image_type = "image/jpeg"
                image_data = f"data:{image_type};base64,{image_data}"

            payload = {
                "model": self.model,
                "max_tokens": 1000,
                "temperature": 0,
                "system": "You are a radiology AI assistant that helps identify potential findings in medical images. You are conservative in your assessments and careful not to overinterpret single images.",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

            logger.info(f"Sending image analysis request for {study_type} study")
            response = self._make_api_request(payload)
            logger.info("Image analysis request succeeded")
            return response["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return self._handle_image_analysis_error(e, study_type)

    def _handle_image_analysis_error(self, error: Exception, study_type: str) -> str:
        """Handle errors during image analysis with appropriate fallback.

        Args:
            error: The exception that occurred.
            study_type: The type of study being analyzed.

        Returns:
            An appropriate error message or fallback response.
        """
        error_str = str(error).lower()

        if "413" in str(error) or "too large" in error_str:
            return "The image was too large to process. Please use a smaller image (under 10MB)."
        elif "unsupported" in error_str or "media_type" in error_str:
            return "The image format is not supported. Please use JPEG or PNG format."
        elif "api key" in error_str or "authentication" in error_str:
            return "Unable to analyze image due to API authentication issues. Please check your API key."

        # Try fallback approach
        try:
            logger.info("Attempting fallback image analysis without image data")
            text_only_payload = {
                "model": self.model,
                "max_tokens": 1000,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": f"I'm reviewing a {study_type} CT scan. Without seeing the image, what are the most common findings or abnormalities that might be observed in this type of scan? Please focus on general patterns rather than specific diagnoses."
                    }
                ]
            }

            fallback_response = self._make_api_request(text_only_payload)
            return (
                f"Note: Image analysis was not possible due to technical limitations. "
                f"Here is general information about {study_type} CT scans:\n\n"
                + fallback_response["content"][0]["text"]
            )
        except Exception:
            return f"Image analysis could not be completed. Error details: {str(error)[:100]}..."

    def generate_impression(self, finding: str, section_name: str) -> str:
        """Generate an appropriate impression for a finding.

        Args:
            finding: The finding text to generate an impression for.
            section_name: The section name (e.g., "chest", "abdomen_pelvis").

        Returns:
            The generated impression text.

        Raises:
            Exception: If the API request fails.
        """
        try:
            prompt = f"""
            Generate an appropriate impression for the following radiology finding in the {section_name} section:

            Finding: {finding}

            The impression should:
            1. Be concise (typically 1-2 sentences)
            2. Use standard radiological terminology
            3. Include relevant clinical implications if appropriate
            4. Suggest follow-up if needed based on standard guidelines

            Return only the impression text with no additional commentary.
            """

            payload = {
                "model": self.model,
                "max_tokens": 150,
                "temperature": 0,
                "system": "You are a radiology report assistant that generates appropriate impression text for findings. You follow standard radiological guidelines for follow-up recommendations.",
                "messages": [{"role": "user", "content": prompt}]
            }

            response = self._make_api_request(payload)
            return response["content"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Error generating impression: {e}")
            raise

    def categorize_findings(
        self,
        findings: list[str],
        categories: list[str],
        section_name: str
    ) -> dict[str, str]:
        """Categorize findings into appropriate categories using Claude.

        Args:
            findings: List of finding texts to categorize.
            categories: List of available category names.
            section_name: The section name for context.

        Returns:
            A dictionary mapping finding text to category name.

        Raises:
            Exception: If the API request fails.
        """
        try:
            categories_str = "\n".join(categories)
            findings_str = "\n".join([f"- {finding}" for finding in findings])

            prompt = f"""
            Categorize each of the following radiology findings into the most appropriate category
            from the list below. Each finding should be assigned to exactly one category.

            Section: {section_name}

            Available categories:
            {categories_str}

            Findings to categorize:
            {findings_str}

            For each finding, return only the finding text and the selected category in this exact format:
            Finding: [exact finding text]
            Category: [exact category name from the list]

            Provide this for each finding, with one blank line between entries.
            """

            payload = {
                "model": self.model,
                "max_tokens": 500,
                "temperature": 0,
                "system": "You are a radiology report assistant that categorizes findings into appropriate sections. You match each finding to exactly one category from the provided list, using the exact category names given.",
                "messages": [{"role": "user", "content": prompt}]
            }

            response = self._make_api_request(payload)
            return self._parse_categorization_response(response, categories)
        except Exception as e:
            logger.error(f"Error categorizing findings: {e}")
            raise

    def _parse_categorization_response(
        self,
        response: dict[str, Any],
        categories: list[str]
    ) -> dict[str, str]:
        """Parse the categorization response from Claude.

        Args:
            response: The API response dictionary.
            categories: List of valid category names.

        Returns:
            A dictionary mapping finding text to category name.
        """
        result: dict[str, str] = {}
        current_finding: Optional[str] = None

        for line in response["content"][0]["text"].strip().split('\n'):
            line = line.strip()
            if line.startswith('Finding:'):
                current_finding = line[len('Finding:'):].strip()
            elif line.startswith('Category:') and current_finding:
                category = line[len('Category:'):].strip()
                if category in categories:
                    result[current_finding] = category
                current_finding = None

        return result
