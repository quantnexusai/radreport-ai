"""Admin page for RadReport AI."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from utils.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


def render_facilities_tab(supabase: SupabaseClient) -> None:
    """Render the facilities management tab.
    
    Args:
        supabase: The Supabase client instance.
    """
    st.header("Facility Management")
    
    # Add new facility
    st.subheader("Add New Facility")
    
    new_facility_name = st.text_input("Facility Name")
    new_chest_template = st.text_area(
        "Chest Technique Template",
        placeholder="e.g., Thin section axial images were obtained through the chest...",
        height=100
    )
    new_abdomen_template = st.text_area(
        "Abdomen Technique Template",
        placeholder="e.g., Thin section axial images were obtained through the abdomen...",
        height=100
    )
    
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
                    st.rerun()
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
                    st.text_area(
                        "Chest Technique",
                        facility["technique_template_chest"],
                        height=100,
                        key=f"chest_{i}"
                    )
                    st.text_area(
                        "Abdomen Technique",
                        facility["technique_template_abdomen"],
                        height=100,
                        key=f"abdomen_{i}"
                    )
                    
                    if st.button(f"Delete {facility['name']}", key=f"delete_{i}"):
                        try:
                            success = supabase.delete_facility(facility['id'])
                            if success:
                                st.success(f"Facility '{facility['name']}' deleted successfully")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete facility '{facility['name']}'")
                        except Exception as e:
                            st.error(f"Error deleting facility: {str(e)}")
        else:
            st.info("No facilities found. Add your first facility above.")
    except Exception as e:
        st.error(f"Error loading facilities: {str(e)}")


def render_templates_tab(supabase: SupabaseClient) -> None:
    """Render the template management tab.
    
    Args:
        supabase: The Supabase client instance.
    """
    st.header("Template Management")
    
    try:
        facilities = supabase.get_facilities()
        if facilities and len(facilities) > 0:
            selected_facility = st.selectbox(
                "Select Facility to Edit Templates",
                options=[f["name"] for f in facilities],
                key="template_facility"
            )
            
            selected_facility_obj = next(
                (f for f in facilities if f["name"] == selected_facility),
                None
            )
            
            if selected_facility_obj:
                facility_id = selected_facility_obj.get('id')
                
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
                            st.rerun()
                        else:
                            st.error("Failed to update templates")
                    except Exception as e:
                        st.error(f"Error updating templates: {str(e)}")
        else:
            st.info("No facilities found. Please add facilities in the Facilities tab first.")
    except Exception as e:
        st.error(f"Error loading facilities for template editing: {str(e)}")


def render_impression_patterns_tab(supabase: SupabaseClient) -> None:
    """Render the impression patterns management tab.
    
    Args:
        supabase: The Supabase client instance.
    """
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
                    
                    if st.button("Delete Pattern", key=f"delete_pattern_{pattern['id']}"):
                        try:
                            success = supabase.delete_impression_pattern(pattern['id'])
                            if success:
                                st.success("Pattern deleted successfully")
                                st.rerun()
                            else:
                                st.error("Failed to delete pattern")
                        except Exception as e:
                            st.error(f"Error deleting pattern: {str(e)}")
        else:
            st.info("No impression patterns found. Add your first pattern below.")
        
        # Add new pattern
        st.subheader("Add New Pattern")
        new_section = st.selectbox("Section", ["chest", "abdomen_pelvis"])
        new_pattern = st.text_input(
            "Finding Pattern",
            help="Enter a pattern to match in findings"
        )
        new_impression = st.text_area(
            "Impression Text",
            help="Enter the impression text to generate for this finding pattern",
            height=100
        )
        
        if st.button("Add Pattern"):
            if new_pattern and new_impression:
                try:
                    success = supabase.add_impression_pattern(
                        new_pattern,
                        new_section,
                        new_impression
                    )
                    if success:
                        st.success("Pattern added successfully")
                        st.rerun()
                    else:
                        st.error("Failed to add pattern")
                except Exception as e:
                    st.error(f"Error adding pattern: {str(e)}")
            else:
                st.warning("Please fill in all fields")
    except Exception as e:
        st.error(f"Error managing impression patterns: {str(e)}")


def render_unmatched_findings_tab(supabase: SupabaseClient) -> None:
    """Render the unmatched findings review tab.
    
    Args:
        supabase: The Supabase client instance.
    """
    st.header("Unmatched Findings")
    try:
        unmatched = supabase.get_unmatched_findings(limit=50)
        
        if unmatched and len(unmatched) > 0:
            st.write(f"Found {len(unmatched)} unmatched findings")
            
            for finding in unmatched:
                finding_preview = finding['finding'][:50] + "..." if len(finding['finding']) > 50 else finding['finding']
                with st.expander(f"{finding['section_name']}: {finding_preview}"):
                    st.write(f"**Section:** {finding['section_name']}")
                    st.write(f"**Finding:** {finding['finding']}")
                    
                    created_at = finding['created_at']
                    date_str = created_at.split('T')[0] if 'T' in created_at else created_at
                    st.write(f"**Date:** {date_str}")
                    
                    if st.button(
                        "Create Pattern for this Finding",
                        key=f"create_pattern_{finding['id']}"
                    ):
                        st.session_state.new_section = finding['section_name']
                        st.session_state.new_pattern = finding['finding']
                        st.session_state.active_tab = 2
                        st.rerun()
                    
                    if st.button(
                        "Delete Unmatched Finding",
                        key=f"delete_unmatched_{finding['id']}"
                    ):
                        try:
                            success = supabase.delete_unmatched_finding(finding['id'])
                            if success:
                                st.success("Unmatched finding deleted")
                                st.rerun()
                            else:
                                st.error("Failed to delete unmatched finding")
                        except Exception as e:
                            st.error(f"Error deleting unmatched finding: {str(e)}")
        else:
            st.info("No unmatched findings found. This is good - it means all findings have matching patterns!")
    except Exception as e:
        st.error(f"Error loading unmatched findings: {str(e)}")


def render_admin_page(supabase: SupabaseClient) -> None:
    """Render the admin page with authentication.
    
    Args:
        supabase: The Supabase client instance.
    """
    st.sidebar.info("Admin features are password protected")
    password = st.sidebar.text_input("Enter admin password", type="password")
    
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password:
        st.sidebar.error("Admin password not configured. Set ADMIN_PASSWORD environment variable.")
        return
    
    if password != admin_password:
        if password:
            st.sidebar.error("Incorrect password")
        return
    
    st.sidebar.success("Admin access granted")
    
    admin_tabs = st.tabs([
        "Facilities",
        "Templates",
        "Impression Patterns",
        "Unmatched Findings"
    ])
    
    with admin_tabs[0]:
        render_facilities_tab(supabase)
    
    with admin_tabs[1]:
        render_templates_tab(supabase)
    
    with admin_tabs[2]:
        render_impression_patterns_tab(supabase)
    
    with admin_tabs[3]:
        render_unmatched_findings_tab(supabase)
