import pandas as pd
import streamlit as st

from menu import build_menu
from sql.dao_list import MOVIMENTI_DAO
from sql.models.movimenti import MovimentiCategory

build_menu()


def get_imposte_di_bollo(imposte_df) -> pd.DataFrame:
    """Get account stamp duty taxes."""
    imposte_df = imposte_df[imposte_df['descrizione']=='Imposta bollo conto corrente']
    imposte_df['data'] = (
        imposte_df['descrizione_completa']
        .str.extract(r'(\d{2}\.\d{2}\.\d{4})', expand=False)
        .pipe(lambda x: pd.to_datetime(x, format='%d.%m.%Y', errors='coerce'))
    )
    imposte_df['importo'] = -imposte_df['importo']
    imposte_df = imposte_df[['data', 'importo']]
    return imposte_df


def get_imposte_dossier(imposte_df) -> pd.DataFrame:
    """Get dossier stamp duty taxes."""

    def extract_dossier(descrizione_completa):
        if pd.isna(descrizione_completa) or not descrizione_completa:
            return None
        parts = descrizione_completa.split(' ')
        return parts[-1] if parts else None
    imposte_df = imposte_df[imposte_df['descrizione']=='Imposta bollo dossier titoli']
    imposte_df['dossier'] = imposte_df['descrizione_completa'].apply(extract_dossier)
    imposte_df['importo'] = -imposte_df['importo']
    imposte_df = imposte_df[['data_operazione', 'importo', 'dossier']]
    return imposte_df

def get_trattenute(imposte_df):
    imposte_df = imposte_df[
            imposte_df['descrizione'].str.lower().str.contains('riten', na=False) |
            (imposte_df['descrizione'] == 'Imposta Sostitutiva Capit.GAIN')
        ]
    imposte_df['importo'] = -imposte_df['importo']
    imposte_df = imposte_df[['data_operazione', 'importo', 'descrizione']]
    return imposte_df


with st.spinner('Caricamento ...'):
    imposte_df = MOVIMENTI_DAO.get_by_category(MovimentiCategory.Tasse)

    imposte_bollo = get_imposte_di_bollo(imposte_df)
    totale_imposte_bollo = sum(imposte_bollo['importo'])

    imposte_dossier = get_imposte_dossier(imposte_df)
    totale_imposte_dossier = sum(imposte_dossier['importo'])

    trattenute = get_trattenute(imposte_df)
    totale_trattenute = sum(trattenute['importo'])

    c1, c2, c3 = st.columns((1, 1, 1))

    c1.subheader('Imposte di bollo')
    c1.metric(label='Totale', value=f'{round(totale_imposte_bollo, 2)} €')
    c1.dataframe(imposte_bollo, column_config= {
        "data": st.column_config.DateColumn("data", format="DD-MM-YYYY")}, hide_index=True)

    c2.subheader('Imposte sul dossier')
    c2.metric(label='Totale', value=f'{round(totale_imposte_dossier, 2)} €')
    c2.dataframe(imposte_dossier, column_config= {
        "data_operazione": st.column_config.DateColumn("data", format="DD-MM-YYYY"),
        "dossier": None}, hide_index=True)

    c3.subheader('Trattenute')
    c3.metric(label='Totale', value=f'{round(totale_trattenute, 2)} €')
    c3.dataframe(trattenute, column_config= {
        "data_operazione": st.column_config.DateColumn("data", format="DD-MM-YYYY")}, hide_index=True)

