import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Logistica CRI Treviglio", page_icon="🚑", layout="wide")

# --- FUNZIONE INVIO DATI A GOOGLE FORM ---
def invia_log_ufficiale(operatore, presidio, azione, note=""):
    # Sostituisci questo URL con il tuo ID del modulo
    form_url = "https://docs.google.com/forms/u/0/d/e/IL_TUO_ID_LUNGO/formResponse"
    
    # Questi entry.ID vanno sostituiti con quelli del tuo modulo (vedi istruzioni sotto)
    payload = {
        "entry.1000001": operatore, # Campo: Chi?
        "entry.1000002": presidio,  # Campo: Cosa?
        "entry.1000003": azione,    # Campo: Azione svolta
        "entry.1000004": note       # Campo: Note/Mezzo
    }
    try:
        requests.post(form_url, data=payload)
    except:
        st.error("Errore di connessione al registro Google.")

# --- INIZIALIZZAZIONE DATI (Session State) ---
if 'db_noleggi' not in st.session_state:
    st.session_state.db_noleggi = pd.DataFrame([
        {"ID": f"CARR_{i:02d}", "Stato": "Disponibile", "Dettagli": "-"} for i in range(1, 10)
    ])
if 'db_monitor' not in st.session_state:
    st.session_state.db_monitor = {"Stato": "In Carica", "Op": "-", "Mezzo": "-"}
if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# --- NAVIGAZIONE ---
def nav(p): st.session_state.pagina = p; st.rerun()

# --- INTERFACCIA ---
st.title("🚑 CRI Treviglio - Logistica Digitale")
st.markdown("---")

if st.session_state.pagina == "home":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🦽 GESTIONE NOLEGGI", use_container_width=True): nav("noleggi")
    with col2:
        if st.button("🖥️ AREA MONITOR (Dipendenti)", use_container_width=True): nav("monitor")

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
                    if st.button("NOLEGGIA", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Fuori"
                        st.session_state.db_noleggi.at[i, 'Dettagli'] = nome
                        invia_log_ufficiale("Volontario", r['ID'], "Inizio Noleggio", f"Utente: {nome}")
                        st.rerun()
                elif r['Stato'] == "Fuori":
                    st.error(f"**{r['ID']}**")
                    st.write(f"In uso: {r['Dettagli']}")
                    if st.button("RIENTRO", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Sanificazione"
                        st.rerun()
                else:
                    st.warning(f"**{r['ID']}** - DA PULIRE")
                    if st.button("CONFERMA SANIFICAZIONE", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Disponibile"
                        invia_log_ufficiale("Volontario", r['ID'], "Sanificazione", "Presidio pulito e pronto")
                        st.rerun()

elif st.session_state.pagina == "monitor":
    st.button("⬅️ Home", on_click=lambda: nav("home"))
    st.header("🖥️ Zoll X Advance")
    m = st.session_state.db_monitor
    st.metric("Stato", m["Stato"], delta=m["Op"])
    
    if m["Stato"] == "In Carica":
        nome_d = st.text_input("Nome Dipendente")
        mezzo_d = st.selectbox("Mezzo", ["BG 11-24", "BG 11-35"])
        if st.button("PRENDI IN CARICO", type="primary"):
            st.session_state.db_monitor.update({"Stato": "In Servizio", "Op": nome_d, "Mezzo": mezzo_d})
            invia_log_ufficiale(nome_d, "ZOLL_ADVANCE", "Inizio Turno", mezzo_d)
            st.rerun()
    else:
        st.info("Eseguire pulizia e ricarica prima di chiudere.")
        if st.button("REGISTRA CHIUSURA E SANIFICAZIONE"):
            invia_log_ufficiale(m["Op"], "ZOLL_ADVANCE", "Fine Turno + Sanificazione", m["Mezzo"])
            st.session_state.db_monitor.update({"Stato": "In Carica", "Op": "-", "Mezzo": "-"})
            st.rerun()
