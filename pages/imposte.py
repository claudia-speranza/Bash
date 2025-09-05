import streamlit as st

from menu import build_menu
from sql.dao_list import MOVIMENTI_DAO

build_menu()




with st.spinner('Caricamento ...'):
    imposte_dossier = MOVIMENTI_DAO.get_imposte_dossier()
    imposte_bollo = MOVIMENTI_DAO.get_imposte_di_bollo()

    c1, c2 = st.columns((1, 1))

    c1.subheader('Imposte di bollo')
    c1.dataframe(imposte_bollo, column_config= {
        "data": st.column_config.DateColumn("data", format="DD-MM-YYYY")}, hide_index=True)

    c2.subheader('Imposte sul dossier')
    c2.dataframe(imposte_dossier, column_config= {
        "data_operazione": st.column_config.DateColumn("data", format="DD-MM-YYYY"),
        "dossier": None}, hide_index=True)
