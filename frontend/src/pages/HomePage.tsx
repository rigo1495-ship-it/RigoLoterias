import { Link } from "react-router-dom";

import { gameCatalog, pathFor } from "../app/gameCatalog";
import { PageContainer } from "../components/PageContainer";
import { StatusBadge } from "../components/StatusBadge";

export function HomePage() {
  return <PageContainer><header className="hero"><p className="eyebrow">Plataforma canónica</p><h1>Análisis modular, reglas explícitas.</h1><p>Phase A establece la arquitectura. Los motores se integrarán y validarán por juego en fases posteriores.</p></header><section className="game-grid">{gameCatalog.map(game => <Link className="game-card" to={pathFor(game.slug)} key={game.slug}><span>{game.category}</span><h2>{game.display_name}</h2><StatusBadge status={game.status} /></Link>)}</section></PageContainer>;
}
