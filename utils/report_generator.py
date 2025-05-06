from .supabase_client import SupabaseClient
from .claude_client import ClaudeClient

class ReportGenerator:
    def __init__(self):
        self.supabase = SupabaseClient()
        self.claude = ClaudeClient()
        self.use_claude_for_unmatched = True  # Set to True to use Claude for unmatched findings
    
    def generate_report(self, facility_name, study_type, sections_data, image_data=None):
        """
        Generate a complete radiology report with findings and impressions
        
        Args:
            facility_name (str): Name of the imaging facility
            study_type (str): Type of study (Full Body, Chest, or Abdomen and Pelvis)
            sections_data (dict): Dictionary of section names to findings text
            image_data (str, optional): Base64-encoded image data
            
        Returns:
            str: The complete formatted radiology report
        """
        facilities = self.supabase.get_facilities()
        
        # Find matching facility
        facility = next((f for f in facilities if f["name"] == facility_name), None)
        if not facility:
            return "Error: Facility not found"
        
        report_sections = []
        impressions = []
        matched_findings = []  # Track findings that generated impressions
        
        # Process each section
        for section_name, findings in sections_data.items():
            if not findings or findings.strip() == "":
                continue
                
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
            
            # Clone default findings to keep originals intact
            modified_findings = dict(default_findings)
            
            # Process each line of findings with Claude for grammar/formatting
            processed_findings = self.claude.process_findings(findings, section_name)
            finding_lines = processed_findings.strip().split('\n')
            
            # Track which findings have been processed
            processed_finding_indexes = set()
            
            # First try to categorize findings by direct category match
            for idx, finding in enumerate(finding_lines):
                for category in default_findings.keys():
                    # Check if the category name appears in the finding
                    if category.lower() in finding.lower():
                        modified_findings[category] = finding
                        processed_finding_indexes.add(idx)
                        
                        # Look up impression for this finding
                        impression = self.supabase.get_impression(finding, section_name)
                        if impression:
                            impressions.append(impression)
                            matched_findings.append(finding)
                        else:
                            # Log the unmatched finding
                            self.supabase.log_unmatched_finding(finding, section_name)
                            
                            # Generate impression with Claude if enabled
                            if self.use_claude_for_unmatched:
                                claude_impression = self.claude.generate_impression(finding, section_name)
                                if claude_impression:
                                    impressions.append(claude_impression)
                                    matched_findings.append(finding)
                        break
            
            # For findings that didn't match any category, use Claude to categorize
            if len(processed_finding_indexes) < len(finding_lines):
                uncategorized_findings = [f for idx, f in enumerate(finding_lines) 
                                         if idx not in processed_finding_indexes]
                
                categories = self.claude.categorize_findings(
                    uncategorized_findings, 
                    list(default_findings.keys()),
                    section_name
                )
                
                # Apply the Claude-suggested categories
                for finding, suggested_category in categories.items():
                    if suggested_category in modified_findings:
                        modified_findings[suggested_category] = finding
                        
                        # Look up impression
                        impression = self.supabase.get_impression(finding, section_name)
                        if impression:
                            impressions.append(impression)
                            matched_findings.append(finding)
                        else:
                            # Log the unmatched finding
                            self.supabase.log_unmatched_finding(finding, section_name)
                            
                            # Generate impression with Claude if enabled
                            if self.use_claude_for_unmatched:
                                claude_impression = self.claude.generate_impression(finding, section_name)
                                if claude_impression:
                                    impressions.append(claude_impression)
                                    matched_findings.append(finding)
            
            # Output all categories with updated findings
            for category, text in modified_findings.items():
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
            image_findings = self.claude.analyze_image(image_data, study_type)
            
            # If image analysis found something not in the text findings
            if image_findings and not image_findings.lower().startswith("no significant"):
                report_sections.append("")
                report_sections.append("IMAGE ANALYSIS NOTES:")
                report_sections.append(image_findings)
        
        return "\n".join(report_sections)