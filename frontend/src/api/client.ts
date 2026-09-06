import type { Game } from "../types/game";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const api = {
  games: () => request<Game[]>("/games"),
  game: (slug: string) => request<Game>(`/games/${slug}`),
  trisDraws: () => request<Array<{ draw_number: string; draw_date: string; winning_number: string }>>("/tris/draws"),
  trisStatistics: () => request<Record<string, unknown>>("/tris/statistics"),
  trisPortfolio: (body: { count: number; strategy: string; seed: number }) => request<{ tickets: string[] }>("/tris/portfolios", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
};
