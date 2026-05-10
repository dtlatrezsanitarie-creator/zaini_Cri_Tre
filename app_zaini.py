import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Logistica CRI Treviglio", page_icon="🚑", layout="wide")

# Titolo Formale
st.title("🚑 Gestione Dinamica Zaini - CRI Treviglio")
st.markdown("---")

# Inizializzazione dati (Stato persistente nella sessione)
if 'db_zaini' not in st.session_state:
    st.session_state.db_zaini = pd.DataFrame([
        {"ID": "ZAINO_3ì01", "Stato": "In Magazzino", "Mezzo": "-", "Ultimo Spostamento": "-"},
        {"ID": "ZAINO_3ì02", "Stato": "In Magazzino", "Mezzo": "-", "Ultimo Spostamento": "-"},
        {"ID": "ZAINO_3ì03", "Stato": "In Magazzino", "Mezzo": "-", "Ultimo Spostamento": "-"},
        {"ID": "ZAINO_3ì04", "Stato": "In Magazzino", "Mezzo": "-", "Ultimo Spostamento": "-"},
    ])

mezzi_bg = ["BG 11-24", "BG 11-25", "BG 11-26", "BG 11-27", "BG 11-35"]

# Sidebar per info
st.sidebar.header("Responsabile Logistica")
st.sidebar.write("**Simone Putelli**")
st.sidebar.info("Sistema di tracciamento zaini circolanti per riduzione sprechi e controllo scadenze.")

# Layout a colonne per gli zaini
cols = st.columns(2)

for index, row in st.session_state.db_zaini.iterrows():
    # Scegliamo la colonna (alternata)
    with cols[index % 2]:
        with st.container():
            # Colore in base allo stato
            colore = "green" if row['Stato'] == "In Magazzino" else "red"
            st.markdown(f"### :{colore}[{row['ID']}]")
            st.write(f"**Stato attuale:** {row['Stato']}")
            st.write(f"**Ubicazione:** {row['Mezzo']}")
            st.caption(f"Ultimo aggiornamento: {row['Ultimo Spostamento']}")

            if row['Stato'] == "In Magazzino":
                mezzo_scelto = st.selectbox(f"Assegna a mezzo:", mezzi_bg, key=f"sel_{row['ID']}")
                if st.button(f"CARICA {row['ID']}", type="primary"):
                    st.session_state.db_zaini.at[index, 'Stato'] = "In Servizio"
                    st.session_state.db_zaini.at[index, 'Mezzo'] = mezzo_scelto
                    st.session_state.db_zaini.at[index, 'Ultimo Spostamento'] = datetime.now().strftime("%d/%m %H:%M")
                    st.rerun()
            else:
                if st.button(f"SCARICA {row['ID']} IN MAGAZZINO"):
                    st.session_state.db_zaini.at[index, 'Stato'] = "In Magazzino"
                    st.session_state.db_zaini.at[index, 'Mezzo'] = "-"
                    st.session_state.db_zaini.at[index, 'Ultimo Spostamento'] = datetime.now().strftime("%d/%m %H:%M")
                    st.rerun()
        st.markdown("---")

# Tabella di riepilogo in fondo (visibile solo a te per controllo rapido)
with st.expander("Visualizza Tabella Dati Completa"):
    st.table(st.session_state.db_zaini)