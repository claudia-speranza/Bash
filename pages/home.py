from datetime import timedelta

import pandas as pd
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

    # Get cumulative sums for each dataset
    investimenti_cum = ordini['EntrateUscite'].cumsum()
    liquidita_cum = movimenti['EntrateUscite'].cumsum()

    # Add investment trace
    fig.add_trace(
        go.Scatter(
            x=ordini['DataValuta'],
            y=investimenti_cum,
            mode='lines',
            name='Investimenti',
            line=dict(color='#1f77b4', width=2)
        )
    )

    # Add liquidity trace
    fig.add_trace(
        go.Scatter(
            x=movimenti['Data'],
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
        pd.DataFrame({'Date': ordini['DataValuta'], 'Type': 'Investimenti', 'Value': investimenti_cum}),
        pd.DataFrame({'Date': movimenti['Data'], 'Type': 'Liquidita', 'Value': liquidita_cum})
    ])

    # Group by date and pivot to get values for each type
    pivot_df = all_dates.pivot_table(index='Date', columns='Type', values='Value', aggfunc='last')

    # Forward fill missing values (to carry forward last known value)
    pivot_df = pivot_df.fillna(method='ffill')

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



with st.spinner('Caricamento ...'):

    create_basic_info()

    col1, col2 = st.columns(2)
    with col1:
        barchart_entrate_uscite()
    with col2:
        plot_liquidita_investimenti()
