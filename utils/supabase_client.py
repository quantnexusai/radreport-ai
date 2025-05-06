import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.client = create_client(url, key)
    
    def get_facilities(self):
        """Get all facilities from the database"""
        response = self.client.table("facilities").select("*").execute()
        return response.data
    
    def get_report_template(self, section_name):
        """Get report template for a specific section"""
        response = self.client.table("report_templates") \
                     .select("*") \
                     .eq("section_name", section_name) \
                     .execute()
        return response.data[0] if response.data else None
    
    def get_impression(self, finding, section_name):
        """
        Match a finding to appropriate impression text using advanced pattern matching.
        
        This function implements a multi-stage matching approach:
        1. First tries exact pattern matches from the database
        2. Then tries partial matches, sorted by match quality
        3. Returns the best match or None if no matches found
        
        Args:
            finding (str): The finding text entered by the radiologist
            section_name (str): The section name (chest, abdomen_pelvis)
            
        Returns:
            str: The matched impression text, or None if no match found
        """
        # First get all patterns for this section
        response = self.client.table("impression_lookup") \
                    .select("*") \
                    .eq("section_name", section_name) \
                    .execute()
        
        if not response.data:
            return None
        
        # Try exact matches first
        finding_lower = finding.lower()
        for record in response.data:
            if record["finding_pattern"].lower() == finding_lower:
                return record["impression_text"]
        
        # No exact match, try partial matches with scoring
        matches = []
        for record in response.data:
            pattern = record["finding_pattern"].lower()
            if pattern in finding_lower:
                # Score based on pattern length and position in the finding
                score = len(pattern)
                # Bonus points if the pattern is at the beginning of the finding
                if finding_lower.startswith(pattern):
                    score += 5
                matches.append((score, record["impression_text"]))
        
        # Return the best match if any
        if matches:
            # Sort by score (highest first)
            matches.sort(reverse=True, key=lambda x: x[0])
            return matches[0][1]
        
        # Try partial word matching as a last resort
        words = finding_lower.split()
        for record in response.data:
            pattern_words = record["finding_pattern"].lower().split()
            common_words = set(words).intersection(set(pattern_words))
            if len(common_words) >= min(2, len(pattern_words)):
                matches.append((len(common_words), record["impression_text"]))
        
        if matches:
            matches.sort(reverse=True, key=lambda x: x[0])
            return matches[0][1]
        
        # No match found
        return None
    
    def log_unmatched_finding(self, finding, section_name):
        """
        Log findings that didn't match any pattern for future pattern additions
        
        Args:
            finding (str): The unmatched finding text
            section_name (str): The section name
        """
        try:
            self.client.table("unmatched_findings").insert({
                "finding": finding,
                "section_name": section_name
            }).execute()
        except Exception as e:
            print(f"Error logging unmatched finding: {e}")
    
    def add_impression_pattern(self, finding_pattern, section_name, impression_text):
        """
        Add a new impression pattern to the database
        
        Args:
            finding_pattern (str): The pattern to match against findings
            section_name (str): The section name (chest, abdomen_pelvis)
            impression_text (str): The impression text to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.table("impression_lookup").insert({
                "finding_pattern": finding_pattern,
                "section_name": section_name,
                "impression_text": impression_text
            }).execute()
            return True
        except Exception as e:
            print(f"Error adding impression pattern: {e}")
            return False
    
    def get_all_impression_patterns(self):
        """Get all impression patterns from the database"""
        response = self.client.table("impression_lookup").select("*").execute()
        return response.data
    
    def get_unmatched_findings(self, limit=100):
        """Get unmatched findings for review"""
        response = self.client.table("unmatched_findings") \
                    .select("*") \
                    .order("created_at", desc=True) \
                    .limit(limit) \
                    .execute()
        return response.data