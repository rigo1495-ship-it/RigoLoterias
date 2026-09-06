import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { AppShell } from "../layouts/AppShell";
import { GamePage } from "../pages/GamePage";
import { HomePage } from "../pages/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";

function renderAt(path: string) {
  return render(<MemoryRouter initialEntries={[path]}><Routes><Route path="/" element={<AppShell />}><Route index element={<HomePage />} /><Route path="games/:slug" element={<GamePage />} /><Route path="*" element={<NotFoundPage />} /></Route></Routes></MemoryRouter>);
}

test("app renders complete navigation", () => {
  renderAt("/");
  for (const label of ["Inicio", "TRIS", "Melate Retro", "Chispazo", "Gana Gato", "Progol Media Semana", "Protouch"]) expect(screen.getByRole("link", { name: label })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "Lotería Nacional" })).not.toBeInTheDocument();
});


test("invalid route renders 404", () => {
  renderAt("/missing");
  expect(screen.getByText("Página no encontrada")).toBeInTheDocument();
});
