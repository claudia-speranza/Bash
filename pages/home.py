from datetime import timedelta, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from menu import build_menu
from sql.dao_list import MOVIMENTI_DAO, ORDINI_DAO, TITOLI_DAO

build_menu()



def create_basic_info(titoli_df):
    today = datetime.now()

    m1 = MOVIMENTI_DAO.get_liquidita()
    m2 = MOVIMENTI_DAO.get_liquidita(today - timedelta(days=30))

    o1 = sum(titoli_df.loc[titoli_df['quantita'] > 0]['valore_di_carico'])

    c1, c2, c3 = st.columns((1, 1, 1))
    c1.metric(label='Liquidità', value=f'{m1} €',
              delta=f'{m2} ultimi 30 giorni')
    c1.metric(label='Valore Investimenti', value=f'{o1} €',)

    c2.metric(label='Patrimonio', value=f'{round(m1 + o1, 2)} €')

    incassi_netti = sum(titoli_df['incassi_netti'])
    capitale_investito = sum(titoli_df['quantita_venduta'] * titoli_df['prezzo_medio_vendita'])
    c3.metric(label='Incassi Netti', value=f'{round(incassi_netti, 2)} €')
    if capitale_investito > 0:
        c3.metric(label='Rendimento', value=f'{round(incassi_netti/capitale_investito*100, 2)} %')




def plot_liquidita_investimenti(ordini_df, movimenti_df):
    fig = go.Figure()

    # Get cumulative sums for each dataset
    investimenti_cum = -ordini_df['importo'].cumsum()
    liquidita_cum = movimenti_df['importo'].cumsum()

    # Add investment trace
    fig.add_trace(
        go.Scatter(
            x=ordini_df['data_operazione'],
            y=investimenti_cum,
            mode='lines',
            name='Investimenti',
            line=dict(color='#1f77b4', width=2)
        )
    )

    # Add liquidity trace
    fig.add_trace(
        go.Scatter(
            x=movimenti_df['data_operazione'],
            y=liquidita_cum,
            mode='lines',
            name='Liquidita',
            line=dict(color='#1f4324', width=2)
        )
    )

    # Create total amount data
    # Since the two datasets might have different dates, we need to handle this properly
    # Combine dates from both datasets
    all_dates = pd.concat([
        pd.DataFrame({'Date': ordini_df['data_operazione'], 'Type': 'Investimenti', 'Value': investimenti_cum}),
        pd.DataFrame({'Date': movimenti_df['data_operazione'], 'Type': 'Liquidita', 'Value': liquidita_cum})
    ])

    # Group by date and pivot to get values for each type
    pivot_df = all_dates.pivot_table(index='Date', columns='Type', values='Value', aggfunc='last')

    # Forward fill missing values (to carry forward last known value)
    pivot_df = pivot_df.bfill()

    # Calculate total (sum of both columns)
    pivot_df['Total'] = pivot_df['Investimenti'] + pivot_df['Liquidita']

    # Add total trace
    fig.add_trace(
        go.Scatter(
            x=pivot_df.index,
            y=pivot_df['Total'],
            mode='lines',
            name='Patrimonio',
            line=dict(color='#ff7f0e', width=3, dash='dot')  # Orange dotted line for total
        )
    )

    # Update layout
    fig.update_layout(
        title='Investimenti e liquidità',
        xaxis_title='Date',
        yaxis_title='Cumulativo',
        showlegend=True,
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.99
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    st.plotly_chart(fig)

def titoli_attivi_table(titoli_df):
    titoli_df = titoli_df.loc[titoli_df['quantita'] > 0]
    titoli_df = titoli_df[['isin', 'titolo', 'quantita', 'strumento', 'valore_di_carico']]
    st.dataframe(titoli_df, width='stretch', hide_index=True,
                 column_config={
                     "isin": st.column_config.TextColumn("Isin"),
                     "titolo": st.column_config.TextColumn("Titolo"),
                     "quantita": st.column_config.NumberColumn("Quantità", format="%d"),
                     "strumento": st.column_config.TextColumn("Strumento"),
                     "valore_di_carico": st.column_config.NumberColumn("Valore", format=('euro'))}
                 )

with st.spinner('Caricamento ...'):
    titoli_df = TITOLI_DAO.get_full_info()

    movimenti_df = MOVIMENTI_DAO.get_in_timerange(as_dataframe=True)
    ordini_df = ORDINI_DAO.get_in_timerange(as_dataframe=True)

    create_basic_info(titoli_df)
    st.subheader('Titoli attivi nel portafoglio')
    titoli_attivi_table(titoli_df)
    plot_liquidita_investimenti(ordini_df, movimenti_df)
