import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import locale

# ---------------------------------------------------------
# 1. CONFIGURAÇÕES GERAIS E UX/UI
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vai Ter Vôlei? 🏐",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados para dar cara de "Produto Profissional"
st.markdown("""
    <style>
    /* Remove padding excessivo do topo */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Cartões de Agendamento */
    .reservation-card {
        background-color: #f8f9fa;
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Badges / Pílulas */
    .badge-time {
        background-color: #2e3138;
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.9em;
    }
    .badge-team {
        background-color: #e0e6ed;
        color: #1f2937;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: 500;
    }
    .high-demand {
        color: #ff4b4b;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. CARREGAMENTO E TRATAMENTO DE DADOS (ETL)
# ---------------------------------------------------------
# Criação do arquivo de exemplo automaticamente (apenas se não existir) para garantir que funcione
def check_or_create_json():
    if not os.path.exists("state.json"):
        sample_data = {
            "reservations": [
                {"account_id": "squad_alfa", "date": "2026-04-04", "hour": "08:00", "status": "confirmed"},
                {"account_id": "squad_alfa", "date": "2026-04-04", "hour": "09:00", "status": "confirmed"},
                {"account_id": "team_beta", "date": "2026-04-04", "hour": "10:00", "status": "confirmed"},
                {"account_id": "squad_alfa", "date": "2026-04-05", "hour": "09:00", "status": "confirmed"},
                {"account_id": "turma_da_tarde", "date": "2026-04-05", "hour": "14:00", "status": "pending"}, # Será filtrado
            ]
        }
        with open("state.json", "w") as f:
            json.dump(sample_data, f)

@st.cache_data
def load_data():
    check_or_create_json()
    with open('state.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Transforma em DataFrame
    df = pd.DataFrame(data['reservations'])
    
    # Filtra apenas CONFIRMADOS
    df = df[df['status'] == 'confirmed'].copy()
    
    # Conversões e tratamento
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['hour'])
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(by=['datetime']).reset_index(drop=True)
    
    # Cria dia da semana pt-BR (sem depender do locale do SO do servidor)
    dias_semana = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
    df['weekday'] = df['datetime'].dt.dayofweek.map(dias_semana)
    
    return df

df_raw = load_data()


# ---------------------------------------------------------
# 3. BARRA LATERAL E FILTROS (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title("🏐 Ajuste o Saque")
st.sidebar.write("Use os filtros abaixo:")

# Lista de contas exclusivas
teams = ["Todas as equipes"] + list(df_raw['account_id'].unique())
selected_team = st.sidebar.selectbox("Filtre por quem reservou:", teams)

# Range de datas
min_date = df_raw['date'].min()
max_date = df_raw['date'].max()

try:
    date_range = st.sidebar.date_input(
        "Selecione o período:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
except:
    date_range = (min_date, max_date) # Fallback

# Aplica filtros
df_filtered = df_raw.copy()
if selected_team != "Todas as equipes":
    df_filtered = df_filtered[df_filtered['account_id'] == selected_team]

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[(df_filtered['date'] >= start_date) & (df_filtered['date'] <= end_date)]


# ---------------------------------------------------------
# 4. DASHBOARD - CABEÇALHO HERO (Regra dos 5 Segundos)
# ---------------------------------------------------------
st.title("Quadra de Vôlei | Visão Geral")

# Tenta encontrar se o "Próximo jogo" está muito distante
hoje = df_raw['date'].min() # Simulando o "hoje" baseado no primeiro dado (já que seu JSON usa 2026)

if not df_filtered.empty:
    next_game = df_filtered.iloc[0]
    next_date_str = next_game['date'].strftime('%d/%m/%Y')
    
    # Caixa de Destaque Superior
    if next_game['date'] == hoje:
        st.success(f"🔥 **BORA PRO JOGO! Hoje ({next_date_str}) TEM VÔLEI!** O próximo horário reservado é às **{next_game['hour']}** por `{next_game['account_id']}`.")
    else:
        st.info(f"⏳ O próximo jogo agendado na quadra será em **{next_game['weekday']}, {next_date_str}** às **{next_game['hour']}**.")
else:
    st.warning("Nenhuma reserva confirmada encontrada para o período/equipe.")
    st.stop() # Para a renderização se não houver dados


# ---------------------------------------------------------
# 5. KPIS RÁPIDOS
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
total_horas = len(df_filtered)
total_times = df_filtered['account_id'].nunique()
busiest_day = df_filtered.groupby('date').size().idxmax().strftime('%d/%m/%y')
busiest_hours = df_filtered.groupby('date').size().max()

col1.metric("⏱️ Total Horas Reservadas", f"{total_horas}h")
col2.metric("👥 Equipes Diferentes", total_times)
col3.metric("🔥 Dia mais Lotado", busiest_day)
col4.metric("📈 Pico Diário", f"{busiest_hours}h no dia")

st.markdown("---")

# ---------------------------------------------------------
# 6. VISÃO PRINCIPAL: A AGENDA (Agrupada e Estilizada)
# ---------------------------------------------------------
st.subheader("📅 Próximas Reservas")

# Agrupa por data para criar os cards iterativos
grouped = df_filtered.groupby(['date', 'weekday'])

# Grid para deixar a UI com ótimo respiro e evitar scroling excessivo
grid_cols = st.columns(2)
col_idx = 0

for (date, weekday), group in grouped:
    horas_total = len(group)
    data_formatada = date.strftime('%d/%m/%Y')
    
    # Se um dia tem 3h ou mais de reserva, recebe flag de "Alta ocupação"
    high_demand_html = " <span class='high-demand'>🔥 Alta Ocupação</span>" if horas_total >= 3 else ""
    
    with grid_cols[col_idx % 2]:
        # Título do dia na timeline
        st.markdown(f"#### {weekday}, {data_formatada} <small>({horas_total}h totais)</small>{high_demand_html}", unsafe_allow_html=True)
        
        html_cards = ""
        # Lista as horas agendadas neste dia
        for _, row in group.iterrows():
            html_cards += f"""
                <div class="reservation-card">
                    <span class="badge-time">⏰ {row['hour']}</span>
                    &nbsp; Reservado por <span class="badge-team">🏅 {row['account_id']}</span>
                </div>
            """
        # Renderiza a lista do dia com html estilizado
        st.markdown(html_cards, unsafe_allow_html=True)
        st.write("") # Spacer

    col_idx += 1


st.markdown("---")

# ---------------------------------------------------------
# 7. INSIGHTS EXTRAS: ANÁLISE GRÁFICA INTELIGENTE
# ---------------------------------------------------------
st.subheader("📊 Insights da Quadra")

col_graf_1, col_graf_2 = st.columns(2)

with col_graf_1:
    # Gráfico 1: Ocupação por time (Quem mais aluga)
    st.write("**Top Parceiros (Quem mais reserva?)**")
    graf_times = df_filtered['account_id'].value_counts().reset_index()
    graf_times.columns = ['Time', 'Horas']
    
    fig_pie = px.pie(graf_times, values='Horas', names='Time', 
                     hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_graf_2:
    # Gráfico 2: Qual a distribuição dos horários no decorrer do dia
    st.write("**Horários de Pico na Quadra**")
    graf_horas = df_filtered['hour'].value_counts().reset_index()
    graf_horas.columns = ['Horário', 'Reservas']
    graf_horas = graf_horas.sort_values('Horário')
    
    fig_bar = px.bar(graf_horas, x='Horário', y='Reservas', text='Reservas',
                     color='Reservas', color_continuous_scale="Reds")
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False, xaxis_type='category')
    st.plotly_chart(fig_bar, use_container_width=True)