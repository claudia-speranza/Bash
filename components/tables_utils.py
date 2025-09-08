import streamlit as st


def build_operation_table(df):
    st.dataframe(df, hide_index=True, width='stretch',
                 column_order=("data_operazione", "importo", "descrizione_completa"),
                 column_config={
                     "data_operazione": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
                     "importo": st.column_config.NumberColumn("Importo", format='euro'),
                     "descrizione_completa": st.column_config.TextColumn("Descrizione completa"),
                 })


def style_dataframe(df):
    def color_rows(row):
        if row['importo'] < 0:
            return ['background-color: #ffebee'] * len(row)  # Light red
        elif row['importo'] > 0:
            return ['background-color: #e8f5e8'] * len(row)  # Light green
        else:
            return [''] * len(row)  # No color for zero values

    return df.style.apply(color_rows, axis=1)
