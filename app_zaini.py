import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Logistica CRI Treviglio", page_icon="🚑", layout="wide")

# --- FUNZIONE INVIO DATI A GOOGLE FORM ---
def invia_log_ufficiale(operatore, presidio, azione, note=""):
    # URL ricavato dal tuo link (sostituito viewform con formResponse)
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLScqHbF6BdWGTfjppuzzgjxMKdybQGM3OTdTTsznqiND5Hl4pQ/formResponse"
    
    # Mapping basato sul tuo link precompilato
    payload = {
        "entry.2109955773": operatore, 
        "entry.1236062721": presidio,  
        "entry.26190509": azione,    
        "entry.58890262": note       
    }
    try:
        requests.post(form_url, data=payload)
    except:
        st.error("Errore di connessione al registro Google.")

# --- INIZIALIZZAZIONE DATI (Session State) ---
if 'db_zaini' not in st.session_state:
    st.session_state.db_zaini = pd.DataFrame([
        {"ID": f"3ì0{i}", "Stato": "In Magazzino", "Mezzo": "-"} for i in range(1, 5)
    ])

if 'db_dae' not in st.session_state:
    st.session_state.db_dae = pd.DataFrame([
        {"ID": f"DAE_0{i}", "Stato": "In Magazzino", "Mezzo": "-"} for i in range(1, 5)
    ])

if 'db_noleggi' not in st.session_state:
    st.session_state.db_noleggi = pd.DataFrame([
        {"ID": f"CARR_{i:02d}", "Stato": "Disponibile", "Dettagli": "-"} for i in range(1, 10)
    ])

if 'db_monitor' not in st.session_state:
    st.session_state.db_monitor = {"Stato": "In Carica", "Op": "-", "Mezzo": "-"}

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# --- NAVIGAZIONE ---
def nav(p): 
    st.session_state.pagina = p
    st.rerun()

# --- INTERFACCIA ---
st.title("🚑 CRI Treviglio - Logistica Digitale")
st.write(f"Registro Sanificazioni e Movimenti attivo")
st.markdown("---")

# --- 1. HOME ---
if st.session_state.pagina == "home":
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 📦 MEZZI & NOLEGGI")
        if st.button("Gestione Zaini e DAE", use_container_width=True): nav("mezzi")
        if st.button("Gestione Carrozzine (Noleggio)", use_container_width=True): nav("noleggi")
    with col2:
        st.error("### 🖥️ AREA DIPENDENTI")
        if st.button("Monitor ZOLL X Advance", use_container_width=True): nav("monitor")

# --- 2. PAGINA MEZZI (ZAINI & DAE) ---
elif st.session_state.pagina == "mezzi":
    st.button("⬅️ Home", on_click=lambda: nav("home"))
    t1, t2 = st.tabs(["🎒 Zaini", "⚡ DAE"])
    mezzi_lista = ["BG 11-24", "BG 11-25", "BG 11-26", "BG 11-27", "BG 11-35", "Appiedati", "Magazzino"]

    with t1:
        cols = st.columns(2)
        for i, r in st.session_state.db_zaini.iterrows():
            with cols[i % 2]:
                with st.container(border=True):
                    c = "green" if r['Stato'] == "In Magazzino" else "red"
                    st.subheader(f":{c}[Zaino {r['ID']}]")
                    if r['Stato'] == "In Magazzino":
                        m = st.selectbox("Carica su:", mezzi_lista, key=f"z_{i}")
                        if st.button(f"CONFERMA CARICO {r['ID']}", key=f"zb_{i}"):
                            st.session_state.db_zaini.at[i, 'Stato'] = "In Servizio"
                            st.session_state.db_zaini.at[i, 'Mezzo'] = m
                            invia_log_ufficiale("Logistica", r['ID'], "Carico su Mezzo", m)
                            st.rerun()
                    else:
                        st.write(f"Attualmente su: **{r['Mezzo']}**")
                        if st.button(f"SCARICA IN MAGAZZINO", key=f"zb_{i}"):
                            st.session_state.db_zaini.at[i, 'Stato'] = "In Magazzino"
                            st.session_state.db_zaini.at[i, 'Mezzo'] = "-"
                            invia_log_ufficiale("Logistica", r['ID'], "Scarico in Magazzino")
                            st.rerun()

    with t2:
        cols = st.columns(2)
        for i, r in st.session_state.db_dae.iterrows():
            with cols[i % 2]:
                with st.container(border=True):
                    c = "green" if r['Stato'] == "In Magazzino" else "red"
                    st.subheader(f":{c}[{r['ID']}]")
                    if r['Stato'] == "In Magazzino":
                        m = st.selectbox("Carica su:", mezzi_lista, key=f"d_{i}")
                        if st.button(f"CONFERMA CARICO {r['ID']}", key=f"db_{i}"):
                            st.session_state.db_dae.at[i, 'Stato'] = "In Servizio"
                            st.session_state.db_dae.at[i, 'Mezzo'] = m
                            invia_log_ufficiale("Logistica", r['ID'], "Carico su Mezzo", m)
                            st.rerun()
                    else:
                        st.write(f"Attualmente su: **{r['Mezzo']}**")
                        if st.button(f"SCARICA IN MAGAZZINO", key=f"db_{i}"):
                            st.session_state.db_dae.at[i, 'Stato'] = "In Magazzino"
                            st.session_state.db_dae.at[i, 'Mezzo'] = "-"
                            invia_log_ufficiale("Logistica", r['ID'], "Scarico in Magazzino")
                            st.rerun()

# --- 3. PAGINA NOLEGGI ---
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
                            invia_log_ufficiale("Volontario Sede", r['ID'], "Inizio Noleggio", f"Utente: {nome}")
                            st.rerun()
                elif r['Stato'] == "Fuori":
                    st.error(f"**{r['ID']}**")
                    st.write(f"In uso: {r['Dettagli']}")
                    if st.button("REGISTRA RIENTRO", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Sanificazione"
                        st.rerun()
                else:
                    st.warning(f"**{r['ID']}** - DA PULIRE")
                    if st.button("CONFERMA SANIFICAZIONE", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Disponibile"
                        invia_log_ufficiale("Volontario Sede", r['ID'], "Sanificazione", "Presidio pulito e pronto")
                        st.rerun()

# --- 4. PAGINA MONITOR ---
elif st.session_state.pagina == "monitor":
    st.button("⬅️ Home", on_click=lambda: nav("home"))
    st.header("🖥️ Zoll X Advance")
    m = st.session_state.db_monitor
    st.metric("Stato", m["Stato"], delta=m["Op"])
    
    if m["Stato"] == "In Carica":
        st.subheader("📥 Inizio Turno (23:00)")
        nome_d = st.text_input("Nome Dipendente Montante")
        mezzo_d = st.selectbox("Mezzo", ["BG 11-24", "BG 11-35"])
        if st.button("PRENDI IN CARICO", type="primary"):
            if nome_d:
                st.session_state.db_monitor.update({"Stato": "In Servizio", "Op": nome_d, "Mezzo": mezzo_d})
                invia_log_ufficiale(nome_d, "ZOLL_ADVANCE", "Inizio Turno", mezzo_d)
                st.rerun()
    else:
        st.subheader("📤 Fine Turno (20:00)")
        c1 = st.checkbox("Scocca sanificata")
        c2 = st.checkbox("Cavi raggruppati")
        c3 = st.checkbox("Monitor in carica")
        if st.button("CHIUDI TURNO E REGISTRA SANIFICAZIONE"):
            if c1 and c2 and c3:
                invia_log_ufficiale(m["Op"], "ZOLL_ADVANCE", "Fine Turno + Sanificazione", m["Mezzo"])
                st.session_state.db_monitor.update({"Stato": "In Carica", "Op": "-", "Mezzo": "-"})
                st.rerun()
            else:
                st.error("Completa i check di pulizia!")
