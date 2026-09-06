import { useEffect, useState } from "react";

import { api } from "../api/client";
import { gameCatalog } from "../app/gameCatalog";
import { GameHeader } from "../components/GameHeader";
import { PageContainer } from "../components/PageContainer";

const tabs = ["Resumen", "Historial", "Frecuencia", "Frecuencia posición", "Atrasos", "Ciclos", "Patrones", "Generador", "Backtest"];

export function TrisPage() {
  const game = gameCatalog.find(item => item.slug === "tris")!;
  const [tab, setTab] = useState("Resumen");
  const [draws, setDraws] = useState<Array<{ draw_number: string; draw_date: string; winning_number: string }>>([]);
  const [statistics, setStatistics] = useState<Record<string, unknown> | null>(null);
  const [tickets, setTickets] = useState<string[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { void Promise.all([api.trisDraws(), api.trisStatistics()]).then(([history, stats]) => { setDraws(history); setStatistics(stats); }).catch(() => setError("El backend TRIS no está disponible.")); }, []);
  const generate = () => { void api.trisPortfolio({ count: 10, strategy: "random", seed: 42 }).then(result => setTickets(result.tickets)).catch(() => setError("No fue posible generar el portafolio.")); };
  return <PageContainer><GameHeader game={{ ...game, status: "available" }} />
    <p className="muted">Análisis descriptivo; no implica capacidad predictiva. Premios y ROI permanecen sin calcular hasta contar con reglas económicas verificadas.</p>
    <nav className="tris-tabs" aria-label="Secciones TRIS">{tabs.map(item => <button className={item === tab ? "active" : ""} key={item} onClick={() => setTab(item)}>{item}</button>)}</nav>
    {error && <p role="alert">{error}</p>}
    {tab === "Resumen" && <section className="empty-panel"><h2>TRIS posicional</h2><p>{draws.length} sorteos cargados. Cinco posiciones D1–D5, conservadas como texto para admitir ceros iniciales.</p><p>Ley del Tercio: <strong>no implementada</strong>; la fuente no aporta una definición inequívoca.</p></section>}
    {tab === "Historial" && <section className="empty-panel"><h2>Historial</h2>{draws.length ? <table><thead><tr><th>Sorteo</th><th>Fecha</th><th>Resultado</th></tr></thead><tbody>{draws.map(draw => <tr key={draw.draw_number}><td>{draw.draw_number}</td><td>{draw.draw_date}</td><td className="tris-number">{draw.winning_number}</td></tr>)}</tbody></table> : <p>Sin sorteos importados.</p>}</section>}
    {["Frecuencia", "Frecuencia posición", "Atrasos", "Ciclos", "Patrones"].includes(tab) && <section className="empty-panel"><h2>{tab}</h2><pre>{JSON.stringify(statistics, null, 2)}</pre></section>}
    {tab === "Generador" && <section className="empty-panel"><h2>Generador reproducible</h2><button onClick={generate}>Generar 10 con semilla 42</button><div className="ticket-grid">{tickets.map(ticket => <span className="tris-number" key={ticket}>{ticket}</span>)}</div></section>}
    {tab === "Backtest" && <section className="empty-panel"><h2>Backtest walk-forward</h2><p>Usa únicamente sorteos anteriores a cada objetivo y compara contra una línea base aleatoria con el mismo número de boletos.</p><p>ROI: no disponible hasta verificar premios y costos.</p></section>}
  </PageContainer>;
}
