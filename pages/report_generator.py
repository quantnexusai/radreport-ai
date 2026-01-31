"""Report generator page for RadReport AI."""

from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING, Optional

import streamlit as st

if TYPE_CHECKING:
    from utils.supabase_client import SupabaseClient
    from utils.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


def render_study_selection() -> str:
    """Render the study type selection component.
    
    Returns:
        str: The selected study type.
    """
    st.header("Study")
    st.write("What kind of study was conducted?")
    return st.radio(
        "Select study type",
        ["Full Body", "Chest", "Abdomen and Pelvis"],
        label_visibility="collapsed"
    )


def render_facility_selection(supabase: SupabaseClient) -> tuple[str, list[dict]]:
    """Render the facility selection component.
    
    Args:
        supabase: The Supabase client instance.
        
    Returns:
        tuple: A tuple of (selected facility name, list of facility dicts).
    """
    st.header("Facility")
    st.write("Where was the study conducted?")
    
    try:
        facilities = supabase.get_facilities()
        if not facilities or len(facilities) == 0:
            st.error("No facilities found in the database. Please add facilities in the Admin section.")
            return "No facility available", []
        
        facility_names = [f["name"] for f in facilities]
        facility = st.radio(
            "Select facility",
            facility_names,
            label_visibility="collapsed"
        )
        return facility, facilities
    except Exception as e:
        st.error(f"Error retrieving facilities: {str(e)}")
        return "Error", []


def render_findings_input(study_type: str) -> dict[str, str]:
    """Render the findings input sections based on study type.
    
    Args:
        study_type: The selected study type.
        
    Returns:
        dict: A dictionary mapping section names to findings text.
    """
    sections_data: dict[str, str] = {}
    
    if study_type in ["Full Body", "Chest"]:
        st.header("Chest")
        st.write("Findings")
        chest_findings = st.text_area(
            "Enter chest findings",
            height=150,
            key="chest",
            label_visibility="collapsed"
        )
        if chest_findings:
            sections_data["chest"] = chest_findings
    
    if study_type in ["Full Body", "Abdomen and Pelvis"]:
        st.header("Abdomen and Pelvis")
        st.write("Findings")
        abdomen_findings = st.text_area(
            "Enter abdomen and pelvis findings",
            height=150,
            key="abdomen",
            label_visibility="collapsed"
        )
        if abdomen_findings:
            sections_data["abdomen_pelvis"] = abdomen_findings
    
    return sections_data


def render_image_upload() -> Optional[str]:
    """Render the image upload component.
    
    Returns:
        Optional[str]: Base64-encoded image data, or None if no image uploaded.
    """
    st.header("Upload Image")
    uploaded_file = st.file_uploader(
        "Upload a radiology image",
        type=["jpg", "jpeg", "png", "dcm"]
    )
    
    if uploaded_file is None:
        return None
    
    if uploaded_file.name.endswith('.dcm'):
        st.info("DICOM processing will be available in a future version")
        return None
    
    bytes_data = uploaded_file.getvalue()
    st.image(bytes_data, caption="Uploaded Image", use_column_width=True)
    return base64.b64encode(bytes_data).decode()


def render_report_output(
    report_generator: ReportGenerator,
    facility: str,
    study_type: str,
    sections_data: dict[str, str],
    image_data: Optional[str]
) -> None:
    """Render the report output section with generate/reset buttons.
    
    Args:
        report_generator: The report generator instance.
        facility: The selected facility name.
        study_type: The selected study type.
        sections_data: Dictionary of section findings.
        image_data: Optional base64-encoded image data.
    """
    st.header("Generated Report")
    
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        reset = st.button("↺ Reset")
    with col_btn2:
        generate = st.button("✓ Generate")
    
    report_container = st.container()
    
    if reset:
        st.session_state.clear()
        st.rerun()
    
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


def render_report_generator(
    supabase: SupabaseClient,
    report_generator: ReportGenerator
) -> None:
    """Render the main report generator page.
    
    Args:
        supabase: The Supabase client instance.
        report_generator: The report generator instance.
    """
    col1, col2 = st.columns([1, 1])
    
    with col1:
        study_type = render_study_selection()
        facility, _ = render_facility_selection(supabase)
        sections_data = render_findings_input(study_type)
        image_data = render_image_upload()
    
    with col2:
        render_report_output(
            report_generator,
            facility,
            study_type,
            sections_data,
            image_data
        )
