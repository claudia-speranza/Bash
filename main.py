import argparse
import os
from datetime import datetime

import streamlit as st

from dataframes.movimenti import Movimenti as MovimentiExcel
from dataframes.ordini import Ordini as OrdiniExcel
from dataframes.titoli import Titoli as TitoliExcel

from sql.daos.movimenti import Movimenti
from sql.daos.ordini import Ordini
from sql.daos.titoli import Titoli

parser = argparse.ArgumentParser()
parser.add_argument('--data-path', default='./data', help='path to csv file containing bank incomes and expenses')

args = parser.parse_args()

ordini = OrdiniExcel.from_excel(os.path.join(args.data_path, 'ordini.xlsx'))
movimenti = MovimentiExcel.from_excel(os.path.join(args.data_path, 'movimenti.xlsx'))
titoli = TitoliExcel.from_excel(os.path.join(args.data_path, 'titoli.xlsx'))

today = datetime.now()




if __name__ == '__main__':
    # st.switch_page("login.py")
    st.set_page_config(layout="wide")
    st.switch_page('pages/home.py')