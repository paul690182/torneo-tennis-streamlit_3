import streamlit as st

st.set_page_config(page_title="Torneo Tennis", layout="wide")

st.title("🏆 Torneo Tennis")

menu = st.sidebar.radio("Naviga", ["Inserisci Risultato", "Classifica"])

if menu == "Inserisci Risultato":
    st.write("Vai alla pagina Inserisci Risultato nel menu Pages.")
    st.write("Oppure clicca su 'pages/inserisci_risultato.py'.")
elif menu == "Classifica":
    from supabase import create_client
    from supabase_config import SUPABASE_URL, SUPABASE_KEY

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    torneo = st.selectbox("Seleziona torneo", ["Advanced", "Top"], key="torneo_classifica")
    tabella_classifica = "classifica_advanced" if torneo == "Advanced" else "classifica_top"

    st.subheader(f"Classifica {torneo}")
    classifica = supabase.table(tabella_classifica).select("*").order("punti", desc=True).execute()
    st.table(classifica.data)
