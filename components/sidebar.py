"""Sidebar components for RadReport AI."""

from __future__ import annotations

from typing import Literal

import streamlit as st

PageChoice = Literal["Report Generator", "Admin"]


def render_sidebar() -> PageChoice:
    """Render the sidebar navigation and return the selected page.
    
    Returns:
        PageChoice: The selected page name.
    """
    menu = ["Report Generator", "Admin"]
    choice: PageChoice = st.sidebar.selectbox("Select Page", menu)
    return choice
