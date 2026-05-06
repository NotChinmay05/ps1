"use client";

import { FileUp, Play } from "lucide-react";
import { ChangeEvent, useState } from "react";
import { EvalResults } from "@/components/EvalResults";
import { ValidationBanner } from "@/components/ValidationBanner";
import { runEvaluation } from "@/lib/api";
import type { EvalResponse, EvalRowInput } from "@/lib/types";
import { parseEvaluationCsv } from "@/lib/validation";

export default function EvaluationPage() {
  const [rows, setRows] = useState<EvalRowInput[]>([]);
  const [result, setResult] = useState<EvalResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    try {
      const text = await file.text();
      const parsed = parseEvaluationCsv(text);
      setRows(parsed);
      setResult(null);
      setError(null);
    } catch (caught) {
      setRows([]);
      setError(caught instanceof Error ? caught.message : "Unable to parse CSV.");
    }
  }

  async function executeEvaluation() {
    if (rows.length === 0) {
      setError("Upload a CSV with rows formatted as filename,expected_song_id.");
      return;
    }

    setIsRunning(true);
    setError(null);

    try {
      setResult(await runEvaluation(rows));
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Evaluation failed. Check the service status and try again.",
      );
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <main className="relative min-h-[calc(100vh-3rem)] overflow-hidden px-4 py-10 sm:px-6">
      <div className="scan-grid pointer-events-none absolute inset-0 opacity-35" />
      <div className="relative mx-auto max-w-6xl space-y-7">
        <section className="max-w-3xl">
          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.22em] text-cyan">Evaluator route</p>
          <h1 className="text-4xl font-semibold leading-tight text-white sm:text-5xl">
            Batch accuracy checks for known query sets.
          </h1>
          <p className="mt-4 text-base leading-7 text-slate-300">
            Upload a CSV of query filenames and expected song IDs to inspect aggregate accuracy and per-query outcomes.
          </p>
        </section>

        <section className="grid gap-5 lg:grid-cols-[0.75fr_1.25fr]">
          <div className="space-y-4">
            <label className="flex min-h-52 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-line bg-white/[0.035] p-6 text-center transition hover:border-cyan/45">
              <FileUp className="mb-4 h-7 w-7 text-cyan" aria-hidden="true" />
              <span className="text-lg font-semibold text-white">Upload evaluation CSV</span>
              <span className="mt-2 text-sm leading-6 text-slate-400">
                Each row should contain filename,expected_song_id.
              </span>
              <input type="file" accept=".csv,text/csv" className="hidden" onChange={handleFile} />
            </label>

            <div className="rounded-lg border border-line bg-panel/78 p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Loaded rows</p>
              <p className="mt-2 text-3xl font-semibold text-white">{rows.length}</p>
            </div>

            <button
              type="button"
              onClick={executeEvaluation}
              disabled={isRunning}
              className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-cyan px-5 text-sm font-bold text-ink transition hover:bg-mint disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Play className="h-4 w-4" aria-hidden="true" />
              {isRunning ? "Running evaluation..." : "Run evaluation"}
            </button>

            <ValidationBanner message={error} />
          </div>

          <EvalResults result={result} />
        </section>
      </div>
    </main>
  );
}
