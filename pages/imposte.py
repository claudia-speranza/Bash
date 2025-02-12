from main import movimenti
from menu import build_menu
import streamlit as st


build_menu()


with st.spinner('Caricamento ...'):
    c1, c2, c3 = st.columns((1, 1, 1))

    c1.subheader('Imposte di bollo')
    c1.dataframe(movimenti.get_imposte_di_bollo(), column_config= {
        "Data": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
        "DataRef": st.column_config.DateColumn("DataRef", format="DD-MM-YYYY")}, hide_index=True)

    c2.subheader('Imposte sul dossier')
    c2.dataframe(movimenti.get_imposte_dossier(), column_config= {
        "Data": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
        "Dossier": None}, hide_index=True)

    c2.subheader('Imposte sul reddito')
    c2.dataframe(movimenti.get_imposte_dossier(), column_config={
        "Data": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
        "Dossier": None}, hide_index=True)