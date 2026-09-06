import type { GameStatus } from "../types/game";

const labels: Record<GameStatus, string> = {
  available: "Available",
  planned: "Planned",
  awaiting_rules: "Awaiting rules",
  disabled: "Disabled",
};

export function StatusBadge({ status }: { status: GameStatus }) {
  return <span className={`status-badge status-${status}`}>{labels[status]}</span>;
}
