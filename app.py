#!/usr/bin/env python3
"""
🏐 Dashboard Profissional de Reservas de Vôlei
─────────────────────────────────────────────────
Um dashboard moderno, intuitivo e encantador para gerenciar
e visualizar reservas de quadra de vôlei.

Execute com: streamlit run dashboard.py
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import date, timedelta
from typing import Optional

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

# ═══════════════════════════════════════════════════════════════════
# 🎨 PAGE CONFIG & DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Reservas · Vôlei 🏐",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# 🎭 DESIGN TOKENS & VARIABLES
# ─────────────────────────────────────────────────────────────────
class Colors:
    """Sistema de cores elegante e coerente"""
    # Primário
    PRIMARY_BLUE = "#3b82f6"
    PRIMARY_DARK = "#1e3a8a"
    
    # Status
    CONFIRMED = "#10b981"
    PENDING = "#f59e0b"
    CANCELLED = "#ef4444"
    
    # Neutros
    BG_DARK = "#0f1219"
    BG_CARD = "#151b28"
    BG_LIGHT = "#1a2139"
    
    TEXT_PRIMARY = "#f0f4f8"
    TEXT_SECONDARY = "#8b95a5"
    TEXT_MUTED = "#596578"
    
    BORDER = "#233047"
    BORDER_SUBTLE = "#1a2839"
    
    # Accent
    ACCENT_PURPLE = "#a78bfa"
    ACCENT_CYAN = "#06b6d4"
    ACCENT_EMERALD = "#10b981"

# ─────────────────────────────────────────────────────────────────
# 🎨 GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@400;600;700;800&display=swap');

    :root {{
        --primary: {Colors.PRIMARY_BLUE};
        --confirmed: {Colors.CONFIRMED};
        --pending: {Colors.PENDING};
        --cancelled: {Colors.CANCELLED};
        --bg-dark: {Colors.BG_DARK};
        --bg-card: {Colors.BG_CARD};
        --text-primary: {Colors.TEXT_PRIMARY};
        --text-secondary: {Colors.TEXT_SECONDARY};
        --border: {Colors.BORDER};
    }}

    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .stApp {{
        background: {Colors.BG_DARK};
        color: {Colors.TEXT_PRIMARY};
    }}

    /* ─── SIDEBAR ─── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {Colors.BG_CARD} 0%, {Colors.BG_LIGHT} 100%) !important;
        border-right: 1px solid {Colors.BORDER_SUBTLE};
    }}

    section[data-testid="stSidebar"] [data-baseweb="select"] {{
        background: {Colors.BG_LIGHT} !important;
        border-color: {Colors.BORDER} !important;
    }}

    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
        background: {Colors.PRIMARY_DARK} !important;
        color: {Colors.PRIMARY_BLUE} !important;
        border-color: {Colors.PRIMARY_BLUE} !important;
    }}

    /* ─── TYPOGRAPHY ─── */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }}

    h1 {{
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, {Colors.TEXT_PRIMARY} 0%, {Colors.ACCENT_CYAN} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    h2 {{
        font-size: 1.4rem !important;
        color: {Colors.TEXT_PRIMARY} !important;
    }}

    /* ─── DIVIDERS ─── */
    hr {{
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, {Colors.BORDER} 50%, transparent 100%);
        margin: 2rem 0 !important;
    }}

    /* ─── METRIC CARDS ─── */
    .metric-card {{
        background: linear-gradient(135deg, {Colors.BG_CARD} 0%, {Colors.BG_LIGHT} 100%);
        border: 1px solid {Colors.BORDER};
        border-radius: 18px;
        padding: 24px;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}

    .metric-card::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, {Colors.PRIMARY_BLUE} 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s;
    }}

    .metric-card:hover {{
        border-color: {Colors.PRIMARY_BLUE};
        box-shadow: 0 0 24px rgba(59, 130, 246, 0.15);
        transform: translateY(-2px);
    }}

    .metric-card:hover::before {{
        opacity: 0.05;
    }}

    .metric-label {{
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {Colors.TEXT_MUTED};
        margin-bottom: 12px;
        display: block;
    }}

    .metric-value {{
        font-family: 'Syne', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, {Colors.TEXT_PRIMARY} 0%, {Colors.PRIMARY_BLUE} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }}

    .metric-sub {{
        font-size: 0.8rem;
        color: {Colors.TEXT_SECONDARY};
        margin-top: 8px;
    }}

    /* ─── STATUS BADGES ─── */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 99px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        transition: all 0.2s;
    }}

    .badge-confirmed {{
        background: rgba(16, 185, 129, 0.15);
        color: {Colors.CONFIRMED};
        border: 1px solid {Colors.CONFIRMED};
    }}

    .badge-pending {{
        background: rgba(245, 158, 11, 0.15);
        color: {Colors.PENDING};
        border: 1px solid {Colors.PENDING};
    }}

    .badge-cancelled {{
        background: rgba(239, 68, 68, 0.15);
        color: {Colors.CANCELLED};
        border: 1px solid {Colors.CANCELLED};
    }}

    /* ─── DAY CARD ─── */
    .day-card {{
        background: linear-gradient(135deg, {Colors.BG_CARD} 0%, {Colors.BG_LIGHT} 100%);
        border: 1px solid {Colors.BORDER};
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .day-card::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        width: 4px;
        height: 0;
        background: linear-gradient(180deg, {Colors.PRIMARY_BLUE}, {Colors.ACCENT_CYAN});
        transition: height 0.4s ease;
    }}

    .day-card.has-reservations::before {{
        height: 100%;
    }}

    .day-card:hover {{
        border-color: {Colors.PRIMARY_BLUE};
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
        transform: translateY(-2px);
    }}

    .day-header {{
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 18px;
        padding-bottom: 14px;
        border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    }}

    .day-name {{
        font-family: 'Syne', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: {Colors.TEXT_PRIMARY};
    }}

    .day-date {{
        font-size: 0.85rem;
        color: {Colors.TEXT_SECONDARY};
    }}

    .day-today {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {Colors.PRIMARY_DARK};
        color: {Colors.PRIMARY_BLUE};
        padding: 4px 12px;
        border-radius: 99px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-left: auto;
    }}

    /* ─── SLOT ROWS ─── */
    .slot-row {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 12px 0;
        border-bottom: 1px solid {Colors.BORDER_SUBTLE};
        transition: background 0.2s;
    }}

    .slot-row:last-child {{
        border-bottom: none;
    }}

    .slot-row:hover {{
        background: {Colors.BG_LIGHT};
        border-radius: 12px;
        padding: 12px 12px;
        margin: 0 -12px;
    }}

    .slot-time {{
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: {Colors.PRIMARY_BLUE};
        min-width: 60px;
    }}

    .slot-account {{
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        font-size: 0.95rem;
        font-weight: 600;
        color: {Colors.TEXT_PRIMARY};
    }}

    .slot-status {{
        margin-left: auto;
    }}

    /* ─── TODAY BANNER ─── */
    .today-banner {{
        background: linear-gradient(135deg, {Colors.PRIMARY_DARK} 0%, rgba(59, 130, 246, 0.1) 100%);
        border: 2px solid {Colors.PRIMARY_BLUE};
        border-radius: 24px;
        padding: 28px 32px;
        margin-bottom: 32px;
        display: flex;
        align-items: center;
        gap: 24px;
        position: relative;
        overflow: hidden;
    }}

    .today-banner::before {{
        content: '';
        position: absolute;
        top: -100%;
        right: -100%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, {Colors.PRIMARY_BLUE} 0%, transparent 70%);
        opacity: 0.05;
        border-radius: 50%;
    }}

    .today-emoji {{
        font-size: 3rem;
        animation: pulse 2s ease-in-out infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.08); }}
    }}

    .today-text {{
        flex: 1;
        z-index: 1;
    }}

    .today-title {{
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: {Colors.TEXT_PRIMARY};
        margin-bottom: 6px;
    }}

    .today-sub {{
        font-size: 0.95rem;
        color: {Colors.TEXT_SECONDARY};
    }}

    /* ─── OCCUPANCY BAR ─── */
    .occupancy-bar {{
        height: 8px;
        background: {Colors.BORDER};
        border-radius: 99px;
        margin: 14px 0;
        overflow: hidden;
        position: relative;
    }}

    .occupancy-bar-fill {{
        height: 100%;
        border-radius: 99px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(90deg, {Colors.PRIMARY_BLUE} 0%, {Colors.ACCENT_CYAN} 100%);
    }}

    .occupancy-bar-fill.high {{
        background: linear-gradient(90deg, {Colors.PENDING} 0%, {Colors.CANCELLED} 100%);
    }}

    .occupancy-info {{
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: {Colors.TEXT_MUTED};
    }}

    /* ─── SECTION TITLE ─── */
    .section-title {{
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 800;
        color: {Colors.TEXT_PRIMARY};
        letter-spacing: -0.01em;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    /* ─── TIMELINE ─── */
    .timeline {{
        background: {Colors.BG_LIGHT};
        border: 1px solid {Colors.BORDER};
        border-radius: 18px;
        padding: 20px;
    }}

    .timeline-item {{
        display: flex;
        gap: 16px;
        padding: 14px 0;
        border-bottom: 1px solid {Colors.BORDER_SUBTLE};
        transition: background 0.2s;
    }}

    .timeline-item:last-child {{
        border-bottom: none;
    }}

    .timeline-item:hover {{
        background: {Colors.BG_CARD};
        border-radius: 12px;
        padding: 14px 12px;
        margin: 0 -12px;
    }}

    .timeline-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-top: 4px;
        flex-shrink: 0;
        border: 2px solid {Colors.BORDER};
        transition: all 0.2s;
    }}

    .timeline-dot.confirmed {{
        background: {Colors.CONFIRMED};
        border-color: {Colors.CONFIRMED};
    }}

    .timeline-dot.pending {{
        background: {Colors.PENDING};
        border-color: {Colors.PENDING};
    }}

    .timeline-dot.cancelled {{
        background: {Colors.CANCELLED};
        border-color: {Colors.CANCELLED};
    }}

    .timeline-content {{
        flex: 1;
        min-width: 0;
    }}

    .timeline-time {{
        font-family: 'Syne', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: {Colors.PRIMARY_BLUE};
    }}

    .timeline-account {{
        font-size: 0.9rem;
        color: {Colors.TEXT_PRIMARY};
        font-weight: 600;
        margin-top: 2px;
    }}

    .timeline-date {{
        font-size: 0.75rem;
        color: {Colors.TEXT_MUTED};
        margin-top: 4px;
    }}

    /* ─── SUMMARY CARD ─── */
    .summary-card {{
        background: {Colors.BG_LIGHT};
        border: 1px solid {Colors.BORDER};
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }}

    .summary-card:hover {{
        border-color: {Colors.PRIMARY_BLUE};
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
    }}

    .summary-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
    }}

    .summary-account {{
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        color: {Colors.TEXT_PRIMARY};
        flex: 1;
    }}

    .summary-bar {{
        height: 6px;
        background: {Colors.BORDER};
        border-radius: 99px;
        margin: 10px 0;
        overflow: hidden;
    }}

    .summary-bar-fill {{
        height: 100%;
        border-radius: 99px;
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* ─── HIDDEN ELEMENTS ─── */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}

    /* ─── SCROLLBAR ─── */
    ::-webkit-scrollbar {{
        width: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: {Colors.BG_DARK};
    }}

    ::-webkit-scrollbar-thumb {{
        background: {Colors.BORDER};
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {Colors.PRIMARY_BLUE};
    }}

    /* ─── ANIMATIONS ─── */
    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}

    .stMetric {{
        animation: slideIn 0.4s ease forwards;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════
# 📊 DATA LOADING & PROCESSING
# ═══════════════════════════════════════════════════════════════════

# Constantes
WEEKDAYS_PT = {
    "Monday": "Segunda",
    "Tuesday": "Terça",
    "Wednesday": "Quarta",
    "Thursday": "Quinta",
    "Friday": "Sexta",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

WEEKDAYS_FULL = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

ACCOUNT_COLORS = [
    "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b",
    "#10b981", "#06b6d4", "#84cc16", "#f97316",
]

MAX_HOURS_PER_DAY = 14


def get_account_color(account: str, accounts: list[str]) -> str:
    """Retorna cor consistente para uma conta"""
    try:
        idx = accounts.index(account) % len(ACCOUNT_COLORS)
    except (ValueError, IndexError):
        idx = 0
    return ACCOUNT_COLORS[idx]


@st.cache_data(show_spinner=False)
def load_reservations() -> pd.DataFrame:
    """Carrega e processa dados do state.json"""
    data_file = Path(__file__).parent / "state.json"
    
    if not data_file.exists():
        raise FileNotFoundError(
            f"❌ Arquivo não encontrado: {data_file}\n\n"
            "Coloque o `state.json` na mesma pasta que este script."
        )
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    reservations = data.get("reservations", [])
    if not reservations:
        return pd.DataFrame()
    
    df = pd.DataFrame(reservations)
    
    # Validar colunas
    required = ["account_id", "date", "hour", "status"]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    
    # Processar datas
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_only"] = df["date"].dt.date
    df["date_label"] = df["date"].dt.strftime("%d/%m/%Y")
    df["weekday_en"] = df["date"].dt.day_name()
    df["weekday"] = df["weekday_en"].map(WEEKDAYS_PT)
    df["weekday_full"] = df["weekday_en"].map(WEEKDAYS_FULL)
    df["status_label"] = df["status"].map({
        "confirmed": "Confirmada",
        "pending": "Pendente",
        "cancelled": "Cancelada",
    }).fillna(df["status"])
    
    df["datetime"] = pd.to_datetime(
        df["date"].dt.strftime("%Y-%m-%d") + " " + df["hour"],
        errors="coerce"
    )
    
    return df.sort_values(["date", "hour"]).reset_index(drop=True)


# Carregar dados
try:
    df_raw = load_reservations()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

if df_raw.empty:
    st.warning("⚠️ Nenhuma reserva encontrada no `state.json`")
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# 🎛️ SIDEBAR - FILTROS
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo/Título
    st.markdown(
        """
        <div style="padding: 16px 0 28px; text-align: center; border-bottom: 1px solid #233047;">
            <div style="font-size: 2.5rem;">🏐</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; 
                        color:#f0f4f8; margin-top:8px;">Vôlei</div>
            <div style="font-size:0.8rem; color:#596578; margin-top:4px;">Gestão de Quadra</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("### 📅 Período")
    available_dates = sorted(df_raw["date_only"].dropna().unique())
    selected_dates = st.multiselect(
        "Selecione as datas",
        options=available_dates,
        default=available_dates,
        format_func=lambda d: d.strftime("%a, %d/%m"),
        label_visibility="collapsed",
    )
    
    st.markdown("### 👤 Contas")
    available_accounts = sorted(df_raw["account_id"].dropna().unique())
    selected_accounts = st.multiselect(
        "Selecione as contas",
        options=available_accounts,
        default=available_accounts,
        label_visibility="collapsed",
    )
    
    st.markdown("### 🔖 Status")
    available_status = ["Confirmada", "Pendente", "Cancelada"]
    selected_status = st.multiselect(
        "Selecione os status",
        options=available_status,
        default=["Confirmada", "Pendente"],
        label_visibility="collapsed",
    )
    
    # Footer sidebar
    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.75rem; color:#4a5a73; text-align:center;">'
        '📂 Lendo dados de <code>state.json</code>'
        '</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════
# 🔍 FILTRAR DADOS
# ═══════════════════════════════════════════════════════════════════

df = df_raw[
    df_raw["date_only"].isin(selected_dates)
    & df_raw["account_id"].isin(selected_accounts)
    & df_raw["status_label"].isin(selected_status)
].copy()

all_accounts = sorted(df_raw["account_id"].dropna().unique().tolist())

# ═══════════════════════════════════════════════════════════════════
# 📱 HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div style="padding: 12px 0;">
        <h1>Reservas de Quadra</h1>
        <p style="color:#8b95a5; font-size:0.95rem; margin-top:8px;">
            Visão em tempo real da ocupação e horários disponíveis
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════
# 🎯 TODAY BANNER
# ═══════════════════════════════════════════════════════════════════

today = date.today()
today_df = df[df["date_only"] == today]
today_confirmed = today_df[today_df["status"] == "Confirmada"]

if not today_df.empty:
    hours_today = len(today_confirmed)
    accounts_today = list(today_confirmed["account_id"].unique())
    times_str = " · ".join(sorted(today_confirmed["hour"].tolist()))
    accounts_str = " · ".join(sorted(accounts_today))
    
    st.markdown(
        f"""
        <div class="today-banner">
            <div class="today-emoji">🟢</div>
            <div class="today-text">
                <div class="today-title">Hoje tem vôlei!</div>
                <div class="today-sub">
                    {hours_today}h confirmada{'s' if hours_today != 1 else ''} 
                    · {accounts_str} · {times_str}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Próxima reserva
    future = df[df["date_only"] > today].sort_values("date")
    if not future.empty:
        next_date = future["date_only"].iloc[0]
        next_label = future["date_label"].iloc[0]
        next_wd = future["weekday_full"].iloc[0]
        delta = (next_date - today).days
        delta_str = f"em {delta} dia{'s' if delta > 1 else ''}"
        
        st.markdown(
            f"""
            <div class="today-banner" style="border-color:#a78bfa; 
                 background: linear-gradient(135deg, #2d1b4e 0%, rgba(167, 139, 250, 0.1) 100%);">
                <div class="today-emoji">📅</div>
                <div class="today-text">
                    <div class="today-title" style="background: linear-gradient(135deg, #d8b4fe 0%, #a78bfa 100%); 
                         -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                        Hoje não há reservas
                    </div>
                    <div class="today-sub" style="color:#9d7ab4;">
                        Próxima: {next_wd}, {next_label} — {delta_str}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="today-banner" style="border-color:#ef4444;
                 background: linear-gradient(135deg, #4a1f1f 0%, rgba(239, 68, 68, 0.1) 100%);">
                <div class="today-emoji">😴</div>
                <div class="today-text">
                    <div class="today-title" style="background: linear-gradient(135deg, #fca5a5 0%, #ef4444 100%);
                         -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                        Nenhuma reserva encontrada
                    </div>
                    <div class="today-sub" style="color:#c85a5a;">
                        Ajuste os filtros ou adicione dados ao state.json
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 📊 KPI CARDS
# ═══════════════════════════════════════════════════════════════════

confirmed_df = df[df["status"] == "Confirmada"]
total_hours = len(confirmed_df)
total_days = df["date_only"].nunique()
total_accounts = df["account_id"].nunique()
avg_hours_per_day = round(total_hours / total_days, 1) if total_days > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">Horas Confirmadas</span>
            <div class="metric-value">{total_hours}h</div>
            <span class="metric-sub">no período filtrado</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">Dias com Reserva</span>
            <div class="metric-value">{total_days}</div>
            <span class="metric-sub">agendados</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">Contas Ativas</span>
            <div class="metric-value">{total_accounts}</div>
            <span class="metric-sub">fazendo reservas</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">Média por Dia</span>
            <div class="metric-value">{avg_hours_per_day}h</div>
            <span class="metric-sub">ocupação média</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 📅 MAIN CONTENT: DIA-A-DIA | PAINEL LATERAL
# ═══════════════════════════════════════════════════════════════════

col_main, col_side = st.columns([2, 1], gap="large")

# ─────────────────────────────────────────────────────────────────
# 📆 DIA-A-DIA
# ─────────────────────────────────────────────────────────────────

with col_main:
    st.markdown('<div class="section-title">📆 Reservas por Dia</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.info("📭 Nenhuma reserva com os filtros aplicados.")
    else:
        grouped = df.groupby("date_only", sort=True)
        
        for dt, group in grouped:
            confirmed_g = group[group["status"] == "Confirmada"]
            n_hours = len(confirmed_g)
            occupancy_pct = min(n_hours / MAX_HOURS_PER_DAY, 1.0)
            is_today = dt == today
            is_busy = occupancy_pct >= 0.7
            
            weekday = group["weekday"].iloc[0]
            date_label = group["date_label"].iloc[0]
            
            # Today badge
            today_tag = (
                '<span class="day-today">📍 Hoje</span>'
                if is_today
                else ""
            )
            
            # Slots
            slots_html = ""
            for _, row in group.sort_values("hour").iterrows():
                acc_color = get_account_color(row["account_id"], all_accounts)
                status_badge = {
                    "Confirmada": f'<span class="badge badge-confirmed">✓ Confirmada</span>',
                    "Pendente": f'<span class="badge badge-pending">⏳ Pendente</span>',
                    "Cancelada": f'<span class="badge badge-cancelled">✗ Cancelada</span>',
                }.get(row["status_label"], f'<span class="badge">{row["status_label"]}</span>')
                
                slots_html += f"""
                <div class="slot-row">
                    <span class="slot-time">{row["hour"]}</span>
                    <span class="slot-account">
                        <span style="color:{acc_color}; font-size:1.2rem;">●</span>
                        {row["account_id"]}
                    </span>
                    <span class="slot-status">{status_badge}</span>
                </div>
                """
            
            # Barra de ocupação
            occupancy_color = "high" if is_busy else ""
            occupancy_bar = f"""
            <div class="occupancy-bar">
                <div class="occupancy-bar-fill {occupancy_color}" 
                     style="width: {int(occupancy_pct * 100)}%;"></div>
            </div>
            <div class="occupancy-info">
                <span>{n_hours}h confirmada{'s' if n_hours != 1 else ''}</span>
                <span>{int(occupancy_pct * 100)}% ocupação</span>
            </div>
            """
            
            st.markdown(
                f"""
                <div class="day-card {'has-reservations' if n_hours > 0 else ''}">
                    <div class="day-header">
                        <span class="day-name">{weekday}{today_tag}</span>
                        <span class="day-date">{date_label}</span>
                    </div>
                    {slots_html}
                    {occupancy_bar}
                </div>
                """,
                unsafe_allow_html=True,
            )

# ─────────────────────────────────────────────────────────────────
# 📋 PAINEL LATERAL
# ─────────────────────────────────────────────────────────────────

with col_side:
    # ⚡ Próximas reservas
    st.markdown('<div class="section-title">⚡ Próximas</div>', unsafe_allow_html=True)
    
    upcoming = df[
        (df["date_only"] >= today) & (df["status"] != "Cancelada")
    ].sort_values("datetime").head(10)
    
    if upcoming.empty:
        st.caption("Nenhuma reserva futura.")
    else:
        timeline_html = '<div class="timeline">'
        for _, row in upcoming.iterrows():
            acc_color = get_account_color(row["account_id"], all_accounts)
            is_today_item = row["date_only"] == today
            date_str = "Hoje" if is_today_item else row["date_label"]
            dot_class = row["status"].lower()
            
            timeline_html += f"""
            <div class="timeline-item">
                <div class="timeline-dot {dot_class}"></div>
                <div class="timeline-content">
                    <div class="timeline-time">{row["hour"]}</div>
                    <div class="timeline-account" style="color:{acc_color};">
                        {row["account_id"]}
                    </div>
                    <div class="timeline-date">{date_str}</div>
                </div>
            </div>
            """
        timeline_html += '</div>'
        st.markdown(timeline_html, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    # 👥 Resumo por conta
    st.markdown('<div class="section-title">👥 Por Conta</div>', unsafe_allow_html=True)
    
    summary = (
        confirmed_df.groupby("account_id", as_index=False)
        .agg(
            horas=("account_id", "count"),
            dias=("date_only", "nunique"),
        )
        .sort_values("horas", ascending=False)
    )
    
    if summary.empty:
        st.caption("Sem dados.")
    else:
        max_hours = summary["horas"].max()
        for _, row in summary.iterrows():
            acc_color = get_account_color(row["account_id"], all_accounts)
            bar_pct = int((row["horas"] / max_hours) * 100) if max_hours > 0 else 0
            
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-header">
                        <span style="color:{acc_color}; font-size:1.2rem;">●</span>
                        <span class="summary-account">{row["account_id"]}</span>
                        <span style="font-size:0.8rem; color:#8b95a5;">{row['dias']}d</span>
                    </div>
                    <div class="summary-bar">
                        <div class="summary-bar-fill" 
                             style="width: {bar_pct}%; background: {acc_color};"></div>
                    </div>
                    <div style="font-size:0.85rem; color:#596578; text-align:right; font-weight:600;">
                        {row["horas"]}h
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ═══════════════════════════════════════════════════════════════════
# 📋 RAW DATA
# ═══════════════════════════════════════════════════════════════════

st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)

with st.expander("🗂️ Ver dados brutos"):
    display_df = df[["date_label", "weekday", "hour", "account_id", "status_label"]].copy()
    display_df.columns = ["Data", "Dia", "Horário", "Conta", "Status"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown(
    '<div style="text-align:center; padding:40px 0 20px; font-size:0.8rem; color:#4a5a73;">'
    '🏐 Dashboard de Reservas de Vôlei · Lendo de state.json'
    '</div>',
    unsafe_allow_html=True,
)