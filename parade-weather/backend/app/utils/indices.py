import math

def compute_heat_index(t_c: float, rh: float) -> float:
    """Heat Index (aprox) en °C. Convierte a °F para fórmula simplificada y vuelve a °C."""
    t_f = t_c * 9/5 + 32
    hi_f = -42.379 + 2.04901523*t_f + 10.14333127*rh - 0.22475541*t_f*rh \
           - 6.83783e-3*t_f*t_f - 5.481717e-2*rh*rh + 1.22874e-3*t_f*t_f*rh \
           + 8.5282e-4*t_f*rh*rh - 1.99e-6*t_f*t_f*rh*rh
    return (hi_f - 32) * 5/9

def compute_wind_chill(t_c: float, wind_ms: float) -> float:
    """Wind Chill en °C (fórmula canadiense con viento en km/h)."""
    v_kmh = wind_ms * 3.6
    if v_kmh < 4.8 or t_c > 10:
        return t_c
    return 13.12 + 0.6215*t_c - 11.37*(v_kmh**0.16) + 0.3965*t_c*(v_kmh**0.16)


def compute_dew_point(t_c: float, rh: float) -> float:
    """Dew point (Magnus)."""
    a, b = 17.62, 243.12
    gamma = (a*t_c/(b+t_c)) + math.log(max(rh,1e-6)/100.0)
    return (b*gamma)/(a-gamma)


def compute_humidex(t_c: float, rh: float) -> float:
    """
    Estima el índice Humidex, una medida de incomodidad por calor y humedad.
    Utiliza la temperatura del aire (°C) y la humedad relativa (%) para calcular el Humidex (°C).
    """
    Td = compute_dew_point(t_c, rh)
    e = 6.11 * math.exp(5417.7530 * (1/273.16 - 1/(273.15 + Td)))
    humidex = t_c + 0.5555 * (e - 10)
    return humidex