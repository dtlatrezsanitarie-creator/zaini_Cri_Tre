import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CRI Treviglio - Logistica", page_icon="🚑", layout="wide")

# --- CONNESSIONE GOOGLE SHEETS ---
# Nota: Assicurati di aver configurato i Secrets su Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNZIONI DI SUPPORTO DATI ---
def load_db(worksheet_name, default_data):
    try:
        # Tenta di leggere dal foglio Google
        return conn.read(worksheet=worksheet_name)
    except:
        # Se il foglio è vuoto o non esiste, usa i dati iniziali
        return pd.DataFrame(default_data)

def save_db(df, worksheet_name):
    # Salva il dataframe su Google Sheets
    conn.update(worksheet=worksheet_name, data=df)
    st.cache_data.clear()

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATABASE (Da Google Sheets) ---
if 'db_zaini' not in st.session_state:
    z_default = [{"ID": f"3ì0{i}", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"} for i in range(1, 5)]
    st.session_state.db_zaini = load_db("ZAINI", z_default)

if 'db_dae' not in st.session_state:
    d_default = [{"ID": f"DAE_0{i}", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"} for i in range(1, 5)]
    st.session_state.db_dae = load_db("DAE", d_default)

if 'db_noleggi' not in st.session_state:
    n_default = [{"ID": f"CARR_{i:02d}", "Tipo": "Carrozzina", "Stato": "Disponibile", "Dettagli": "-"} for i in range(1, 10)]
    st.session_state.db_noleggi = load_db("NOLEGGI", n_default)

if 'db_monitor' not in st.session_state:
    m_default = [{"Stato": "In Carica", "Operatore": "-", "Mezzo": "-", "Check": "-"}]
    st.session_state.db_monitor = load_db("MONITOR", m_default)

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# --- VARIABILI GLOBALI ---
mezzi_lista = ["BG 11-24", "BG 11-25", "BG 11-26", "BG 11-27", "BG 11-35", "Appiedati", "Magazzino"]

def nav(pag): 
    st.session_state.pagina = pag
    st.rerun()

# --- HEADER ---
st.title("🚑 CRI Treviglio - Hub Logistica")
st.write(f"Sincronizzato con Registro Digitale | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("---")

# --- LOGICA NAVIGAZIONE ---

# 1. HOME MENU
if st.session_state.pagina == "home":
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 📦 LOGISTICA MEZZI")
        if st.button("Gestione Zaini e DAE"): nav("mezzi")
        st.warning("### 🦽 NOLEGGIO SOCIALE")
        if st.button("Gestione Carrozzine"): nav("noleggio")
    with col2:
        st.error("### 🖥️ AREA DIPENDENTI")
        st.write("Accesso esclusivo per il monitor Zoll X Advance")
        if st.button("Gestione Monitor Advance"): nav("dipendenti")

# 2. PAGINA MEZZI
elif st.session_state.pagina == "mezzi":
    st.button("⬅️ Torna alla Home", on_click=lambda: nav("home"))
    t1, t2 = st.tabs(["🎒 Zaini Serie 3ì", "⚡ Defibrillatori DAE"])
    
    with t1:
        cols = st.columns(2)
        for i, r in st.session_state.db_zaini.iterrows():
            with cols[i % 2]:
                with st.container(border=True):
                    c = "green" if r['Stato'] == "In Magazzino" else "red"
                    st.subheader(f":{c}[Zaino {r['ID']}]")
                    st.write(f"Posizione: **{r['Mezzo']}**")
                    if r['Stato'] == "In Magazzino":
                        m = st.selectbox("Assegna a:", mezzi_lista, key=f"z_sel_{i}")
                        if st.button(f"CARICA {r['ID']}", key=f"z_btn_{i}"):
                            st.session_state.db_zaini.at[i, 'Stato'] = "In Servizio"
                            st.session_state.db_zaini.at[i, 'Mezzo'] = m
                            save_db(st.session_state.db_zaini, "ZAINI")
                            st.rerun()
                    else:
                        if st.button(f"SCARICA {r['ID']}", key=f"z_btn_{i}"):
                            st.session_state.db_zaini.at[i, 'Stato'] = "In Magazzino"
                            st.session_state.db_zaini.at[i, 'Mezzo'] = "-"
                            save_db(st.session_state.db_zaini, "ZAINI")
                            st.rerun()

    with t2:
        cols = st.columns(2)
        for i, r in st.session_state.db_dae.iterrows():
            with cols[i % 2]:
                with st.container(border=True):
                    c = "green" if r['Stato'] == "In Magazzino" else "red"
                    st.subheader(f":{c}[{r['ID']}]")
                    st.write(f"Posizione: **{r['Mezzo']}**")
                    if r['Stato'] == "In Magazzino":
                        m = st.selectbox("Assegna a:", mezzi_lista, key=f"d_sel_{i}")
                        if st.button(f"CARICA {r['ID']}", key=f"d_btn_{i}"):
                            st.session_state.db_dae.at[i, 'Stato'] = "In Servizio"
                            st.session_state.db_dae.at[i, 'Mezzo'] = m
                            save_db(st.session_state.db_dae, "DAE")
                            st.rerun()
                    else:
                        if st.button(f"SCARICA {r['ID']}", key=f"d_btn_{i}"):
                            st.session_state.db_dae.at[i, 'Stato'] = "In Magazzino"
                            st.session_state.db_dae.at[i, 'Mezzo'] = "-"
                            save_db(st.session_state.db_dae, "DAE")
                            st.rerun()

# 3. PAGINA NOLEGGIO
elif st.session_state.pagina == "noleggio":
    st.button("⬅️ Torna alla Home", on_click=lambda: nav("home"))
    st.header("🦽 Gestione Noleggio Carrozzine")
    cols = st.columns(3)
    for i, r in st.session_state.db_noleggi.iterrows():
        with cols[i % 3]:
            with st.container(border=True):
                if r['Stato'] == "Disponibile":
                    st.success(f"**{r['ID']}**")
                    nome = st.text_input("Utente", key=f"n_{i}")
                    if st.button("NOLEGGIA", key=f"b_{i}"):
                        if nome:
                            st.session_state.db_noleggi.at[i, 'Stato'] = "Fuori"
                            st.session_state.db_noleggi.at[i, 'Dettagli'] = nome
                            save_db(st.session_state.db_noleggi, "NOLEGGI")
                            st.rerun()
                elif r['Stato'] == "Fuori":
                    st.error(f"**{r['ID']}**")
                    st.write(f"Utente: {r['Dettagli']}")
                    if st.button("REGISTRA RIENTRO", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Sanificazione"
                        save_db(st.session_state.db_noleggi, "NOLEGGI")
                        st.rerun()
                else:
                    st.warning(f"**{r['ID']}**")
                    st.write("DA SANIFICARE")
                    if st.button("PULIZIA COMPLETATA", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Disponibile"
                        st.session_state.db_noleggi.at[i, 'Dettagli'] = "-"
                        save_db(st.session_state.db_noleggi, "NOLEGGI")
                        st.rerun()

# 4. PAGINA DIPENDENTI
elif st.session_state.pagina == "dipendenti":
    st.button("⬅️ Torna alla Home", on_click=lambda: nav("home"))
    st.header("🖥️ Monitor ZOLL X Advance")
    
    # Il database monitor è un dataframe con una sola riga (index 0)
    m = st.session_state.db_monitor.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Stato", m["Stato"])
    c2.metric("Operatore", m["Operatore"])
    c3.metric("Mezzo", m["Mezzo"])
    
    st.markdown("---")
    
    if m["Stato"] == "In Carica":
        st.subheader("📥 Inizio Turno (ore 23:00)")
        n_dip = st.text_input("Nome Dipendente")
        m_dip = st.selectbox("Mezzo:", ["BG 11-24", "BG 11-35"])
        if st.button("PRENDI IN CARICO", type="primary"):
            if n_dip:
                st.session_state.db_monitor.at[0, 'Stato'] = "IN SERVIZIO"
                st.session_state.db_monitor.at[0, 'Operatore'] = n_dip
                st.session_state.db_monitor.at[0, 'Mezzo'] = m_dip
                save_db(st.session_state.db_monitor, "MONITOR")
                st.rerun()
    else:
        st.subheader("📤 Fine Turno (ore 20:00)")
        ck1 = st.checkbox("Sanificato")
        ck2 = st.checkbox("Cavi Integri")
        ck3 = st.checkbox("In Carica")
        if st.button("CHIUDI TURNO"):
            if ck1 and ck2 and ck3:
                st.session_state.db_monitor.at[0, 'Stato'] = "In Carica"
                st.session_state.db_monitor.at[0, 'Operatore'] = "-"
                st.session_state.db_monitor.at[0, 'Mezzo'] = "-"
                save_db(st.session_state.db_monitor, "MONITOR")
                st.rerun()
