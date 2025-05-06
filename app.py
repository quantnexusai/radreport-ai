import streamlit as st
import base64
from utils.report_generator import ReportGenerator
from utils.supabase_client import SupabaseClient
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
supabase = SupabaseClient()
report_generator = ReportGenerator()

# Set page config
st.set_page_config(
    page_title="RadReport AI",
    page_icon="🏥",
    layout="wide"
)

# App title
st.title("RadReport AI - Multimodal Radiology Report Generator")

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
    
    # Get facilities from database
    facilities = supabase.get_facilities()
    facility_names = [f["name"] for f in facilities]
    
    facility = st.radio(
        "Select facility",
        facility_names,
        label_visibility="collapsed"
    )
    
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
        st.experimental_rerun()
    
    if generate:
        with st.spinner("Generating report..."):
            if not sections_data:
                report_container.error("Please enter findings for at least one section.")
            else:
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

# Create additional pages (hidden in a menu in v1)
menu = ["Report Generator", "Admin"]
choice = st.sidebar.selectbox("Select Page", menu)

if choice == "Admin":
    st.sidebar.info("Admin features are password protected")
    password = st.sidebar.text_input("Enter admin password", type="password")
    
    if password == "admin1234":  # Replace with a secure password mechanism
        st.sidebar.success("Admin access granted")
        
        admin_tabs = st.tabs(["Templates", "Impression Patterns", "Unmatched Findings"])
        
        with admin_tabs[0]:
            st.header("Facility Templates")
            # Display facilities and their templates
            for facility in facilities:
                st.subheader(facility["name"])
                st.text_area(f"Chest technique for {facility['name']}", facility["technique_template_chest"], height=100)
                st.text_area(f"Abdomen technique for {facility['name']}", facility["technique_template_abdomen"], height=100)
        
        with admin_tabs[1]:
            st.header("Impression Patterns")
            patterns = supabase.get_all_impression_patterns()
            
            # Display existing patterns
            st.subheader("Existing Patterns")
            for pattern in patterns:
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    st.write(f"**Section:** {pattern['section_name']}")
                with col2:
                    st.write(f"**Pattern:** {pattern['finding_pattern']}")
                with col3:
                    st.write(f"**Impression:** {pattern['impression_text']}")
                st.divider()
            
            # Add new pattern
            st.subheader("Add New Pattern")
            new_section = st.selectbox("Section", ["chest", "abdomen_pelvis"])
            new_pattern = st.text_input("Finding Pattern")
            new_impression = st.text_area("Impression Text", height=100)
            
            if st.button("Add Pattern"):
                if new_pattern and new_impression:
                    success = supabase.add_impression_pattern(new_pattern, new_section, new_impression)
                    if success:
                        st.success("Pattern added successfully")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add pattern")
                else:
                    st.warning("Please fill in all fields")
        
        with admin_tabs[2]:
            st.header("Unmatched Findings")
            unmatched = supabase.get_unmatched_findings(limit=50)
            
            if unmatched:
                st.write(f"Found {len(unmatched)} unmatched findings")
                
                for finding in unmatched:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.write(f"**Section:** {finding['section_name']}")
                    with col2:
                        st.write(f"**Finding:** {finding['finding']}")
                    with col3:
                        st.write(f"**Date:** {finding['created_at'].split('T')[0]}")
                    
                    # Add a button to create a pattern from this finding
                    if st.button(f"Create Pattern for: {finding['finding'][:20]}...", key=finding['id']):
                        # Pre-fill the pattern form
                        st.session_state.new_section = finding['section_name']
                        st.session_state.new_pattern = finding['finding']
                        st.session_state.active_tab = 1  # Switch to the Impression Patterns tab
                        st.experimental_rerun()
                    
                    st.divider()
            else:
                st.info("No unmatched findings found")
    else:
        if password:
            st.sidebar.error("Incorrect password")