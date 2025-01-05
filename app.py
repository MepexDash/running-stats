import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Sett sidekonfigurasjon
st.set_page_config(
    page_title="Løpestatistikk 2025",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for moderne styling og mobil-responsivitet
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stProgress > div > div > div > div {
        background-color: #00cc99;
    }
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
        color: #1f1f1f;
    }
    .medium-font {
        font-size: 16px !important;
        color: #2c3e50;
    }
    .stats-container {
        background-color: white;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow-x: auto;
    }
    /* Mobile-spesifikke justeringer */
    @media (max-width: 640px) {
        .stats-container {
            padding: 8px;
            margin: 4px 0;
        }
        .stMarkdown {
            font-size: 14px;
        }
    }
    /* Gjør tabeller scrollbare horisontalt på mobil */
    .table-container {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    </style>
""", unsafe_allow_html=True)

# Definere individuelle mål
individual_goals = {
    "Helle": 1100,
    "Torbjørn": 1100,
    "Henrik": 1000,
    "Joakim": 750,
    "Eirik": 700,
    "Carl Frederik": 700,
    "Jens": 700,
    "Miriam": 600,
    "Anders": 500,
    "Kaia": 100,
    "Charlotte": 100,
    "Silje": None  # Ingen definert mål
}

# Hovedtittel
st.title("🏃 Løpestatistikk 2025")
st.markdown("### Felles mål: 7350 km")

# Simuler eksempeldata
def generate_sample_data():
    names = list(individual_goals.keys())
    current_date = datetime.now()
    data = []
    
    for name in names:
        # Generer data for hver person for de siste 30 dagene
        for i in range(30):
            date = current_date - timedelta(days=i)
            
            # Sett daglig gjennomsnitt basert på årsmål eller standardverdi
            if individual_goals[name] is not None:
                daily_average = individual_goals[name] / 365 * 1.5  # Litt høyere for variasjon
            else:
                daily_average = 2.0  # Standard daglig gjennomsnitt for løpere uten mål
                
            distance = max(0, np.random.normal(daily_average, daily_average/2))
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'name': name,
                'distance': round(distance, 2)
            })
    
    return pd.DataFrame(data)

df = generate_sample_data()

# Sidepanel for filtrering
st.sidebar.header("Filtrer data")

# Legg til "Velg alle" knapp
if st.sidebar.button("Velg alle"):
    selected_runner = list(individual_goals.keys())
else:
    selected_runner = st.sidebar.multiselect(
        "Velg løpere",
        options=list(individual_goals.keys()),
        default=list(individual_goals.keys())
    )

# Beregn nøkkeltall
filtered_df = df[df['name'].isin(selected_runner)]
total_distance = filtered_df['distance'].sum()

# Beregn måloppnåelse basert på valgte løpere
selected_goals_total = sum(individual_goals[name] for name in selected_runner if individual_goals[name] is not None)
goal_percentage = (total_distance / selected_goals_total) * 100 if selected_goals_total > 0 else 0
average_per_person = total_distance / len(selected_runner) if selected_runner else 0

# Vis hovedstatistikk i kolonner
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.metric("Total distanse", f"{total_distance:.1f} km")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    if len(selected_runner) == len(individual_goals):
        st.metric("Prosent av fellesmål", f"{(total_distance/7350*100):.1f}%")
        st.progress(min(total_distance/7350, 1.0))
    else:
        st.metric("Prosent av individuelle mål", f"{goal_percentage:.1f}%")
        st.progress(min(goal_percentage/100, 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.metric("Gjennomsnitt per person", f"{average_per_person:.1f} km")
    st.markdown('</div>', unsafe_allow_html=True)

# Grafer i scrollbar container
st.markdown('<div class="table-container">', unsafe_allow_html=True)
st.markdown("### 📊 Statistikk")

# Tabs for ulike visualiseringer
tab1, tab2, tab3 = st.tabs(["Individuell statistikk", "Tidslinje", "Ukentlig oversikt"])

with tab1:
    # Stolpediagram for individuell statistikk med mållinjer
    individual_stats = filtered_df.groupby('name')['distance'].sum().reset_index()
    
    # Legg til mållinjer for hver person
    fig_individual = go.Figure()
    
    for name in individual_stats['name']:
        distance = individual_stats[individual_stats['name'] == name]['distance'].iloc[0]
        fig_individual.add_trace(go.Bar(
            x=[name],
            y=[distance],
            name=f"{name} ({distance:.1f} km)",
            text=[f"{distance:.1f} km"],
            textposition='auto',
        ))
        
        # Legg til mållinje hvis personen har et definert mål
        if name in individual_goals and individual_goals[name] is not None:
            fig_individual.add_trace(go.Scatter(
                x=[name],
                y=[individual_goals[name]],
                mode='markers',
                name=f"Mål: {individual_goals[name]} km",
                marker=dict(symbol='line-ns', size=20, line=dict(width=2)),
                showlegend=False
            ))
    
    fig_individual.update_layout(
        title='Distanse vs. individuelle mål',
        template='plotly_white',
        showlegend=False,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),  # Mindre marginer på mobil
        autosize=True,
    )
    st.plotly_chart(fig_individual, use_container_width=True)

with tab2:
    # Linjediagram for utvikling over tid
    daily_progress = filtered_df.groupby('date')['distance'].sum().reset_index()
    daily_progress['cumulative'] = daily_progress['distance'].cumsum()
    
    fig_progress = px.line(
        daily_progress,
        x='date',
        y='cumulative',
        title='Kumulativ distanse over tid',
        template='plotly_white'
    )
    
    # Legg til mållinjer basert på valgte løpere
    if len(selected_runner) == len(individual_goals):
        fig_progress.add_hline(
            y=7350,
            line_dash="dash",
            annotation_text="Fellesmål: 7350 km",
            annotation_position="bottom right"
        )
    else:
        fig_progress.add_hline(
            y=selected_goals_total,
            line_dash="dash",
            annotation_text=f"Samlede individuelle mål: {selected_goals_total} km",
            annotation_position="bottom right"
        )
    
    st.plotly_chart(fig_progress, use_container_width=True)

with tab3:
    # Ukentlig oversikt
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    filtered_df['week'] = filtered_df['date'].dt.isocalendar().week
    weekly_stats = filtered_df.groupby(['week', 'name'])['distance'].sum().reset_index()
    
    fig_weekly = px.bar(
        weekly_stats,
        x='week',
        y='distance',
        color='name',
        title='Ukentlig distanse per person',
        barmode='group',
        template='plotly_white'
    )
    st.plotly_chart(fig_weekly, use_container_width=True)

# Leaderboard med måloppnåelse
st.markdown("### 🏆 Toppliste")
leaderboard = filtered_df.groupby('name')['distance'].sum().sort_values(ascending=False)

for i, (name, distance) in enumerate(leaderboard.items(), 1):
    goal = individual_goals[name]
    if goal is not None:
        progress = (distance / goal) * 100
        st.markdown(f"{i}. **{name}**: {distance:.1f} km ({progress:.1f}% av personlig mål på {goal} km)")
    else:
        st.markdown(f"{i}. **{name}**: {distance:.1f} km")

# Motiverende melding basert på fremgang
if goal_percentage < 25:
    st.info("💪 Vi har en god vei å gå - la oss holde motivasjonen oppe!")
elif goal_percentage < 50:
    st.info("🎯 Vi er på god vei mot målet!")
elif goal_percentage < 75:
    st.success("🌟 Imponerende innsats! Vi nærmer oss målet!")
else:
    st.success("🎉 Fantastisk jobbet! Målet er innen rekkevidde!")
