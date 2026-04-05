import streamlit as st
import pandas as pd
import json
import os
import time

# ---------------------------------------------------------
# 1. SETUP DE MOTOR DE JOGO (PAGE CONFIG)
# ---------------------------------------------------------
st.set_page_config(page_title="GAMEDAY | Hub da Equipe", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. INJEÇÃO DE GRÁFICOS SPORTS BROADCAST (HTML / CSS3 Avançado)
# ---------------------------------------------------------
css_code = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;600;700&family=Chakra+Petch:ital,wght@0,600;0,700;1,700&display=swap');

    /* BASE DA PLATAFORMA (The Arena / White mode per request mas com muito neon!) */
    [data-testid="stAppViewContainer"] { background-color: #f6f7fb !important; background-image: radial-gradient(#d3dce6 1px, transparent 1px); background-size: 20px 20px;}
    header[data-testid="stHeader"] { display: none; }
    
    .block-container { 
        max-width: 1400px; padding-top: 1rem; padding-bottom: 3rem; 
        font-family: 'Chakra Petch', sans-serif;
    }
    
    h1, h2, h3, h4 { text-transform: uppercase; margin: 0; padding: 0; line-height: 1; }

    /* ANIMAÇÕES / KEYFRAMES (O Videogame em movimento) */
    @keyframes barFill { 0% { width: 0%; } }
    @keyframes pulseAlert { 
        0% { box-shadow: 0 0 0 0px rgba(255, 42, 70, 0.6); border-color: rgba(255, 42, 70, 0.8); }
        50% { box-shadow: 0 0 25px 5px rgba(255, 42, 70, 0.2); border-color: rgba(255, 42, 70, 0.3); }
        100% { box-shadow: 0 0 0 0px rgba(255, 42, 70, 0); border-color: rgba(255, 42, 70, 0.8); }
    }
    @keyframes slideInDown {
        0% { transform: translateY(30px) skewX(-2deg); opacity: 0; }
        100% { transform: translateY(0) skewX(0); opacity: 1; }
    }
    @keyframes neonGlow {
        from { filter: drop-shadow(0 0 2px #fff) drop-shadow(0 0 10px #FFD700); }
        to { filter: drop-shadow(0 0 2px #fff) drop-shadow(0 0 18px #00FFFF); }
    }

    /* TÍTULO PRINCIPAL (Jumbotron Broadcast Style) */
    .title-banner {
        font-family: 'Teko', sans-serif; font-size: 75px; font-weight: 700; color: #111; letter-spacing: -2px;
        position: relative; margin-bottom: 25px; margin-top: 20px; display: inline-block;
    }
    .title-banner::after { /* Faixa sublinhada estilo velocidade / marca */
        content: ''; position: absolute; left: 0; bottom: -5px; width: 60%; height: 6px; 
        background: linear-gradient(90deg, #00A8FF, #FFD700); transform: skewX(-25deg);
    }
    
    .subtitle { font-family: 'Chakra Petch', sans-serif; color: #444; font-size: 16px; font-style: italic; letter-spacing: 3px; font-weight: 600;}

    /* TELÃO DO JOGO ATUAL (Match Highlight EA Sports) */
    .next-match-jumbotron {
        background: linear-gradient(135deg, #09131d 0%, #172433 100%); position: relative; overflow: hidden;
        border-radius: 12px; padding: 40px; margin-bottom: 40px; display: flex; flex-direction: column; 
        border-left: 8px solid #00D2FF; box-shadow: 0 15px 35px -5px rgba(0,0,0,0.15); animation: slideInDown 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .jumbotron-bg-text { /* Numero gigante opaco de fundo */
        position: absolute; right: -20px; top: -50px; font-family: 'Teko', sans-serif; font-size: 350px; 
        color: rgba(255,255,255,0.03); line-height: 1; font-weight: 700; transform: skewX(-5deg); z-index: 1;
    }
    .jumbo-badge { 
        display: inline-block; padding: 5px 12px; background: #FFD700; color: #111; font-size: 12px; 
        font-weight: 700; letter-spacing: 2px; transform: skewX(-15deg); margin-bottom: 15px; z-index: 2; position: relative;
    }
    .jumbo-clock { 
        font-size: 45px; font-family: 'Teko', sans-serif; font-weight: 600; color: #FFF; margin-top: 5px; text-shadow: 0 0 10px rgba(0,210,255,0.5); z-index: 2; position: relative;
    }

    /* ESTATÍSTICA DO TEAM SEASON STATS (Numbers panel) */
    .season-stats-container {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; animation: slideInDown 0.7s;
    }
    .stat-cube {
        background: #fff; border: 2px solid #e1e8ed; padding: 25px; border-radius: 8px; position: relative; text-align: left;
    }
    .stat-cube::before {
        content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; border-radius: 6px 0 0 6px;
    }
    .cube-hours::before { background: #3b82f6; } /* Azul Time */
    .cube-days::before { background: #10b981; }   /* Verde Play */
    .cube-pico::before { background: #FF2A46; }    /* Vermelho Máximo */
    
    .cube-label { color: #64748b; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;}
    .cube-number { font-family: 'Teko', sans-serif; font-size: 55px; line-height: 0.9; color: #0b0e14;}

    /* GRID DAS MATCHES (A Programação NBA Broadcasting / Caixa Esportiva de TV) */
    .match-calendar-title { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; font-size: 26px; font-style: italic;}
    .match-calendar-title span { background: #111; color: white; padding: 6px 16px; transform: skewX(-15deg); }
    
    .grid-container {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; animation: slideInDown 0.9s;
    }

    /* CARD DA PARTIDA INDIVIDUAL ESTILO GAME PASS */
    .fixture-card {
        background: white; display: flex; flex-direction: column;
        border: 1px solid #dbe2e8; padding-bottom: 0px; position: relative; overflow: hidden;
        /* Corte obliquo no topo */
        clip-path: polygon(0 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%);
    }

    .fixture-header {
        background: #0f172a; padding: 20px; display: flex; justify-content: space-between; align-items: baseline; position: relative;
    }
    .date-day { font-size: 24px; color: #fff; font-family: 'Chakra Petch'; font-style: italic;}
    .hours-vol { background: #FFD700; color: #111; padding: 2px 10px; font-weight: 700; font-size: 14px; font-family: 'Arial'; border-radius: 4px; box-shadow: inset 0 -3px 0 rgba(0,0,0,0.2);}
    
    .fixture-body { padding: 20px 25px 0 25px; background: url('https://www.transparenttextures.com/patterns/clean-gray-paper.png'); background-color: #fbfdff;}
    
    /* Play-By-Play Timeline */
    .time-slot { 
        display: flex; gap: 15px; margin-bottom: 12px; align-items: center; border-left: 2px solid #e1e8ed; padding-left: 10px;
    }
    .badge-hour {
        font-family: 'Teko', sans-serif; font-size: 22px; color: #111; padding: 0px 8px; min-width: 65px; border-bottom: 2px solid #3b82f6; text-align: center;
    }
    .badge-user { font-family: 'Chakra Petch'; color: #475569; font-size: 14px; font-weight: 600; }

    /* MOTOR DE RESISTENCIA & ESTAMINA VINCULADO AO TIME DA VIDA REAL */
    .engine-section { padding: 20px 25px; border-top: 1px dashed #cbd5e1; margin-top: 10px; background: white;}
    .engine-header { display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #475569; margin-bottom: 12px;}
    .engine-title { text-transform: uppercase;}
    .engine-level { text-transform: uppercase;}
    
    .stamina-track { width: 100%; height: 16px; background: #e2e8f0; position: relative; border-radius: 10px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px;}
    .stamina-fill { 
        height: 100%; width: 0%; border-radius: 10px; animation: barFill 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; position: relative; overflow: hidden;
    }
    /* Estriamentos oblíquos passando na barra de energia p dar ilusão q tem gás girando */
    .stamina-fill::after {
        content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(-45deg, rgba(255,255,255,0.25) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.25) 50%, rgba(255,255,255,0.25) 75%, transparent 75%, transparent); background-size: 15px 15px; z-index: 1; opacity: 0.8;
    }
    
    .sys-report { font-family: 'Arial'; font-size: 11px; font-weight: 600; line-height: 1.3;}

    /* Lógicas Condicionais CSS Baseando Cores Na Stamina Da Partida */
    /* 1 A 2 Horas - ZONA AZUL WARMUP */
    .mode-warmup .stamina-fill { background: linear-gradient(90deg, #3b82f6, #00D2FF); box-shadow: inset 0 -3px rgba(0,0,0,0.1);}
    .mode-warmup .engine-level { color: #2563eb; }
    
    /* 3 Horas - ZONA AMARELO MATCHDAY */
    .mode-game .stamina-fill { background: linear-gradient(90deg, #fbbf24, #FAD201); box-shadow: inset 0 -3px rgba(0,0,0,0.1); }
    .mode-game .engine-level { color: #d97706; }
    
    /* >3 HORAS - ZONA REDZONE/OVERTIME: Aplica frame Pulse vermelho animado em looping nas caixas pai da fixture pra destacar O perigo*/
    .mode-survival .stamina-fill { background: linear-gradient(90deg, #ef4444, #dc2626); box-shadow: inset 0 -3px rgba(0,0,0,0.15);}
    .mode-survival .engine-level { color: #dc2626; font-weight: 800; animation: pulseAlert 1.5s infinite;}
    .survival-border { animation: pulseAlert 1.5s infinite alternate !important; border: 2px solid #ef4444; clip-path: none;}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. EXTRAÇÃO DE DADOS & CORE SQUAD LOGIC (Simulador de Base JSON)
# ---------------------------------------------------------
def guarantee_engine_running():
    # Cria os dados automaticamente para gerar cenário com partidas com diferentes cargas físicas para testes.
    if not os.path.exists("state.json"):
        dummy = {
            "reservations": [
                {"account_id": "Acc_Principal", "date": "2026-05-10", "hour": "08:00", "status": "confirmed"},
                {"account_id": "Acc_Amigos02", "date": "2026-05-10", "hour": "09:00", "status": "confirmed"},
                {"account_id": "Acc_Principal", "date": "2026-05-12", "hour": "18:00", "status": "confirmed"},
                {"account_id": "Acc_EmpresaX", "date": "2026-05-12", "hour": "19:00", "status": "confirmed"},
                {"account_id": "Acc_Amigos02", "date": "2026-05-12", "hour": "20:00", "status": "confirmed"},
                {"account_id": "Acc_Principal", "date": "2026-05-14", "hour": "09:00", "status": "confirmed"},
                {"account_id": "Acc_Amigos02", "date": "2026-05-15", "hour": "08:00", "status": "confirmed"},
                {"account_id": "Acc_EmpresaX", "date": "2026-05-15", "hour": "09:00", "status": "confirmed"},
                {"account_id": "Acc_EmpresaX", "date": "2026-05-15", "hour": "10:00", "status": "confirmed"},
                {"account_id": "Acc_Principal", "date": "2026-05-15", "hour": "11:00", "status": "confirmed"},
                {"account_id": "Acc_Amigos02", "date": "2026-05-15", "hour": "14:00", "status": "confirmed"}, # Exemplo Survirval Massivo (5 hrs numa sexta!)
            ]
        }
        with open("state.json", "w") as f:
            json.dump(dummy, f)

@st.cache_data
def ingest_data():
    guarantee_engine_running()
    with open('state.json', 'r', encoding='utf-8') as f:
        df = pd.DataFrame(json.load(f)['reservations'])
        
    df = df[df['status'] == 'confirmed'].copy()
    if df.empty: return df
    
    df['dt_calc'] = pd.to_datetime(df['date'] + ' ' + df['hour'])
    df = df.sort_values(by=['dt_calc']).reset_index(drop=True)
    df['just_date'] = df['dt_calc'].dt.date
    
    semana_mapping = {0:'SEGUNDA', 1:'TERÇA', 2:'QUARTA', 3:'QUINTA', 4:'SEXTA', 5:'SÁBADO', 6:'DOMINGO'}
    df['br_dia'] = df['dt_calc'].dt.dayofweek.map(semana_mapping)
    return df

engine_df = ingest_data()

# ---------------------------------------------------------
# 4. VIEW RENDERING DA NARRATIVA NBA/SPORTS DA EQUIPE
# ---------------------------------------------------------
if engine_df.empty:
    st.info("QUADRA OFFLINE: Sem eventos esportivos na liga até o presente momento.")
    st.stop()

# Story 1.1: O Fôlego Totais Da Temporada Até Aqui e Próximo Jogo a pisar
kickoff = engine_df.iloc[0]
dia_mes = kickoff['dt_calc'].strftime('%d %b')
peak_hard = engine_df.groupby('date').size().max()

st.markdown('<div class="subtitle">ESTATÍSTICA ATUAL DA SQUADRA - LOG DA BASE COMPARTILHADA</div>', unsafe_allow_html=True)
st.markdown('<div class="title-banner">MATCHDAY HUB SQUADRA</div>', unsafe_allow_html=True)

# THE BIG SCREEN! Jumbotron indicando primeira bola quicando
st.markdown(f"""
<div class="next-match-jumbotron">
    <div class="jumbotron-bg-text">NEXT</div>
    <div>
        <span class="jumbo-badge">PRIMEIRO SAQUE PREVISTO: QUADRA AQUECENDO!</span>
        <div style="font-family:'Chakra Petch'; font-size:24px; color:#fff; font-weight:700;">{kickoff['br_dia']}, <span style="color:#00D2FF;">{dia_mes}</span></div>
        <div class="jumbo-clock">{kickoff['hour']} Hrs  — TIME AO CHÃO</div>
        <div style="color: #94a3b8; font-family:'Arial'; font-size:14px; margin-top:5px; z-index:2; position:relative;">Account Responsável: <b style="color:white">{kickoff['account_id']}</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

# STORY 1.2: Scoreboard do Torneio Inteiro Agrupado de vcs.
st.markdown(f"""
<div class="season-stats-container">
    <div class="stat-cube cube-hours">
        <div class="cube-label">Carga Volumétrica Assumida</div>
        <div class="cube-number">{len(engine_df)} <span style="font-size:20px;">hrs totais</span></div>
    </div>
    <div class="stat-cube cube-days">
        <div class="cube-label">Jornadas / Convocação em Dias</div>
        <div class="cube-number">{engine_df['just_date'].nunique()} <span style="font-size:20px;">Rodadas Fixas</span></div>
    </div>
    <div class="stat-cube cube-pico">
        <div class="cube-label">Grau Máximo de Estamina Detectada Num Único Dia</div>
        <div class="cube-number">{peak_hard} <span style="font-size:20px;">hrs corridas em PICO.</span></div>
    </div>
</div>
""", unsafe_allow_html=True)


# STORY 2: GAME DAY BY GAME DAY TIMELINES & PLAY ANALYTICS WITH ANIMATED ENDURANCE PROGRESS 
st.markdown('<div class="match-calendar-title"><span>FIXTURE REPORTS DA NOSSA ARENA DIÁRIA</span> AVISOS CLÍNICOS E O MOTOR FISIOLÓGICO:</div>', unsafe_allow_html=True)

html_fixture = '<div class="grid-container">'
bateria_total = engine_df.groupby(['just_date', 'br_dia'])

for (obj_dt, diastr), matches in bateria_total:
    duration_hs = len(matches)
    dat_str = obj_dt.strftime('%d/%m')
    
    # Motor de Jogo calculando resistência Base (O Game tem um cap teórico fictício pro player barra verde que usamos de ref 1 até as ~6 horas)
    fill_percent = min((duration_hs / 5) * 100, 100) # Se marcar 5 hs no memo dia dá 100% cap

    if duration_hs <= 2:
        game_css_mode = "mode-warmup"
        urgencia = "AQUECIMENTO PADRÃO / TÁTICO - ROTINA LIVRE E CONFORTÁVEL"
        desc = "Carga leve associada. Níveis aeróbicos previstos ficam seguros; o gasto calórico operando baixo exige no maximo dois rounds em blocos fluidos dos set ups. Beba Água antes do primeiro saque apenas, sem tensão no gás."
        adtn_box_pulse = "" 
    elif duration_hs == 3:
        game_css_mode = "mode-game"
        urgencia = "ZONA INTENSA ENTRADA EM QUADRA ALERTA. "
        desc = "O Esforço foi acionado com uma bateria robusta! Time subirá exigência cardio alta. Recomendação técnica pro Squadra agendador dos horários interlaçados — Foquem rodizios firmes para respirarem entre cada time da rede externa!!"
        adtn_box_pulse = "" 
    else: 
        game_css_mode = "mode-survival"
        urgencia = "[!_ZONA RED DE REDES CORTES ESTAMINA RED_ZONE]"
        desc = "Sobrecarga de Eventos Maciça Marcada. Mais de três lotes! ATUALIZAR GELO E ÁGUA RESERVAS NA SQUAD! Time submetido sob altíssimo gasto — Criei turnos nas contas em conjunto — Ninguem sobreviverá full sem reservas fora em quadra! O GAME DAY FICOU SURVIVOR NO ROLO!!!"
        adtn_box_pulse = "survival-border"

    # Montando a Playlist de jogo
    log_jogadas = ""
    for _, lz in matches.iterrows():
         log_jogadas += f'<div class="time-slot"><div class="badge-hour">{lz["hour"]}</div><div class="badge-user">Reserva ativa root :: <span>{lz["account_id"]}</span></div></div>'
        
    html_fixture += f"""
    <div class="fixture-card {adtn_box_pulse} {game_css_mode}">
        <div class="fixture-header">
            <div class="date-day">{diastr} / {dat_str}</div>
            <div class="hours-vol">{duration_hs} HORAS DURAÇÃO BASE LOAD!</div>
        </div>
        
        <div class="fixture-body">
            {log_jogadas}
        </div>
        
        <!-- ESTAMINA DO TEAM SIMULATOR PARA PARTIDA -->
        <div class="engine-section">
             <div class="engine-header">
                 <div class="engine-title">MÉTRICA CINETÍCA CARDIO: SQUAD ENGINE CHECK</div>
                 <div class="engine-level">{urgencia}</div>
             </div>
             
             <div class="stamina-track">
                <!-- Inline variable bar push length do css engine pra o front -->
                <div class="stamina-fill" style="width: {fill_percent}%"></div>
             </div>
             <div class="sys-report" style="color:#64748b;">Relato Técnico P/ Carga Da Roda: <span style="color:#334155; font-style:italic;">"{desc}"</span></div>
        </div>
        
    </div>
    """
    
html_fixture += "</div>"
st.markdown(html_fixture, unsafe_allow_html=True)