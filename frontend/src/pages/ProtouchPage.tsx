import { useState } from "react";
import { api } from "../api/client";
import { gameCatalog } from "../app/gameCatalog";
import { GameHeader } from "../components/GameHeader";
import { PageContainer } from "../components/PageContainer";

export function ProtouchPage() {
  const game = gameCatalog.find(item => item.slug === "protouch")!;
  const [selections, setSelections] = useState<string[]>(Array(13).fill("L"));
  const [initial, setInitial] = useState("local-1");
  const [portfolio, setPortfolio] = useState<{line_count: number; cost_mxn: number} | null>(null);
  const doubles = selections.filter(value => value.length === 2).length;
  const triples = selections.filter(value => value.length === 3).length;
  const lines = selections.reduce((total, value) => total * value.length, 1);
  const valid = (triples === 0 && doubles <= 8) || (doubles === 0 && triples <= 5) || (doubles <= 2 && triples <= 4);
  const toggle = (index: number, outcome: string) => setSelections(values => values.map((value, position) => position !== index ? value : value.includes(outcome) ? value.replace(outcome, "") || outcome : `${value}${outcome}`));
  return <PageContainer><GameHeader game={game}/><p className="muted"><b>D</b> significa diferencia final de hasta 6 puntos, a favor de cualquiera; no significa empate. El resultado Protouch usa el marcador reglamentario oficial.</p>
    <section className="empty-panel"><h2>PROTOUCH INICIAL</h2><p>Selección sencilla independiente: primer touchdown del partido designado.</p><select value={initial} onChange={event => setInitial(event.target.value)}><option value="local-1">Equipo local · 1er cuarto</option><option value="local-2">Equipo local · 2º cuarto</option><option value="visitor-1">Equipo visitante · 1er cuarto</option><option value="visitor-2">Equipo visitante · 2º cuarto</option><option value="no-touch">Sin Touch</option></select></section>
    <section className="empty-panel"><h2>PROTOUCH · 13 partidos</h2><div className="pool-grid"><div className="pool-head">#</div><div className="pool-head">Local</div><div className="pool-head">Diferencia</div><div className="pool-head">Visita</div><div className="pool-head">Partido</div>{selections.map((selected, index) => <><span key={`n-${index}`}>{index + 1}</span>{["L", "D", "V"].map(outcome => <label key={`${index}-${outcome}`}><input type="checkbox" checked={selected.includes(outcome)} onChange={() => toggle(index, outcome)}/>{outcome}</label>)}<span key={`m-${index}`}>{selected.length === 1 ? "Simple" : selected.length === 2 ? "Doble" : "Triple"}</span></>)}</div><p>Dobles: {doubles} · Triples: {triples} · Líneas sencillas: {lines} · Costo: ${lines * 10} MXN</p>{!valid && <p className="error">Límite oficial excedido: 8 dobles, 5 triples o combinación máxima 2 dobles + 4 triples.</p>}<button disabled={!valid} onClick={() => void api.protouchPortfolio({number_of_portfolios: 1, strategy: "coverage_optimized", random_seed: 42}).then(setPortfolio)}>Generar cartera</button>{portfolio && <p>Cartera: {portfolio.line_count} líneas · ${portfolio.cost_mxn} MXN</p>}</section>
    <section className="empty-panel"><h2>Modelo predictivo</h2><p>not implemented: no se muestran probabilidades ni barras sin datos de fútbol verificables, corte temporal y calibración.</p></section>
  </PageContainer>;
}
