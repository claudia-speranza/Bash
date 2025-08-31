from plotly.subplots import make_subplots

from main import movimenti, ordini
from menu import build_menu
import streamlit as st
import plotly.graph_objects as go


build_menu()
imposte_dossier = movimenti.get_imposte_dossier()
imposte_bollo = movimenti.get_imposte_di_bollo()


def plot_imposte_investimenti():
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add investments to primary y-axis
    fig.add_trace(
        go.Scatter(
            x=ordini['DataValuta'],
            y=ordini['EntrateUscite'].cumsum(),
            mode='lines',
            name='Investimenti',
            line=dict(color='#1f77b4', width=2)
        ),
        secondary_y=False  # Use primary y-axis
    )

    # Add taxes to secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=imposte_dossier['Data'],
            y=imposte_dossier['Importo'].abs().cumsum(),
            mode='lines',
            name='Imposte Dossier',
            line=dict(color='#1f4324', width=2)
        ),
        secondary_y=True  # Use secondary y-axis
    )

    # Update layout
    fig.update_layout(
        title='Investimenti e imposte',
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

    # Set x-axis title
    fig.update_xaxes(title_text='Date')

    # Set y-axes titles
    fig.update_yaxes(title_text='Investimenti Cumulativo', secondary_y=False)
    fig.update_yaxes(title_text='Imposte Dossier Cumulativo', secondary_y=True)

    st.plotly_chart(fig)

with st.spinner('Caricamento ...'):
    c1, c2, c3 = st.columns((1, 1, 1))

    c1.subheader('Imposte di bollo')
    c1.dataframe(imposte_bollo, column_config= {
        "Data": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
        "DataRef": st.column_config.DateColumn("DataRef", format="DD-MM-YYYY")}, hide_index=True)

    c2.subheader('Imposte sul dossier')
    c2.dataframe(imposte_dossier, column_config= {
        "Data": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
        "Dossier": None}, hide_index=True)

    with c3:
        plot_imposte_investimenti()