"""Application configuration and initialization."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

if TYPE_CHECKING:
    from supabase import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def get_supabase_client() -> Client:
    """Create and return a Supabase client for testing connection.
    
    Returns:
        Client: A configured Supabase client instance.
        
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are missing.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY environment variables are missing")
    return create_client(url, key)


def test_supabase_connection() -> str:
    """Test the Supabase database connection.
    
    Returns:
        str: A status message indicating connection success or failure with details.
    """
    try:
        client = get_supabase_client()
        
        # Test facilities table
        facilities_response = client.table("facilities").select("count", count="exact").execute()
        facilities_count = facilities_response.count if hasattr(facilities_response, 'count') else 0
        
        # Test impression lookup table
        patterns_response = client.table("impression_lookup").select("count", count="exact").execute()
        patterns_count = patterns_response.count if hasattr(patterns_response, 'count') else 0
        
        # Test unmatched findings table
        unmatched_response = client.table("unmatched_findings").select("count", count="exact").execute()
        unmatched_count = unmatched_response.count if hasattr(unmatched_response, 'count') else 0
        
        return (
            f"Connection successful. Facilities: {facilities_count}, "
            f"Impression patterns: {patterns_count}, Unmatched findings: {unmatched_count}"
        )
    except Exception as e:
        return f"Connection error: {str(e)}"


def configure_page() -> None:
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="RadReport AI",
        page_icon="🏥",
        layout="wide"
    )


def render_header() -> None:
    """Render the application header."""
    st.title("RadReport AI")
    st.markdown(
        "<h3 style='margin-top:-15px; color: #6c757d;'>"
        "Multimodal Radiology Report Generator</h3>",
        unsafe_allow_html=True
    )


def render_footer() -> None:
    """Render the application footer."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6c757d;'>"
        "RadReport AI v1.0 | &copy; 2025</div>",
        unsafe_allow_html=True
    )


def render_debug_sidebar() -> None:
    """Render the debug tools in the sidebar."""
    with st.sidebar:
        debug_expand = st.expander("Debug Tools")
        with debug_expand:
            if 'debug_mode' not in st.session_state:
                st.session_state.debug_mode = False
            st.session_state.debug_mode = st.checkbox(
                "Enable Debug Mode",
                value=st.session_state.debug_mode
            )
            if st.session_state.debug_mode:
                if st.button("Test Supabase Connection"):
                    connection_status = test_supabase_connection()
                    st.code(connection_status)
