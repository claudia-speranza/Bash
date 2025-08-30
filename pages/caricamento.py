import pandas as pd
import streamlit as st

from menu import build_menu
from sql.daos.movimenti import Movimenti
from sql.daos.ordini import Ordini
from sql.daos.titoli import Titoli
from sql.utils import convert_file_to_table

build_menu()

MOVIMENTI_DAO = Movimenti()
TITOLI_DAO = Titoli()
ORDINI_DAO = Ordini()


def adapt_movimenti_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"Data_Operazione": "data_operazione",
                            "Data_Valuta": "data_valuta",
                            "Descrizione": "descrizione",
                            "Descrizione_Completa": "descrizione_completa"})
    df['importo'] = df['Entrate'].fillna(0) - df['Uscite'].fillna(0)
    df = df.drop(columns=['Entrate', 'Uscite'])
    df['data_operazione'] = pd.to_datetime(df['data_operazione'], dayfirst=True)
    df['data_valuta'] = pd.to_datetime(df['data_valuta'], dayfirst=True)
    return df


def adapt_ordini_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"Operazione": "data_operazione",
                            "Data valuta": "data_valuta",
                            "Isin": "isin",
                            "Descrizione": "descrizione",
                            "Titolo": "titolo",
                            "Segno": "segno",
                            "Quantita": "quantita",
                            "Divisa": "divisa",
                            "Prezzo": "prezzo",
                            "Cambio": "cambio",
                            "Controvalore": "controvalore",
                            "Commissioni Fondi Sw/Ingr/Uscita": "commissioni_fondi_sw",
                            "Commissioni Fondi Banca Corrispondente": "commissioni_fondi_banca",
                            "Spese Fondi Sgr": "spese_fondi_sgr",
                            "Commissioni amministrato": "commissioni_amministrato"
                            })
    df['data_operazione'] = pd.to_datetime(df['data_operazione'], dayfirst=True)
    df['data_valuta'] = pd.to_datetime(df['data_valuta'], dayfirst=True)
    df['segno'] = df['segno'].map({'A': 1, 'V': -1}).fillna(0).astype(int)
    return df


def adapt_titoli_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename({"Isin": "isin",
                    "Titolo": "titolo",
                    "Simbolo": "simbolo",
                    "Mercato": "mercato",
                    "Strumento": "strumento",
                    "Valuta": "valuta"
                    })
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
