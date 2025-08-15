import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import os
from PIL import Image
import time
import glob
from dotenv import load_dotenv
import pymysql

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
CHURRASCO_DATE = os.getenv('CHURRASCO_DATE', '2025-12-06')
CHURRASCO_TIME = os.getenv('CHURRASCO_TIME', '18:00')
TIMEZONE = os.getenv('CHURRASCO_TIMEZONE', 'America/Sao_Paulo')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
IMAGE_WIDTH = 400
IMAGE_HEIGHT = 300

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_TABLE = os.getenv('DB_TABLE', 'confra_pagamentos')

VALOR_MENSAL_POR_COLABORADOR = 63.07

# Configurar página
st.set_page_config(
    page_title="Churrasco",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'photo_index' not in st.session_state:
    st.session_state.photo_index = 0
if 'last_photo_change' not in st.session_state:
    st.session_state.last_photo_change = time.time()
if 'right_image_index' not in st.session_state:
    st.session_state.right_image_index = 0
if 'last_right_image_change' not in st.session_state:
    st.session_state.last_right_image_change = time.time()
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = set()
if 'last_upload_hash' not in st.session_state:
    st.session_state.last_upload_hash = None
if 'database_data' not in st.session_state:
    st.session_state.database_data = None
if 'last_db_update' not in st.session_state:
    st.session_state.last_db_update = 0

# CSS personalizado para tema escuro
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .countdown-container {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
    }
    
    .countdown-text {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .photo-container {
        background: #2E2E2E;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #FF6B35;
    }
    
    .sidebar-text {
        color: #FF6B35;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .generic-message {
        color: #FFB84D;
        font-style: italic;
        text-align: center;
        padding: 2rem;
        background: #1E1E1E;
        border-radius: 10px;
        border: 1px dashed #FF6B35;
    }
    
    .stApp {
        background-color: #0E1117;
    }
    
    .metric-container {
        background: #1E1E1E;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
    }
    
    /* CSS aprimorado para remover completamente o fundo das imagens */
    .transparent-image {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .transparent-image img {
        background: transparent !important;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
        mix-blend-mode: screen !important;
        filter: contrast(1.1) brightness(1.1);
    }
    
    /* Remove fundo padrão do streamlit das imagens */
    div[data-testid="stImage"] {
        background: transparent !important;
    }
    
    div[data-testid="stImage"] > div {
        background: transparent !important;
    }
    
    /* Remove fundo das imagens na galeria */
    .gallery-image {
        background: transparent !important;
        border: none !important;
    }
    
    .gallery-image img {
        background: transparent !important;
        mix-blend-mode: screen !important;
        filter: contrast(1.2) brightness(1.1);
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

def query_database():
    """Conectar ao banco MySQL e executar SELECT na tabela confra_pagamentos"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            sql = f"SELECT * FROM {DB_DATABASE}.{DB_TABLE};"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            print(f"\n=== CONSULTA BANCO DE DADOS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Total de registros encontrados: {len(resultados)}")
            
            for linha in resultados:
                print(linha)
            
            print("=" * 60)
            
            return resultados
            
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {str(e)}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

@st.fragment(run_every=60)
def database_monitor():
    """Monitor do banco de dados que executa a cada 1 minuto"""
    current_time = time.time()
    if current_time - st.session_state.last_db_update >= 60:
        st.session_state.database_data = query_database()
        st.session_state.last_db_update = current_time

def create_upload_folder():
    """Criar pasta de uploads se não existir"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def get_countdown():
    """Calcular tempo restante para o churrasco"""
    try:
        tz = pytz.timezone(TIMEZONE)
        churrasco_datetime = datetime.strptime(f"{CHURRASCO_DATE} {CHURRASCO_TIME}", "%Y-%m-%d %H:%M")
        churrasco_datetime = tz.localize(churrasco_datetime)
        
        now = datetime.now(tz)
        diff = churrasco_datetime - now
        
        if diff.total_seconds() <= 0:
            return "🎉 CHURRASCO ROLANDO! 🎉"
        
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"⏰ {days} dias, {hours}h {minutes}m"
        elif hours > 0:
            return f"⏰ {hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"⏰ {minutes}m {seconds}s"
        else:
            return f"⏰ {seconds}s"
            
    except Exception as e:
        return f"⏰ Erro no cronômetro: {str(e)}"

def get_today_photos():
    """Obter fotos do dia atual"""
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = os.path.join(UPLOAD_FOLDER, f"{today}_*.jpg")
    photos = glob.glob(pattern)
    return photos

def cleanup_old_photos():
    """Limpar fotos antigas (manter apenas do dia atual)"""
    today = datetime.now().strftime("%Y-%m-%d")
    all_photos = glob.glob(os.path.join(UPLOAD_FOLDER, "*.jpg"))
    
    for photo in all_photos:
        filename = os.path.basename(photo)
        if not filename.startswith(today):
            try:
                os.remove(photo)
            except:
                pass

def create_real_data():
    """Criar dados reais baseados no banco de dados"""
    # Se não temos dados do banco, usar dados padrão
    if not st.session_state.database_data:
        st.session_state.database_data = query_database()
    
    data = st.session_state.database_data
    
    if not data:
        # Fallback para dados de exemplo se banco não estiver disponível
        return create_sample_data()
    
    # Meses do churrasco (agosto a dezembro)
    meses = ['Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    campos_pagamento = ['agosto_pago', 'setembro_pago', 'outubro_pago', 'novembro_pago', 'dezembro_pago']
    
    total_colaboradores = len(data)
    valor_esperado_por_mes = total_colaboradores * VALOR_MENSAL_POR_COLABORADOR
    
    valores_devidos = []
    valores_pagos = []
    
    for campo in campos_pagamento:
        # Contar quantos colaboradores pagaram este mês
        pagaram = sum(1 for colaborador in data if colaborador.get(campo, 0) == 1)
        valor_arrecadado = pagaram * VALOR_MENSAL_POR_COLABORADOR
        
        valores_devidos.append(valor_esperado_por_mes)
        valores_pagos.append(valor_arrecadado)
    
    df_data = {
        'Mês': meses,
        'Valor Devido': valores_devidos,
        'Valor Pago': valores_pagos
    }
    
    return pd.DataFrame(df_data)

def create_sample_data():
    """Criar dados de exemplo para o dashboard (fallback)"""
    months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    data = {
        'Mês': months,
        'Valor Devido': [150, 200, 180, 220, 190, 250, 300, 280, 320, 350, 400, 500],
        'Valor Pago': [120, 180, 150, 200, 170, 230, 250, 260, 280, 300, 350, 450]
    }
    
    return pd.DataFrame(data)

def resize_image(image_path_or_pil, target_width=IMAGE_WIDTH, target_height=IMAGE_HEIGHT):
    """Redimensionar imagem para tamanho padrão mantendo proporção"""
    try:
        if isinstance(image_path_or_pil, str):
            img = Image.open(image_path_or_pil)
        else:
            img = image_path_or_pil
        
        # Converter para RGB se necessário
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Redimensionar mantendo proporção
        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Criar nova imagem com fundo preto para preencher o espaço
        new_img = Image.new('RGB', (target_width, target_height), (30, 30, 30))
        
        # Centralizar a imagem redimensionada
        x = (target_width - img.width) // 2
        y = (target_height - img.height) // 2
        new_img.paste(img, (x, y))
        
        return new_img
    except Exception as e:
        st.error(f"Erro ao redimensionar imagem: {str(e)}")
        return None

@st.fragment(run_every=1)
def update_dynamic_content():
    """Atualizar apenas cronômetro e fotos sem recarregar página inteira"""
    current_time = time.time()
    
    # Atualizar cronômetro
    countdown_text = get_countdown()
    st.markdown(f"""
    <div class="countdown-container">
        <div class="countdown-text">{countdown_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Atualizar fotos do dia
    st.markdown("### 📸 Fotos do Dia")
    today_photos = get_today_photos()
    
    if today_photos:
        if current_time - st.session_state.last_photo_change >= 5:
            st.session_state.photo_index = (st.session_state.photo_index + 1) % len(today_photos)
            st.session_state.last_photo_change = current_time
        
        current_photo = today_photos[st.session_state.photo_index]
        
        try:
            resized_img = resize_image(current_photo)
            if resized_img:
                st.image(resized_img, caption=f"📸 Foto {st.session_state.photo_index + 1}/{len(today_photos)}")
            else:
                st.markdown('<div class="generic-message">🤔 Dev\'s estão desanimados para o churrasco...</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div class="generic-message">🤔 Dev\'s estão desanimados para o churrasco...</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="generic-message">🤔 Dev\'s estão desanimados para o churrasco...</div>', unsafe_allow_html=True)

@st.fragment(run_every=1)
def update_right_slideshow():
    """Atualizar slideshow da coluna direita com tamanho estático"""
    import time, os
    from PIL import Image

    # ========================
    # PARÂMETROS DE TAMANHO
    # ========================
    TARGET_W = 210   # largura fixa em px
    TARGET_H = 440   # altura fixa em px
    FIT_MODE = "contain"  # "contain" (sem cortes) ou "cover" (preenche recortando)
    BG = (0, 0, 0, 0)     # fundo transparente RGBA

    def fit_to_canvas(img: Image.Image, tw: int, th: int, mode: str = "contain", bg=(0,0,0,0)) -> Image.Image:
        """Ajusta a imagem para caber em (tw x th) mantendo RGBA e tamanho final fixo."""
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        iw, ih = img.size
        if mode == "cover":
            scale = max(tw / iw, th / ih)
        else:  # contain
            scale = min(tw / iw, th / ih)

        nw = max(1, int(round(iw * scale)))
        nh = max(1, int(round(ih * scale)))
        resized = img.resize((nw, nh), Image.LANCZOS)

        if mode == "cover":
            # recorte central para exatamente tw x th
            left = max(0, (nw - tw) // 2)
            top = max(0, (nh - th) // 2)
            right = min(nw, left + tw)
            bottom = min(nh, top + th)
            cropped = resized.crop((left, top, right, bottom))
            # Se por arredondamento ficou menor, centraliza numa lona
            if cropped.size != (tw, th):
                canvas = Image.new("RGBA", (tw, th), bg)
                cx = (tw - cropped.size[0]) // 2
                cy = (th - cropped.size[1]) // 2
                canvas.paste(cropped, (cx, cy), cropped)
                return canvas
            return cropped
        else:
            # contain: centraliza com bordas/pad transparente
            canvas = Image.new("RGBA", (tw, th), bg)
            x = (tw - nw) // 2
            y = (th - nh) // 2
            canvas.paste(resized, (x, y), resized)
            return canvas

    current_time = time.time()

    # Lista das imagens para o slideshow
    right_images = [
        "images/silvio_orgulhoso.png",
#        "images/familia_silvio_cleiton.png",
#        "images/silvinho.png"
    ]
    image_names = ["Silvio Orgulhoso"]
#    image_names = ["Silvio Orgulhoso", "Família Silvio", "Silvinho"]

    # Alternar imagem a cada 5 segundos
    if current_time - st.session_state.last_right_image_change >= 5:
        st.session_state.right_image_index = (st.session_state.right_image_index + 1) % len(right_images)
        st.session_state.last_right_image_change = current_time

    current_image_path = right_images[st.session_state.right_image_index]
    current_name = image_names[st.session_state.right_image_index]

    try:
        # Container com caixa fixa para evitar "salto" no layout
        st.markdown(
            f'<div width:{TARGET_W}px; height:{TARGET_H}px; margin-left:auto; margin-right:auto;">',unsafe_allow_html=True
        )

        if os.path.exists(current_image_path):
            img = Image.open(current_image_path)
            fixed = fit_to_canvas(img, TARGET_W, TARGET_H, mode=FIT_MODE, bg=BG)

            # Não usar use_container_width, para respeitar o tamanho fixo
            st.image(
                fixed,
                caption=f"{current_name} ({st.session_state.right_image_index + 1}/{len(right_images)})",
                use_container_width=False,
                width=TARGET_W  # reforça largura fixa; altura já é TARGET_H na própria imagem
            )
        else:
            # Placeholder com o mesmo tamanho da caixa
            st.markdown(
                f'''
                <div style="
                    width:{TARGET_W}px; height:{TARGET_H}px;
                    background: rgba(30,30,30,0.8);
                    padding: 0.75rem; border-radius: 10px; text-align: center;
                    border: 2px dashed #FF6B35; display:flex; align-items:center; justify-content:center; flex-direction:column;
                ">
                    <p style="color: #FFB84D; margin: 0.25rem 0;">{current_name}</p>
                    <p style="color: #888; margin: 0;">Imagem não encontrada</p>
                    <p style="color: #666; font-size: 0.8rem; margin: 0;">Verifique: {current_image_path}</p>
                </div>
                ''',
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.markdown(
            f'''
            <div style="
                margin-top: 1rem; width:{TARGET_W}px; height:{TARGET_H}px;
                background: rgba(30,30,30,0.8);
                padding: 0.75rem; border-radius: 10px; text-align: center;
                border: 2px dashed #FF6B35; display:flex; align-items:center; justify-content:center; flex-direction:column;
            ">
                <p style="color: #FFB84D; margin: 0.25rem 0;">{current_name}</p>
                <p style="color: #888; margin: 0;">Erro: {str(e)}</p>
            </div>
            ''',
            unsafe_allow_html=True
        )

def get_file_hash(file_content):
    """Gerar hash do arquivo para evitar duplicatas"""
    import hashlib
    return hashlib.md5(file_content).hexdigest()

def main():
    # Título principal
    # st.markdown('<h1 class="main-header">🔥 Dashboard do Churrasco 2025 🥩</h1>', unsafe_allow_html=True)
    
    # Criar pasta de uploads
    create_upload_folder()
    
    # Limpar fotos antigas
    cleanup_old_photos()
    
    database_monitor()
    
    # Layout em 3 colunas
    col1, col2, col3 = st.columns([3, 6, 1])
    
    # COLUNA ESQUERDA (30%)
    with col1:
        st.markdown('''
                    <div class="sidebar-text">📊 Streamlit é melhor que Power BI! 🚀</div>
                    <style>
                        /* 1) Remove o padding esquerdo do primeiro column em qualquer linha de colunas */
                        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
                        padding-left: 15px !important;
                        }

                        /* 2) (Opcional) Cola o container da página na margem lateral esquerda do viewport
                            Se não quiser colar tudo no limite da página, remova esta regra. */
                        div.block-container {
                        padding-left: 15px !important;
                        }

                        /* 3) (Opcional) Alguns componentes ainda têm recuos próprios; aqui colamos o uploader */
                        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child
                        [data-testid="stFileUploader"] > div:first-child {
                        margin-left: 15px !important;
                        padding-left: 15px !important;
                        }
                        </style>
                    ''', unsafe_allow_html=True)
        
        update_dynamic_content()
        
        # Botão de upload
        uploaded_file = st.file_uploader("Adicionar Foto", type=['jpg', 'jpeg', 'png'], key="photo_upload")
        
        if uploaded_file is not None:
            # Gerar hash do arquivo para verificar se já foi processado
            file_content = uploaded_file.getvalue()
            file_hash = get_file_hash(file_content)
            
            # Verificar se este arquivo já foi processado
            if file_hash != st.session_state.last_upload_hash:
                # Salvar foto com timestamp do dia
                today = datetime.now().strftime("%Y-%m-%d")
                timestamp = datetime.now().strftime("%H%M%S")
                filename = f"{today}_{timestamp}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Verificar se arquivo já existe
                if not os.path.exists(filepath):
                    try:
                        # Abrir imagem do upload
                        img = Image.open(uploaded_file)
                        
                        # Redimensionar para tamanho padrão
                        resized_img = resize_image(img)
                        
                        if resized_img:
                            # Salvar imagem redimensionada
                            resized_img.save(filepath, 'JPEG', quality=85)
                            
                            # Atualizar controle de uploads
                            st.session_state.last_upload_hash = file_hash
                            st.session_state.uploaded_files.add(file_hash)
                            
                            st.success("📸 Foto salva com sucesso!")
                            time.sleep(1)  # Pequena pausa para mostrar a mensagem
                            st.rerun()
                        else:
                            st.error("❌ Erro ao processar a imagem!")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar foto: {str(e)}")
                else:
                    st.warning("📸 Esta foto já foi salva!")
            else:
                st.info("📸 Arquivo já processado!")

    # COLUNA CENTRAL (40%) - Conteúdo estático
    with col2:
        # st.markdown("### Streamlit é melhor que Power BI!")
#        st.markdown('''<div class="sidebar-text">📊 Streamlit é melhor que Power BI! 🚀</div>''', unsafe_allow_html=True)

        df = create_real_data()
        
        # Gráfico de barras
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Valor Devido',
            x=df['Mês'],
            y=df['Valor Devido'],
            marker_color='#FF6B35',
            text=[f'R$ {v:.2f}' for v in df['Valor Devido']],
            textposition='auto',
        ))
        
        fig.add_trace(go.Bar(
            name='Valor Pago',
            x=df['Mês'],
            y=df['Valor Pago'],
            marker_color='#4CAF50',
            text=[f'R$ {v:.2f}' for v in df['Valor Pago']],
            textposition='auto',
        ))
        
        fig.update_layout(
            title='💰 Controle Financeiro Mensal',
            xaxis_title='Mês',
            yaxis_title='Valor (R$)',
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(size=16, color='#FF6B35'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas
        col_m1, col_m2, col_m3 = st.columns(3)
        
        total_devido = df['Valor Devido'].sum()
        total_pago = df['Valor Pago'].sum()
        pendente = total_devido - total_pago
        
        with col_m1:
            st.metric("💸 Total Devido", f"R$ {total_devido:,.2f}")
        
        with col_m2:
            st.metric("✅ Total Pago", f"R$ {total_pago:,.2f}")
        
        with col_m3:
            st.metric("⏳ Pendente", f"R$ {pendente:,.2f}")
    
    # COLUNA DIREITA (30%) - Conteúdo estático
    with col3:
        # st.markdown("### 🖼️ Galeria do Churrasco")
        
        update_right_slideshow()

if __name__ == "__main__":
    main()
