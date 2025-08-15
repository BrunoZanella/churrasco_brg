import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import time
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="🔥 ChurrasCode - Dashboard de Pagamentos",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = None
if 'error_cache' not in st.session_state:
    st.session_state.error_cache = None

# CSS customizado para deixar mais bonito
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: white;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6B35;
    }
    
    .countdown-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    
    .countdown-number {
        font-size: 4rem;
        font-weight: bold;
        margin: 0;
    }
    
    .status-pago {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-pendente {
        background-color: #dc3545;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .refresh-info {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data_from_database():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE'),
            port=int(os.getenv('DB_PORT')),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            sql = f"SELECT * FROM {os.getenv('DB_DATABASE')}.confra_pagamentos;"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            # Converter para DataFrame
            df = pd.DataFrame(resultados)
            return df, None
            
    except Exception as e:
        return None, str(e)
    finally:
        if 'conn' in locals():
            conn.close()

def days_until_churrasco():
    today = date.today()
    current_year = today.year
    
    # Data do evento: 6 de dezembro do ano atual
    target_date = date(current_year, 12, 6)
    
    # Se já passou a data deste ano, calcular para o próximo ano
    if today > target_date:
        target_date = date(current_year + 1, 12, 6)
    
    delta = target_date - today
    return max(0, delta.days), target_date

current_time = datetime.now()
time_diff = (current_time - st.session_state.last_update).total_seconds()

if time_diff >= 60 or st.session_state.data_cache is None:
    # Carregar novos dados
    new_df, new_error = load_data_from_database()
    st.session_state.data_cache = new_df
    st.session_state.error_cache = new_error
    st.session_state.last_update = current_time

# Usar dados do cache
df = st.session_state.data_cache
error = st.session_state.error_cache

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🔥 ChurrasCode 🥩</h1>
    <p>Dashboard de Pagamentos - Equipe de TI | "Compilando sabores, debugando a fome!"</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="refresh-info">
    <strong>🔄 Auto-refresh:</strong> Os dados são atualizados automaticamente a cada minuto | 
    Última atualização: <strong>{}</strong>
</div>
""".format(st.session_state.last_update.strftime('%H:%M:%S')), unsafe_allow_html=True)

if error:
    st.error(f"❌ Erro ao conectar com o banco de dados: {error}")
    st.stop()

if df is None or df.empty:
    st.warning("⚠️ Nenhum dado encontrado no banco de dados.")
    st.stop()

days_left, event_date = days_until_churrasco()

# Sidebar com informações
st.sidebar.markdown("## 🎯 Informações do Evento")
st.sidebar.markdown(f"**📅 Data:** {event_date.strftime('%d de %B de %Y')}")
st.sidebar.markdown("**👥 Participantes:** " + str(len(df)) + " devs")
st.sidebar.markdown("**💰 Status:** Em andamento")
st.sidebar.markdown(f"**🔄 Última sync:** {st.session_state.last_update.strftime('%H:%M:%S')}")

st.sidebar.markdown("---")
st.sidebar.markdown("## 🤖 Memes do Dia")
memes = [
    "🐛 Bug no churrasco: Carne não compila!",
    "☕ Coffee.exe stopped working, iniciando Beer.exe",
    "🔥 404: Vegetariano not found",
    "💻 while(hungry) { eat(); }",
    "🥩 Carne em produção, sem rollback!"
]
st.sidebar.markdown("*" + memes[int(time.time()) % len(memes)] + "*")

# Contador regressivo
st.markdown(f"""
<div class="countdown-card">
    <h2>⏰ Contagem Regressiva</h2>
    <p class="countdown-number">{days_left}</p>
    <p>{"dias para o ChurrasCode!" if days_left > 0 else "É HOJE! 🎉"}</p>
</div>
""", unsafe_allow_html=True)

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

# Calcular estatísticas
total_colaboradores = len(df)
meses = ['agosto_pago', 'setembro_pago', 'outubro_pago', 'novembro_pago', 'dezembro_pago']
pagamentos_por_mes = {mes: df[mes].sum() for mes in meses}
total_pagamentos = sum(pagamentos_por_mes.values())
taxa_pagamento = (pagamentos_por_mes['agosto_pago'] / total_colaboradores) * 100

with col1:
    st.metric(
        label="👥 Total de Devs",
        value=total_colaboradores,
        delta="Equipe completa!"
    )

with col2:
    st.metric(
        label="💰 Pagamentos Agosto",
        value=f"{pagamentos_por_mes['agosto_pago']}/{total_colaboradores}",
        delta=f"{taxa_pagamento:.1f}%"
    )

with col3:
    st.metric(
        label="🔥 Total Arrecadado",
        value=f"R$ {pagamentos_por_mes['agosto_pago'] * 50:.2f}",
        delta="Estimativa R$ 50/pessoa"
    )

with col4:
    st.metric(
        label="📊 Status Geral",
        value="Em Progresso",
        delta="Cobrando galera! 😅"
    )

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Pagamentos por Mês")
    
    # Preparar dados para o gráfico
    meses_nomes = ['Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    valores = [pagamentos_por_mes[mes] for mes in meses]
    
    fig_bar = px.bar(
        x=meses_nomes,
        y=valores,
        title="Evolução dos Pagamentos",
        color=valores,
        color_continuous_scale="Oranges"
    )
    fig_bar.update_layout(
        showlegend=False,
        xaxis_title="Mês",
        yaxis_title="Quantidade de Pagamentos"
    )
    st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")

with col2:
    st.subheader("🥧 Status Agosto")
    
    pagos = pagamentos_por_mes['agosto_pago']
    pendentes = total_colaboradores - pagos
    
    fig_pie = px.pie(
        values=[pagos, pendentes],
        names=['Pagos 💚', 'Pendentes 🔴'],
        title="Situação dos Pagamentos de Agosto",
        color_discrete_sequence=['#28a745', '#dc3545']
    )
    st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

# Lista detalhada dos colaboradores
st.subheader("👨‍💻 Lista de Colaboradores e Status de Pagamentos")

# Preparar dados para exibição
display_df = df.copy()
meses_display = ['Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
meses_cols = ['agosto_pago', 'setembro_pago', 'outubro_pago', 'novembro_pago', 'dezembro_pago']

# Criar DataFrame para exibição
result_data = []
for _, row in display_df.iterrows():
    row_data = {
        'ID': row['colaborador_id'],
        'Nome': row['nome_colaborador']
    }
    
    for mes_display, mes_col in zip(meses_display, meses_cols):
        status = "✅ Pago" if row[mes_col] == 1 else "❌ Pendente"
        row_data[mes_display] = status
    
    result_data.append(row_data)

result_df = pd.DataFrame(result_data)

def highlight_status(val):
    if "✅" in str(val):
        return 'background-color: #d4edda; color: #155724'
    elif "❌" in str(val):
        return 'background-color: #f8d7da; color: #721c24'
    return ''

styled_df = result_df.style.map(highlight_status, subset=meses_display)
st.dataframe(styled_df, use_container_width=True, hide_index=True, key="colaboradores_table")

# Seção de insights
st.subheader("🧠 Insights do Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **📈 Análise Atual:**
    - {pagamentos_por_mes['agosto_pago']} de {total_colaboradores} devs já pagaram agosto
    - Taxa de pagamento: {taxa_pagamento:.1f}%
    - Faltam {total_colaboradores - pagamentos_por_mes['agosto_pago']} pagamentos
    """)

with col2:
    if taxa_pagamento >= 70:
        st.success("🎉 Ótima adesão! O churrasco está garantido!")
    elif taxa_pagamento >= 50:
        st.warning("⚠️ Precisamos cobrar mais alguns devs!")
    else:
        st.error("🚨 Alerta: Poucos pagamentos! Hora de fazer aquele PR no grupo! 😅")

if time_diff >= 60:
    time.sleep(2)  # Pequena pausa para evitar refresh muito rápido
    st.rerun()

# Footer divertido
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
    <h4>🔥 Stramlit e melhor que Power BI ❤️</h4>
    <p><em>"Onde código vira churrasco e bugs viram risadas!"</em></p>
    <p>🥩 Feito com carinho pela equipe de TI | Conectado ao banco em tempo real 🐛</p>
</div>
""", unsafe_allow_html=True)
