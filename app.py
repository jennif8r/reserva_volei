import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Vôlei Praça Osvaldo | Hub da Equipe", layout="wide", initial_sidebar_state="collapsed")

css_code = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;600;700&family=Chakra+Petch:ital,wght@0,600;0,700;1,700&display=swap');

    /* BASE DA PLATAFORMA DA PRAÇA */
    [data-testid="stAppViewContainer"] { background-color: #f6f7fb !important; background-image: radial-gradient(#d3dce6 1px, transparent 1px); background-size: 20px 20px;}
    header[data-testid="stHeader"] { display: none; }
    
    .block-container { max-width: 1400px; padding-top: 1rem; padding-bottom: 3rem; font-family: 'Chakra Petch', sans-serif; }
    h1, h2, h3, h4 { text-transform: uppercase; margin: 0; padding: 0; line-height: 1; }

    /* ANIMAÇÕES ESPORTIVAS */
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

    /* TÍTULO PRINCIPAL & ASSINATURA DA EQUIPE LGBT+ */
    .title-banner { font-family: 'Teko', sans-serif; font-size: 75px; font-weight: 700; color: #111; letter-spacing: -1px; position: relative; margin-bottom: 25px; margin-top: 20px; display: inline-block; }
    
    /* RAINBOW SPORTS STRIPE (Toque Pride Neon Moderno Sem Emoji) */
    .title-banner::after { 
        content: ''; position: absolute; left: 0; bottom: -5px; width: 60%; height: 7px; 
        background: linear-gradient(90deg, #FF0018 0%, #FFA52C 20%, #FFFF41 40%, #008018 60%, #0000F9 80%, #86007D 100%); 
        transform: skewX(-25deg); 
    }
    
    .subtitle { font-family: 'Chakra Petch', sans-serif; color: #444; font-size: 17px; font-style: italic; letter-spacing: 3px; font-weight: 600; text-transform: uppercase;}

    /* TELÃO JUMBOTRON DA PRAÇA */
    .next-match-jumbotron { background: linear-gradient(135deg, #09131d 0%, #172433 100%); position: relative; overflow: hidden; border-radius: 12px; padding: 40px; margin-bottom: 40px; display: flex; flex-direction: column; border-left: 8px solid #ff0055; box-shadow: 0 15px 35px -5px rgba(0,0,0,0.15); animation: slideInDown 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .jumbotron-bg-text { position: absolute; right: -20px; top: -50px; font-family: 'Teko', sans-serif; font-size: 300px; color: rgba(255,255,255,0.03); line-height: 1; font-weight: 700; transform: skewX(-5deg); z-index: 1; white-space: nowrap; }
    .jumbo-badge { display: inline-block; padding: 5px 12px; background: #FFD700; color: #111; font-size: 13px; font-weight: 800; letter-spacing: 2px; transform: skewX(-15deg); margin-bottom: 15px; z-index: 2; position: relative; box-shadow: 0 4px 10px rgba(0,0,0,0.5);}
    .jumbo-clock { font-size: 45px; font-family: 'Teko', sans-serif; font-weight: 600; color: #FFF; margin-top: 5px; text-shadow: 0 0 10px rgba(255,0,85,0.4); z-index: 2; position: relative; }

    /* KPIS SQUAD SCOREBOARD */
    .season-stats-container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; animation: slideInDown 0.7s; }
    .stat-cube { background: #fff; border: 2px solid #e1e8ed; padding: 25px; border-radius: 8px; position: relative; text-align: left; }
    .stat-cube::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; border-radius: 6px 0 0 6px; }
    .cube-hours::before { background: #3b82f6; } 
    .cube-days::before { background: #ff0055; }   
    .cube-pico::before { background: #FF2A46; }    
    .cube-label { color: #64748b; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;}
    .cube-number { font-family: 'Teko', sans-serif; font-size: 55px; line-height: 0.9; color: #0b0e14;}

    /* CALENDÁRIO DA OSVALDO */
    .match-calendar-title { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; font-size: 26px; font-style: italic;}
    .match-calendar-title span { background: #111; color: white; padding: 6px 16px; transform: skewX(-15deg); font-weight: 700;}
    .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; animation: slideInDown 0.9s; }

    /* OS CARTOES DA QUADRA DE RUA */
    .fixture-card { background: white; display: flex; flex-direction: column; border: 1px solid #dbe2e8; padding-bottom: 0px; position: relative; overflow: hidden; clip-path: polygon(0 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%); }
    .fixture-header { background: #0f172a; padding: 20px; display: flex; justify-content: space-between; align-items: baseline; position: relative; }
    .date-day { font-size: 24px; color: #fff; font-family: 'Chakra Petch'; font-style: italic; font-weight: 700;}
    .hours-vol { background: #FFD700; color: #111; padding: 4px 10px; font-weight: 800; font-size: 14px; font-family: 'Arial'; border-radius: 4px; box-shadow: inset 0 -3px 0 rgba(0,0,0,0.2);}
    .fixture-body { padding: 20px 25px 0 25px; background: url('https://www.transparenttextures.com/patterns/clean-gray-paper.png'); background-color: #fbfdff;}
    
    .time-slot { display: flex; gap: 15px; margin-bottom: 12px; align-items: center; border-left: 2px solid #e1e8ed; padding-left: 10px; }
    .badge-hour { font-family: 'Teko', sans-serif; font-size: 22px; color: #111; padding: 0px 8px; min-width: 65px; border-bottom: 2px solid #ff0055; text-align: center; font-weight:600;}
    .badge-user { font-family: 'Chakra Petch'; color: #475569; font-size: 14px; font-weight: 600; text-transform: uppercase; }

    /* ESTAMINA FISIOLÓGICA & NARRATIVA DO SQUAD */
    .engine-section { padding: 20px 25px; border-top: 1px dashed #cbd5e1; margin-top: 10px; background: white;}
    .engine-header { display: flex; justify-content: space-between; font-size: 13px; font-weight: 800; color: #475569; margin-bottom: 12px;}
    .stamina-track { width: 100%; height: 16px; background: #e2e8f0; position: relative; border-radius: 10px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px;}
    .stamina-fill { height: 100%; border-radius: 10px; animation: barFill 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; position: relative; overflow: hidden; }
    .stamina-fill::after { content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(-45deg, rgba(255,255,255,0.25) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.25) 50%, rgba(255,255,255,0.25) 75%, transparent 75%, transparent); background-size: 15px 15px; z-index: 1; opacity: 0.8; }
    .sys-report { font-family: 'Arial'; font-size: 12px; font-weight: 600; line-height: 1.4; margin-top: 5px; }

    /* MÓDULOS DE AVISO DA ENERGIA (Diferença entre ferver ou relaxar) */
    .mode-warmup .stamina-fill { background: linear-gradient(90deg, #3b82f6, #00D2FF); }
    .mode-warmup .engine-level { color: #2563eb; }
    .mode-game .stamina-fill { background: linear-gradient(90deg, #fbbf24, #FAD201); }
    .mode-game .engine-level { color: #d97706; }
    .mode-survival .stamina-fill { background: linear-gradient(90deg, #ef4444, #dc2626); }
    .mode-survival .engine-level { color: #dc2626; font-weight: 800; animation: pulseAlert 1.5s infinite;}
    .survival-border { animation: pulseAlert 1.5s infinite alternate !important; border: 2px solid #ef4444; clip-path: none;}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

def generate_sample_if_none():
    if not os.path.exists("state.json"):
        dummy = {
            "reservations": [
                {"account_id": "Conta_Matriz", "date": "2026-05-10", "hour": "08:00", "status": "confirmed"},
                {"account_id": "Reserva_Amigo", "date": "2026-05-10", "hour": "09:00", "status": "confirmed"},
                {"account_id": "Conta_Matriz", "date": "2026-05-12", "hour": "18:00", "status": "confirmed"},
                {"account_id": "AmigaX", "date": "2026-05-12", "hour": "19:00", "status": "confirmed"},
                {"account_id": "Conta_Matriz", "date": "2026-05-12", "hour": "20:00", "status": "confirmed"},
                {"account_id": "Conta_Matriz", "date": "2026-05-15", "hour": "08:00", "status": "confirmed"},
                {"account_id": "AmigaX", "date": "2026-05-15", "hour": "09:00", "status": "confirmed"},
                {"account_id": "AmigaX", "date": "2026-05-15", "hour": "10:00", "status": "confirmed"},
                {"account_id": "Reserva_Amigo", "date": "2026-05-15", "hour": "11:00", "status": "confirmed"}
            ]
        }
        with open("state.json", "w") as f:
            json.dump(dummy, f)

@st.cache_data
def get_league_data():
    generate_sample_if_none()
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

df_jogo = get_league_data()

if df_jogo.empty:
    st.info("QUADRA DA PRAÇA OFFLINE: Nosso time não marcou jogada para o período consultado.")
    st.stop()

primeira_bola = df_jogo.iloc[0]
dia_mes = primeira_bola['dt_calc'].strftime('%d %b')
pico_semana = df_jogo.groupby('date').size().max()

st.markdown('<div class="subtitle">ARENA OSVALDO — O HUB OFICIAL DA NOSSA SQUAD</div>', unsafe_allow_html=True)
st.markdown('<div class="title-banner">PRIDE COURT</div>', unsafe_allow_html=True)

html_topo = f"""<div class="next-match-jumbotron">
<div class="jumbotron-bg-text">OSVALDO</div>
<div>
<span class="jumbo-badge">BOLA AO ALTO — PRIMEIRA JANELA DE JOGO ABERTA</span>
<div style="font-family:'Chakra Petch'; font-size:26px; color:#fff; font-weight:700; margin-top: 5px;">{primeira_bola['br_dia']}, <span style="color:#ff0055;">{dia_mes}</span></div>
<div class="jumbo-clock">{primeira_bola['hour']} HRS — A REDE TE CHAMA</div>
<div style="color: #cbd5e1; font-family:'Arial'; font-size:14px; margin-top:8px; z-index:2; position:relative; text-transform:uppercase;">Identificação Log Praça via: <b style="color:white">{primeira_bola['account_id']}</b></div>
</div>
</div>
"""
st.markdown(html_topo, unsafe_allow_html=True)

html_stats = f"""<div class="season-stats-container">
<div class="stat-cube cube-hours">
<div class="cube-label">Carga Volumétrica Em Aberto</div>
<div class="cube-number">{len(df_jogo)} <span style="font-size:22px;">hs garantidas na praça</span></div>
</div>
<div class="stat-cube cube-days">
<div class="cube-label">Diárias Presenciais Firmadas</div>
<div class="cube-number">{df_jogo['just_date'].nunique()} <span style="font-size:22px;">Días para estarmos juntas</span></div>
</div>
<div class="stat-cube cube-pico">
<div class="cube-label">Lote Cinetico Massivo Estimado</div>
<div class="cube-number">{pico_semana} <span style="font-size:22px;">hs agrupadas no PICO.</span></div>
</div>
</div>
"""
st.markdown(html_stats, unsafe_allow_html=True)

st.markdown('<div class="match-calendar-title"><span>OCUPAÇÕES DE CIMENTO</span> RAIO X DO CORTADOR OFICIAL DA EQUIPE:</div>', unsafe_allow_html=True)

html_fixture = '<div class="grid-container">'
grupo_dias = df_jogo.groupby(['just_date', 'br_dia'])

for (obj_dt, diastr), matches in grupo_dias:
    horas = len(matches)
    dstr = obj_dt.strftime('%d/%m')
    fill_bar = int(min((horas / 5) * 100, 100))

    if horas <= 2:
        tipo, aviso = "mode-warmup", "TREINO SOLTO E RESENHA MODERADA"
        dica, adcional = "O tempo reservado garante saques relaxados e fôlego à disposição sem estressar as panturrilhas pro resto da semana do time.", "" 
    elif horas == 3:
        tipo, aviso = "mode-game", "JOGO PEGADO — EXIGÊNCIA ATLÉTICA PRESENTE"
        dica, adcional = "Aqui já tem close físico acontecendo na Osvaldo! Garantir banco de rodízio bom na sombra pra recuperar aeróbico antes da próxima pontuação pesada das partidas contínuas.", "" 
    else: 
        tipo, aviso = "mode-survival", "[ ! CHÃO QUENTE - O PICO DA ESTAMINA GERAL ACIONOU ! ]"
        dica, adcional = "QUATRO+ HORAS AGENDADAS CONSECUTIVAMENTE HOJE? Isso é Resistência Extrema das Cortadoras da praça. Ninguém pisa hoje em quadra de estômago vazio: Organizem rodizio tático e providenciem bastante hidratação coletiva e perna forte pro sol!!", "survival-border"

    slots = "".join([f'<div class="time-slot"><div class="badge-hour">{lz["hour"]}</div><div class="badge-user">Reserva efetuada p/:: <span style="color:#000;">{lz["account_id"]}</span></div></div>' for _, lz in matches.iterrows()])

    html_fixture += f"""<div class="fixture-card {tipo} {adcional}">
<div class="fixture-header"><div class="date-day">{diastr} / {dstr}</div><div class="hours-vol">{horas} HRS JOGADOS!</div></div>
<div class="fixture-body">{slots}</div>
<div class="engine-section">
<div class="engine-header"><div class="engine-title" style="font-weight:900;">PREVISÃO CALÓRICA DIÁRIA DO SQUAD</div><div class="engine-level">{aviso}</div></div>
<div class="stamina-track"><div class="stamina-fill" style="width: {fill_bar}%;"></div></div>
<div class="sys-report" style="color:#64748b;">Conselho Tático Quadra Externa: <span style="color:#0f172a;">"{dica}"</span></div>
</div>
</div>"""

html_fixture += '</div>'
st.markdown(html_fixture, unsafe_allow_html=True)