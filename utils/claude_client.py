import os
import requests
import json
import base64
import time
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class ClaudeClient:
    def __init__(self):
        self.api_key = os.environ.get("CLAUDE_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-7-sonnet-20250219"
        logger.info(f"Initialized Claude client with model: {self.model}")
        
    def _make_api_request(self, payload):
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Set a longer timeout for image requests
        timeout = 60  # 60 seconds
        
        # Add better error handling and retry logic
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
                else:
                    error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    
                    # If rate limited, wait and retry
                    if response.status_code == 429:
                        retry_count += 1
                        wait_time = min(2 ** retry_count, 60)  # Exponential backoff
                        logger.info(f"Rate limited. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    
                    # For other errors, raise immediately
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
        
    def process_findings(self, findings, section):
        """Process findings text with Claude to correct grammar and format"""
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
    
    def analyze_image(self, image_data, study_type):
        """Process radiology image with Claude vision capabilities"""
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
                # If it's just base64 without the data URL prefix, add it
                image_type = "image/jpeg"  # Assuming JPEG, adjust if needed
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
            
            # Add detailed logging for debugging
            logger.info(f"Sending image analysis request for {study_type} study")
            
            response = self._make_api_request(payload)
            
            logger.info("Image analysis request succeeded")
            return response["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            
            # More specific error handling - actually analyze what went wrong
            if "413" in str(e) or "too large" in str(e).lower():
                return "The image was too large to process. Please use a smaller image (under 10MB)."
            elif "unsupported" in str(e).lower() or "media_type" in str(e).lower():
                return "The image format is not supported. Please use JPEG or PNG format."
            elif "api key" in str(e).lower() or "authentication" in str(e).lower():
                return "Unable to analyze image due to API authentication issues. Please check your API key."
            else:
                # Try a fallback approach with just the text prompt
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
                    return f"Note: Image analysis was not possible due to technical limitations. Here is general information about {study_type} CT scans:\n\n" + fallback_response["content"][0]["text"]
                except:
                    return f"Image analysis could not be completed. Error details: {str(e)[:100]}..."
    
    def generate_impression(self, finding, section_name):
        """Generate an appropriate impression for a finding using Claude"""
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
    
    def categorize_findings(self, findings, categories, section_name):
        """Use Claude to categorize findings into appropriate categories"""
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
            
            # Parse Claude's response to extract finding-to-category mappings
            result = {}
            current_finding = None
            
            for line in response["content"][0]["text"].strip().split('\n'):
                line = line.strip()
                if line.startswith('Finding:'):
                    current_finding = line[len('Finding:'):].strip()
                elif line.startswith('Category:') and current_finding:
                    category = line[len('Category:'):].strip()
                    if category in categories:  # Ensure category is in the allowed list
                        result[current_finding] = category
                    current_finding = None
            
            return result
        except Exception as e:
            logger.error(f"Error categorizing findings: {e}")
            raise