import argparse

import streamlit as st

parser = argparse.ArgumentParser()
parser.add_argument('--data-path', default='./data', help='path to csv file containing bank incomes and expenses')

args = parser.parse_args()


if __name__ == '__main__':
    # st.switch_page("login.py")
    st.set_page_config(layout="wide")
    st.switch_page('pages/home.py')