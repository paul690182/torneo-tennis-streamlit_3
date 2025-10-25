
import streamlit as st

# Simulazione dati Supabase
classifica = {'data': [{'Giocatore': 'Mario', 'Punti': 100}, {'Giocatore': 'Luigi', 'Punti': 90}]}
storico = {'data': [{'Match': 'Mario vs Luigi', 'Risultato': '2-1'}]}

if classifica and 'data' in classifica:
    st.table(classifica['data'])

if storico and 'data' in storico:
    st.table(storico['data'])
