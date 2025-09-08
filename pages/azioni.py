from components.tables_utils import style_dataframe
from menu import build_menu
import streamlit as st

from sql.dao_list import TITOLI_DAO, ORDINI_DAO
from sql.daos.ordini import analyze_orders_df
from sql.models.titoli import TitoliModel

build_menu()


def build_titolo_table(titolo: TitoliModel):
    st.subheader('Dettagli titolo')
    st.markdown(f"Isin: **{titolo.isin}**  \n"
                f"Titolo: **{titolo.titolo}**  \n"
                f"Simbolo: **{titolo.simbolo}**  \n"
                f"Mercato: **{titolo.mercato}**  \n"
                f"Strumento: **{titolo.strumento}**  \n"
                f"Valuta: **{titolo.valuta}**  \n")

    st.subheader('Ordini associati')
    ordini_df = ORDINI_DAO.get_by_isin(titolo.isin)
    ordini_metrics = analyze_orders_df(ordini_df)

    ordini_df_styled = style_dataframe(ordini_df)
    st.dataframe(ordini_df_styled,
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
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"Quantita attiva: **{ordini_metrics['quantita']}**  \n"
                    f"Prezzo medio di acquisto: **{ordini_metrics['prezzo_medio'] }€**  \n"
                    f"Totale commissioni: **{ordini_metrics['commissioni']}€**  \n")
    with col2:
        data_chart = ordini_df[['importo']].copy()
        valore = round(ordini_metrics['quantita']*ordini_metrics['prezzo_medio']+ordini_metrics['incassi_netti'], 2)
        st.metric(
            "Valore", f"{valore} €",  f"{ordini_metrics['incassi_netti']} €", chart_data=data_chart, chart_type="area", border=True
        )

with st.spinner('Caricamento ...'):
    all_titoli = TITOLI_DAO.get_azioni()
    option = st.selectbox(
        label='Informazioni dettagliate su titolo',
        placeholder="Seleziona titolo...",
        options=(all_titoli),
        format_func=lambda t: t.titolo,
        index=None
    )
    if option:
        build_titolo_table(option)