import React, { useState } from "react";

type Probs = {
  very_hot: number;
  very_cold: number;
  very_windy: number;
  very_wet: number;
  very_uncomfortable: number;
};

type Driver = { label: string; value: number; unit: string; contribution: number };

type ApiResponse = {
  location: { lat: number; lon: number };
  when: { date_iso: string; lead_hours: number; tz: string };
  probabilities: Probs;
  top_risks: string[];
  drivers: Driver[];
  confidence: "low" | "medium" | "high";
  suggestions: string[];
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8088";

const riskEmoji: Record<keyof Probs, string> = {
  very_hot: "🔥",
  very_cold: "🥶",
  very_windy: "💨",
  very_wet: "🌧️",
  very_uncomfortable: "😵",
};

function Pill({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct < 25 ? "bg-green-600" : pct < 50 ? "bg-yellow-500" : pct < 75 ? "bg-orange-500" : "bg-red-600";
  return <span className={`text-white px-2 py-1 rounded-full text-sm ${color}`}>{pct}%</span>;
}

export default function App() {
  const [lat, setLat] = useState<number>(-34.905);
  const [lon, setLon] = useState<number>(-56.191);
  const [dateIso, setDateIso] = useState<string>(new Date().toISOString().slice(0, 10));
  const [profile, setProfile] = useState<string>("default");
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat, lon, date_iso: dateIso, profile }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json: ApiResponse = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen px-6 py-8 bg-slate-950 text-slate-100">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Will It Rain On My Parade?</h1>
        <p className="mb-6 text-slate-300">Probabilidad personalizada de condiciones adversas para tu evento.</p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm mb-1">Latitud</label>
            <input
              type="number"
              value={lat}
              onChange={(e) => setLat(parseFloat(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Longitud</label>
            <input
              type="number"
              value={lon}
              onChange={(e) => setLon(parseFloat(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Fecha</label>
            <input
              type="date"
              value={dateIso}
              onChange={(e) => setDateIso(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Perfil</label>
            <select
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2"
            >
              <option value="default">Default</option>
              <option value="family">Familia</option>
              <option value="trail_runner">Trail Runner</option>
              <option value="fishing">Pesca</option>
              <option value="photographer">Fotógrafo</option>
              <option value="cycling">Ciclismo</option>
            </select>
          </div>
        </div>

        <button
          onClick={submit}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50"
        >
          {loading ? "Calculando…" : "Consultar"}
        </button>

        {error && <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded">Error: {error}</div>}

        {data && (
          <div className="mt-8 space-y-6">
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Resultado</h2>
                <span className="text-sm text-slate-400">Confianza: {data.confidence}</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mt-4">
                {Object.entries(data.probabilities).map(([k, v]) => {
                  const key = k as keyof Probs;
                  return (
                    <div key={k} className="p-3 rounded-xl bg-slate-800/60">
                      <div className="text-2xl">{riskEmoji[key]}</div>
                      <div className="text-sm text-slate-400">{k.replace("very_", "muy ")}</div>
                      <div className="mt-2">
                        <Pill value={v as number} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <h3 className="font-semibold mb-2">Principales riesgos</h3>
              <ul className="list-disc pl-5 text-slate-300">
                {data.top_risks.length === 0 ? (
                  <li>Sin riesgos relevantes 🎉</li>
                ) : (
                  data.top_risks.map((r) => <li key={r}>{r}</li>)
                )}
              </ul>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <h3 className="font-semibold mb-3">¿Por qué?</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {data.drivers.map((d, i) => (
                  <div key={i} className="p-3 rounded-xl bg-slate-800/60 flex items-center justify-between">
                    <div>
                      <div className="text-slate-200">{d.label}</div>
                      <div className="text-slate-400 text-sm">
                        {d.value} {d.unit}
                      </div>
                    </div>
                    <Pill value={d.contribution} />
                  </div>
                ))}
              </div>
            </div>

            {data.suggestions.length > 0 && (
              <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
                <h3 className="font-semibold mb-2">Sugerencias</h3>
                <ul className="list-disc pl-5 text-slate-300">
                  {data.suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
