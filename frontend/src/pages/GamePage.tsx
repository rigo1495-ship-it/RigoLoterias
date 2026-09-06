import { useParams } from "react-router-dom";

import { gameCatalog } from "../app/gameCatalog";
import { GameHeader } from "../components/GameHeader";
import { PageContainer } from "../components/PageContainer";
import { NotFoundPage } from "./NotFoundPage";

export function GamePage() {
  const { slug = "" } = useParams();
  const normalized = slug.replaceAll("-", "_");
  const game = gameCatalog.find(item => item.slug === normalized);
  if (!game) return <NotFoundPage />;
  const message = game.status === "awaiting_rules"
    ? "Las reglas y el modelo de este juego deben definirse y verificarse antes de su implementación."
    : "Este módulo está planificado. Su motor todavía no ha sido integrado ni validado.";
  return <PageContainer><GameHeader game={game} /><section className="empty-panel"><h2>{game.status === "awaiting_rules" ? "Awaiting rules" : "Planned"}</h2><p>{message}</p><p className="muted">No se muestran análisis, probabilidades ni datos simulados.</p></section></PageContainer>;
}
