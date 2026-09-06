import { useEffect, useState } from "react";
import { api } from "../api/client";
import { gameCatalog } from "../app/gameCatalog";
import { GameHeader } from "../components/GameHeader";
import { PageContainer } from "../components/PageContainer";

const positions = ["A1", "A2", "A3", "B1", "B3", "C1", "C2", "C3"];
const tabs = ["Resumen", "Historial", "Frecuencia", "Frecuencia por posición", "Atrasos", "Patrones", "Generador", "Cobertura/diversidad", "Backtest"];

export function GanaGatoPage() {
  const game = gameCatalog.find(item => item.slug === "gana_gato")!;
  const [tab, setTab] = useState("Resumen");
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [values, setValues] = useState<number[]>(Array(8).fill(1));
  const [tickets, setTickets] = useState<number[][]>([]);
  const [error, setError] = useState("");
  useEffect(() => { void api.ganaGatoAnalysis().then(setAnalysis).catch(() => setError("No fue posible cargar Gana Gato.")); }, []);
  const cells = [0, 1, 2, 3, "center", 4, 5, 6, 7] as const;
  const generate = () => void api.ganaGatoPortfolio({number_of_tickets: 10, strategy: "coverage_optimized", random_seed: 42}).then(result => setTickets(result.tickets));
  return <PageContainer><GameHeader game={game}/><p className="muted">Análisis descriptivo; no implica predicción. Premio y ROI no disponibles sin datos económicos oficiales.</p>
    {error && <p role="alert">{error}</p>}
    <nav className="tris-tabs">{tabs.map(item => <button key={item} className={tab === item ? "active" : ""} onClick={() => setTab(item)}>{item}</button>)}</nav>
    {tab === "Generador" ? <section className="empty-panel"><h2>Generador posicional</h2><div className="gato-board" aria-label="Tablero Gana Gato">{cells.map(cell => cell === "center" ? <div className="gato-center" key="center">★<small>Comodín</small></div> : <label key={positions[cell]}>{positions[cell]}<select aria-label={positions[cell]} value={values[cell]} onChange={event => setValues(current => current.map((value, index) => index === cell ? Number(event.target.value) : value))}>{[1,2,3,4,5].map(value => <option key={value}>{value}</option>)}</select></label>)}</div><button onClick={generate}>Generar cartera</button><div className="ticket-grid">{tickets.map((ticket, index) => <span key={index}>{ticket.join(" · ")}</span>)}</div></section>
      : <section className="empty-panel"><h2>{tab}</h2>{analysis === null ? <p>Cargando…</p> : <pre>{JSON.stringify(analysis, null, 2)}</pre>}</section>}
  </PageContainer>;
}
