import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "../layouts/AppShell";
import { GamePage } from "../pages/GamePage";
import { HomePage } from "../pages/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { TrisPage } from "../pages/TrisPage";
import { CombinationGamePage } from "../pages/CombinationGamePage";

export const router = createBrowserRouter([
  { path: "/", element: <AppShell />, children: [
    { index: true, element: <HomePage /> },
    { path: "games/tris", element: <TrisPage /> },
    { path: "games/melate", element: <CombinationGamePage /> },
    { path: "games/melate-retro", element: <CombinationGamePage /> },
    { path: "games/chispazo", element: <CombinationGamePage /> },
    { path: "games/:slug", element: <GamePage /> },
    { path: "*", element: <NotFoundPage /> },
  ] },
]);
