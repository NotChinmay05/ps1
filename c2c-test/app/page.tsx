"use client";

import { AudioLines, BrainCircuit, Clock3, Fingerprint, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";
import { AudioDropzone } from "@/components/AudioDropzone";
import { ResultCard } from "@/components/ResultCard";
import { ValidationBanner } from "@/components/ValidationBanner";
import { submitQuery } from "@/lib/api";
import type { QueryResponse, QueryValidationCode } from "@/lib/types";
import { getValidationMessage } from "@/lib/validation";

export default function Home() {
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(file: File | Blob) {
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await submitQuery(file);
      setResult(response);
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Identification failed. Check the service status and try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleValidationError(code: QueryValidationCode) {
    setError(getValidationMessage(code));
  }

  return (
    <main className="relative min-h-[calc(100vh-3rem)] overflow-hidden">
      <div className="scan-grid pointer-events-none absolute inset-0 opacity-45" />
      <section className="relative mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-7xl items-center gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:py-14">
        <div className="space-y-8">
          <div className="max-w-3xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-cyan">
              <Fingerprint className="h-3.5 w-3.5" aria-hidden="true" />
              Audio fingerprint engine
            </div>
            <h1 className="max-w-4xl text-5xl font-semibold leading-[0.96] tracking-normal text-white sm:text-6xl lg:text-7xl">
              Identify a track from a noisy fragment.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
              Upload or record a short snippet and inspect the matched source, confidence, and end-to-end latency in one focused workspace.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <SignalPill icon={<BrainCircuit className="h-4 w-4" />} label="Fuzzy retrieval" value="noise aware" />
            <SignalPill icon={<Clock3 className="h-4 w-4" />} label="Telemetry" value="ms latency" />
            <SignalPill icon={<ShieldCheck className="h-4 w-4" />} label="Validation" value="preflight checks" />
          </div>

          <div className="rounded-lg border border-line bg-panel/72 p-4 shadow-glow backdrop-blur-xl sm:p-5">
            <AudioDropzone
              disabled={isSubmitting}
              onSubmit={handleSubmit}
              onValidationError={handleValidationError}
            />
            <div className="mt-4">
              <ValidationBanner message={error} />
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <AudioVisual isSubmitting={isSubmitting} />
          <ResultCard result={result} />
        </div>
      </section>
    </main>
  );
}

function SignalPill({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-line bg-white/[0.035] p-4">
      <div className="mb-3 text-cyan">{icon}</div>
      <p className="text-xs uppercase tracking-[0.16em] text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function AudioVisual({ isSubmitting }: { isSubmitting: boolean }) {
  const bars = [38, 72, 48, 90, 56, 78, 44, 84, 62, 96, 42, 70, 52, 88, 46, 74, 58, 82];

  return (
    <section className="relative overflow-hidden rounded-lg border border-line bg-panel/78 p-6 backdrop-blur-xl">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-amber">Live trace</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            {isSubmitting ? "Matching fingerprint" : "Index awaiting snippet"}
          </h2>
        </div>
        <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-cyan/25 bg-cyan/10">
          <AudioLines className="h-5 w-5 text-cyan" aria-hidden="true" />
        </div>
      </div>

      <div className="flex h-56 items-center justify-between gap-2 rounded-lg border border-line bg-ink/70 px-5">
        {bars.map((height, index) => (
          <span
            key={height + index}
            className="audio-line block w-full rounded-full bg-gradient-to-t from-cyan via-mint to-amber"
            style={{
              height: `${height}%`,
              animationDelay: `${index * 90}ms`,
              animationPlayState: isSubmitting ? "running" : "paused",
            }}
          />
        ))}
      </div>

      <div className="mt-5 grid grid-cols-3 gap-3 text-center">
        <TraceStat label="Candidates" value={isSubmitting ? "128" : "--"} />
        <TraceStat label="Offset" value={isSubmitting ? "1.7s" : "--"} />
        <TraceStat label="Threshold" value="72%" />
      </div>
    </section>
  );
}

function TraceStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line bg-white/[0.035] px-3 py-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-mono text-sm text-slate-200">{value}</p>
    </div>
  );
}
