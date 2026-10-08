/// <reference types="vitest/config" />
import path from "node:path";

import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const API = "http://127.0.0.1:8000";

export default defineConfig({
  // The router plugin must come before react(); the wrong order fails silently.
  plugins: [tanstackRouter({ target: "react", autoCodeSplitting: true }), react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(import.meta.dirname, "src") },
  },
  server: {
    host: "127.0.0.1",
    // The browser calls the same origin; Vite sends API paths on. No CORS needed.
    proxy: { "/api": API, "/health": API },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["src/test/setup.ts"],
    css: false,
  },
});
