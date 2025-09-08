from components.tables_utils import style_dataframe
from menu import build_menu
import streamlit as st

from sql.dao_list import TITOLI_DAO, ORDINI_DAO
from sql.models.titoli import TitoliModel

build_menu()


def build_titolo_table(titolo: TitoliModel):
    st.subheader('Dettagli obbligazione')
    st.markdown(f"Isin: **{titolo.isin}**  ")
    st.markdown(f"Valuta: **{titolo.valuta}**  ")

    st.subheader('Ordini associati')
    ordini_df = style_dataframe(ORDINI_DAO.get_by_isin(titolo.isin))
    st.dataframe(ordini_df,
                 hide_index=True, width='stretch',
                 column_order=("data_operazione", "quantita", "prezzo", "valuta" "controvalore", "importo", "commissione", "tipo_commissione"),
                 column_config={
                    "data_operazione": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
                    "quantita": st.column_config.NumberColumn("Quantità", format="plain"),
                    "prezzo": st.column_config.NumberColumn("Prezzo", format="%.2f"),
                    "valuta": st.column_config.TextColumn("Valuta"),
                    "importo": st.column_config.NumberColumn("Importo", format="euro"),
                    "commissione": st.column_config.NumberColumn("Commissione", format="%.2f"),
                    "tipo_commissione": st.column_config.TextColumn("Tipo commissione")
                 })

with st.spinner('Caricamento ...'):
    all_titoli = TITOLI_DAO.get_obbligazioni()
    option = st.selectbox(
        label='Informazioni dettagliate su obbligazione',
        placeholder="Seleziona obbligazione...",
        options=(all_titoli),
        format_func=lambda t: t.titolo,
        index=None
    )
    if option:
        build_titolo_table(option)