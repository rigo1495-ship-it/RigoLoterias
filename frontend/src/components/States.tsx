export function LoadingState() {
  return <p className="state">Cargando…</p>;
}

export function EmptyState({ message = "No hay datos disponibles." }: { message?: string }) {
  return <p className="state">{message}</p>;
}

export function ErrorState({ message }: { message: string }) {
  return <p className="state state-error">{message}</p>;
}
