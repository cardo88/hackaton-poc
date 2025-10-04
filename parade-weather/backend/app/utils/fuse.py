def fuse_probabilities(probs: dict, lead_hours: int) -> dict:
    """Fusión simple forecast+clima via peso alfa según lead time.
    Cuanto más cerca el evento, mayor peso del pronóstico (aquí ya viene implícito en probs).
    Aplicamos un suavizado para evitar 0/1 duros.
    """
    alpha = max(0.3, min(0.9, 1.0 - (lead_hours/240.0)))  # 10 días ~ 240 h
    fused = {}
    for k, v in probs.items():
        fused[k] = round( max(0.0, min(1.0, alpha*v + (1-alpha)*0.3*v + 0.05)), 2 )
    return fused

def combine_sources(sources: list, weights: list) -> dict:
    """
    Combina múltiples fuentes de probabilidad con pesos definidos.
    sources: lista de diccionarios con probabilidades.
    weights: lista de pesos correspondientes a cada fuente.
    Retorna un diccionario con la media ponderada para cada clave.
    """
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("La suma de los pesos no puede ser cero.")
    normalized_weights = [w / total_weight for w in weights]

    combined = {}
    keys = set()
    for source in sources:
        keys.update(source.keys())

    for key in keys:
        weighted_sum = 0.0
        for source, weight in zip(sources, normalized_weights):
            weighted_sum += source.get(key, 0.0) * weight
        combined[key] = round(weighted_sum, 4)

    return combined