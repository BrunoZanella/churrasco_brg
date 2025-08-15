# Arquivo principal para deploy no Streamlit Cloud
# Este arquivo importa e executa o dashboard principal

import sys
import os

# Adiciona o diretório scripts ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from churrasco_dashboard import *
except ImportError as e:
    import streamlit as st
    st.error(f"Erro ao importar o dashboard: {e}")
    st.info("Verifique se todos os arquivos estão no local correto e se o arquivo .env está configurado.")
    st.info("Para deploy no Streamlit Cloud, configure as variáveis de ambiente no painel de configurações.")
