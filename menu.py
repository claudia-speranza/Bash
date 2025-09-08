import streamlit as st

def build_menu():
    st.set_page_config(layout="wide")
    st.markdown(
        f'''
            <style>
                .sidebar .sidebar-content {{
                    width: 50 px;
                }}
            </style>
        ''',
        unsafe_allow_html=True
    )
    st.sidebar.title("Bank Dashboard")

    st.sidebar.page_link("pages/home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/movimenti.py", label="Movimenti")
    st.sidebar.page_link("pages/azioni.py", label="Azioni")
    st.sidebar.page_link("pages/obbligazioni.py", label="Obbligazioni")
    st.sidebar.page_link("pages/pac.py", label="PAC", disabled=True)
    st.sidebar.page_link("pages/imposte.py", label="Imposte")
    st.sidebar.page_link("pages/caricamento.py", label="Caricamento Dati")

