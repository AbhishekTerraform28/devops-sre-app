import os
import signal
import time
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator
import redis

from app.database import get_db

app = FastAPI(title="Order Management SRE Service", version="1.0.0")

from app.database import Base, engine

# Yeh line database ke andar saari missing tables physical roop se create karti hai:
Base.metadata.create_all(bind=engine)

# SRE Observability: Expose /metrics
Instrumentator().instrument(app).expose(app)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_timeout=2)

# --- SRE Health Probes ---

@app.get("/healthz", status_code=status.HTTP_200_OK)
def liveness():
    """Liveness probe: container zinda hai ya nahi."""
    return {"status": "alive"}

@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness(db: Session = Depends(get_db)):
    """Readiness probe: DB aur Redis dono ready hain ya nahi."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(exc)}")

    try:
        r = get_redis_client()
        r.ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cache unavailable: {str(exc)}")

    return {"status": "ready"}

# --- Business & Chaos Endpoints ---

@app.get("/")
def root():
    return {"message": "Order SRE Microservice Operational"}

@app.post("/orders")
def create_order(item: str, quantity: int):
    return {"order_id": int(time.time()), "item": item, "quantity": quantity, "status": "CONFIRMED"}

@app.get("/simulate-crash")
def simulate_crash():
    """Chaos engineering: Pod crash simulate karne ke liye."""
    os.kill(os.getpid(), signal.SIGTERM)
