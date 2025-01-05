import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os

# Sett sidekonfigurasjon for mobil
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Konstanter
YEARLY_GOAL = 7350  # kilometer
RUNNERS = ["Carl Frederik", "Kaia", "Miriam", "Torbjørn", "Henrik", 
          "Eirik", "Charlotte", "Jens", "Helle", "Anders", "Joakim", "Silje"]
ACTIVITIES = ["Løping", "Gåing"]

# Funksjon for å laste data
def load_data():
    if os.path.exists('running_data.json'):
        with open('running_data.json', 'r') as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame(columns=['dato', 'løper', 'aktivitet', 'distanse', 'tid', 'tempo'])

# Funksjon for å lagre data
def save_data(df):
    with open('running_data.json', 'w') as f:
        json.dump(df.to_dict('records'), f)

# Last eksisterende data
df = load_data()

# App tittel
st.title("🏃‍♂️ Løperegistrering 2025")

# Registreringsskjema
st.header("Registrer aktivitet")

with st.form("registrering"):
    col1, col2 = st.columns(2)
    
    with col1:
        løper = st.selectbox("Velg løper", RUNNERS)
        aktivitet = st.selectbox("Velg aktivitet", ACTIVITIES)
        dato = st.date_input("Dato", date.today())
    
    with col2:
        distanse = st.number_input("Distanse (km)", min_value=0.0, step=0.1)
        timer = st.number_input("Timer", min_value=0, step=1)
        minutter = st.number_input("Minutter", min_value=0, max_value=59, step=1)
        
    submitted = st.form_submit_button("Registrer")
    
    if submitted:
        tid_minutter = timer * 60 + minutter
        if distanse > 0:
            tempo = round(tid_minutter / distanse, 1)
        else:
            tempo = 0
            
        ny_aktivitet = pd.DataFrame({
            'dato': [dato],
            'løper': [løper],
            'aktivitet': [aktivitet],
            'distanse': [distanse],
            'tid': [tid_minutter],
            'tempo': [tempo]
        })
        
        df = pd.concat([df, ny_aktivitet], ignore_index=True)
        save_data(df)
        st.success("Aktivitet registrert!")
        st.experimental_rerun()

# Statistikk
if not df.empty:
    st.header("Statistikk")
    
    # Total distanse og måloppnåelse
    total_km = df['distanse'].sum()
    progress = (total_km / YEARLY_GOAL) * 100
    
    # Beregn forventet progress basert på dagens dato
    days_in_year = 366 if date.today().year % 4 == 0 else 365
    day_of_year = date.today().timetuple().tm_yday
    expected_progress = (day_of_year / days_in_year) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total distanse", f"{total_km:.1f} km")
    with col2:
        st.metric("Måloppnåelse", f"{progress:.1f}%")
    
    # Fremgangsmåler
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = progress,
        delta = {'reference': expected_progress},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, expected_progress], 'color': "lightgray"},
                {'range': [expected_progress, 100], 'color': "white"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': expected_progress
            }
        },
        title = {'text': "Måloppnåelse vs. Forventet"}
    ))
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistikk per løper
    løper_stats = df.groupby('løper')['distanse'].agg(['sum', 'count']).round(1)
    løper_stats.columns = ['Total distanse (km)', 'Antall aktiviteter']
    løper_stats = løper_stats.sort_values('Total distanse (km)', ascending=False)
    
    # Visualiser løperstatistikk
    fig = px.bar(løper_stats, 
                 x=løper_stats.index, 
                 y='Total distanse (km)',
                 title="Distanse per løper")
    fig.update_layout(xaxis_title="Løper", yaxis_title="Total distanse (km)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Vis detaljert statistikk
    st.subheader("Detaljert statistikk per løper")
    st.dataframe(løper_stats, use_container_width=True)
    
    # Månedlig oversikt
    df['måned'] = pd.to_datetime(df['dato']).dt.strftime('%B')
    monthly_stats = df.groupby('måned')['distanse'].sum().round(1)
    
    fig = px.bar(monthly_stats, 
                 title="Distanse per måned")
    fig.update_layout(xaxis_title="Måned", yaxis_title="Total distanse (km)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Vis siste aktiviteter
    st.subheader("Siste aktiviteter")
    siste_aktiviteter = df.sort_values('dato', ascending=False).head(10)
    siste_aktiviteter['dato'] = pd.to_datetime(siste_aktiviteter['dato']).dt.strftime('%d.%m.%Y')
    siste_aktiviteter['tid'] = siste_aktiviteter['tid'].apply(lambda x: f"{int(x//60)}t {int(x%60)}m")
    st.dataframe(siste_aktiviteter[['dato', 'løper', 'aktivitet', 'distanse', 'tid', 'tempo']], 
                use_container_width=True)

else:
    st.info("Ingen aktiviteter registrert ennå. Registrer din første aktivitet ovenfor!")
