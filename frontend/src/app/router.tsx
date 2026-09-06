import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "../layouts/AppShell";
import { GamePage } from "../pages/GamePage";
import { HomePage } from "../pages/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { TrisPage } from "../pages/TrisPage";

export const router = createBrowserRouter([
  { path: "/", element: <AppShell />, children: [
    { index: true, element: <HomePage /> },
    { path: "games/tris", element: <TrisPage /> },
    { path: "games/:slug", element: <GamePage /> },
    { path: "*", element: <NotFoundPage /> },
  ] },
]);
