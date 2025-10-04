

# 🌦️ Will It Rain On My Parade? (NASA Space Apps Challenge 2025)

Este proyecto es un **MVP** desarrollado para el desafío **“Will It Rain On My Parade?”** de la NASA Space Apps Challenge 2025.  
Permite consultar la probabilidad de condiciones adversas (muy caliente, muy frío, muy ventoso, muy mojado o muy incómodo) para una ubicación y fecha determinada, usando datos de **NASA POWER**, **IMERG** (precipitación) y climatología aproximada.

---

## 🚀 Estructura del proyecto

```
parade-weather/
├─ backend/
│  ├─ app/
│  │  ├─ main.py                # FastAPI principal (endpoints /health y /query)
│  │  ├─ models.py              # (vacío o futuro, para Pydantic models extra)
│  │  ├─ services/
│  │  │  ├─ power.py            # Stub + fetch real NASA POWER API
│  │  │  ├─ imerg.py            # (pendiente, lluvia de GPM IMERG)
│  │  │  └─ climatology.py      # Percentiles climatológicos aproximados
│  │  └─ utils/
│  │     ├─ indices.py          # Cálculo HI, WC, Dew Point, Humidex
│  │     └─ fuse.py             # Fusión de probabilidades y combinación de fuentes
│  └─ requirements.txt          # Dependencias (FastAPI, httpx, etc.)
└─ frontend/
│  └─ src/
│     └─ App.tsx                # React + Tailwind, UI minimal de consulta
└─ tests/
   └─ test_query.py
```

---

## 🛠️ Backend (FastAPI)

### Instalación

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # en Linux/macOS
# .venv\Scripts\activate    # en Windows

pip install -r requirements.txt
```

### Ejecución local

```bash
uvicorn app.main:app --reload --port 8088
```

El backend quedará en: [http://localhost:8088](http://localhost:8088)

---

## 💻 Frontend (React + Vite + Tailwind)

### Instalación

```bash
cd frontend
npm install
```

### Ejecución local

```bash
npm run dev
```

Abrir en: [http://localhost:5173](http://localhost:5173)

> El frontend espera la variable `VITE_API_URL` (por defecto usa `http://localhost:8088`).

---

## 📡 Fuentes de datos

- [NASA POWER API](https://power.larc.nasa.gov/)
- [GPM IMERG](https://gpm.nasa.gov/data/directory)
- Climatología derivada (aproximada en MVP)

---

## 📋 Roadmap

- [x] Backend FastAPI con índices (HI, WC, Humidex)
- [x] Servicio de precipitación IMERG (stub + fallback a POWER)
- [x] Frontend React + Tailwind minimal
- [ ] Integrar IMERG real vía Harmony/CMR
- [ ] Precalcular percentiles climatológicos reales (p10/p50/p90)
- [ ] Añadir selección en mapa (Leaflet/MapLibre)
- [ ] Exportar resultados (PDF/CSV)

---

## 🏆 Créditos

Equipo participante de la **NASA Space Apps Challenge 2025**.  
Datos proporcionados por NASA Earth Science Division.