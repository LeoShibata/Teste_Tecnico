-- Tabela Bronze (Dados Brutos)
-- Armazena todos os dados de enriquecimento retornados pela API.
CREATE TABLE IF NOT EXISTS bronze_enrichments (
    id SERIAL PRIMARY KEY,
    raw_data JSONB NOT NULL,
    dw_ingested_at TIMESTAMP DEFAULT NOW(), -- data/hora em que registro foi ingerido pela primeira vez na Bronze
    dw_updated_at TIMESTAMP DEFAULT NOW()   -- data/hora da última atualização do registro na Bronze
);

-- Tabela Gold (Dados Refinados)
-- Processa apenas registros da Bronze que ainda não foram processados.
CREATE TABLE IF NOT EXISTS gold_enrichments (
    id_enriquecimento VARCHAR(50) PRIMARY KEY,
    id_workspace VARCHAR(50) NOT NULL,
    nome_workspace VARCHAR(255),
    total_contatos INT,
    tipo_contato VARCHAR(50),
    status_processamento VARCHAR(50),
    data_criacao TIMESTAMP,
    data_atualizacao TIMESTAMP,

    -- Campos Calculados/Transformados
    duracao_processamento_minutos FLOAT, -- diferença em minutos entre data_atualizacao e data_criacao
    tempo_por_contato_minutos FLOAT,     -- duracao_processamento_minutos / total_contatos
    processamento_sucesso BOOLEAN,       -- true se status_processamento = "CONCLUIDO"
    categoria_tamanho_job VARCHAR(50),   -- PEQUENO, MEDIO...
    necessita_reprocessamento BOOLEAN,   -- true se status original = "FAILED" ou "CANCELED"
    data_atualizacao_dw TIMESTAMP        -- data/hora da execução do processamento (snapshot)
);