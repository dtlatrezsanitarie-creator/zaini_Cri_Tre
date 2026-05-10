import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Logistica CRI Treviglio", page_icon="🚑", layout="wide")

# Titolo Formale
st.title("🚑 Gestione Logistica Dinamica - CRI Treviglio")
st.markdown("---")

# 1. INIZIALIZZAZIONE DATI ZAINI
if 'db_zaini' not in st.session_state:
    st.session_state.db_zaini = pd.DataFrame([
        {"ID": "ZAINO_3ì01", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "ZAINO_3ì02", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "ZAINO_3ì03", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "ZAINO_3ì04", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
    ])

# 2. INIZIALIZZAZIONE DATI DAE
if 'db_dae' not in st.session_state:
    st.session_state.db_dae = pd.DataFrame([
        {"ID": "DAE_01", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "DAE_02", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "DAE_03", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "DAE_04", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
    ])

mezzi_bg = ["BG 11-24", "BG 11-25", "BG 11-26", "BG 11-27", "BG 11-35", "Postazione Fissa", "Zaino Appiedati"]

# Sidebar
st.sidebar.header("Responsabile Logistica")
st.sidebar.write("**Simone Putelli**")
st.sidebar.info("Sistema di tracciamento asset circolanti (Zaini e DAE).")

# --- SEZIONE ZAINI ---
st.header("📦 Monitoraggio Zaini (3ì)")
cols_zaini = st.columns(2)

for index, row in st.session_state.db_zaini.iterrows():
    with cols_zaini[index % 2]:
        colore = "green" if row['Stato'] == "In Magazzino" else "red"
        st.markdown(f"### :{colore}[{row['ID']}]")
        st.write(f"**Ubicazione:** {row['Mezzo']}")
        st.caption(f"Ultimo: {row['Aggiornato']}")

        if row['Stato'] == "In Magazzino":
            m_scelto = st.selectbox(f"Assegna {row['ID']}:", mezzi_bg, key=f"z_{row['ID']}")
            if st.button(f"CARICA {row['ID']}", type="primary"):
                st.session_state.db_zaini.at[index, 'Stato'] = "In Servizio"
                st.session_state.db_zaini.at[index, 'Mezzo'] = m_scelto
                st.session_state.db_zaini.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                st.rerun()
        else:
            if st.button(f"SCARICA {row['ID']} IN MAGAZZINO"):
                st.session_state.db_zaini.at[index, 'Stato'] = "In Magazzino"
                st.session_state.db_zaini.at[index, 'Mezzo'] = "-"
                st.session_state.db_zaini.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                st.rerun()
        st.markdown("---")

st.markdown("<br>", unsafe_allow_html=True)

# --- SEZIONE DAE ---
st.header("⚡ Monitoraggio DAE")
cols_dae = st.columns(2)

for index, row in st.session_state.db_dae.iterrows():
    with cols_dae[index % 2]:
        colore_dae = "green" if row['Stato'] == "In Magazzino" else "red"
        st.markdown(f"### :{colore_dae}[{row['ID']}]")
        st.write(f"**Ubicazione:** {row['Mezzo']}")
        st.caption(f"Ultimo: {row['Aggiornato']}")

        if row['Stato'] == "In Magazzino":
            m_dae_scelto = st.selectbox(f"Assegna {row['ID']}:", mezzi_bg, key=f"d_{row['ID']}")
            if st.button(f"CARICA {row['ID']}", type="primary", key=f"btn_d_{row['ID']}"):
                st.session_state.db_dae.at[index, 'Stato'] = "In Servizio"
                st.session_state.db_dae.at[index, 'Mezzo'] = m_dae_scelto
                st.session_state.db_dae.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                st.rerun()
        else:
            if st.button(f"SCARICA {row['ID']} IN MAGAZZINO", key=f"btn_s_{row['ID']}"):
                st.session_state.db_dae.at[index, 'Stato'] = "In Magazzino"
                st.session_state.db_dae.at[index, 'Mezzo'] = "-"
                st.session_state.db_dae.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                st.rerun()
        st.markdown("---")
