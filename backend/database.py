from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "telemetry.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class TelemetryRecord(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    device_id: Mapped[str] = mapped_column(String(50), nullable=False)
    pecas_produzidas: Mapped[int] = mapped_column(Integer, nullable=False)
    temperatura_c: Mapped[float] = mapped_column(Float, nullable=False)
    rpm_motor: Mapped[int] = mapped_column(Integer, nullable=False)
    status_maquina: Mapped[str] = mapped_column(String(20), nullable=False)
    tempo_ciclo_s: Mapped[float] = mapped_column(Float, nullable=False)
    eficiencia_pct: Mapped[float] = mapped_column(Float, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
