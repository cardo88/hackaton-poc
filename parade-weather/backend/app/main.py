from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timezone

from .utils.indices import compute_heat_index, compute_wind_chill, compute_dew_point
from .utils.fuse import fuse_probabilities
from .services.power import get_power_daily
from .services.climatology import get_percentiles

app = FastAPI(title="Parade Weather API", version="0.1.0")

class Sensitivity(BaseModel):
    heat: Optional[float] = 0.5
    cold: Optional[float] = 0.5
    wind: Optional[float] = 0.5
    wet: Optional[float] = 0.5
    discomfort: Optional[float] = 0.5

class QueryIn(BaseModel):
    lat: float
    lon: float
    date_iso: str
    profile: str = Field(default="default")
    sensitivity: Optional[Sensitivity] = None

@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}

@app.post("/query")
async def query(inq: QueryIn):
    # 1) Datos diarios (NASA POWER, stub): Tmax, Tmin, RH, wind, precip, radiation
    power = await get_power_daily(inq.lat, inq.lon, inq.date_iso)

    # 2) Índices
    hi = compute_heat_index(power["tmax"], power["rh"])  # °C
    wc = compute_wind_chill(power["tmin"], power["wind"])  # °C
    dp = compute_dew_point(power["tavg"], power["rh"])  # °C

    # 3) Percentiles locales por DOY (climatología)
    doy = int(datetime.fromisoformat(inq.date_iso).strftime("%j"))
    pct = await get_percentiles(inq.lat, inq.lon, doy)

    # 4) Heurísticas de probabilidad por categoría (MVP)
    probs: Dict[str, float] = {
        "very_hot": float(hi > max(pct["HI"].get("p90", 32), 32.0)),
        "very_cold": float(wc < min(pct["WC"].get("p10", 5), 5.0)),
        "very_windy": float(power["wind"] > max(pct["WIND"].get("p90", 10.0), 10.0)),
        "very_wet": float(
            (power.get("pop", 0) >= 50) or (power.get("precip", 0) >= max(pct["PRCP"].get("p90", 5), 5))
        ),
        "very_uncomfortable": float((dp >= 20.0) or (hi >= 32.0) or (wc <= 0.0))
    }

    # 5) Fusión climatología + pronóstico (escala 0..1)
    fused = fuse_probabilities(probs, lead_hours=power.get("lead_hours", 72))

    # 6) Explicabilidad
    drivers = [
        {"label": "Tmax", "value": power["tmax"], "unit": "°C", "contribution": fused["very_hot"]},
        {"label": "Viento", "value": power["wind"], "unit": "m/s", "contribution": fused["very_windy"]},
        {"label": "PoP", "value": power.get("pop", 0), "unit": "%", "contribution": fused["very_wet"]},
        {"label": "Dew Point", "value": dp, "unit": "°C", "contribution": fused["very_uncomfortable"]},
    ]

    # 7) Confianza simple
    spread = power.get("spread", 0.2)
    confidence = "high" if spread < 0.15 else ("medium" if spread < 0.35 else "low")

    # 8) Sugerencias
    suggestions = []
    if fused["very_wet"] > 0.3:
        suggestions.append("Mover a 09:00–11:00 reduce riesgo de lluvia")
    if fused["very_windy"] > 0.3:
        suggestions.append("Usar zona protegida del viento o reubicar 1–2 km")

    return {
        "location": {"lat": inq.lat, "lon": inq.lon},
        "when": {"date_iso": inq.date_iso, "lead_hours": power.get("lead_hours", 72), "tz": "America/Montevideo"},
        "probabilities": fused,
        "top_risks": sorted([k for k,v in fused.items() if v>0.3], key=lambda k: fused[k], reverse=True)[:2],
        "drivers": drivers,
        "confidence": confidence,
        "suggestions": suggestions
    }

# Para AWS Lambda: descomentar estas dos líneas
# from mangum import Mangum
# handler = Mangum(app)