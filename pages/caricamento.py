import numpy as np
import pandas as pd
import streamlit as st

from sql.dao_list import MOVIMENTI_DAO, TITOLI_DAO, ORDINI_DAO
from menu import build_menu
from sql.utils import convert_file_to_table

build_menu()


def adapt_movimenti_df(df: pd.DataFrame) -> pd.DataFrame:
    rename_dict = {"Data_Operazione": "data_operazione",
                   "Data_Valuta": "data_valuta",
                   "Descrizione": "descrizione",
                   "Descrizione_Completa": "descrizione_completa"}
    df = df.rename(columns=rename_dict)
    df['importo'] = df['Entrate'].fillna(0) + df['Uscite'].fillna(0)
    df = df.drop(columns=['Entrate', 'Uscite', 'Stato'])
    df['data_operazione'] = pd.to_datetime(df['data_operazione'], dayfirst=True)
    df['data_valuta'] = pd.to_datetime(df['data_valuta'], dayfirst=True)
    return df


def adapt_ordini_df(df: pd.DataFrame) -> pd.DataFrame:
    rename_dict = {"Operazione": "data_operazione",
                   "Data valuta": "data_valuta",
                   "Isin": "isin",
                   "Descrizione": "descrizione",
                   "Segno": "segno",
                   "Quantita": "quantita",
                   "Divisa": "divisa",
                   "Prezzo": "prezzo",
                   "Cambio": "cambio",
                   "Controvalore": "controvalore",
                   }
    df = df.rename(columns=rename_dict)
    df['data_operazione'] = pd.to_datetime(df['data_operazione'], dayfirst=True)
    df['data_valuta'] = pd.to_datetime(df['data_valuta'], dayfirst=True)
    df['importo'] = df['controvalore'] * df['segno'].map({'A': -1, 'V': 1}).fillna(1).astype(int)

    commissioni = [
        "Commissioni Fondi Sw/Ingr/Uscita",
        "Commissioni Fondi Banca Corrispondente",
        "Spese Fondi Sgr",
        "Commissioni amministrato"
    ]
    conditions = [ df[comm] > 0 for comm in commissioni ]

    df['commissione'] = df[commissioni].fillna(0).sum(axis=1)
    df['tipo_commissione'] = np.select(conditions, commissioni, default="Nessuna")

    df = df.drop(columns=['Titolo','Commissioni Fondi Sw/Ingr/Uscita', 'Commissioni Fondi Banca Corrispondente',
                          'Spese Fondi Sgr', 'Commissioni amministrato'])
    return df


def adapt_titoli_df(df: pd.DataFrame) -> pd.DataFrame:
    print(df.head())

    rename_dict = {"ISIN": "isin",
                   "Titolo": "titolo",
                   "Simbolo": "simbolo",
                   "Mercato": "mercato",
                   "Strumento": "strumento",
                   "Valuta": "valuta"
                   }
    df = df.rename(columns=rename_dict)
    for col in set(df.columns) - set(rename_dict.values()):
        del df[col]
    return df


uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:

    filename = uploaded_file.name

    if filename.startswith('movements') or filename.startswith('movimenti'):
        dataframe = convert_file_to_table(uploaded_file)
        if dataframe is None:
            msg = f'Could not convert {filename} to table'
        else:
            dataframe = adapt_movimenti_df(dataframe)
            result, msg = MOVIMENTI_DAO.insert_from_dataframe(dataframe)
        st.write(msg)

    elif filename.startswith('Lista Titoli') or filename.startswith('ordini'):
        dataframe = convert_file_to_table(uploaded_file)
        if dataframe is None:
            msg = f'Could not convert {filename} to table'
        else:
            dataframe = adapt_ordini_df(dataframe)
            result, msg = ORDINI_DAO.insert_from_dataframe(dataframe)
        st.write(msg)

    elif filename.startswith('portafoglio') or filename.startswith('titoli'):
        dataframe = convert_file_to_table(uploaded_file)
        if dataframe is None:
            msg = f'Could not convert {filename} to table'
        else:
            dataframe = adapt_titoli_df(dataframe)
            result, msg = TITOLI_DAO.insert_from_dataframe(dataframe)
        st.write(msg)

    else:
        st.write(f'Could not understand file origin of {filename} ')
