export type GameStatus = "available" | "planned" | "awaiting_rules" | "disabled";

export type Capability =
  | "history"
  | "statistics"
  | "analysis"
  | "generation"
  | "backtesting"
  | "simulation"
  | "contests"
  | "settlement";

export interface Game {
  slug: string;
  display_name: string;
  category: string;
  status: GameStatus;
  capabilities: Capability[];
}
