import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CRI Treviglio - Logistica", page_icon="🚑", layout="wide")

# --- CUSTOM CSS PER RENDERE L'INTERFACCIA PROFESSIONALE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATABASE (SESSION STATE) ---
if 'db_zaini' not in st.session_state:
    st.session_state.db_zaini = pd.DataFrame([
        {"ID": f"3ì0{i}", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"} for i in range(1, 5)
    ])

if 'db_dae' not in st.session_state:
    st.session_state.db_dae = pd.DataFrame([
        {"ID": f"DAE_0{i}", "Stato": "In Magazzino", "Mezzo": "-", "Aggiornato": "-"} for i in range(1, 5)
    ])

if 'db_noleggi' not in st.session_state:
    carrozzine = [{"ID": f"CARR_{i:02d}", "Tipo": "Carrozzina", "Stato": "Disponibile", "Dettagli": "-"} for i in range(1, 10)]
    st.session_state.db_noleggi = pd.DataFrame(carrozzine)

if 'db_monitor' not in st.session_state:
    st.session_state.db_monitor = {"Stato": "In Carica", "Operatore": "-", "Mezzo": "-", "Check": "-"}

if 'pagina' not in st.session_state:
    st.session_state.pagina = "home"

# --- VARIABILI GLOBALI ---
mezzi_lista = ["BG 11-24", "BG 11-25", "BG 11-26", "BG 11-27", "BG 11-35", "Appiedati", "Magazzino"]

# --- FUNZIONI DI NAVIGAZIONE ---
def nav(pag): 
    st.session_state.pagina = pag
    st.rerun()

# --- HEADER FISSO ---
st.title("🚑 CRI Treviglio - Hub Logistica")
st.write(f"Oggi è il {datetime.now().strftime('%d/%m/%Y')}")
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

# 2. PAGINA MEZZI (ZAINI E DAE)
elif st.session_state.pagina == "mezzi":
    if st.button("⬅️ Torna alla Home"): nav("home")
    
    tab1, tab2 = st.tabs(["🎒 Zaini Serie 3ì", "⚡ Defibrillatori DAE"])
    
    with tab1:
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
                            st.rerun()
                    else:
                        if st.button(f"SCARICA {r['ID']}", key=f"z_btn_{i}"):
                            st.session_state.db_zaini.at[i, 'Stato'] = "In Magazzino"
                            st.session_state.db_zaini.at[i, 'Mezzo'] = "-"
                            st.rerun()

    with tab2:
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
                            st.rerun()
                    else:
                        if st.button(f"SCARICA {r['ID']}", key=f"d_btn_{i}"):
                            st.session_state.db_dae.at[i, 'Stato'] = "In Magazzino"
                            st.session_state.db_dae.at[i, 'Mezzo'] = "-"
                            st.rerun()

# 3. PAGINA NOLEGGIO (CARROZZINE)
elif st.session_state.pagina == "noleggio":
    if st.button("⬅️ Torna alla Home"): nav("home")
    st.header("🦽 Gestione Noleggio Carrozzine")
    
    cols = st.columns(3)
    for i, r in st.session_state.db_noleggi.iterrows():
        with cols[i % 3]:
            with st.container(border=True):
                if r['Stato'] == "Disponibile":
                    st.success(f"**{r['ID']}**")
                    nome = st.text_input("Utente", key=f"n_{i}", placeholder="Nome e Cognome")
                    if st.button("NOLEGGIA", key=f"b_{i}"):
                        if nome:
                            st.session_state.db_noleggi.at[i, 'Stato'] = "Fuori"
                            st.session_state.db_noleggi.at[i, 'Dettagli'] = nome
                            st.rerun()
                elif r['Stato'] == "Fuori":
                    st.error(f"**{r['ID']}**")
                    st.write(f"Utente: {r['Dettagli']}")
                    if st.button("REGISTRA RIENTRO", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Sanificazione"
                        st.rerun()
                else:
                    st.warning(f"**{r['ID']}**")
                    st.write("DA SANIFICARE")
                    if st.button("OK PULITA", key=f"b_{i}"):
                        st.session_state.db_noleggi.at[i, 'Stato'] = "Disponibile"
                        st.session_state.db_noleggi.at[i, 'Dettagli'] = "-"
                        st.rerun()

# 4. PAGINA DIPENDENTI (MONITOR ZOLL)
elif st.session_state.pagina == "dipendenti":
    if st.button("⬅️ Torna alla Home"): nav("home")
    st.header("🖥️ Monitor ZOLL X Advance")
    
    m = st.session_state.db_monitor
    c1, c2, c3 = st.columns(3)
    c1.metric("Stato", m["Stato"])
    c2.metric("Operatore", m["Operatore"])
    c3.metric("Mezzo", m["Mezzo"])
    
    st.markdown("---")
    
    if m["Stato"] == "In Carica":
        st.subheader("📥 Presa in Carico (Inizio Turno)")
        nome_dip = st.text_input("Nome Dipendente Montante")
        mezzo_dip = st.selectbox("Mezzo assegnato:", ["BG 11-24", "BG 11-35"])
        if st.button("INIZIA SERVIZIO", type="primary"):
            if nome_dip:
                st.session_state.db_monitor.update({"Stato": "IN SERVIZIO", "Operatore": nome_dip, "Mezzo": mezzo_dip})
                st.rerun()
    else:
        st.subheader("📤 Fine Turno (Rientro)")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c1 = st.checkbox("Monitor pulito")
            c2 = st.checkbox("Cavi controllati")
        with col_c2:
            c3 = st.checkbox("Messo sotto carica")
        
        if st.button("REGISTRA CHIUSURA"):
            if c1 and c2 and c3:
                st.session_state.db_monitor.update({"Stato": "In Carica", "Operatore": "-", "Mezzo": "-"})
                st.success("Ottimo lavoro! Monitor pronto per il prossimo turno.")
                st.rerun()
            else:
                st.error("Completa tutti i check prima di chiudere!")
