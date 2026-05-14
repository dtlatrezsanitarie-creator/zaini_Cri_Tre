import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CRI Treviglio - Logistica", page_icon="🚑", layout="wide")

# --- CONNESSIONE CLOUD (Google Sheets) ---
# Questa parte permette all'app di salvare i dati stabilmente
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNZIONE PER SALVARE E LOGGARE ---
def salva_e_log(df_da_salvare, nome_foglio, operatore, presidio, azione, note=""):
    # 1. Salva lo stato attuale sul foglio Google per la memoria dell'app
    conn.update(worksheet=nome_foglio, data=df_da_salvare)
    
    # 2. Invia la riga al Registro Storico (il tuo modulo Google)
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
    st.cache_data.clear()

# --- INIZIALIZZAZIONE DATABASE (Legge dal Cloud o crea default) ---
if 'db_noleggi' not in st.session_state:
    try:
        st.session_state.db_noleggi = conn.read(worksheet="NOLEGGI")
    except:
        st.session_state.db_noleggi = pd.DataFrame([
            {"ID": f"CARR_{i:02d}", "Stato": "Disponibile", "Dettagli": "-"} for i in range(1, 10)
        ])

if 'db_monitor' not in st.session_state:
    try:
        st.session_state.db_monitor = conn.read(worksheet="MONITOR")
    except:
        st.session_state.db_monitor = pd.DataFrame([{"Stato": "In Carica", "Op": "-", "Mezzo": "-"}])

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# --- NAVIGAZIONE ---
def nav(p): 
    st.session_state.pagina = p
    st.rerun()

# --- INTERFACCIA ---
st.title("🚑 CRI Treviglio - Hub Logistica")
st.markdown("---")

# 1. HOME
if st.session_state.pagina == "home":
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 🦽 NOLEGGI")
        if st.button("Gestione Carrozzine", use_container_width=True): nav("noleggi")
    with col2:
        st.error("### 🖥️ DIPENDENTI")
        if st.button("Monitor ZOLL X Advance", use_container_width=True): nav("monitor")

# 2. PAGINA NOLEGGI
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

# 3. PAGINA MONITOR
elif st.session_state.pagina == "monitor":
    st.button("⬅️ Home", on_click=lambda: nav("home"))
    st.header("🖥️ Monitor Zoll X Advance")
    m = st.session_state.db_monitor.iloc[0]
    
    st.metric("Stato", m["Stato"], delta=m["Op"])
    
    if m["Stato"] == "In Carica":
        nome_d = st.text_input("Nome Dipendente Montante")
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
                op_attuale = m['Op']
                st.session_state.db_monitor.at[0, 'Stato'] = "In Carica"
                st.session_state.db_monitor.at[0, 'Op'] = "-"
                st.session_state.db_monitor.at[0, 'Mezzo'] = "-"
                salva_e_log(st.session_state.db_monitor, "MONITOR", op_attuale, "ZOLL_ADVANCE", "Fine Turno + Sanif", m['Mezzo'])
                st.rerun()
