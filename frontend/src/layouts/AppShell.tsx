import { NavLink, Outlet } from "react-router-dom";

import { pathFor } from "../app/gameCatalog";

const primary = [
  ["TRIS", "tris"],
  ["Chispazo", "chispazo"],
  ["Gana Gato", "gana_gato"],
  ["Protouch", "protouch"],
];

export function AppShell() {
  const link = ({ isActive }: { isActive: boolean }) => (isActive ? "nav-link active" : "nav-link");
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span>RL</span><strong>RigoLoterias</strong></div>
        <nav aria-label="Navegación principal">
          <NavLink to="/" end className={link}>Inicio</NavLink>
          {primary.slice(0, 1).map(([name, slug]) => <NavLink key={slug} to={pathFor(slug)} className={link}>{name}</NavLink>)}
          <div className="nav-group"><span>Melate</span>
            <NavLink to={pathFor("melate")} className={link}>Melate</NavLink>
            <NavLink to={pathFor("melate_retro")} className={link}>Melate Retro</NavLink>
          </div>
          {primary.slice(1, 4).map(([name, slug]) => <NavLink key={slug} to={pathFor(slug)} className={link}>{name}</NavLink>)}
          <div className="nav-group"><span>Progol</span>
            <NavLink to={pathFor("progol")} className={link}>Progol</NavLink>
            <NavLink to={pathFor("progol_media_semana")} className={link}>Progol Media Semana</NavLink>
          </div>
          {primary.slice(4).map(([name, slug]) => <NavLink key={slug} to={pathFor(slug)} className={link}>{name}</NavLink>)}
        </nav>
      </aside>
      <section className="content"><Outlet /></section>
    </div>
  );
}
