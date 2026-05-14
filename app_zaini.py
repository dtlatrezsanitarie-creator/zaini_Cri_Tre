import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CRI Treviglio - Logistica", page_icon="🚑", layout="wide")

# --- CONNESSIONE GOOGLE SHEETS ---
# Questa connessione rende l'app "autonoma" leggendo i dati dal foglio
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNZIONI DI PERSISTENZA ---
def carica_stato(worksheet_name, default_df):
    try:
        # Legge i dati dal foglio Google
        return conn.read(worksheet=worksheet_name)
    except:
        # Se il foglio non esiste o è vuoto, usa i dati iniziali
        return default_df

def salva_e_log(df, worksheet_name, operatore, presidio, azione, note=""):
    # 1. Salva lo stato attuale nel database (sovrascrive lo stato per la persistenza)
    conn.update(worksheet=worksheet_name, data=df)
    
    # 2. Invia il log cronologico al Google Form (per il registro storico)
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLScqHbF6BdWGTfjppuzzgjxMKdybQGM3OTdTTsznqiND5Hl4pQ/formResponse"
    payload = {
        "entry.2109955773": operatore, 
        "entry.1236062721": presidio,  
        "entry.26190509": azione,    
        "entry.58890262": note       
    }
    try:
        requests.post(form_url, data=payload)
    except:
        pass
    
    st.cache_data.clear() # Pulisce la cache per vedere subito le modifiche

# --- INIZIALIZZAZIONE DATI PERSISTENTI ---
# Se l'app si riavvia, caricherà l'ultimo stato salvato su Google Sheets

if 'db_noleggi' not in st.session_state:
    n_def = pd.DataFrame([{"ID": f"CARR_{i:02d}", "Stato": "Disponibile", "Dettagli": "-"} for i in range(1, 10)])
    st.session_state.db_noleggi = carica_stato("NOLEGGI", n_def)

if 'db_monitor' not in st.session_state:
    m_def = pd.DataFrame([{"Stato": "In Carica", "Op": "-", "Mezzo": "-"}])
    st.session_state.db_monitor = carica_stato("MONITOR", m_def)

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# --- NAVIGAZIONE ---
def nav(p): 
    st.session_state.pagina = p
    st.rerun()

st.title("🚑 CRI Treviglio - Logistica Persistente")
st.markdown("---")

# --- HOME ---
if st.session_state.pagina == "home":
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 🦽 NOLEGGI")
        if st.button("Gestione Carrozzine", use_container_width=True): nav("noleggi")
    with col2:
        st.error("### 🖥️ DIPENDENTI")
        if st.button("Monitor ZOLL X Advance", use_container_width=True): nav("monitor")

# --- PAGINA NOLEGGI ---
elif st.session_state.pagina == "noleggi":
    st.button("⬅️ Home", on_click=lambda: nav("home"))
    st.header("🦽 Registro Carrozzine")
    cols = st.columns(3)
    
    for i, r in st.session_state.db_noleggi.iterrows():
        with cols[i % 3]:
            with st.container(border=True):
                if r['Stato'] == "Disponibile":
                    st.success(f"**{r['ID']}**")
                    nome = st.text_input("Utente", key=f"n_{i}")
                    if st.button("CONSEGNA", key=f"b_{i}"):
                        if nome:
                            st.session_state.db_noleggi.at[i, 'Stato'] = "Fuori"
                            st.session_state.db_noleggi.at[i, 'Dettagli'] = nome
                            salva_e_log(st.session_state.db_noleggi, "NOLEGGI", "Volontario", r['ID'], "Inizio Noleggio", nome)
                            st.rerun()
                elif r['Stato'] == "Fuori":
                    st.error(f"**{r['ID']}**")
                    st.write(f"In uso: {r['Dettagli']}")
                    if st.button("RIENTRO", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Sanificazione"
                        salva_e_log(st.session_state.db_noleggi, "NOLEGGI", "Volontario", r['ID'], "Rientro", r['Dettagli'])
                        st.rerun()
                else:
                    st.warning(f"**{r['ID']}** - DA PULIRE")
                    if st.button("CONFERMA PULIZIA", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Disponibile"
                        st.session_state.db_noleggi.at[i, 'Dettagli'] = "-"
                        salva_e_log(st.session_state.db_noleggi, "NOLEGGI", "Volontario", r['ID'], "Sanificazione", "OK")
                        st.rerun()

# --- PAGINA MONITOR ---
elif st.session_state.pagina == "monitor":
    st.button("⬅️ Home", on_click=lambda: nav("home"))
    st.header("🖥️ Monitor Zoll X Advance")
    
    # Prendiamo la prima riga del dataframe monitor
    m = st.session_state.db_monitor.iloc[0]
    
    col_a, col_b = st.columns(2)
    col_a.metric("Stato", m["Stato"])
    col_b.metric("Operatore", m["Op"])

    if m["Stato"] == "In Carica":
        nome_d = st.text_input("Nome Dipendente")
        mezzo_d = st.selectbox("Mezzo", ["BG 11-24", "BG 11-35"])
        if st.button("PRENDI IN CARICO", type="primary"):
            if nome_d:
                st.session_state.db_monitor.at[0, 'Stato'] = "In Servizio"
                st.session_state.db_monitor.at[0, 'Op'] = nome_d
                st.session_state.db_monitor.at[0, 'Mezzo'] = mezzo_d
                salva_e_log(st.session_state.db_monitor, "MONITOR", nome_d, "ZOLL_ADVANCE", "Inizio Turno", mezzo_d)
                st.rerun()
    else:
        st.write(f"In servizio su {m['Mezzo']}")
        c1 = st.checkbox("Sanificato")
        c2 = st.checkbox("In Carica")
        if st.button("FINE TURNO"):
            if c1 and c2:
                # Salviamo il nome prima di resettare
                vecchio_op = m['Op']
                st.session_state.db_monitor.at[0, 'Stato'] = "In Carica"
                st.session_state.db_monitor.at[0, 'Op'] = "-"
                st.session_state.db_monitor.at[0, 'Mezzo'] = "-"
                salva_e_log(st.session_state.db_monitor, "MONITOR", vecchio_op, "ZOLL_ADVANCE", "Fine Turno + Sanif", m['Mezzo'])
                st.rerun()
