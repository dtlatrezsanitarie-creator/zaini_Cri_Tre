import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Logistica CRI Treviglio", page_icon="🚑", layout="wide")

# --- INIZIALIZZAZIONE DATI (PERSISTENTI NELLA SESSIONE) ---

# 1. Database Zaini
if 'db_zaini' not in st.session_state:
    st.session_state.db_zaini = pd.DataFrame([
        {"ID": "ZAINO_3ì01", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "ZAINO_3ì02", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "ZAINO_3ì03", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "ZAINO_3ì04", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
    ])

# 2. Database DAE
if 'db_dae' not in st.session_state:
    st.session_state.db_dae = pd.DataFrame([
        {"ID": "DAE_01", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "DAE_02", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "DAE_03", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
        {"ID": "DAE_04", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"},
    ])

# 3. Database Noleggi (Carrozzine e Stampelle)
if 'db_noleggi' not in st.session_state:
    st.session_state.db_noleggi = pd.DataFrame([
        {"ID": "CARR_01", "Tipo": "Carrozzina", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "CARR_02", "Tipo": "Carrozzina", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "CARR_03", "Tipo": "Carrozzina", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "CARR_04", "Tipo": "Carrozzina", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "CARR_05", "Tipo": "Carrozzina", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "CARR_06", "Tipo": "Carrozzina", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "CARR_07", "Tipo": "Carrozzina", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "STAM_01", "Tipo": "Coppia Stampelle", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
        {"ID": "STAM_02", "Tipo": "Coppia Stampelle", "Stato": "Disponibile", "Utente": "-", "Cauzione": 0, "Aggiornato": "-"},
    ])

if 'pagina' not in st.session_state:
    st.session_state.pagina = "menu"

mezzi_bg = ["BG 11-24", "BG 11-25", "BG 11-26", "BG 11-27", "BG 11-35", "Armadio", "Squadra Appiedata"]

# --- FUNZIONI DI NAVIGAZIONE ---
def vai_a_zaini(): st.session_state.pagina = "zaini"
def vai_a_dae(): st.session_state.pagina = "dae"
def vai_a_noleggi(): st.session_state.pagina = "noleggi"
def vai_a_menu(): st.session_state.pagina = "menu"

# --- MENU PRINCIPALE (PAGINA DI "LOGIN") ---
if st.session_state.pagina == "menu":
    st.title("🚑 Hub Logistica CRI Treviglio")
    st.write(f"Benvenuto! Seleziona l'operazione da effettuare:")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### 📦 ZAINI\nGestione zaini 3ì01-3ì04")
        if st.button("GESTIONE ZAINI", use_container_width=True, type="primary"):
            vai_a_zaini()
            st.rerun()

    with col2:
        st.success("### ⚡ DAE\nGestione defibrillatori 01-04")
        if st.button("GESTIONE DAE", use_container_width=True, type="primary"):
            vai_a_dae()
            st.rerun()

    with col3:
        st.warning("### 🦽 NOLEGGI\nCarrozzine e Stampelle")
        if st.button("GESTIONE NOLEGGI", use_container_width=True, type="primary"):
            vai_a_noleggi()
            st.rerun()
    
    st.markdown("---")
    st.caption("Sistema ottimizzato per smartphone e tablet - Logistica Sanitaria CRI Treviglio")

# --- PAGINA GESTIONE ZAINI ---
elif st.session_state.pagina == "zaini":
    st.button("⬅️ Torna al Menu", on_click=vai_a_menu)
    st.header("📦 Gestione Zaini (Serie 3ì)")
    
    cols = st.columns(2)
    for index, row in st.session_state.db_zaini.iterrows():
        with cols[index % 2]:
            with st.container(border=True):
                colore = "green" if row['Stato'] == "In Magazzino" else "red"
                st.markdown(f"### :{colore}[{row['ID']}]")
                st.write(f"**Ubicazione:** {row['Mezzo']}")
                st.caption(f"Ultimo: {row['Aggiornato']}")

                if row['Stato'] == "In Magazzino":
                    m_scelto = st.selectbox(f"Assegna a:", mezzi_bg, key=f"z_{row['ID']}")
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

# --- PAGINA GESTIONE DAE ---
elif st.session_state.pagina == "dae":
    st.button("⬅️ Torna al Menu", on_click=vai_a_menu)
    st.header("⚡ Gestione Defibrillatori (DAE)")
    
    cols = st.columns(2)
    for index, row in st.session_state.db_dae.iterrows():
        with cols[index % 2]:
            with st.container(border=True):
                colore = "green" if row['Stato'] == "In Magazzino" else "red"
                st.markdown(f"### :{colore}[{row['ID']}]")
                st.write(f"**Ubicazione:** {row['Mezzo']}")
                st.caption(f"Ultimo: {row['Aggiornato']}")

                if row['Stato'] == "In Magazzino":
                    m_scelto = st.selectbox(f"Assegna a:", mezzi_bg, key=f"d_{row['ID']}")
                    if st.button(f"CARICA {row['ID']}", type="primary"):
                        st.session_state.db_dae.at[index, 'Stato'] = "In Servizio"
                        st.session_state.db_dae.at[index, 'Mezzo'] = m_scelto
                        st.session_state.db_dae.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                        st.rerun()
                else:
                    if st.button(f"SCARICA {row['ID']} IN MAGAZZINO"):
                        st.session_state.db_dae.at[index, 'Stato'] = "In Magazzino"
                        st.session_state.db_dae.at[index, 'Mezzo'] = "-"
                        st.session_state.db_dae.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                        st.rerun()

# --- PAGINA GESTIONE NOLEGGI ---
elif st.session_state.pagina == "noleggi":
    st.button("⬅️ Torna al Menu", on_click=vai_a_menu)
    st.header("🦽 Gestione Noleggio Presidi Sociali")
    
    cols = st.columns(2)
    for index, row in st.session_state.db_noleggi.iterrows():
        with cols[index % 2]:
            with st.container(border=True):
                colore = "green" if row['Stato'] == "Disponibile" else "red"
                st.markdown(f"### :{colore}[{row['ID']} - {row['Tipo']}]")
                
                if row['Stato'] == "Disponibile":
                    st.write("**Stato:** Disponibile in Sede")
                    with st.expander(f"Esegui Noleggio {row['ID']}"):
                        u_nome = st.text_input("Nome Utente", key=f"u_{row['ID']}")
                        u_cauzione = st.number_input("Cauzione Versata (€)", min_value=0, key=f"c_{row['ID']}")
                        if st.button(f"CONFERMA CONSEGNA", key=f"btn_nol_{row['ID']}", type="primary"):
                            if u_nome:
                                st.session_state.db_noleggi.at[index, 'Stato'] = "Noleggiato"
                                st.session_state.db_noleggi.at[index, 'Utente'] = u_nome
                                st.session_state.db_noleggi.at[index, 'Cauzione'] = u_cauzione
                                st.session_state.db_noleggi.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                                st.rerun()
                            else:
                                st.error("Inserire il nome dell'utente!")
                else:
                    st.write(f"**Stato:** NOLEGGIATO")
                    st.write(f"**Utente:** {row['Utente']}")
                    st.write(f"**Cauzione:** {row['Cauzione']} €")
                    st.caption(f"Consegnato il: {row['Aggiornato']}")
                    
                    if st.button(f"REGISTRA RIENTRO {row['ID']}", key=f"btn_rie_{row['ID']}"):
                        st.session_state.db_noleggi.at[index, 'Stato'] = "Disponibile"
                        st.session_state.db_noleggi.at[index, 'Utente'] = "-"
                        st.session_state.db_noleggi.at[index, 'Cauzione'] = 0
                        st.session_state.db_noleggi.at[index, 'Aggiornato'] = datetime.now().strftime("%d/%m %H:%M")
                        st.rerun()
