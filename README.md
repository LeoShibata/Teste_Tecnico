# Teste Técnico - Pipeline de Ingestão Periódica + API + Dashboard

Este repositório contém a solução para o teste técnico. O projeto consiste em uma pipeline completa de ingestão, processamento e visualização de dados de enriquecimento (B2B).

## Arquitetura da Solução

A solução foi orquestrada utilizando **Docker Compose** e integra os seguintes serviços:

* **PostgreSQL (Data Warehouse):**
    * **Camada Bronze:** Armazena o JSON bruto (`raw_data`).
    * **Camada Gold:** Dados limpos, traduzidos, desduplicados e com métricas calculadas (ex: duração do processamento).
* **n8n (Workflow Engine):**
    * Responsável pela ingestão periódica (5 min), tratamento de erros (Retry com Backoff) e transformação de dados (Bronze → Gold).
* **API (Python/FastAPI):**
    * *Fonte:* Simula uma API externa com paginação, geração de dados aleatórios e erros esporádicos (Rate Limit/429).
    * *Analytics:* Expõe endpoints de leitura otimizados consumindo a camada Gold.
* **Dashboard (Streamlit):**
    * Interface interativa para monitoramento de KPIs e visualização dos dados em tempo real.

### Fluxo de Dados
1.  **Ingestão:** O n8n consulta a API a cada 5 minutos, trata erros (429/Retry) e salva os dados brutos na tabela `bronze_enrichments`.
2.  **Processamento:** Um workflow lê os dados pendentes da Bronze (em lotes), aplica regras de negócio/tradução e atualiza a tabela `gold_enrichments`.
3.  **Visualização:** O Dashboard consome a API de Analytics (que lê da Gold) para exibir métricas em tempo real.

---

## Como Executar o Projeto

### Pré-requisitos
* Docker e Docker Compose instalados.
* Git instalado.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone <https://github.com/LeoShibata/Teste_Tecnico.git>
    cd Teste_Tecnico
    ```

2.  **Suba o ambiente:**
    ```bash
    docker-compose up --build -d
    ```
    *Aguardar alguns instantes para que todos os containers (Postgres, n8n, API, Dashboard) iniciem.*

3.  **Acesse os serviços:**
    * **Dashboard:** [http://localhost:8501](http://localhost:8501)
    * **n8n:** [http://localhost:5678](http://localhost:5678)
    * **API Docs:** [http://localhost:3000/docs](http://localhost:3000/docs)

---

## Configuração dos Workflows (n8n)

Para que a automação funcione, é necessário importar os workflows criados:

1.  Acesse o n8n em [http://localhost:5678](http://localhost:5678).
    * **Usuário:** `admin`
    * **Senha:** `admin` (ou conforme configurado no seu ambiente).
2.  Vá em **Workflows** > **Add Workflow** > **Import from File**.
3.  Selecione os arquivos `.json` localizados na pasta `/workflows` deste repositório.
4.  * **Configuração de Credenciais:**
    * Ao importar, verifique os nós de **Postgres**. Se a credencial não vier configurada, crie uma nova credencial "Postgres" com os seguintes dados (baseados no `docker-compose.yml`):
        * **Host:** `postgres`
        * **User:** `user`
        * **Password:** `password`
        * **Database:** `driva_db`
5.  **Ative** o workflow "Orquestrador" (botão **Activate** no canto superior direito) para iniciar o agendamento automático a cada 5 minutos.

---

## Detalhes Técnicos e Decisões

* **Batch Processing:** Foi implementada uma lógica de processamento em lote no workflow Gold (limit = 10000) para garantir que grandes volumes de dados acumulados na camada Bronze sejam processados corretamente, evitando gargalos de leitura.
* **Tratamento de Erros:** O workflow de Ingestão possui Retry automático com backoff para lidar com o erro simulado `429 Too Many Requests` da API.
* **Idempotência:** A tabela Gold utiliza chaves primárias para garantir que reprocessamentos apenas atualizem os dados (Upsert), evitando duplicidade.

## Uso de IA

Conforme sugerido nas instruções do teste, ferramentas de IA foram utilizadas para:
1.  **Infraestrutura:** Auxílio na configuração inicial do `docker-compose.yml`, volumes e rede interna entre containers.
2.  **Debugging:** Identificação do problema de limite de leitura no nó do Postgres (n8n), que travava o dashboard em 50 registros.
3.  **SQL:** Geração do script `init.sql` para criação das tabelas Bronze e Gold.

---

## Endpoints da API

A API serve tanto como fonte de dados quanto como backend para o dashboard:

* `GET /v1/enrichments`: Retorna dados simulados para o n8n (Requer header `Authorization: Bearer driva_test_key_abc123xyz789`).
* `GET /analytics/overview`: Retorna KPIs agregados (Total, Sucesso, Tempo Médio).
* `GET /analytics/enrichments`: Lista detalhada e paginada dos jobs processados na camada Gold.

---

## Estrutura do Repositório

```text
.
├── api/                # Código da API (Python/FastAPI) e Dockerfile
├── dashboard/          # Código do Dashboard (Streamlit) e Dockerfile
├── workflows/          # JSONs dos fluxos do n8n (Ingestão, Processamento, Orquestrador)
├── docker-compose.yml  # Orquestração dos containers
├── init.sql            # Script de inicialização do Banco de Dados
└── README.md           # Documentação do projeto
```