import argparse
import os
from datetime import datetime

import streamlit as st

from dataframes.movimenti import Movimenti
from dataframes.ordini import Ordini
from dataframes.titoli import Titoli
from sql.manager import DBInstance

parser = argparse.ArgumentParser()
parser.add_argument('--data-path', default='./data', help='path to csv file containing bank incomes and expenses')

args = parser.parse_args()

ordini = Ordini.from_excel(os.path.join(args.data_path, 'ordini.xlsx'))
movimenti = Movimenti.from_excel(os.path.join(args.data_path, 'movimenti.xlsx'))
titoli = Titoli.from_excel(os.path.join(args.data_path, 'titoli.xlsx'))

today = datetime.now()


if __name__ == '__main__':
    # st.switch_page("login.py")
    st.set_page_config(layout="wide")
    st.switch_page('pages/home.py')