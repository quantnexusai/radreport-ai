import os
import anthropic
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class ClaudeClient:
    def __init__(self):
        self.api_key = os.environ.get("CLAUDE_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-7-sonnet-20250219"  # Using your specified model
        logger.info(f"Initialized Claude client with model: {self.model}")
        
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
            
            # Use the Messages API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system="You are a radiology report assistant that helps format findings into proper medical terminology and grammar. You never change measurements or clinical observations.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
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
            
            # Use the Messages API with image content
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system="You are a radiology AI assistant that helps identify potential findings in medical images. You are conservative in your assessments and careful not to overinterpret single images.",
                messages=[
                    {"role": "user", "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                        {"type": "text", "text": prompt}
                    ]}
                ]
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise
    
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
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                temperature=0,
                system="You are a radiology report assistant that generates appropriate impression text for findings. You follow standard radiological guidelines for follow-up recommendations.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
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
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0,
                system="You are a radiology report assistant that categorizes findings into appropriate sections. You match each finding to exactly one category from the provided list, using the exact category names given.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse Claude's response to extract finding-to-category mappings
            result = {}
            current_finding = None
            
            for line in response.content[0].text.strip().split('\n'):
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