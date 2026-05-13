import { Gauge, Music2, Timer, WandSparkles } from "lucide-react";
import type { QueryResponse } from "@/lib/types";

type ResultCardProps = {
  result: QueryResponse | null;
};

export function ResultCard({ result }: ResultCardProps) {
  if (!result) {
    return (
      <section className="rounded-lg border border-dashed border-line bg-white/[0.025] p-6 text-sm text-slate-400">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg border border-line bg-white/[0.04]">
          <WandSparkles className="h-5 w-5 text-cyan" aria-hidden="true" />
        </div>
        <p>Submit an audio snippet to see the closest source, confidence score, and measured latency.</p>
      </section>
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <section className="rounded-lg border border-cyan/25 bg-panel/86 p-5 shadow-glow">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-cyan">
            Best match
          </p>
          <h2 className="text-2xl font-semibold text-white">{result.match?.title ?? "Unknown source"}</h2>
          <p className="mt-1 text-sm text-slate-300">
            {result.match ? `${result.match.artist} / ${result.match.genre}` : "No indexed song crossed the threshold"}
          </p>
        </div>
        <div className="rounded-full border border-mint/25 bg-mint/10 px-3 py-1 text-sm font-semibold text-mint">
          {result.status}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-line bg-white/[0.035] p-4">
          <Music2 className="mb-3 h-4 w-4 text-amber" aria-hidden="true" />
          <p className="text-xs text-slate-400">Song ID</p>
          <p className="mt-1 font-mono text-sm text-slate-100">{result.match?.songId ?? "NONE"}</p>
        </div>
        <div className="rounded-lg border border-line bg-white/[0.035] p-4">
          <Timer className="mb-3 h-4 w-4 text-cyan" aria-hidden="true" />
          <p className="text-xs text-slate-400">Latency</p>
          <p className="mt-1 font-mono text-sm text-slate-100">{String(result.latencyMs)} ms</p>
        </div>
        <div className="rounded-lg border border-line bg-white/[0.035] p-4">
          <Gauge className="mb-3 h-4 w-4 text-mint" aria-hidden="true" />
          <p className="text-xs text-slate-400">Duration</p>
          <p className="mt-1 font-mono text-sm text-slate-100">{result.match?.duration ?? "--"}</p>
        </div>
      </div>

      <div className="mt-5">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-slate-300">Confidence</span>
          <span className="font-mono text-mint">{String(confidencePercent)}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-mint via-cyan to-amber"
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
      </div>
    </section>
  );
}
