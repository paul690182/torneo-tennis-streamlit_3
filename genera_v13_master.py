import streamlit as st
import subprocess
import os

PDF_FILE = "SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf"

# ---------- FUNZIONE GENERAZIONE ----------
def genera_pdf():
    try:
        subprocess.run(["python3", "genera_pdf_adobe.py"], check=True)
        return True
    except Exception as e:
        return str(e)

# ---------- UI STREAMLIT ----------
def mostra_pdf_ui():
    st.divider()
    st.subheader("📄 Generazione PDF V13 MASTER")

    # Pulsante genera
    if st.button("📄 Genera PDF V13 MASTER"):
        result = genera_pdf()

        if result == True:
            st.success("✅ PDF generato!")
        else:
            st.error(f"Errore: {result}")

    # Pulsante download
    if os.path.exists(PDF_FILE):
        with open(PDF_FILE, "rb") as f:
            st.download_button(
                "⬇️ Scarica PDF",
                f,
                file_name="torneo_V13_MASTER.pdf",
                mime="application/pdf"
            )
