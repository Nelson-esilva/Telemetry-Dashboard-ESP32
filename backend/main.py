from datetime import datetime, timezone

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import TelemetryRecord, get_db, init_db
from backend.models import TelemetryCreate, TelemetryResponse

app = FastAPI(title="Telemetria de Produção", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/telemetry", response_model=TelemetryResponse, status_code=201)
def create_telemetry(payload: TelemetryCreate, db: Session = Depends(get_db)) -> TelemetryRecord:
    record = TelemetryRecord(
        timestamp=datetime.now(timezone.utc),
        device_id=payload.device_id,
        pecas_produzidas=payload.pecas_produzidas,
        temperatura_c=payload.temperatura_c,
        rpm_motor=payload.rpm_motor,
        status_maquina=payload.status_maquina.value,
        tempo_ciclo_s=payload.tempo_ciclo_s,
        eficiencia_pct=payload.eficiencia_pct,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/telemetry", response_model=list[TelemetryResponse])
def list_telemetry(limit: int = 100, db: Session = Depends(get_db)) -> list[TelemetryRecord]:
    limit = max(1, min(limit, 1000))
    return (
        db.query(TelemetryRecord)
        .order_by(TelemetryRecord.timestamp.desc())
        .limit(limit)
        .all()
    )
