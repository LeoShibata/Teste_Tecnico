from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
from typing import Optional

# Configuração de Banco de Dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/driva_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
fake = Faker('pt_BR')

app = FastAPI()
security = HTTPBearer()

API_KEY_EXPECTED = "driva_test_key_abc123xyz789"

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY_EXPECTED:
        raise HTTPException(status_code = 403, detail = "Credenciais inválidas")
    return credentials.credentials

@app.get("/")
def read_root(): 
    return {"message": "API Driva rodando com sucesso!"}

# EndPoint de Fonte
@app.get("/v1/enrichments", dependencies = [Depends(verify_api_key)])
def get_enrichments(page: int = 1, limit: int = 50):
    if random.random() < 0.05: # 5% de chance de erro 429
        raise HTTPException(status_code = 429, detail = "Too Many Requests")
    
    TOTAL_ITEMS = 5000
    total_pages = (TOTAL_ITEMS // limit) + (1 if TOTAL_ITEMS % limit > 0 else 0)

    data = []
    for _ in range(limit):
        created = fake.date_time_between(start_date = '-30d', end_date = 'now')
        updated = created + timedelta(minutes = random.randint(1, 120))

        item = {
            "id": str(uuid.uuid4()),
            "id_workspace": str(uuid.uuid4()),
            "workspace_name": fake.company(),
            "total_contacts": random.randint(5, 2000),
            "contact_type": random.choice(["COMPANY", "PERSON"]),
            "status": random.choice(["COMPLETED", "COMPLETED", "COMPLETED", "FAILED", "PROCESSING"]),
            "created_at": created.isoformat(),
            "updated_at": updated.isoformat()
        }
        data.append(item)

    return {
        "meta": {
            "current_page": page,
            "items_per_page": limit,
            "total_items": TOTAL_ITEMS,
            "total_pages": total_pages
        },
        "data": data
    }

# EndPoint de Analytics
@app.get("/analytics/overview")
def get_analytics():
    query = text("""
        SELECT             
            COUNT(*) as total_jobs,
            COUNT(CASE WHEN processamento_sucesso THEN 1 END) as sucessos,
            AVG(duracao_processamento_minutos) as tempo_medio
        FROM gold_enrichments
    """)

    with engine.connect() as conn:
        result = conn.execute(query).first()

    if not result:
        return {
            "total_jobs": 0,
            "sucessos": 0,
            "tempo_medio_minutos": 0
        }
    
    return {
        "total_jobs": result[0] or 0,
        "sucessos": result[1] or 0,
        "tempo_medio_minutos": round(result[2] or 0, 2)
    }