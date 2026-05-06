import { CheckCircle2, FileSpreadsheet, XCircle } from "lucide-react";
import type { EvalResponse } from "@/lib/types";

type EvalResultsProps = {
  result: EvalResponse | null;
};

export function EvalResults({ result }: EvalResultsProps) {
  if (!result) {
    return (
      <section className="rounded-lg border border-dashed border-line bg-white/[0.025] p-6 text-sm text-slate-400">
        <FileSpreadsheet className="mb-4 h-5 w-5 text-amber" aria-hidden="true" />
        Upload a CSV and run the batch to inspect accuracy, false positives, and false negatives.
      </section>
    );
  }

  return (
    <section className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Accuracy" value={`${result.accuracy}%`} tone="mint" />
        <Metric label="False positives" value={String(result.falsePositives)} tone="amber" />
        <Metric label="False negatives" value={String(result.falseNegatives)} tone="rose" />
      </div>

      <div className="overflow-hidden rounded-lg border border-line">
        <div className="max-h-[420px] overflow-auto">
          <table className="w-full min-w-[720px] border-collapse text-left text-sm">
            <thead className="sticky top-0 bg-panel text-xs uppercase tracking-[0.16em] text-slate-400">
              <tr>
                <th className="px-4 py-3">File</th>
                <th className="px-4 py-3">Expected</th>
                <th className="px-4 py-3">Predicted</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Result</th>
              </tr>
            </thead>
            <tbody>
              {result.rows.map((row) => (
                <tr key={`${row.filename}-${row.expectedSongId}`} className="border-t border-line">
                  <td className="px-4 py-3 text-slate-200">{row.filename}</td>
                  <td className="px-4 py-3 font-mono text-slate-300">{row.expectedSongId}</td>
                  <td className="px-4 py-3 font-mono text-slate-300">{row.predictedSongId ?? "NONE"}</td>
                  <td className="px-4 py-3 font-mono text-slate-300">{Math.round(row.confidence * 100)}%</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center gap-2 rounded-full px-2.5 py-1 text-xs font-semibold ${
                        row.passed ? "bg-mint/10 text-mint" : "bg-rose/10 text-rose"
                      }`}
                    >
                      {row.passed ? <CheckCircle2 className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
                      {row.passed ? "pass" : "fail"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: "mint" | "amber" | "rose" }) {
  const toneClass = {
    mint: "text-mint",
    amber: "text-amber",
    rose: "text-rose",
  }[tone];

  return (
    <div className="rounded-lg border border-line bg-white/[0.035] p-4">
      <p className="text-xs uppercase tracking-[0.16em] text-slate-500">{label}</p>
      <p className={`mt-2 text-3xl font-semibold ${toneClass}`}>{value}</p>
    </div>
  );
}
