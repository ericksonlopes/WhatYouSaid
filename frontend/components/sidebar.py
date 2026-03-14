"""Sidebar component for navigation and subject management."""

import streamlit as st
from frontend.utils.services import init_basic_services, list_subjects
from frontend.components.task_cards import render_ingestion_history

def _handle_subject_change():
    """Callback when the subject selectbox changes."""
    selected_name = st.session_state["sidebar_selected_subject"]
    # We need to find the ID corresponding to this name. 
    # Since we don't have the list here easily without re-fetching, 
    # we'll let the main render function handle the ID sync but 
    # ONLY if the name changed.
    st.session_state["main_view"] = "dashboard"

def render_sidebar(safe_rerun):
    with st.sidebar:
        st.title("🎙️ WhatYouSaid")
        st.caption("Person-centric Knowledge Hub")
        st.markdown("---")

        # Top Navigation: Chat
        chat_active = st.session_state.get("main_view") == "chat"
        if st.button("💬 Chat", key="sidebar_chat_btn", use_container_width=True, type="primary" if chat_active else "secondary"):
            st.session_state["main_view"] = "chat"
            st.rerun()

        st.markdown("---")
        st.subheader("📚 Subjects")
        
        services_for_sidebar = init_basic_services()
        sidebar_ks = services_for_sidebar["ks_service"]
        _side_subs = list_subjects(sidebar_ks)
        
        if _side_subs:
            _options = [s.name for s in _side_subs]
            
            # Ensure we have a valid selection in state
            current_name = st.session_state.get("sidebar_selected_subject")
            if current_name not in _options:
                current_name = _options[0] if _options else None
                st.session_state["sidebar_selected_subject"] = current_name

            # Find current index for selectbox
            try:
                default_index = _options.index(current_name) if current_name in _options else 0
            except ValueError:
                default_index = 0

            selected_name = st.selectbox(
                "Current Context", 
                options=_options, 
                index=default_index,
                key="sidebar_selected_subject",
                label_visibility="collapsed",
                on_change=_handle_subject_change
            )
            
            # Sync the ID based on the selected name
            selected_subject_obj = next((s for s in _side_subs if s.name == selected_name), None)
            if selected_subject_obj:
                st.session_state["selected_subject_id"] = str(selected_subject_obj.id)
        else:
            st.info("No subjects found. Create one to get started.")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        
        # Dashboard Button
        dash_active = st.session_state.get("main_view") == "dashboard"
        if st.button("📊 Dashboard", key="sidebar_dashboard_btn", use_container_width=True, type="primary" if dash_active else "secondary"):
            st.session_state["main_view"] = "dashboard"
            st.rerun()

        from frontend.dialogs.subject_dialog import open_create_subject

        if st.button("➕ New Subject", key="open_create_subject_btn", use_container_width=True):
            if callable(open_create_subject):
                open_create_subject(sidebar_ks, safe_rerun)

        st.markdown("---")

        # Settings Button
        settings_active = st.session_state.get("main_view") == "settings"
        if st.button("⚙️ Settings", key="sidebar_settings_btn", use_container_width=True, type="primary" if settings_active else "secondary"):
            st.session_state["main_view"] = "settings"
            st.rerun()
