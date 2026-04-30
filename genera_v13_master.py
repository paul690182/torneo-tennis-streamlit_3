import subprocess
import os

if st.button("📄 Genera PDF V13 MASTER"):
    try:
        subprocess.run(["python", "genera_pdf_adobe.py"], check=True)
        st.success("✅ PDF generato!")
    except Exception as e:
        st.error(f"Errore: {e}")

if os.path.exists("SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf"):
    with open("SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf", "rb") as f:
        st.download_button(
            "⬇️ Scarica PDF",
            f,
            file_name="torneo_V13_MASTER.pdf",
            mime="application/pdf"
        )
