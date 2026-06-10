from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class StatusMaquina(str, Enum):
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    ALARM = "ALARM"


class TelemetryCreate(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=50)
    pecas_produzidas: int = Field(..., ge=0)
    temperatura_c: float = Field(..., ge=0, le=150)
    rpm_motor: int = Field(..., ge=0, le=10000)
    status_maquina: StatusMaquina
    tempo_ciclo_s: float = Field(..., gt=0, le=3600)
    eficiencia_pct: float = Field(..., ge=0, le=100)


class TelemetryResponse(BaseModel):
    id: int
    timestamp: datetime
    device_id: str
    pecas_produzidas: int
    temperatura_c: float
    rpm_motor: int
    status_maquina: str
    tempo_ciclo_s: float
    eficiencia_pct: float

    model_config = {"from_attributes": True}
