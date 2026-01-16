import streamlit as st
import pandas as pd
import requests
import altair as alt

# Configuração da Página
st.set_page_config(page_title = "Monitoramento Driva", page_icon = "🚀", layout = "wide")

# CSS para ajustar tamanho da fonte dos números (Métricas)
st.markdown("<style>[data-testid='stMetricValue'] { font-size: 24px; }</style>", unsafe_allow_html=True)

# Funções de Carga
def get_kpis():
    try:
        return requests.get("http://driva_api:3000/analytics/overview").json()
    except:
        return None

def get_data():
    try:
        resp = requests.get("http://driva_api:3000/analytics/enrichments?limit=1000")
        return pd.DataFrame(resp.json()) if resp.status_code == 200 else pd.DataFrame()
    except:
        return pd.DataFrame()

# Sidebar (Filtros e Botão)
with st.sidebar:
    st.header("Filtros & Controle")
    
    # Botão Simples
    if st.button('🔄 Atualizar Agora'):
        st.rerun()
    
    st.divider()
    
    # Carrega dados
    df = get_data()
    
    # Filtros
    if not df.empty:
        status_filter = st.multiselect("Status:", df['status_processamento'].unique(), default=df['status_processamento'].unique())
        tipo_filter = st.multiselect("Tipo:", df['tipo_contato'].unique(), default = df['tipo_contato'].unique())
        
        # Aplica filtros
        df_filtered = df[df['status_processamento'].isin(status_filter) & df['tipo_contato'].isin(tipo_filter)]
    else:
        df_filtered = pd.DataFrame()

# Layout Principal
st.title("🚀 HubDriva | Monitoramento")
st.markdown("---")

# KPIs
kpis = get_kpis()
if kpis:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total", kpis.get("total_jobs", 0))
    c2.metric("✅ Sucessos", kpis.get("sucessos", 0))
    c3.metric("⏱ Tempo Médio", f"{kpis.get('tempo_medio_minutos', 0)} min")
    
    total = kpis.get("total_jobs", 1)
    taxa = (kpis.get("sucessos", 0) / total * 100) if total > 0 else 0
    c4.metric("📈 Taxa Sucesso", f"{taxa:.1f}%")
    st.progress(taxa / 100)

# Gráficos e Tabelas
if not df_filtered.empty:
    st.subheader("📊 Análise Visual")
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.altair_chart(alt.Chart(df_filtered).mark_bar().encode(
            x = 'status_processamento', y = 'count()', color='status_processamento', tooltip = ['count()']
        ).interactive(), use_container_width=True)

    with col_graf2:
        st.altair_chart(alt.Chart(df_filtered).mark_arc(innerRadius = 50).encode(
            theta=alt.Theta("count()", stack = True), color="tipo_contato", tooltip = ['tipo_contato', 'count()']
        ), use_container_width = True)

    st.markdown("---")
    st.subheader("📋 Detalhes")
    
    # Tabela Simples
    st.dataframe(
        df_filtered,
        use_container_width = True,
        hide_index = True,
        column_config = {
            "id_enriquecimento": st.column_config.TextColumn("ID", width = "small"),
            "duracao_processamento_minutos": st.column_config.NumberColumn(
                "Duração (min)", 
                format="%.1f"
            )
        }
    )
else:
    st.warning("Aguardando dados da API...")