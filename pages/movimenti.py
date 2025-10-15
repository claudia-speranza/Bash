import plotly.graph_objects as go
import streamlit as st

from components.tables_utils import build_operation_table
from menu import build_menu
from sql.dao_list import MOVIMENTI_DAO, ORDINI_DAO
from sql.models.movimenti import MovimentiCategory, MovimentiModel

build_menu()


def barchart_entrate_uscite_ext():
    fig = go.Figure()
    monthly_sum_in = MOVIMENTI_DAO.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_entrata() & MovimentiModel.is_category(MovimentiCategory.Bonifici)) )
    monthly_sum_out = MOVIMENTI_DAO.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_uscita() & MovimentiModel.is_category(MovimentiCategory.Bonifici)) )

    # Add income bars
    fig.add_trace(go.Bar(
        x=monthly_sum_in['month'],
        y=monthly_sum_in['total'],
        name='Entrate',
        marker_color='#2ecc71'
    ))

    # Add expense bars
    fig.add_trace(go.Bar(
        x=monthly_sum_out['month'],
        y=monthly_sum_out['total'],
        name='Uscite',
        marker_color='#ff0000'
    ))

    # Update layout
    fig.update_layout(
        title='Movimenti conti esterni',
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

def barchart_entrate_uscite_portafoglio():
    fig = go.Figure()
    monthly_sum_in = MOVIMENTI_DAO.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_entrata() & MovimentiModel.is_category(MovimentiCategory.CompravenditaTitoli)))
    monthly_sum_out = MOVIMENTI_DAO.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_uscita() & MovimentiModel.is_category(MovimentiCategory.CompravenditaTitoli)))

    # Add income bars
    fig.add_trace(go.Bar(
        x=monthly_sum_in['month'],
        y=monthly_sum_in['total'],
        name='Entrate',
        marker_color='#2ecc71'
    ))

    # Add expense bars
    fig.add_trace(go.Bar(
        x=monthly_sum_out['month'],
        y=monthly_sum_out['total'],
        name='Uscite',
        marker_color='#ff0000'
    ))

    # Update layout
    fig.update_layout(
        title='Movimenti portafoglio',
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


def create_badges():
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    c1.metric(label='Bonifici', value=f'{MOVIMENTI_DAO.sum_by_category(MovimentiCategory.Bonifici)} €')
    c2.metric(label='CompravenditaTitoli', value=f'{MOVIMENTI_DAO.sum_by_category(MovimentiCategory.CompravenditaTitoli)} €')
    c3.metric(label='Tasse', value=f'{MOVIMENTI_DAO.sum_by_category(MovimentiCategory.Tasse)} €')
    c4.metric(label='SpeseConto', value=f'{MOVIMENTI_DAO.sum_by_category(MovimentiCategory.SpeseConto)} €')


with st.spinner('Caricamento ...'):
    movimenti_df = MOVIMENTI_DAO.get_in_timerange(as_dataframe=True)
    ordini_df = ORDINI_DAO.get_in_timerange(as_dataframe=True)
    create_badges()
    col1, col2 = st.columns([2, 1])

    with col1:
        st.image('components/schema.svg', width='stretch')
        option = st.selectbox(
            "Elenco movimenti per categoria",
            (MovimentiCategory.list_values()),
        )

        build_operation_table(MOVIMENTI_DAO.get_by_category(category=MovimentiCategory(option)))
    with col2:
        barchart_entrate_uscite_ext()
        barchart_entrate_uscite_portafoglio()

