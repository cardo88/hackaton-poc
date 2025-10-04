import math

async def get_percentiles(lat: float, lon: float, doy: int) -> dict:
    """
    Retorna percentiles p10/p50/p90 por variable (HI, WC, WIND, PRCP) para el
    día del año (doy) y ubicación aproximados.

    MVP: modelo climatológico aproximado y determinístico (sin I/O):
      - Calcula un ciclo estacional con senos/cosenos ajustado por hemisferio.
      - Ajusta por latitud (|lat| ↑ ⇒ amplitud térmica ↓ y viento ↑ en promedio).
      - Devuelve percentiles razonables para un primer prototipo.

    En producción:
      - Reemplazar por lookup a tiles precalculados (Zarr/NetCDF/JSON) por DOY.
      - O bien usar reanálisis (p.ej., MERRA-2) para construir percentiles reales.
    """
    # --- Ciclo estacional básico ---
    # Desfase hemisférico: invertimos estación si lat < 0
    # Usamos 365 días para el ciclo; offset centra "verano" en DOY ~ 200 en hemisferio norte
    offset = 200
    if lat < 0:
        offset = (offset + 182) % 365  # ~medio año

    # Señales estacionales (rango -1..1)
    theta = 2 * math.pi * ((doy - offset) / 365.0)
    s = math.sin(theta)
    c = math.cos(theta)

    # --- Temperatura base (°C) ---
    # Media anual aproximada decrece con |lat|; amplitud también.
    mean_t = 18.0 - 0.12 * abs(lat)  # ~18°C en lat 0; ~7°C en lat 90
    amp_t = max(6.0, 12.0 - 0.08 * abs(lat))  # menor amplitud hacia polos
    t50 = mean_t + amp_t * s

    # Construimos percentiles para índices derivados
    # Heat Index (HI) p50≈T50 en climas templados; p90 +4°C, p10 -4°C aprox
    hi_p50 = t50
    hi_p90 = hi_p50 + 4.0
    hi_p10 = hi_p50 - 4.0

    # Wind Chill (WC) relevante en frío y viento: usa T50 - ajuste
    wc_p50 = t50 - 2.0
    wc_p10 = wc_p50 - 6.0  # más frío extremo
    wc_p90 = wc_p50 + 6.0

    # --- Viento (m/s) ---
    # Media de viento algo mayor en latitudes medias; modulación estacional suave
    mean_wind = 4.0 + 0.03 * abs(lat)       # 4–6.7 m/s aprox
    amp_wind = 1.0 + 0.01 * abs(lat)        # 1–1.9 m/s
    wind_p50 = max(0.5, mean_wind + 0.5 * c * amp_wind)
    wind_p90 = wind_p50 + 3.0
    wind_p10 = max(0.5, wind_p50 - 2.0)

    # --- Precipitación diaria (mm) ---
    # Estacionalidad simple: más precip en estación "húmeda" (cerca de s>0).
    wet_season = max(0.0, s)  # 0..1
    # Ajuste por costa vs interior (muy aproximado) usando lon (ruido determinista)
    coastiness = 0.3 + 0.2 * (0.5 + 0.5 * math.sin(math.radians(lon)))  # 0.3..0.5
    prcp_p50 = 1.0 + 6.0 * wet_season * coastiness         # 1..4 mm típicos
    prcp_p90 = prcp_p50 + 6.0 * (0.6 + 0.4 * wet_season)    # 4..10+ mm
    prcp_p10 = max(0.0, prcp_p50 - 1.5)

    return {
        "HI":   {"p10": round(hi_p10, 1),  "p50": round(hi_p50, 1),  "p90": round(hi_p90, 1)},
        "WC":   {"p10": round(wc_p10, 1),  "p50": round(wc_p50, 1),  "p90": round(wc_p90, 1)},
        "WIND": {"p10": round(wind_p10, 1),"p50": round(wind_p50, 1),"p90": round(wind_p90, 1)},
        "PRCP": {"p10": round(prcp_p10, 1),"p50": round(prcp_p50, 1),"p90": round(prcp_p90, 1)}
    }