import "@fontsource-variable/inter";
import "@fontsource-variable/jetbrains-mono";
import "./styles.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "@/app/providers";

const root = document.getElementById("root");
if (root === null) throw new Error("index.html has no #root element");

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
