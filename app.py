import streamlit as st
import base64
from utils.report_generator import ReportGenerator
from utils.supabase_client import SupabaseClient
import io

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

# Sidebar for admin functions (optional for v1)
with st.sidebar:
    st.subheader("About")
    st.write("AI-powered radiology report generator using Claude and structured templates.")
    
    st.divider()
    
    # Add admin features here in future versions

# Main form
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Study")
    st.write("What kind of study was conducted?")
    study_type = st.radio(
        "Select study type",
        ["Full Body", "Chest", "Abdomen and Pelvis"],
        label_visibility="collapsed"
    )
    
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
        chest_findings = st.text_area("Findings", height=150, key="chest")
        sections_data["chest"] = chest_findings
    
    if study_type in ["Full Body", "Abdomen and Pelvis"]:
        st.header("Abdomen and Pelvis")
        abdomen_findings = st.text_area("Findings", height=150, key="abdomen")
        sections_data["abdomen_pelvis"] = abdomen_findings
    
    # Image upload
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
    col1, col2 = st.columns([1, 1])
    with col1:
        reset = st.button("🔄 Reset")
    with col2:
        generate = st.button("🚀 Generate")
    
    # Report output area
    report_output = st.empty()
    
    if reset:
        # Clear all form fields
        st.experimental_rerun()
    
    if generate:
        with st.spinner("Generating report..."):
            report = report_generator.generate_report(
                facility, 
                study_type, 
                sections_data,
                image_data
            )
            
            report_output.text_area(
                "Generated Report", 
                report, 
                height=600
            )
            
            # Add download button
            report_bytes = report.encode()
            st.download_button(
                "Download Report",
                report_bytes,
                "radiology_report.txt",
                "text/plain"
            )