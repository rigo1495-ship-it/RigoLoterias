import { Link } from "react-router-dom";
import { PageContainer } from "../components/PageContainer";

export function NotFoundPage() {
  return <PageContainer><section className="empty-panel"><p className="eyebrow">404</p><h1>Página no encontrada</h1><Link to="/">Volver al inicio</Link></section></PageContainer>;
}
