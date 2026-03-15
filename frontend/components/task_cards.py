"""Component for tracking ingestion task history and showing notifications via st.toast."""

import streamlit as st
from frontend.utils.services import init_basic_services

@st.fragment(run_every="5s")
def _show_history_fragment(ig_service, visible=True):
    """
    Tracks ingestion jobs and shows notifications.
    If visible=True, renders the Notification UI.
    Regardless of visibility, shows st.toast for status changes.
    """
    if visible:
        st.markdown("### 🔔 Notifications")
        st.caption("RECENT NOTIFICATIONS")
    
    try:
        selected_sid = st.session_state.get("selected_subject_id")
        if not selected_sid:
            if visible:
                st.caption("Select a subject to see history.")
            return
        
        from uuid import UUID
        try:
            sid = UUID(selected_sid)
        except Exception:
            sid = str(selected_sid)
            
        # Fetch recent jobs
        jobs = ig_service.list_recent_jobs_by_subject(sid, limit=10)
        if not jobs:
            if visible:
                st.caption("No recent ingestion jobs.")
            return

        # --- Initialization of tracking state ---
        # We track statuses per subject to avoid toasts when switching contexts.
        if "notification_state" not in st.session_state:
            st.session_state["notification_state"] = {}

        # If this is the first time we see THIS specific subject in this session,
        # or we haven't initialized it yet, we populate the state WITHOUT showing toasts.
        subject_key = str(sid)
        is_first_run_for_subject = subject_key not in st.session_state["notification_state"]
        
        if is_first_run_for_subject:
            st.session_state["notification_state"][subject_key] = {}
            for job in jobs:
                status_obj = job.status
                status_val = status_obj.value if hasattr(status_obj, "value") else str(status_obj).lower()
                st.session_state["notification_state"][subject_key][str(job.id)] = status_val
            # On first run for a subject, we just initialize and continue
            # If not visible, we can stop here.
            if not visible:
                return

        # Fetch CS service to get source titles for explicit toasts
        services = init_basic_services()
        cs_service = services.get("cs_service")

        all_cards_html = ""
        for job in jobs:
            job_id_str = str(job.id)
            # Extract clean status string
            status_obj = job.status
            status_val = status_obj.value if hasattr(status_obj, "value") else str(status_obj).lower()
            
            # --- Toast Notification Logic ---
            # Only process toasts if NOT the very first run for this subject
            if not is_first_run_for_subject:
                last_status = st.session_state["notification_state"][subject_key].get(job_id_str)
                
                # We notify if:
                # 1. It's a brand new job (not in our tracking yet)
                # 2. The status has changed
                if last_status != status_val:
                    source_title = "Unknown"
                    if cs_service and job.content_source_id:
                        try:
                            source = cs_service.get_by_id(job.content_source_id)
                            if source:
                                source_title = source.title or source.external_source
                        except Exception:
                            pass

                    type_label = job.ingestion_type.capitalize() if job.ingestion_type else 'Ingestion'
                    item_info = f"[{type_label}] {source_title}"
                    
                    if status_val == "finished":
                        st.toast(f"✅ **Finished**: {item_info}", icon="🎉", duration="long")
                    elif status_val == "failed":
                        st.toast(f"❌ **Failed**: {item_info}", icon="🚨",   duration="long")
                    elif status_val == "processing":
                        st.toast(f"⚙️ **Processing**: {item_info}", icon="🔄",  duration="short")
                    elif status_val == "started":
                        st.toast(f"🚀 **Started**: {item_info}", icon="🆕",  duration="short")
                    
                    # Update tracking state for this subject
                    st.session_state["notification_state"][subject_key][job_id_str] = status_val

            # --- UI Rendering Logic (if visible) ---
            if visible and len(all_cards_html.split('task-card')) <= 4: # Limit UI to 4 cards
                status_map = {
                    "finished": {"color": "#10b981", "label": "Completed", "stats": "1 success, 0 failed"},
                    "processing": {"color": "#3b82f6", "label": "Processing", "stats": "In progress..."},
                    "started": {"color": "#f59e0b", "label": "Started", "stats": "Queued"},
                    "failed": {"color": "#ef4444", "label": "Failed", "stats": "0 success, 1 failed"}
                }
                s_info = status_map.get(status_val, {"color": "#71717a", "label": status_val.capitalize(), "stats": ""})
                ts = job.created_at.strftime("%H:%M")
                
                dur_str = ""
                if job.finished_at and job.started_at:
                    dur = (job.finished_at - job.started_at).total_seconds()
                    dur_str = f"{int(dur)}s" if dur < 60 else f"{int(dur // 60)}m {int(dur % 60)}s"

                all_cards_html += f"""
                    <div class="task-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <b style="color: white; font-size: 0.9em;">Ingestion | {job.ingestion_type.capitalize() if job.ingestion_type else 'Generic'}</b>
                            <span style="color: {s_info['color']}; font-size: 0.8em; font-weight: 600;">{s_info['label']}</span>
                        </div>
                        <div style="font-size: 0.8em; color: #71717a; margin-top: 6px; line-height: 1.4;">
                            ID: <span style="font-family: monospace; font-size: 0.85em;">{str(job.id)[:8]}</span> <br>
                            {s_info['stats']} • {ts} {f'({dur_str})' if dur_str else ''}
                        </div>
                    </div>
                """
        
        if visible:
            st.html(f'<div class="notifications-container">{all_cards_html}</div>')

    except Exception as e:
        if visible:
            st.error(f"Failed to load notifications: {e}")


def render_ingestion_history(ig_service):
    _show_history_fragment(ig_service, visible=True)
