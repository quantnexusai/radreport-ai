import streamlit as st
import base64
from utils.report_generator import ReportGenerator
from utils.supabase_client import SupabaseClient
import io
from dotenv import load_dotenv
import logging
from supabase import create_client  # Make sure to import this
import os  # Make sure to import this

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug section - ADD THIS CODE HERE
def test_supabase_connection():
    try:
        # Create test client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            return "SUPABASE_URL or SUPABASE_KEY environment variables are missing"
        
        client = create_client(url, key)
        
        # Test facilities table
        facilities_response = client.table("facilities").select("count", count="exact").execute()
        facilities_count = facilities_response.count if hasattr(facilities_response, 'count') else 0
        
        # Test impression lookup table
        patterns_response = client.table("impression_lookup").select("count", count="exact").execute()
        patterns_count = patterns_response.count if hasattr(patterns_response, 'count') else 0
        
        # Test unmatched findings table
        unmatched_response = client.table("unmatched_findings").select("count", count="exact").execute()
        unmatched_count = unmatched_response.count if hasattr(unmatched_response, 'count') else 0
        
        return f"Connection successful. Facilities: {facilities_count}, Impression patterns: {patterns_count}, Unmatched findings: {unmatched_count}"
    except Exception as e:
        return f"Connection error: {str(e)}"

# Initialize clients - EXISTING CODE STARTS AGAIN HERE
try:
    supabase = SupabaseClient()
    report_generator = ReportGenerator()
    logger.info("Successfully initialized Supabase client and Report Generator")
except Exception as e:
    logger.error(f"Error initializing services: {e}")

# Set page config
st.set_page_config(
    page_title="RadReport AI",
    page_icon="🏥",
    layout="wide"
)

# App title with separate subtitle in smaller text
st.title("RadReport AI")
st.markdown("<h3 style='margin-top:-15px; color: #6c757d;'>Multimodal Radiology Report Generator</h3>", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    # Study Type Selection
    st.header("Study")
    st.write("What kind of study was conducted?")
    study_type = st.radio(
        "Select study type",
        ["Full Body", "Chest", "Abdomen and Pelvis"],
        label_visibility="collapsed"
    )
    
    # Facility Selection
    st.header("Facility")
    st.write("Where was the study conducted?")
    
    # Get facilities from database with error handling
    try:
        facilities = supabase.get_facilities()
        if not facilities or len(facilities) == 0:
            st.error("No facilities found in the database. Please add facilities in the Admin section.")
            facility = "No facility available"
            facility_names = ["No facility available"]
        else:
            facility_names = [f["name"] for f in facilities]
            facility = st.radio(
                "Select facility",
                facility_names,
                label_visibility="collapsed"
            )
    except Exception as e:
        st.error(f"Error retrieving facilities: {str(e)}")
        facility = "Error"
        facilities = []
        facility_names = ["Error loading facilities"]
    
    # Dynamic sections based on study type
    sections_data = {}
    
    if study_type in ["Full Body", "Chest"]:
        st.header("Chest")
        st.write("Findings")
        chest_findings = st.text_area("Enter chest findings", height=150, key="chest", label_visibility="collapsed")
        if chest_findings:
            sections_data["chest"] = chest_findings
    
    if study_type in ["Full Body", "Abdomen and Pelvis"]:
        st.header("Abdomen and Pelvis")
        st.write("Findings")
        abdomen_findings = st.text_area("Enter abdomen and pelvis findings", height=150, key="abdomen", label_visibility="collapsed")
        if abdomen_findings:
            sections_data["abdomen_pelvis"] = abdomen_findings
    
    # Image Upload
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Upload a radiology image", type=["jpg", "jpeg", "png", "dcm"])
    
    image_data = None
    if uploaded_file is not None:
        # Handle DICOM files differently if needed
        if uploaded_file.name.endswith('.dcm'):
            # For v1, we'll just display a message
            st.info("DICOM processing will be available in a future version")
        else:
            # Convert to base64 for Claude
            bytes_data = uploaded_file.getvalue()
            image_data = base64.b64encode(bytes_data).decode()
            st.image(bytes_data, caption="Uploaded Image", use_column_width=True)

with col2:
    st.header("Generated Report")
    
    # Generate and reset buttons
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        reset = st.button("↺ Reset")
    with col_btn2:
        generate = st.button("✓ Generate")
    
    # Report output area
    report_container = st.container()
    
    if reset:
        # Clear all form fields
        st.session_state.clear()
        st.experimental_rerun()
    
    if generate:
        with st.spinner("Generating report..."):
            if not sections_data:
                report_container.error("Please enter findings for at least one section.")
            elif facility in ["No facility available", "Error"]:
                report_container.error("Please select a valid facility before generating a report.")
            else:
                try:
                    report = report_generator.generate_report(
                        facility, 
                        study_type, 
                        sections_data,
                        image_data
                    )
                    
                    report_container.text_area(
                        "Generated Report", 
                        report, 
                        height=600
                    )
                    
                    # Add download button
                    report_bytes = report.encode()
                    report_container.download_button(
                        "Download Report",
                        report_bytes,
                        "radiology_report.txt",
                        "text/plain"
                    )
                except Exception as e:
                    report_container.error(f"Error generating report: {str(e)}")
                    logger.error(f"Report generation failed: {e}")

# Add a footer with version info
st.markdown("---")
st.markdown("<div style='text-align: center; color: #6c757d;'>RadReport AI v1.0 | &copy; 2025</div>", unsafe_allow_html=True)

# Create additional pages (hidden in a menu in v1)
menu = ["Report Generator", "Admin"]
choice = st.sidebar.selectbox("Select Page", menu)

# Debug mode in sidebar - ADD THIS CODE HERE
with st.sidebar:
    debug_expand = st.expander("Debug Tools")
    with debug_expand:
        if 'debug_mode' not in st.session_state:
            st.session_state.debug_mode = False
        st.session_state.debug_mode = st.checkbox("Enable Debug Mode", value=st.session_state.debug_mode)
        if st.session_state.debug_mode:
            if st.button("Test Supabase Connection"):
                connection_status = test_supabase_connection()
                st.code(connection_status)

if choice == "Admin":
    st.sidebar.info("Admin features are password protected")
    password = st.sidebar.text_input("Enter admin password", type="password")
    
    if password == "admin1234":  # Replace with a secure password mechanism
        st.sidebar.success("Admin access granted")
        
        admin_tabs = st.tabs(["Facilities", "Templates", "Impression Patterns", "Unmatched Findings"])
        
        # New Facilities tab
        with admin_tabs[0]:
            st.header("Facility Management")
            
            # Add new facility
            st.subheader("Add New Facility")
            
            new_facility_name = st.text_input("Facility Name")
            new_chest_template = st.text_area("Chest Technique Template", 
                placeholder="e.g., Thin section axial images were obtained through the chest using a GE Lightspeed scanner. No intravenous contrast was used.",
                height=100)
            new_abdomen_template = st.text_area("Abdomen Technique Template",
                placeholder="e.g., Thin section axial images were obtained through the abdomen and pelvis using a GE Lightspeed scanner. No intravenous contrast was used.",
                height=100)
            
            if st.button("Add Facility"):
                if new_facility_name and new_chest_template and new_abdomen_template:
                    try:
                        success = supabase.add_facility(
                            new_facility_name,
                            new_chest_template,
                            new_abdomen_template
                        )
                        if success:
                            st.success(f"Facility '{new_facility_name}' added successfully")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to add facility")
                    except Exception as e:
                        st.error(f"Error adding facility: {str(e)}")
                else:
                    st.warning("Please fill in all fields")
            
            # Display existing facilities
            st.subheader("Existing Facilities")
            try:
                facilities = supabase.get_facilities()
                if facilities and len(facilities) > 0:
                    for i, facility in enumerate(facilities):
                        with st.expander(f"{facility['name']}"):
                            st.text_area(f"Chest Technique", facility["technique_template_chest"], height=100, key=f"chest_{i}")
                            st.text_area(f"Abdomen Technique", facility["technique_template_abdomen"], height=100, key=f"abdomen_{i}")
                            
                            if st.button(f"Delete {facility['name']}", key=f"delete_{i}"):
                                try:
                                    success = supabase.delete_facility(facility['id'])
                                    if success:
                                        st.success(f"Facility '{facility['name']}' deleted successfully")
                                        st.experimental_rerun()
                                    else:
                                        st.error(f"Failed to delete facility '{facility['name']}'")
                                except Exception as e:
                                    st.error(f"Error deleting facility: {str(e)}")
                else:
                    st.info("No facilities found. Add your first facility above.")
            except Exception as e:
                st.error(f"Error loading facilities: {str(e)}")
        
        # Template Management tab (renamed from previous Templates tab)
        with admin_tabs[1]:
            st.header("Template Management")
            
            # First select a facility to edit templates
            try:
                if facilities and len(facilities) > 0:
                    selected_facility = st.selectbox(
                        "Select Facility to Edit Templates",
                        options=[f["name"] for f in facilities],
                        key="template_facility"
                    )
                    
                    # Find the selected facility object
                    selected_facility_obj = next((f for f in facilities if f["name"] == selected_facility), None)
                    
                    if selected_facility_obj:
                        facility_id = selected_facility_obj.get('id')
                        
                        # Edit templates
                        st.subheader(f"Edit Templates for {selected_facility}")
                        
                        updated_chest = st.text_area(
                            "Chest Technique Template", 
                            selected_facility_obj.get("technique_template_chest", ""),
                            height=150
                        )
                        
                        updated_abdomen = st.text_area(
                            "Abdomen and Pelvis Technique Template",
                            selected_facility_obj.get("technique_template_abdomen", ""),
                            height=150
                        )
                        
                        if st.button("Update Templates"):
                            try:
                                success = supabase.update_facility_templates(
                                    facility_id,
                                    updated_chest,
                                    updated_abdomen
                                )
                                if success:
                                    st.success(f"Templates for {selected_facility} updated successfully")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to update templates")
                            except Exception as e:
                                st.error(f"Error updating templates: {str(e)}")
                else:
                    st.info("No facilities found. Please add facilities in the Facilities tab first.")
            except Exception as e:
                st.error(f"Error loading facilities for template editing: {str(e)}")
        
        # Impression Patterns tab (moved to third position)
        with admin_tabs[2]:
            st.header("Impression Patterns")
            try:
                patterns = supabase.get_all_impression_patterns()
                
                # Display existing patterns
                st.subheader("Existing Patterns")
                if patterns and len(patterns) > 0:
                    for pattern in patterns:
                        with st.expander(f"{pattern['section_name']}: {pattern['finding_pattern']}"):
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.write(f"**Section:** {pattern['section_name']}")
                                st.write(f"**Pattern:** {pattern['finding_pattern']}")
                            with col2:
                                st.write(f"**Impression:** {pattern['impression_text']}")
                            
                            if st.button(f"Delete Pattern", key=f"delete_pattern_{pattern['id']}"):
                                try:
                                    success = supabase.delete_impression_pattern(pattern['id'])
                                    if success:
                                        st.success("Pattern deleted successfully")
                                        st.experimental_rerun()
                                    else:
                                        st.error("Failed to delete pattern")
                                except Exception as e:
                                    st.error(f"Error deleting pattern: {str(e)}")
                else:
                    st.info("No impression patterns found. Add your first pattern below.")
                
                # Add new pattern
                st.subheader("Add New Pattern")
                new_section = st.selectbox("Section", ["chest", "abdomen_pelvis"])
                new_pattern = st.text_input("Finding Pattern", 
                    help="Enter a pattern to match in findings, e.g., 'liver is enlarged' or 'nodule in left lower lobe'")
                new_impression = st.text_area("Impression Text", 
                    help="Enter the impression text to generate for this finding pattern",
                    height=100)
                
                if st.button("Add Pattern"):
                    if new_pattern and new_impression:
                        try:
                            success = supabase.add_impression_pattern(new_pattern, new_section, new_impression)
                            if success:
                                st.success("Pattern added successfully")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to add pattern")
                        except Exception as e:
                            st.error(f"Error adding pattern: {str(e)}")
                    else:
                        st.warning("Please fill in all fields")
            except Exception as e:
                st.error(f"Error managing impression patterns: {str(e)}")
        
        # Unmatched Findings tab (moved to fourth position)
        with admin_tabs[3]:
            st.header("Unmatched Findings")
            try:
                unmatched = supabase.get_unmatched_findings(limit=50)
                
                if unmatched and len(unmatched) > 0:
                    st.write(f"Found {len(unmatched)} unmatched findings")
                    
                    for finding in unmatched:
                        with st.expander(f"{finding['section_name']}: {finding['finding'][:50]}..."):
                            st.write(f"**Section:** {finding['section_name']}")
                            st.write(f"**Finding:** {finding['finding']}")
                            st.write(f"**Date:** {finding['created_at'].split('T')[0] if 'T' in finding['created_at'] else finding['created_at']}")
                            
                            # Add a button to create a pattern from this finding
                            if st.button(f"Create Pattern for this Finding", key=f"create_pattern_{finding['id']}"):
                                # Pre-fill the pattern form and switch tabs
                                if 'new_section' not in st.session_state:
                                    st.session_state.new_section = finding['section_name']
                                if 'new_pattern' not in st.session_state:
                                    st.session_state.new_pattern = finding['finding']
                                st.session_state.active_tab = 2  # Switch to the Impression Patterns tab (index 2)
                                st.experimental_rerun()
                            
                            # Option to delete the unmatched finding
                            if st.button(f"Delete Unmatched Finding", key=f"delete_unmatched_{finding['id']}"):
                                try:
                                    success = supabase.delete_unmatched_finding(finding['id'])
                                    if success:
                                        st.success("Unmatched finding deleted")
                                        st.experimental_rerun()
                                    else:
                                        st.error("Failed to delete unmatched finding")
                                except Exception as e:
                                    st.error(f"Error deleting unmatched finding: {str(e)}")
                else:
                    st.info("No unmatched findings found. This is good - it means all findings have matching patterns!")
            except Exception as e:
                st.error(f"Error loading unmatched findings: {str(e)}")
    else:
        if password:
            st.sidebar.error("Incorrect password")