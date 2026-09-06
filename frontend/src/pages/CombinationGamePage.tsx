import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { gameCatalog } from "../app/gameCatalog";
import { GameHeader } from "../components/GameHeader";
import { PageContainer } from "../components/PageContainer";

const tabs=["Resumen","Historial","Frecuencia","Atrasos","Intervalos","Ciclos","Ley del Tercio","Patrones","Generador","Cobertura","Backtest"];
export function CombinationGamePage(){
 const {slug="melate"}=useParams();const id=slug.replaceAll("-","_");const game=gameCatalog.find(x=>x.slug===id)!;
 const [tab,setTab]=useState("Resumen");const [data,setData]=useState<Record<string,unknown>|null>(null);const [tickets,setTickets]=useState<number[][]>([]);const [error,setError]=useState("");
 useEffect(()=>{setData(null);setError("");void api.combinationAnalysis(id).then(setData).catch(()=>setError("No fue posible cargar el juego."))},[id]);
 if(error)return <PageContainer><GameHeader game={game}/><p role="alert">{error}</p></PageContainer>;
 if(data===null)return <PageContainer><GameHeader game={game}/><p>Cargando…</p></PageContainer>;
 return <PageContainer><GameHeader game={game}/><p className="muted">Análisis descriptivo, no predictivo. Premios y ROI: unavailable.</p><nav className="tris-tabs">{tabs.map(x=><button key={x} className={tab===x?"active":""} onClick={()=>setTab(x)}>{x}</button>)}</nav>{tab==="Ley del Tercio"?<section className="empty-panel"><h2>Ley del Tercio</h2><p>LT, CA y PC: not_implemented.</p></section>:tab==="Generador"?<section className="empty-panel"><h2>Generador</h2><button onClick={()=>void api.combinationPortfolio(id,{number_of_tickets:10,strategy:"coverage_optimized",random_seed:42}).then(x=>setTickets(x.tickets)).catch(()=>setError("Generación inválida."))}>Generar cartera</button><p>{tickets.map(x=>x.join(" · ")).join(" | ")}</p></section>:<section className="empty-panel"><h2>{tab}</h2><pre>{JSON.stringify(data,null,2)}</pre></section>}</PageContainer>;
}
