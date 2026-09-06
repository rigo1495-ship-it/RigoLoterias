import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "../layouts/AppShell";
import { GamePage } from "../pages/GamePage";
import { HomePage } from "../pages/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { TrisPage } from "../pages/TrisPage";
import { CombinationGamePage } from "../pages/CombinationGamePage";
import { GanaGatoPage } from "../pages/GanaGatoPage";
import { PoolGamePage } from "../pages/PoolGamePage";

export const router = createBrowserRouter([
  { path: "/", element: <AppShell />, children: [
    { index: true, element: <HomePage /> },
    { path: "games/tris", element: <TrisPage /> },
    { path: "games/melate", element: <CombinationGamePage /> },
    { path: "games/melate-retro", element: <CombinationGamePage /> },
    { path: "games/chispazo", element: <CombinationGamePage /> },
    { path: "games/gana-gato", element: <GanaGatoPage /> },
    { path: "games/progol", element: <PoolGamePage /> },
    { path: "games/progol-media-semana", element: <PoolGamePage /> },
    { path: "games/:slug", element: <GamePage /> },
    { path: "*", element: <NotFoundPage /> },
  ] },
]);
