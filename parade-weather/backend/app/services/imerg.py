

"""
Servicio IMERG (GPM) para precipitación diaria.

Este módulo expone un método principal `get_imerg_daily` que intenta obtener
precipitación diaria (mm) y una probabilidad de precipitación (PoP %) para una
ubicación (lat, lon) y fecha ISO (YYYY-MM-DD).

MVP:
  - Intenta usar un fetch real (IMERG V07) si se implementa `fetch_imerg_v07_daily`.
  - Si no está implementado o falla, hace fallback a NASA POWER para precipitación
    diaria y estima PoP simple.

Producción:
  - Reemplazar `fetch_imerg_v07_daily` con integración real a GES DISC / Harmony-CMR,
    o pre-procesar tiles diarios y consultarlos por punto.
"""

from __future__ import annotations
import os
from typing import Dict, List, Optional

import httpx

# Reutilizamos POWER como fallback si IMERG no está disponible
from .power import fetch_power_api, get_power_daily


async def get_imerg_daily(lat: float, lon: float, date_iso: str) -> Dict[str, float]:
    """
    Obtiene precipitación diaria (mm) y PoP (%) para (lat, lon, date_iso).

    Estrategia:
      1) Intentar IMERG V07 con `fetch_imerg_v07_daily` (requiere EARTHDATA_TOKEN).
      2) Si falla o no está implementado, usar precip de POWER como aproximación.

    Retorna:
      {
        "precip_mm": float,
        "pop_percent": int,
        "source": "IMERG-V07" | "POWER-fallback" | "STUB"
      }
    """
    try:
        token = os.getenv("EARTHDATA_TOKEN")
        if token:
            imerg = await fetch_imerg_v07_daily(lat, lon, date_iso, token)
            if imerg and "precip_mm" in imerg:
                # Aseguramos campos esperados
                imerg.setdefault("pop_percent", estimate_pop_from_daily(imerg["precip_mm"]))
                imerg.setdefault("source", "IMERG-V07")
                return imerg
    except Exception:
        # Silenciamos en MVP, pero podrías loggear/monitorizar
        pass

    # Fallback a NASA POWER
    try:
        power = await fetch_power_api(lat, lon, date_iso)
    except Exception:
        power = await get_power_daily(lat, lon, date_iso)  # último recurso: stub aleatorio

    precip = float(power.get("precip", 0.0))
    pop = estimate_pop_from_daily(precip)
    return {"precip_mm": round(precip, 1), "pop_percent": pop, "source": "POWER-fallback"}


async def fetch_imerg_v07_daily(
    lat: float,
    lon: float,
    date_iso: str,
    earthdata_token: str,
) -> Optional[Dict[str, float]]:
    """
    (Placeholder) Descarga/consulta IMERG Final Run V07 (3IMERGDF) para el día y punto.

    Nota importante:
      - El acceso a IMERG en GES DISC generalmente requiere autenticación (Earthdata Login).
      - La forma recomendada hoy es mediante CMR/Harmony (descarga del píxel o recorte por bbox).
      - Implementación completa implica:
          1) Buscar el granule por fecha en CMR (collection GPM_3IMERGDF_07).
          2) Solicitar subsetting espacial (bbox pequeño alrededor de lat,lon).
          3) Descargar/leer el NetCDF y extraer el valor en el grid más cercano.
      - Por simplicidad del hackathon, este método se deja como esqueleto. Si se cuenta
        con un endpoint de subsetting ya preparado, impleméntalo aquí.

    Retorna:
      dict con al menos {"precip_mm": float, "pop_percent": int, "source": "IMERG-V07"}
      o None si no se pudo obtener.
    """
    # ========== EJEMPLO DE ESTRUCTURA (NO FUNCIONAL COMPLETO) ==========
    # cmr_search_url = "https://cmr.earthdata.nasa.gov/search/granules"
    # harmony_subset_url = "https://harmony.earthdata.nasa.gov/GPM_3IMERGDF_07/ogc-api-coverages/1.0/collections/..."
    # headers = {"Authorization": f"Bearer {earthdata_token}"}
    #
    # async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
    #     # 1) Buscar granule por fecha (YYYY-MM-DD)
    #     # 2) Solicitar subset por bbox muy pequeño alrededor del punto
    #     # 3) Descargar/parsear valor (NetCDF → precip diaria)
    #     ...
    #
    # Ejemplo de retorno:
    # return {"precip_mm": 7.2, "pop_percent": 70, "source": "IMERG-V07"}
    return None
    # ===================================================================


def estimate_pop_from_daily(precip_mm: float) -> int:
    """
    Estima probabilidad de precipitación (PoP %) a partir de precipitación diaria total.
    Heurística simple para MVP:
      - 0 mm   → 10%
      - 0–2 mm → 30%
      - 2–5 mm → 50%
      - 5–15 mm → 70%
      - >15 mm → 85%
    """
    if precip_mm <= 0.0:
        return 10
    if precip_mm <= 2.0:
        return 30
    if precip_mm <= 5.0:
        return 50
    if precip_mm <= 15.0:
        return 70
    return 85