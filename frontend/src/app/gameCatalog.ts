import type { Game } from "../types/game";

export const gameCatalog: Game[] = [
  { slug: "tris", display_name: "TRIS", category: "positional", status: "available", capabilities: ["history", "statistics", "analysis", "generation", "backtesting", "simulation", "settlement"] },
  { slug: "melate", display_name: "Melate", category: "combination", status: "available", capabilities: ["history", "statistics", "analysis", "generation", "backtesting", "simulation"] },
  { slug: "melate_retro", display_name: "Melate Retro", category: "combination", status: "available", capabilities: ["history", "statistics", "analysis", "generation", "backtesting", "simulation"] },
  { slug: "chispazo", display_name: "Chispazo", category: "combination", status: "available", capabilities: ["history", "statistics", "analysis", "generation", "backtesting", "simulation", "settlement"] },
  { slug: "loteria_nacional", display_name: "Lotería Nacional", category: "dedicated", status: "awaiting_rules", capabilities: [] },
  { slug: "gana_gato", display_name: "Gana Gato", category: "board", status: "available", capabilities: ["history", "statistics", "analysis", "generation", "backtesting", "simulation", "settlement"] },
  { slug: "progol", display_name: "Progol", category: "pool", status: "planned", capabilities: [] },
  { slug: "progol_media_semana", display_name: "Progol Media Semana", category: "pool", status: "planned", capabilities: [] },
  { slug: "protouch", display_name: "Protouch", category: "protouch", status: "planned", capabilities: [] },
];

export const pathFor = (slug: string) => `/games/${slug.replaceAll("_", "-")}`;
