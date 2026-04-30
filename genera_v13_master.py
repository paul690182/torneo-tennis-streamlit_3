import streamlit as st
import subprocess
import os

PDF_FILE = "SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf"

def genera_pdf():
    try:
        result = subprocess.run(
            ["python3", "genera_pdf_adobe.py"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True
        else:
            return result.stderr

    except Exception as e:
        return str(e)

def mostra_pdf_ui():
    st.divider()
    st.subheader("📄 Generazione PDF V13 MASTER")

    if st.button("📄 Genera PDF V13 MASTER"):
        result = genera_pdf()

        if result == True:
            st.success("✅ PDF generato!")
        else:
            st.error("❌ Errore durante la generazione PDF:")
            st.code(result)

    if os.path.exists(PDF_FILE):
        with open(PDF_FILE, "rb") as f:
            st.download_button(
                "⬇️ Scarica PDF",
                f,
                file_name="torneo_V13_MASTER.pdf",
                mime="application/pdf"
            )
