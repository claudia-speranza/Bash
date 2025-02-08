from datetime import timedelta

import plotly.graph_objects as go
import streamlit as st

from main import movimenti, ordini, today
from menu import build_menu

build_menu()

def create_basic_info():
    m1 = round(movimenti.liquidita, 2)
    m2 = round(movimenti.filtered(today - timedelta(days=30)).liquidita, 2)
    o1 = round(ordini.investimenti, 2)
    o2 = round(ordini.filtered(today - timedelta(days=30)).investimenti, 2)

    c1, c2, c3 = st.columns((1, 1, 1))
    c1.metric(label='Liquidità', value=f'{m1} €',
              delta=f'{m2} ultimi 30 giorni')
    c1.metric(label='Investimenti', value=f'{o1} €',
              delta=f'{o2} ultimi 30 giorni')


    c3.metric(label='Patrimonio', value=f'{round(m1 + o1, 2)} €',
              delta=f'{round(m2 + o2, 2)} ultimi 30 giorni')


def barchart_entrate_uscite():
    fig = go.Figure()
    monthly_sums = movimenti.get_monthly_in_and_out()

    # Add income bars
    fig.add_trace(go.Bar(
        x=monthly_sums['Data'],
        y=monthly_sums['Entrate'],
        name='Entrate',
        marker_color='#2ecc71'
    ))

    # Add expense bars
    fig.add_trace(go.Bar(
        x=monthly_sums['Data'],
        y=monthly_sums['Uscite'],
        name='Uscite',
        marker_color='#ff0000'
    ))

    # Update layout
    fig.update_layout(
        title='Entrate e uscite mensili',
        xaxis_title='Mese',
        yaxis_title='Totale',
        barmode='group',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    st.plotly_chart(fig)

def plot_liquidita_investimenti():
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ordini['Data'],
            y=ordini['EntrateUscite'].cumsum(),
            mode='lines',
            name='Investimenti',
            line=dict(color='#1f77b4', width=2)
        )
    )
    fig.add_trace(
        go.Scatter(
            x=movimenti['Data'],
            y=movimenti['EntrateUscite'].cumsum(),
            mode='lines',
            name='Liquidita',
            line=dict(color='#1f4324', width=2)
        )
    )

    # Update layout
    fig.update_layout(
        title='Investimenti e liquidita',
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



with st.spinner('Caricamento ...'):

    create_basic_info()

    col1, col2 = st.columns(2)
    with col1:
        barchart_entrate_uscite()
    with col2:
        plot_liquidita_investimenti()
