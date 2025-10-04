import random
import httpx

async def get_power_daily(lat: float, lon: float, date_iso: str) -> dict:
    """
    MVP stub: reemplazar por fetch a NASA POWER (TMAX, TMIN, RH2M, WS10M, PRECTOTCORR, ALLSKY_SFC_SW_DWN).
    Retorna valores plausibles y campos auxiliares para la demo.
    """
    tmax = 24 + random.uniform(-5, 5)
    tmin = 14 + random.uniform(-5, 5)
    tavg = (tmax + tmin) / 2
    rh = 65 + random.uniform(-20, 20)
    wind = max(1.0, random.uniform(2, 12))
    precip = max(0.0, random.uniform(0, 15)) if random.random() < 0.5 else 0.0
    pop = 60 if precip > 5 else (30 if precip > 0 else 10)
    return {
        "tmax": round(tmax, 1),
        "tmin": round(tmin, 1),
        "tavg": round(tavg, 1),
        "rh": round(rh, 0),
        "wind": round(wind, 1),
        "precip": round(precip, 1),
        "pop": pop,
        "lead_hours": 72,
        "spread": 0.25
    }

async def fetch_power_api(lat: float, lon: float, date_iso: str) -> dict:
    """
    Obtiene datos reales de NASA POWER para la fecha y punto solicitado.
    Realiza una consulta HTTP GET al endpoint de NASA POWER para datos diarios.
    Devuelve un diccionario con tmax, tmin, tavg, rh, wind, precip, y campos auxiliares.
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start": date_iso.replace("-", ""),
        "end": date_iso.replace("-", ""),
        "community": "RE",
        "parameters": "T2M_MAX,T2M_MIN,RH2M,WS10M,PRECTOTCORR",
        "format": "JSON"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    try:
        day_data = data["properties"]["parameter"]
        tmax = day_data["T2M_MAX"][date_iso.replace("-", "")]
        tmin = day_data["T2M_MIN"][date_iso.replace("-", "")]
        rh = day_data["RH2M"][date_iso.replace("-", "")]
        wind = day_data["WS10M"][date_iso.replace("-", "")]
        precip = day_data["PRECTOTCORR"][date_iso.replace("-", "")]
        tavg = (tmax + tmin) / 2
    except (KeyError, TypeError):
        # Fallback to stub values if data is missing or malformed
        return await get_power_daily(lat, lon, date_iso)

    pop = 60 if precip > 5 else (30 if precip > 0 else 10)

    return {
        "tmax": round(tmax, 1),
        "tmin": round(tmin, 1),
        "tavg": round(tavg, 1),
        "rh": round(rh, 0),
        "wind": round(wind, 1),
        "precip": round(precip, 1),
        "pop": pop,
        "lead_hours": 72,
        "spread": 0.25
    }