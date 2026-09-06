import type { Game } from "../types/game";
import { StatusBadge } from "./StatusBadge";

export function GameHeader({ game }: { game: Game }) {
  return (
    <header className="game-header">
      <div>
        <p className="eyebrow">{game.category}</p>
        <h1>{game.display_name}</h1>
      </div>
      <StatusBadge status={game.status} />
    </header>
  );
}
