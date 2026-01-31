"""RadReport AI - Multimodal Radiology Report Generator.

This is the main entry point for the Streamlit application.
"""

from __future__ import annotations

import logging

from config import (
    configure_page,
    render_header,
    render_footer,
    render_debug_sidebar,
    logger,
)
from components.sidebar import render_sidebar
from pages.report_generator import render_report_generator
from pages.admin import render_admin_page
from utils.report_generator import ReportGenerator
from utils.supabase_client import SupabaseClient

# Initialize clients
try:
    supabase = SupabaseClient()
    report_generator = ReportGenerator()
    logger.info("Successfully initialized Supabase client and Report Generator")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    supabase = None
    report_generator = None

# Configure page
configure_page()

# Render header
render_header()

# Main content
if supabase and report_generator:
    render_report_generator(supabase, report_generator)
else:
    import streamlit as st
    st.error("Failed to initialize services. Please check your configuration.")

# Render footer
render_footer()

# Sidebar navigation
choice = render_sidebar()

# Debug tools
render_debug_sidebar()

# Admin page
if choice == "Admin" and supabase:
    render_admin_page(supabase)
