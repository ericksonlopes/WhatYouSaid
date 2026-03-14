"""Content Sources tab renderer."""

from uuid import UUID

import streamlit as st


def _render_header_and_button(services, safe_rerun):
    with st.container(horizontal=True):
        st.header("Content Sources")
        st.space("stretch")

        if st.button("Sync", key="sync_btn"):
            st.rerun()

        if st.button("Add Knowledge", key="add_knowledge_btn", type="primary"):
            try:
                from frontend.dialogs.add_knowledge_dialog import open_add_knowledge
                open_add_knowledge(services, safe_rerun)
            except Exception as e:
                st.error(f"Erro ao abrir diálogo de Add Knowledge: {e}")


def _fetch_content_sources(services):
    cs = services["cs_service"]
    selected_subject_id = st.session_state.get("selected_subject_id")
    
    if not selected_subject_id:
        return []

    try:
        try:
            sid = UUID(selected_subject_id)
        except Exception:
            sid = selected_subject_id
        return cs.list_by_subject(subject_id=sid)
    except Exception as e:
        st.error(f"Error listing content sources: {e}")
        return []


def _build_rows(content_sources, settings):
    table_rows = []
    source_ids = []
    if content_sources:
        for c in content_sources:
            # Main title from database, fallback to ID/Source
            title = getattr(c, 'title', None) or getattr(c, 'external_source', None) or str(getattr(c, 'id', ''))
            ext_source = getattr(c, 'external_source', None) or ""
            
            stype = getattr(c, 'source_type', None)
            if stype is not None:
                try:
                    ctype = stype.value if hasattr(stype, 'value') else str(stype)
                except Exception:
                    ctype = str(stype)
            else:
                ctype = getattr(c, 'mime_type', None) or "application/pdf"
                
            chunks = getattr(c, 'chunks', 0)
            embedding = getattr(c, 'embedding_model', "N/A")
            dims = getattr(c, 'dimensions', 0)
            status = getattr(c, 'processing_status', getattr(c, 'status', 'pending'))
            
            table_rows.append({
                "title": title,
                "external_source": ext_source,
                "type": ctype,
                "chunks": chunks,
                "embedding": embedding,
                "dims": dims,
                "status": str(status).lower(),
            })
            source_ids.append(str(getattr(c, 'id', '')))
    return table_rows, source_ids


def _render_table(table_rows, source_ids, selected_subject_name):
    if not selected_subject_name:
        st.info("Please select a Subject in the sidebar to view content sources.")
        return

    st.caption(f"Showing sources for: **{selected_subject_name}**")

    if not table_rows:
        st.info(f"No content sources found for '{selected_subject_name}'.")
        return

    # Injetar CSS para fazer os componentes nativos parecerem a tabela HTML original
    st.markdown("""
        <style>
        /* Estilo para simular as linhas da tabela */
        .source-row {
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding: 10px 0;
            transition: background 0.2s;
        }
        
        /* Reset total do botão do Streamlit para o título */
        div.stButton > button[kind="secondary"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            color: #e6eef7 !important;
            text-align: left !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: color 0.2s ease, transform 0.1s ease !important;
            min-height: unset !important;
            line-height: 1.4 !important;
            box-shadow: none !important;
        }
        
        /* Efeito de Hover no Título */
        div.stButton > button[kind="secondary"]:hover {
            color: #3b82f6 !important;
            background: transparent !important;
            text-decoration: none !important;
        }
        
        /* Feedback ao clicar */
        div.stButton > button[kind="secondary"]:active {
            transform: translateY(1px);
            color: #2563eb !important;
        }

        /* Ajuste do container do botão para evitar pulos de layout */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
            gap: 0px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header da "Tabela"
    h_cols = st.columns([35, 10, 8, 17, 10, 15, 5])
    headers = ["Source", "Type", "Chunks", "Model", "Dims", "Status", ""]
    for col, header in zip(h_cols, headers):
        if header:
            col.markdown(f'<span style="color: #9aa4ad; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">{header}</span>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)

    # Linhas da "Tabela"
    for i, r in enumerate(table_rows):
        src_id = source_ids[i]
        
        # Container para simular a linha (tr)
        with st.container():
            c_src, c_type, c_chunks, c_model, c_dims, c_status, c_actions = st.columns([35, 10, 8, 17, 10, 15, 5])
            
            with c_src:
                # Botão estilizado como link (Título)
                if st.button(r['title'], key=f"btn_title_{src_id}"):
                    st.session_state["source_id_to_view"] = src_id
                    st.session_state["source_title_to_view"] = r['title']
                    st.rerun()
                st.markdown(f'<span class="source-sub">{r["external_source"]}</span>', unsafe_allow_html=True)
            
            with c_type:
                st.markdown(f'<span class="meta-text">{r["type"].upper()}</span>', unsafe_allow_html=True)
            
            with c_chunks:
                st.markdown(f'<span class="meta-text">{r["chunks"]}</span>', unsafe_allow_html=True)
            
            with c_model:
                raw_emb = r.get('embedding')
                m_name = raw_emb.split('/')[-1] if raw_emb and '/' in raw_emb else (raw_emb or "N/A")
                st.markdown(f'<span class="meta-text" title="{raw_emb or ""}">{m_name}</span>', unsafe_allow_html=True)
            
            with c_dims:
                st.markdown(f'<span class="meta-text">{r["dims"]}</span>', unsafe_allow_html=True)
            
            with c_status:
                s_class = f"badge-{r['status']}" if r['status'] in ['done', 'processing', 'pending', 'error'] else "badge-active"
                st.markdown(f'<span class="badge {s_class}">{r["status"]}</span>', unsafe_allow_html=True)
            
            with c_actions:
                st.markdown('<span class="action-dots">⋮</span>', unsafe_allow_html=True)
            
            # Divisor de linha
            st.markdown("<div style='border-bottom: 1px solid rgba(255,255,255,0.05); margin: 8px 0;'></div>", unsafe_allow_html=True)

    # Footer
    st.caption(f"Total: {len(table_rows)} items")


def render(services, settings, safe_rerun):
    # Header + Add Knowledge button (Keep outside fragment)
    _render_header_and_button(services, safe_rerun)

    chunk_service = services["chunk_service"]

    @st.fragment(run_every="3s")
    def table_fragment():
        content_sources = _fetch_content_sources(services)
        table_rows, source_ids = _build_rows(content_sources, settings)

        selected_subject_name = st.session_state.get("sidebar_selected_subject")
        _render_table(table_rows, source_ids, selected_subject_name)

        # Trigger dialog se houver seleção no session_state
        if "source_id_to_view" in st.session_state:
            sid = st.session_state.pop("source_id_to_view")
            title = st.session_state.pop("source_title_to_view")
            
            from frontend.dialogs.source_chunks_dialog import show_source_chunks_dialog
            show_source_chunks_dialog(sid, title, chunk_service)

    table_fragment()
