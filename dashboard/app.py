import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(
    page_title="Monitoramento de Enriquecimento",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Processamento de Dados")
st.markdown("Monitoramento em tempo real de pipeline **Bronze** -> **Gold**")

def get_data():
    try:
        response = requests.get("http://driva_api:3000/analytics/overview")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API Offline: {e}")
        return None

if st.button('🔄 Atualizar Agora'):
    st.rerun()

col1, col2, col3 = st.columns(3)

data = get_data()

if data:
    col1.metric("Total de Jobs", data.get("total_jobs", 0))
    col2.metric("Sucessos", data.get("sucessos", 0))

    tempo = data.get("tempo_medio_minutos", 0)
    col3.metric("Tempo Médio", f"{tempo} min")

    total = data.get("total_jobs", 1)
    sucesso = data.get("sucessos", 0)
    if total > 0:
        perc = sucesso / total
        st.progress(perc, text=f"Taxa de Sucesso: {perc*100:.1f}%")
    
    st.success("Conectado à API com sucesso!")
else:
    st.warning("Aguardando conexão...")

st.markdown("---")
st.subheader("📋 Últimos Enriquecimentos (Detalhes)")

def get_enrichments_table():
    try:
        response = requests.get("http://driva_api:3000/analytics/enrichments?limit=20")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


# exibir tabela
listas_dados = get_enrichments_table()

if listas_dados:
    df = pd.DataFrame(listas_dados)
    st.dataframe(
        df,
        width="stretch",
        column_config={
            "id_enriquecimento": "ID",
            "nome_workspace": "Workspace",
            "status_processamento": "Status",
            "tipo_contato": "Tipo",
            "duracao_processamento_minutos": st.column_config.NumberColumn(
                "Duracao (min)",
                format="%.1f min"
            )
        }
    )  
else:
    st.info("Aguardando dados na tabela Gold...")