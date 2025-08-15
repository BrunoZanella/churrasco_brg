import streamlit as st
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import pytz
from dateutil import parser
import time
import tempfile
import base64
from PIL import Image
import io

def image_to_base64(image_path):
    """Converte imagem para base64 para uso no CSS"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        else:
            # Se não encontrar a imagem, cria uma placeholder
            return None
    except Exception as e:
        st.error(f"Erro ao carregar imagem {image_path}: {e}")
        return None

# Configuração da página
st.set_page_config(
    page_title="Churrasco",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para estilo tech/Apple
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* CSS mais agressivo para remover espaçamentos superiores */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stApp {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }
    
    .stApp > header {
        height: 0px !important;
        display: none !important;
        visibility: hidden !important;
    }
    
    .main {
        padding: 0px !important;
        margin: 0px !important;
        padding-top: 0px !important;
        margin-top: 0px !important;
    }
    
    .main > div {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }
    
    .main .block-container {
        padding-top: 0px !important;
        margin-top: 0px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: none !important;
    }
    
    /* Remove todos os elementos do header do Streamlit */
    .stApp > div[data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    .stApp > div[data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    .stApp > div[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Remove qualquer padding/margin do viewport */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    .css-1d391kg, .css-18e3th9, .css-1y4p8pa {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }
    
    /* Hero header ajustado para compensar */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 14px;
        margin: 0px 0 2rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main {
        font-family: -apple-system, "SF Pro Display", Inter, "Segoe UI", Roboto, sans-serif;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .countdown {
        font-size: 1.5rem;
        font-weight: 600;
        background: rgba(255,255,255,0.2);
        padding: 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .glass-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .kpi-card {
        background: rgba(255,255,255,0.95);
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
    
    /* Barra de progresso customizada com Silvio Santos */
    .custom-progress-container {
        position: relative;
        width: 100%;
        height: 20px;
        background: linear-gradient(90deg, #e5e7eb 0%, #f3f4f6 100%);
        border-radius: 10px;
        margin: 1rem 0;
        overflow: visible;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .custom-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #10b981, #059669);
        border-radius: 10px;
        transition: width 0.5s ease;
        position: relative;
    }
    
    .silvio-indicator {
        position: absolute;
        top: -35px;
        right: -25px;
        width: 100px;
        height: 100px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: visible;
        transition: right 0.5s ease;
    }
    
    .silvio-indicator img {
        width: 100px;
        height: 100px;
        object-fit: contain;
    }
    
    /* Adicionando estilo para a porcentagem embaixo da imagem */
    .silvio-percentage {
        position: absolute;
        top: 90px;
        font-size: 14px;
        font-weight: 600;
        color: #1f2937;
        background: rgba(255, 255, 255, 0.9);
        padding: 2px 6px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        white-space: nowrap;
    }

    /* Adicionando estilos para modais */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-content {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: modalSlideIn 0.3s ease-out;
    }
    
    @keyframes modalSlideIn {
        from {
            opacity: 0;
            transform: translateY(-20px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .modal-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1f2937;
    }
    
    .modal-buttons {
        display: flex;
        gap: 1rem;
        justify-content: flex-end;
        margin-top: 1.5rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background: #f3f4f6;
        color: #374151;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s ease;
    }
    
    .btn-secondary:hover {
        background: #e5e7eb;
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .btn-danger:hover {
        transform: translateY(-1px);
    }
    
    /* Adicionando estilos para status de pagamento coloridos */
    .status-pago {
        color: #10b981 !important;
        font-weight: 600 !important;
    }
    
    .status-pendente {
        color: #ef4444 !important;
        font-weight: 600 !important;
    }
    
    /* Adicionando estilo para meses futuros */
    .status-futuro {
        color: #f97316 !important;
        font-weight: 600 !important;
    }

    /* Remove header/toolbar para eliminar o espaço superior */
    header[data-testid="stHeader"] { display: none; }
    div[data-testid="stToolbar"] { display: none; }

    /* Zera/ajusta o padding do container principal */
    div.block-container { padding-top: 0rem; }

    /* Fallbacks para diferentes versões */
    section.main > div.block-container { padding-top: 0rem; }
    section[data-testid="stMain"] { padding-top: 0rem; }      
</style>
""", unsafe_allow_html=True)

# Configurações
def load_config():
    """Carrega configurações do ambiente"""
    def get_secret_safe(key, default):
        """Obtém secret de forma segura, retornando default se não existir"""
        try:
            return st.secrets.get(key, default)
        except:
            return default
    
    config = {
        'DB_HOST': os.getenv('DB_HOST', get_secret_safe('DB_HOST', 'localhost')),
        'DB_PORT': int(os.getenv('DB_PORT', get_secret_safe('DB_PORT', 3306))),
        'DB_USER': os.getenv('DB_USER', get_secret_safe('DB_USER', 'root')),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', get_secret_safe('DB_PASSWORD', '')),
        'DB_NAME': os.getenv('DB_NAME', get_secret_safe('DB_NAME', 'churrasco')),
        'DB_TABLE': os.getenv('DB_TABLE', get_secret_safe('DB_TABLE', 'pagamentos')),
        'EVENT_DATE': os.getenv('EVENT_DATE', get_secret_safe('EVENT_DATE', '2025-12-06')),
        'EVENT_TIME': os.getenv('EVENT_TIME', get_secret_safe('EVENT_TIME', '16:00')),
        'EVENT_TZ': os.getenv('EVENT_TZ', get_secret_safe('EVENT_TZ', 'America/Sao_Paulo')),
        'PAYMENT_MONTHS': os.getenv('PAYMENT_MONTHS', get_secret_safe('PAYMENT_MONTHS', 'agosto_pago,setembro_pago,outubro_pago,novembro_pago,dezembro_pago')).split(','),
        'JSON_PATH': os.getenv('JSON_PATH', get_secret_safe('JSON_PATH', 'data.json')),
        'DB_READONLY': os.getenv('DB_READONLY', get_secret_safe('DB_READONLY', '1')) == '1'
    }
    return config

# Valor do pagamento
PAYMENT_VALUE = Decimal('63.07')

# Funções de banco de dados (SOMENTE LEITURA)
@st.cache_data(ttl=60)
def read_mysql_data(config):
    """Lê dados do MySQL (SOMENTE SELECT)"""
    try:
        connection_string = f"mysql+mysqlconnector://{config['DB_USER']}:{config['DB_PASSWORD']}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"
        engine = create_engine(connection_string)
        
        # Query SELECT apenas
        query = f"SELECT colaborador_id, nome_colaborador, {', '.join(config['PAYMENT_MONTHS'])} FROM {config['DB_TABLE']} ORDER BY nome_colaborador"
        
        df = pd.read_sql(query, engine)
        engine.dispose()
        
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com MySQL: {e}")
        return pd.DataFrame()

# Funções JSON
def load_json(json_path):
    """Carrega dados do JSON"""
    if not os.path.exists(json_path):
        # Cria a partir do seed_data.json ou defaults
        if os.path.exists('seed_data.json'):
            with open('seed_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "itens": [],
                "pessoas_extras": {}
            }
        save_json_atomic(data, json_path)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_atomic(data, json_path):
    """Salva JSON de forma atômica"""
    temp_path = json_path + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, json_path)

def add_item(colaborador_id, nome_colaborador, item, quantidade, unidade, observacoes, json_path):
    """Adiciona item ao JSON"""
    data = load_json(json_path)
    
    new_item = {
        "colaborador_id": colaborador_id,
        "nome_colaborador": nome_colaborador,
        "item": item,
        "quantidade": quantidade,
        "unidade": unidade,
        "observacoes": observacoes
    }
    
    data["itens"].append(new_item)
    save_json_atomic(data, json_path)

def set_pessoas_extras(mapping_por_id, json_path):
    """Define pessoas extras no JSON"""
    data = load_json(json_path)
    data["pessoas_extras"] = mapping_por_id
    save_json_atomic(data, json_path)

# Funções de cálculo
def format_currency(value):
    """Formata valor em reais"""
    if isinstance(value, Decimal):
        value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def calculate_financials(df, meses_pagamento):
    """Calcula dados financeiros"""
    if df.empty:
        return {
            'total_devido': Decimal('0'),
            'total_arrecadado': Decimal('0'),
            'percentual_pago': 0,
            'colaboradores_count': 0
        }
    
    colaboradores_count = len(df)
    total_devido = PAYMENT_VALUE * len(meses_pagamento) * colaboradores_count
    
    # Soma pagamentos realizados
    pagamentos_realizados = 0
    for mes in meses_pagamento:
        if mes in df.columns:
            pagamentos_realizados += df[mes].sum()
    
    total_arrecadado = PAYMENT_VALUE * pagamentos_realizados
    percentual_pago = (pagamentos_realizados / (len(meses_pagamento) * colaboradores_count) * 100) if colaboradores_count > 0 else 0
    
    return {
        'total_devido': total_devido,
        'total_arrecadado': total_arrecadado,
        'percentual_pago': percentual_pago,
        'colaboradores_count': colaboradores_count
    }

def get_countdown(event_datetime):
    """Calcula contagem regressiva"""
    now = datetime.now(event_datetime.tzinfo)
    if now >= event_datetime:
        return "Evento em andamento! 🎉"
    
    delta = event_datetime - now
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days}d {hours}h {minutes}m {seconds}s"

if 'editing' not in st.session_state:
    st.session_state.editing = False
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()
if 'edit_item_index' not in st.session_state:
    st.session_state.edit_item_index = None
if 'delete_item_index' not in st.session_state:
    st.session_state.delete_item_index = None
if 'show_edit_modal' not in st.session_state:
    st.session_state.show_edit_modal = False
if 'show_delete_modal' not in st.session_state:
    st.session_state.show_delete_modal = False
if 'show_add_modal' not in st.session_state:
    st.session_state.show_add_modal = False

# Carrega configurações
config = load_config()
json_data = load_json(config['JSON_PATH'])

current_time = time.time()
should_refresh = (
    not st.session_state.editing and 
    (current_time - st.session_state.last_refresh) >= 60
)

if should_refresh:
    st.session_state.last_refresh = current_time
    st.cache_data.clear()
    st.rerun()

# Header Hero - usa configurações do .env
try:
    tz = pytz.timezone(config['EVENT_TZ'])
    event_datetime = tz.localize(datetime.strptime(f"{config['EVENT_DATE']} {config['EVENT_TIME']}", "%Y-%m-%d %H:%M"))
    countdown = get_countdown(event_datetime)
    event_display = f"{event_datetime.strftime('%d/%m/%Y às %H:%M')}"
except:
    countdown = "Data inválida"
    event_display = f"{config['EVENT_DATE']} às {config['EVENT_TIME']}"

# Convertendo imagens do cabeçalho para base64
header_images_b64 = {}
header_image_paths = {
    'silvinho': 'images/silvinha.png',
    'familia': 'images/david.png'
}

for key, path in header_image_paths.items():
    b64 = image_to_base64(path)
    if b64:
        header_images_b64[key] = f"data:image/png;base64,{b64}"
    else:
        # Placeholder se não encontrar a imagem
        header_images_b64[key] = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiNGRkQ3MDAiLz4KPHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHg9IjIwIiB5PSIyMCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiI+CjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjMiLz4KPC9zdmc+Cjwvc3ZnPg=="

st.markdown(f"""
<div class="hero-header">
    <div style="display: flex; align-items: center; justify-content: space-between; position: relative;">
        <img src="{header_images_b64.get('silvinho', '')}" alt="Silvio Santos" style="width: 150px; height: 150px; object-fit: contain; border-radius: 8px;">
        <div style="flex: 1; text-align: center;">
            <div class="hero-title">Dashboard do Churrasco</div>
            <div class="hero-subtitle">{event_display}</div>
        </div>
        <img src="{header_images_b64.get('familia', '')}" alt="Família Silvio Santos" style="width: 150px; height: 150px; object-fit: contain; border-radius: 8px;">
    </div>
    <div class="countdown" style="margin-top: 1rem;">{countdown}</div>
</div>
""", unsafe_allow_html=True)

# Carrega dados do MySQL
df_mysql = read_mysql_data(config)

# Calcula financeiros
financials = calculate_financials(df_mysql, config['PAYMENT_MONTHS'])

# KPIs
st.markdown("### Indicadores")
kpi_cols = st.columns(6)

with kpi_cols[0]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{format_currency(financials['total_devido'])}</div>
        <div class="kpi-label">Total Devido</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{format_currency(financials['total_arrecadado'])}</div>
        <div class="kpi-label">Arrecadado ({financials['percentual_pago']:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{financials['colaboradores_count']}</div>
        <div class="kpi-label">Colaboradores</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    itens_count = len(json_data.get('itens', []))
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{itens_count}</div>
        <div class="kpi-label">Itens Cadastrados</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    pessoas_extras_total = sum(json_data.get('pessoas_extras', {}).values())
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{pessoas_extras_total}</div>
        <div class="kpi-label">Pessoas Extras</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[5]:
    publico_estimado = financials['colaboradores_count'] + pessoas_extras_total
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{publico_estimado}</div>
        <div class="kpi-label">Público Estimado</div>
    </div>
    """, unsafe_allow_html=True)

silvio_images_b64 = {}
image_paths = {
    'silvio1': 'images/silvio_orgulhoso_face.png',
    'silvio2': 'images/silvio_orgulhoso_face.png', 
    'silvio3': 'images/silvio_orgulhoso_face.png'
}

for key, path in image_paths.items():
    b64 = image_to_base64(path)
    if b64:
        silvio_images_b64[key] = f"data:image/png;base64,{b64}"
    else:
        # Placeholder se não encontrar a imagem
        silvio_images_b64[key] = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1zbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjUiIGZpbGw9IiNGRkQ3MDAiLz4KPHN2ZyB3aWR0aD0iMzAiIGhlaWdodD0iMzAiIHg9IjEwIiB5PSIxMCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiI+CjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjMiLz4KPHBhdGggZD0ibTMgMTIgMS41LTEuNUw5IDEybC0xLjUgMS41TDMgMTJabTYuNS0zLjVMMTEgN2w0IDQtMS41IDEuNUw5IDguNVptNy41IDcuNUwxNyAxN2wtNCA0IDEuNSAxLjVMMTggMTZabS03LjUgMy41TDEzIDE3bC00LTQgMS41LTEuNUwxNSAxNS41WiIvPgo8L3N2Zz4KPC9zdmc+"

# Barra de progresso
st.markdown("### Progresso dos Pagamentos")

progress_value = financials['percentual_pago'] / 100
percentual = financials['percentual_pago']

if percentual <= 40:
    silvio_image_url = silvio_images_b64.get('silvio1', '')
elif percentual <= 70:
    silvio_image_url = silvio_images_b64.get('silvio2', '')
else:
    silvio_image_url = silvio_images_b64.get('silvio3', '')

st.markdown(f"""
<div class="custom-progress-container">
    <div class="custom-progress-bar" style="width: {percentual}%;">
        <div class="silvio-indicator">
            <img src="{silvio_image_url}" alt="Silvio Santos" />
            <div class="silvio-percentage">{percentual:.1f}%</div>
        </div>
    </div>
</div>
<br>
<br>
<!--
<div class="progress-text">
    <strong>{percentual:.1f}%</strong> dos pagamentos realizados
</div>
-->
""", unsafe_allow_html=True)

# Tabela de Pagamentos (MySQL - SOMENTE LEITURA)
st.markdown("### Status dos Pagamentos")

if not df_mysql.empty:
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        nome_filter = st.text_input("Filtrar por nome", placeholder="Digite o nome...")
    with col2:
        status_filter = st.selectbox("Filtrar por status", ["Todos", "Com pagamento", "Sem pagamento"])
    
    # Aplica filtros
    df_display = df_mysql.copy()
    
    if nome_filter:
        df_display = df_display[df_display['nome_colaborador'].str.contains(nome_filter, case=False, na=False)]
    
    # Determina o mês atual
    mes_atual = datetime.now().month
    meses_nomes = {
        8: 'agosto_pago',
        9: 'setembro_pago', 
        10: 'outubro_pago',
        11: 'novembro_pago',
        12: 'dezembro_pago'
    }
    
    def get_status_message(valor, mes_nome):
        """Retorna mensagem baseada no valor e período do mês"""
        if valor == 1:
            return "Orgulho do Silvio"
        
        # Extrai o número do mês do nome
        mes_num = None
        for num, nome in meses_nomes.items():
            if nome == mes_nome:
                mes_num = num
                break
        
        if mes_num is None:
            return "Qual a dificuldade?"
        
        # Se é mês passado ou atual
        if mes_num <= mes_atual:
            return "Qual a dificuldade?"
        else:
            return "Tá no orçamento?"
    
    for mes in config['PAYMENT_MONTHS']:
        if mes in df_display.columns:
            df_display[mes] = df_display[mes].apply(
                lambda x, mes_nome=mes: get_status_message(x, mes_nome)
            )
    
    # Calcula coluna "Pago (R$)"
    df_display['Pago (R$)'] = 0
    for mes in config['PAYMENT_MONTHS']:
        if mes in df_mysql.columns:  # usa df_mysql original para cálculo numérico
            df_display['Pago (R$)'] += df_mysql[mes] * float(PAYMENT_VALUE)
    
    if status_filter == "Com pagamento":
        df_display = df_display[df_display['Pago (R$)'] > 0]
    elif status_filter == "Sem pagamento":
        df_display = df_display[df_display['Pago (R$)'] == 0]
    
    # Formata valores monetários
    df_display['Pago (R$)'] = df_display['Pago (R$)'].apply(lambda x: format_currency(Decimal(str(x))))
    
    # Renomeia colunas para exibição
    display_columns = ['nome_colaborador'] + [mes for mes in config['PAYMENT_MONTHS'] if mes in df_display.columns] + ['Pago (R$)']
    df_display = df_display[display_columns]
    
    column_config = {
        'nome_colaborador': st.column_config.TextColumn('Nome do Colaborador', width='medium'),
        'Pago (R$)': st.column_config.TextColumn('Pago (R$)', width='small')
    }
    
    for mes in config['PAYMENT_MONTHS']:
        if mes in df_display.columns:
            mes_display = mes.replace('_pago', '').title()
            column_config[mes] = st.column_config.TextColumn(mes_display, width='small')
    
    def color_status(val):
        """Aplica cores aos status de pagamento"""
        if val == "Orgulho do Silvio":
            return 'color: #10b981; font-weight: 600'
        elif val == "Qual a dificuldade?":
            return 'color: #ef4444; font-weight: 600'
        elif val == "Tá no orçamento?":
            return 'color: #f97316; font-weight: 600'
        return ''
    
    st.dataframe(
        df_display.style.map(color_status, subset=[mes for mes in config['PAYMENT_MONTHS'] if mes in df_display.columns]),
        column_config=column_config,
        hide_index=True,
        use_container_width=True
    )

else:
    st.warning("⚠️ Nenhum dado encontrado no MySQL")

# Cadastro de Itens (JSON) - Botão + ao lado do título
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <h3 style="margin: 0;">Itens do Churrasco</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([6, 1])
with col1:
    pass  # Espaço vazio para alinhamento
with col2:
    if st.button("➕ Novo Item", key="add_item_btn", help="Adicionar novo item"):
        st.session_state.show_add_modal = True
        st.session_state.editing = True
        st.rerun()

# Modal de cadastro de novo item
if st.session_state.get('show_add_modal', False):
    with st.container():
        st.markdown("### Cadastrar Novo Item")
        
        with st.form("form_itens", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                if not df_mysql.empty:
                    colaborador_options = {f"{row['nome_colaborador']} (ID: {row['colaborador_id']})": row['colaborador_id'] 
                                         for _, row in df_mysql.iterrows()}
                    selected_colaborador = st.selectbox("Colaborador", options=list(colaborador_options.keys()))
                    colaborador_id = colaborador_options[selected_colaborador]
                    nome_colaborador = selected_colaborador.split(' (ID:')[0]
                else:
                    st.warning("Nenhum colaborador encontrado")
                    colaborador_id = None
                    nome_colaborador = ""
                
                item = st.text_input("Item", placeholder="Ex: Chopp, Carvão, Linguiça...")
            
            with col2:
                quantidade = st.number_input("Quantidade", min_value=1, value=1)
                unidade = st.text_input("Unidade", placeholder="Ex: barril 50L, kg, pacote...")
            
            observacoes = st.text_area("Observações", placeholder="Informações adicionais...")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Cadastrar Item", type="primary")
                
                if submitted and colaborador_id:
                    if item.strip():
                        add_item(colaborador_id, nome_colaborador, item.strip(), quantidade, unidade.strip(), observacoes.strip(), config['JSON_PATH'])
                        st.success(f"✅ Item '{item}' cadastrado para {nome_colaborador}!")
                        st.session_state.show_add_modal = False
                        st.session_state.editing = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Por favor, informe o item")
            
            with col2:
                if st.form_submit_button("Cancelar"):
                    st.session_state.show_add_modal = False
                    st.session_state.editing = False
                    st.rerun()

# Modal de edição de item
if st.session_state.get('show_edit_modal', False) and st.session_state.edit_item_index is not None:
    item_to_edit = json_data['itens'][st.session_state.edit_item_index]
    
    st.markdown("### Editar Item")
    
    with st.form("form_edit_item"):
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_mysql.empty:
                colaborador_options = {f"{row['nome_colaborador']} (ID: {row['colaborador_id']})": row['colaborador_id'] 
                                     for _, row in df_mysql.iterrows()}
                
                # Encontrar o colaborador atual
                current_colaborador = None
                for key, value in colaborador_options.items():
                    if value == item_to_edit['colaborador_id']:
                        current_colaborador = key
                        break
                
                selected_colaborador = st.selectbox("Colaborador", 
                                                   options=list(colaborador_options.keys()),
                                                   index=list(colaborador_options.keys()).index(current_colaborador) if current_colaborador else 0)
                colaborador_id = colaborador_options[selected_colaborador]
                nome_colaborador = selected_colaborador.split(' (ID:')[0]
            else:
                st.warning("Nenhum colaborador encontrado")
                colaborador_id = item_to_edit['colaborador_id']
                nome_colaborador = item_to_edit['nome_colaborador']
            
            item = st.text_input("Item", value=item_to_edit['item'])
        
        with col2:
            quantidade = st.number_input("Quantidade", min_value=1, value=item_to_edit['quantidade'])
            unidade = st.text_input("Unidade", value=item_to_edit['unidade'])
        
        observacoes = st.text_area("Observações", value=item_to_edit.get('observacoes', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Salvar Alterações", type="primary"):
                if item.strip():
                    # Atualizar item
                    json_data['itens'][st.session_state.edit_item_index] = {
                        'colaborador_id': colaborador_id,
                        'nome_colaborador': nome_colaborador,
                        'item': item.strip(),
                        'quantidade': quantidade,
                        'unidade': unidade.strip(),
                        'observacoes': observacoes.strip()
                    }
                    save_json_atomic(json_data, config['JSON_PATH'])
                    st.success(f"✅ Item '{item}' atualizado!")
                    st.session_state.show_edit_modal = False
                    st.session_state.edit_item_index = None
                    st.session_state.editing = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Por favor, informe o item")
        
        with col2:
            if st.form_submit_button("Cancelar"):
                st.session_state.show_edit_modal = False
                st.session_state.edit_item_index = None
                st.session_state.editing = False
                st.rerun()

# Modal de confirmação de exclusão de item
if st.session_state.get('show_delete_modal', False) and st.session_state.delete_item_index is not None:
    item_to_delete = json_data['itens'][st.session_state.delete_item_index]
    
    st.markdown("### Confirmar Exclusão")
    st.warning(f"Tem certeza que deseja excluir o item **{item_to_delete['item']}** de **{item_to_delete['nome_colaborador']}**?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Sim, Excluir", type="primary", use_container_width=True):
            # Remover item
            json_data['itens'].pop(st.session_state.delete_item_index)
            save_json_atomic(json_data, config['JSON_PATH'])
            st.success(f"✅ Item '{item_to_delete['item']}' excluído!")
            st.session_state.show_delete_modal = False
            st.session_state.delete_item_index = None
            st.session_state.editing = False
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.show_delete_modal = False
            st.session_state.delete_item_index = None
            st.session_state.editing = False
            st.rerun()

# Lista de itens cadastrados
if json_data.get('itens'):
    st.markdown("#### Itens Cadastrados")
    
    # CSS para os cards de itens
    st.markdown("""
    <style>
    .item-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        /* Adicionando altura fixa e flexbox para alinhamento consistente */
        min-height: 180px;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .item-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    .item-title {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
    }
    .item-details {
        color: #666;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .item-collaborator {
        color: #888;
        font-size: 12px;
        margin-bottom: 15px;
    }
    .item-buttons {
        display: flex;
        gap: 10px;
        justify-content: flex-end;
    }
    /* Adicionando container para conteúdo flexível */
    .item-content {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Organizando itens em grid de 3 colunas
    items_per_row = 3
    items = json_data['itens']
    
    for i in range(0, len(items), items_per_row):
        cols = st.columns(items_per_row)
        
        for j, col in enumerate(cols):
            item_index = i + j
            if item_index < len(items):
                item = items[item_index]
                
                with col:
                    observacoes_html = ""
                    if item.get("observacoes") and item["observacoes"].strip():
                        observacoes_html = f'<div class="item-details" style="font-style: italic;">{item["observacoes"]}</div>'
                    
                    st.markdown(f"""
                    <div class="item-card">
                        <div class="item-content">
                            <div class="item-title">{item['item']}</div>
                            <div class="item-details">{item['quantidade']} {item['unidade']}</div>
                            <div class="item-collaborator">👤 {item['nome_colaborador']}</div>
                            {observacoes_html}
                    <!--    </div> -->
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botões fora do card HTML mas dentro da coluna
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button("✏️ Editar", key=f"edit_{item_index}", help="Editar item", use_container_width=True):
                            st.session_state.edit_item_index = item_index
                            st.session_state.show_edit_modal = True
                            st.session_state.editing = True
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️ Excluir", key=f"delete_{item_index}", help="Excluir item", use_container_width=True):
                            st.session_state.delete_item_index = item_index
                            st.session_state.show_delete_modal = True
                            st.session_state.editing = True
                            st.rerun()

# Pessoas Extras (JSON)
with st.expander("👥 Pessoas Extras por Colaborador", expanded=False):
    if not df_mysql.empty:
        with st.form("form_pessoas_extras"):
            pessoas_extras = json_data.get('pessoas_extras', {})
            
            extras_data = {}
            for _, row in df_mysql.iterrows():
                colaborador_id = str(row['colaborador_id'])
                nome = row['nome_colaborador']
                current_value = pessoas_extras.get(colaborador_id, 0)
                
                extras_data[colaborador_id] = st.number_input(
                    f"👤 {nome}",
                    min_value=0,
                    value=current_value,
                    key=f"extras_{colaborador_id}"
                )
            
            if st.form_submit_button("Salvar Pessoas Extras", type="primary"):
                set_pessoas_extras(extras_data, config['JSON_PATH'])
                st.success("✅ Pessoas extras salvas!")
                st.session_state.editing = False
                time.sleep(1)
                st.rerun()

# JavaScript para preservar posição de rolagem
st.markdown("""
<script>
// Função para salvar posição de scroll
function saveScrollPosition() {
    sessionStorage.setItem('dashboardScrollPosition', window.pageYOffset || document.documentElement.scrollTop);
}

// Função para restaurar posição de scroll
function restoreScrollPosition() {
    const savedPosition = sessionStorage.getItem('dashboardScrollPosition');
    if (savedPosition && savedPosition !== '0') {
        // Aguarda um pouco para garantir que o conteúdo foi carregado
        setTimeout(() => {
            window.scrollTo({
                top: parseInt(savedPosition),
                behavior: 'instant'
            });
        }, 100);
    } else {
        // Se não há posição salva, vai para o topo
        window.scrollTo({
            top: 0,
            behavior: 'instant'
        });
    }
}

// Salva posição antes do reload
window.addEventListener('beforeunload', saveScrollPosition);

// Salva posição periodicamente durante o uso
setInterval(saveScrollPosition, 5000);

// Restaura posição quando a página carrega
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', restoreScrollPosition);
} else {
    restoreScrollPosition();
}

window.addEventListener('load', function() {
    const savedPosition = sessionStorage.getItem('dashboardScrollPosition');
    if (!savedPosition || savedPosition === '0') {
        setTimeout(() => {
            window.scrollTo({
                top: 0,
                behavior: 'instant'
            });
        }, 200);
    }
});

// Detecta quando usuário está editando para pausar salvamento
const inputs = document.querySelectorAll('input, textarea, select');
inputs.forEach(input => {
    input.addEventListener('focus', () => {
        sessionStorage.setItem('userEditing', 'true');
    });
    input.addEventListener('blur', () => {
        sessionStorage.removeItem('userEditing');
        saveScrollPosition();
    });
});
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* CSS específico para colorir texto na tabela do Streamlit */
    .stDataFrame [data-testid="stDataFrameCell"] {
        font-weight: 500;
    }
    
    /* Fallbacks usando JavaScript para aplicar cores */
    .status-text-pago {
        color: #10b981 !important;
        font-weight: 600 !important;
    }
    
    .status-text-pendente {
        color: #ef4444 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# st.markdown("---")
# col1, col2, col3 = st.columns(3)

# with col1:
#     if st.session_state.editing:
#         st.caption("Atualização pausada (editando)")
#     else:
#         next_refresh = 60 - (current_time - st.session_state.last_refresh)
#         st.caption(f"Próxima atualização em {int(next_refresh)}s")

# with col2:
#     st.caption(f"Última atualização: {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%H:%M:%S')}")

# with col3:
#     st.caption(f"Dados: MySQL + JSON local")

