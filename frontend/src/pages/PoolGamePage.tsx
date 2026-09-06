import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { gameCatalog } from "../app/gameCatalog";
import { GameHeader } from "../components/GameHeader";
import { PageContainer } from "../components/PageContainer";

const tabs = ["Resumen", "Concursos", "Frecuencia", "Patrones", "Generador", "Cobertura", "Backtest"];

export function PoolGamePage() {
  const { slug = "progol" } = useParams();
  const id = slug.replaceAll("-", "_");
  const game = gameCatalog.find(item => item.slug === id)!;
  const matchCount = id === "progol" ? 14 : 9;
  const [tab, setTab] = useState("Resumen");
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [selections, setSelections] = useState<string[]>(Array(matchCount).fill("L"));
  const [portfolio, setPortfolio] = useState<{line_count: number; cost_mxn: number} | null>(null);
  useEffect(() => { setSelections(Array(matchCount).fill("L")); void api.poolAnalysis(id).then(setAnalysis); }, [id, matchCount]);
  const toggle = (index: number, outcome: string) => setSelections(values => values.map((value, position) => position === index ? (value.includes(outcome) ? value.replace(outcome, "") || outcome : `${value}${outcome}`) : value));
  return <PageContainer><GameHeader game={game}/><p className="muted">Resultados oficiales L/E/V al final del tiempo reglamentario. Datos predictivos de mercado, Elo y forma: no implementados sin fuentes reproducibles.</p>
    <nav className="tris-tabs">{tabs.map(item => <button key={item} className={tab === item ? "active" : ""} onClick={() => setTab(item)}>{item}</button>)}</nav>
    {tab === "Generador" ? <section className="empty-panel"><h2>Quiniela {id === "progol" ? "Progol" : "Progol 1/2 Semana"}</h2><div className="pool-grid"><div className="pool-head">#</div><div className="pool-head">Local</div><div className="pool-head">Empate</div><div className="pool-head">Visita</div><div className="pool-head">Match</div>{selections.map((selected, index) => <><span key={`n-${index}`}>{index + 1}</span>{["L", "E", "V"].map(outcome => <label key={`${index}-${outcome}`}><input type="checkbox" checked={selected.includes(outcome)} onChange={() => toggle(index, outcome)}/>{outcome}</label>)}<span key={`m-${index}`}>{selected.length === 1 ? "Simple" : selected.length === 2 ? "Doble" : "Triple"}</span></>)}</div><button onClick={() => void api.poolPortfolio(id, {number_of_portfolios: 1, strategy: "random_uniform", random_seed: 42}).then(setPortfolio)}>Generar cartera</button>{portfolio && <p>Line count: {portfolio.line_count} · Costo: ${portfolio.cost_mxn} MXN</p>}{id === "progol" && <section className="revancha"><h3>Progol Revancha</h3><p>Modalidad complementaria de 7 partidos; requiere participación Progol. Se habilita al cargar la quiniela oficial del concurso.</p></section>}</section> : <section className="empty-panel"><h2>{tab}</h2>{analysis ? <pre>{JSON.stringify(analysis, null, 2)}</pre> : <p>Cargando…</p>}</section>}
  </PageContainer>;
}
