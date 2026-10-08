import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

export type ThemeChoice = "light" | "dark" | "system";
type Resolved = "light" | "dark";

const STORAGE_KEY = "theme";
const media = () => window.matchMedia("(prefers-color-scheme: dark)");

function readChoice(): ThemeChoice {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved === "light" || saved === "dark" ? saved : "system";
  } catch {
    return "system"; // storage blocked (private mode): follow the system
  }
}

type ThemeState = {
  choice: ThemeChoice;
  resolved: Resolved;
  setChoice: (choice: ThemeChoice) => void;
};

const ThemeContext = createContext<ThemeState | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [choice, setChoiceState] = useState<ThemeChoice>(readChoice);
  const [systemDark, setSystemDark] = useState(() => media().matches);

  useEffect(() => {
    const query = media();
    const onChange = () => setSystemDark(query.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, []);

  const resolved: Resolved = choice === "system" ? (systemDark ? "dark" : "light") : choice;

  useEffect(() => {
    document.documentElement.classList.toggle("dark", resolved === "dark");
  }, [resolved]);

  const setChoice = useCallback((next: ThemeChoice) => {
    setChoiceState(next);
    try {
      if (next === "system") localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Storage blocked: the choice lasts for this page only.
    }
  }, []);

  const value = useMemo(() => ({ choice, resolved, setChoice }), [choice, resolved, setChoice]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeState {
  const state = useContext(ThemeContext);
  if (state === null) throw new Error("useTheme needs <ThemeProvider>");
  return state;
}
