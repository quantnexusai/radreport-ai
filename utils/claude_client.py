import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
    
    def process_findings(self, findings, section):
        """Process findings text with Claude to correct grammar and format"""
        prompt = f"""
        Please convert these radiology findings into properly formatted, grammatically 
        correct complete sentences for a {section} CT report:
        
        {findings}
        
        Return only the formatted findings with no additional commentary.
        """
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a radiology report assistant that helps format findings into proper medical terminology and grammar.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def analyze_image(self, image_data, study_type):
        """Process radiology image with Claude vision capabilities"""
        prompt = f"""
        Please analyze this {study_type} CT scan image and provide any notable observations 
        that might complement the radiologist's findings. Focus only on obvious abnormalities
        visible in this single image. Be conservative and specific in your assessment.
        """
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a radiology AI assistant that helps identify potential findings in medical images.",
            messages=[
                {"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                    {"type": "text", "text": prompt}
                ]}
            ]
        )
        
        return response.content[0].text