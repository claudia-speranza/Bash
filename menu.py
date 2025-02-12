import streamlit as st

def build_menu():
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
    st.sidebar.page_link("pages/azioni.py", label="Azioni")
    st.sidebar.page_link("pages/obbligazioni.py", label="Obbligazioni", disabled=True)
    st.sidebar.page_link("pages/pac.py", label="PAC", icon="2️⃣", disabled=True)
    st.sidebar.page_link("pages/imposte.py", label="Imposte")
