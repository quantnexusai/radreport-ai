import os
from supabase import create_client
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            logger.error("Supabase URL or key is missing in environment variables")
            raise ValueError("Supabase URL or key is missing")
            
        try:
            self.client = create_client(url, key)
            # Test connection by fetching a simple query
            self.client.table("facilities").select("count", count="exact").execute()
            logger.info("Successfully connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def get_facilities(self):
        """Get all facilities from the database"""
        try:
            response = self.client.table("facilities").select("*").execute()
            logger.info(f"Retrieved {len(response.data)} facilities")
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving facilities: {e}")
            raise
    
    def add_facility(self, name, technique_template_chest, technique_template_abdomen):
        """Add a new facility to the database"""
        try:
            response = self.client.table("facilities").insert({
                "name": name,
                "technique_template_chest": technique_template_chest,
                "technique_template_abdomen": technique_template_abdomen
            }).execute()
            logger.info(f"Added new facility: {name}")
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error adding facility: {e}")
            return False
    
    def delete_facility(self, facility_id):
        """Delete a facility from the database"""
        try:
            response = self.client.table("facilities").delete().eq("id", facility_id).execute()
            logger.info(f"Deleted facility with ID: {facility_id}")
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error deleting facility: {e}")
            return False
    
    def update_facility_templates(self, facility_id, technique_template_chest, technique_template_abdomen):
        """Update a facility's templates"""
        try:
            response = self.client.table("facilities").update({
                "technique_template_chest": technique_template_chest,
                "technique_template_abdomen": technique_template_abdomen,
                "updated_at": "now()"
            }).eq("id", facility_id).execute()
            logger.info(f"Updated templates for facility with ID: {facility_id}")
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error updating facility templates: {e}")
            return False
    
    def get_report_template(self, section_name):
        """Get report template for a specific section"""
        try:
            response = self.client.table("report_templates") \
                         .select("*") \
                         .eq("section_name", section_name) \
                         .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting report template: {e}")
            raise
    
    def get_impression(self, finding, section_name):
        """Match a finding to appropriate impression text using pattern matching."""
        try:
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
        except Exception as e:
            logger.error(f"Error matching impression: {e}")
            return None
    
    def log_unmatched_finding(self, finding, section_name):
        """Log findings that didn't match any pattern for future pattern additions"""
        try:
            response = self.client.table("unmatched_findings").insert({
                "finding": finding,
                "section_name": section_name
            }).execute()
            logger.info(f"Logged unmatched finding in section {section_name}")
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error logging unmatched finding: {e}")
            return False
    
    def delete_unmatched_finding(self, finding_id):
        """Delete an unmatched finding from the database"""
        try:
            response = self.client.table("unmatched_findings").delete().eq("id", finding_id).execute()
            logger.info(f"Deleted unmatched finding with ID: {finding_id}")
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error deleting unmatched finding: {e}")
            return False
    
    def add_impression_pattern(self, finding_pattern, section_name, impression_text):
        """Add a new impression pattern to the database"""
        try:
            response = self.client.table("impression_lookup").insert({
                "finding_pattern": finding_pattern,
                "section_name": section_name,
                "impression_text": impression_text
            }).execute()
            logger.info(f"Added new impression pattern: {finding_pattern}")
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error adding impression pattern: {e}")
            return False
    
    def delete_impression_pattern(self, pattern_id):
        """Delete an impression pattern from the database"""
        try:
            response = self.client.table("impression_lookup").delete().eq("id", pattern_id).execute()
            logger.info(f"Deleted impression pattern with ID: {pattern_id}")
            return True if response.data else False
        except Exception as e:
            logger.error(f"Error deleting impression pattern: {e}")
            return False
    
    def get_all_impression_patterns(self):
        """Get all impression patterns from the database"""
        try:
            response = self.client.table("impression_lookup").select("*").execute()
            logger.info(f"Retrieved {len(response.data)} impression patterns")
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving impression patterns: {e}")
            raise
    
    def get_unmatched_findings(self, limit=100):
        """Get unmatched findings for review"""
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