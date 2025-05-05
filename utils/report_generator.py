from .supabase_client import SupabaseClient
from .claude_client import ClaudeClient

class ReportGenerator:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.claude = ClaudeClient()
    
    def generate_report(self, facility_name, study_type, sections_data, image_data=None):
        """Generate a complete radiology report"""
        facilities = self.supabase.get_facilities()
        
        # Find matching facility
        facility = next((f for f in facilities if f["name"] == facility_name), None)
        if not facility:
            return "Error: Facility not found"
        
        report_sections = []
        impressions = []
        
        # Process each section
        for section_name, findings in sections_data.items():
            # Get template for this section
            template = self.supabase.get_report_template(section_name)
            if not template:
                continue
            
            # Create section header
            if section_name == "chest":
                report_sections.append("CT CHEST WITHOUT CONTRAST:")
                technique = facility["technique_template_chest"]
            else:
                report_sections.append("CT ABDOMEN AND PELVIS WITHOUT CONTRAST")
                technique = facility["technique_template_abdomen"]
            
            # Add technique section
            report_sections.append("TECHNIQUE:")
            report_sections.append(technique)
            report_sections.append("")
            
            # Process findings
            report_sections.append("FINDINGS:")
            default_findings = template["default_findings"]
            
            if not findings:
                # Use default findings if none provided
                for category, text in default_findings.items():
                    report_sections.append(f"{category}: {text}")
            else:
                # Process each finding with Claude and update the template
                processed_findings = self.claude.process_findings(findings, section_name)
                finding_lines = processed_findings.strip().split('\n')
                
                # This is a simplified approach - in reality, you'd need more
                # sophisticated NLP to match findings to categories
                for finding in finding_lines:
                   for category in default_findings.keys():
                       if category.lower() in finding.lower():
                           default_findings[category] = finding
                           # Look up impression
                           impression = self.supabase.get_impression(finding, section_name)
                           if impression:
                               impressions.append(impression)
                           break
                
                # Output all categories with updated findings
                for category, text in default_findings.items():
                    report_sections.append(f"{category}: {text}")
            
            report_sections.append("")
        
        # Add impressions section
        if impressions:
            report_sections.append("IMPRESSION:")
            for i, impression in enumerate(impressions, 1):
                report_sections.append(f"{i}. {impression}")
        else:
            report_sections.append("IMPRESSION:")
            report_sections.append("Unremarkable exam.")
        
        # Analyze image if provided
        if image_data:
            image_analysis = self.claude.analyze_image(image_data, study_type)
            report_sections.append("")
            report_sections.append("IMAGE ANALYSIS NOTES:")
            report_sections.append(image_analysis)
        
        return "\n".join(report_sections)