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
        response = self.client.table("facilities").select("*").execute()
        return response.data
    
    def get_report_template(self, section_name):
        response = self.client.table("report_templates") \
                     .select("*") \
                     .eq("section_name", section_name) \
                     .execute()
        return response.data[0] if response.data else None
    
    def get_impression(self, finding_pattern, section_name):
        # This is a simplified version. In reality, you might need
        # more complex pattern matching logic
        response = self.client.table("impression_lookup") \
                     .select("*") \
                     .eq("section_name", section_name) \
                     .ilike("finding_pattern", f"%{finding_pattern}%") \
                     .execute()
        return response.data[0]["impression_text"] if response.data else None