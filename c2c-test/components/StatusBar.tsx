"use client";

import { Activity, Database, RadioTower } from "lucide-react";
import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";

export function StatusBar() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let active = true;

    async function refresh() {
      try {
        const response = await getHealth();
        if (active) {
          setHealth(response);
        }
      } catch {
        if (active) {
          setHealth({
            songsLoaded: 0,
            indexReady: false,
            status: "offline",
            updatedAt: new Date().toISOString(),
          });
        }
      }
    }

    refresh();
    const interval = window.setInterval(refresh, 8000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const statusColor =
    health?.status === "healthy"
      ? "bg-mint"
      : health?.status === "degraded"
        ? "bg-amber"
        : "bg-rose";

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-ink/86 backdrop-blur-xl">
      <div className="mx-auto flex min-h-12 w-full max-w-7xl items-center justify-between gap-3 px-4 text-xs text-slate-300 sm:px-6">
        <div className="flex min-w-0 items-center gap-2">
          <RadioTower className="h-4 w-4 shrink-0 text-cyan" aria-hidden="true" />
          <span className="truncate font-semibold tracking-wide text-slate-100">EchoTrace</span>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          <div className="flex shrink-0 items-center gap-2 rounded-full border border-line bg-white/[0.04] px-3 py-1.5">
            <span className={`h-2 w-2 rounded-full ${statusColor}`} />
            <span className="capitalize">{health?.status ?? "checking"}</span>
          </div>
          <div className="flex shrink-0 items-center gap-2 rounded-full border border-line bg-white/[0.04] px-3 py-1.5">
            <Database className="h-3.5 w-3.5 text-amber" aria-hidden="true" />
            <span>{health ? health.songsLoaded.toLocaleString() : "..."} songs</span>
          </div>
          <div className="flex shrink-0 items-center gap-2 rounded-full border border-line bg-white/[0.04] px-3 py-1.5">
            <Activity className="h-3.5 w-3.5 text-mint" aria-hidden="true" />
            <span className={health?.indexReady ? "shiny-text font-semibold" : "text-slate-400"}>
              {health?.indexReady ? "index ready" : "index warming"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
