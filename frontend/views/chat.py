"""Chat view for interacting with the knowledge base."""

import streamlit as st
from frontend.utils.services import init_basic_services, list_subjects

def render_chat_view():
    st.title("💬 Knowledge Chat")
    st.caption("Ask questions about your ingested content.")
    
    st.markdown("---")

    # Fetch all available knowledge subjects
    services = init_basic_services()
    ks_service = services["ks_service"]
    all_subjects = list_subjects(ks_service)
    subject_names = [s.name for s in all_subjects] if all_subjects else []

    # Initialize empty selection if not present
    if "chat_selected_knowledge" not in st.session_state:
        st.session_state["chat_selected_knowledge"] = []

    # Knowledge selection
    selected_knowledge = st.multiselect(
        "Select Knowledge Base(s)",
        options=subject_names,
        key="chat_selected_knowledge",
        help="Choose which subjects to include in the chat context."
    )

    st.markdown("---")
    
    # Placeholder for Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Context info for debugging/future use
        context_info = f" (Context: {', '.join(selected_knowledge) if selected_knowledge else 'None'})"
        response = f"Echo: {prompt}\n\n{context_info}\n\n(Chat integration with RAG is coming soon!)"
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
