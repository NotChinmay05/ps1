import type {
  EvalResponse,
  EvalRowInput,
  HealthResponse,
  QueryResponse,
  SongMatch,
} from "@/lib/types";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const apiMode = process.env.NEXT_PUBLIC_API_MODE ?? "mock";
const shouldUseMock = apiMode !== "live";

const mockSongs = [
  {
    songId: "TRK-1048",
    title: "Midnight Signal",
    artist: "Asha V",
    duration: "3:42",
    genre: "Synthwave",
  },
  {
    songId: "TRK-2190",
    title: "Static Bloom",
    artist: "Nira Sound Lab",
    duration: "4:08",
    genre: "Electronic",
  },
  {
    songId: "TRK-3074",
    title: "Low Tide Memory",
    artist: "The Lattice",
    duration: "2:57",
    genre: "Indie",
  },
];

export async function getHealth(): Promise<HealthResponse> {
  if (!shouldUseMock) {
    const response = await fetch(`${apiBaseUrl}/health`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Health check failed with ${response.status}`);
    }

    return normalizeHealth(await response.json());
  }

  await delay(180);

  return {
    songsLoaded: 3248,
    indexReady: true,
    status: "healthy",
    updatedAt: new Date().toISOString(),
  };
}

export async function submitQuery(file: File | Blob): Promise<QueryResponse> {
  const startedAt = performance.now();

  if (!shouldUseMock) {
    const form = new FormData();
    form.append("file", file, file instanceof File ? file.name : "recording.webm");

    const response = await fetch(`${apiBaseUrl}/api/v1/identify`, {
      method: "POST",
      body: form,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(message ?? `Identification failed with ${response.status}`);
    }

    return normalizeIdentify(await response.json(), Math.round(performance.now() - startedAt));
  }

  await delay(980);

  const sizeSignal = Math.max(0, Math.min(1, file.size / 1_200_000));
  const song = mockSongs[Math.floor(sizeSignal * mockSongs.length) % mockSongs.length];
  const confidence = Math.round((0.82 + sizeSignal * 0.12) * 100) / 100;

  return {
    match: song,
    confidence,
    latencyMs: Math.round(performance.now() - startedAt),
    status: "matched",
  };
}

export async function runEvaluation(rows: EvalRowInput[]): Promise<EvalResponse> {
  if (!shouldUseMock) {
    throw new Error("The backend does not expose a batch evaluation endpoint yet.");
  }

  await delay(1200);

  const results = rows.map((row, index) => {
    const passed = index % 5 !== 3;
    const predictedSongId = passed
      ? row.expectedSongId
      : index % 2 === 0
        ? "UNKNOWN"
        : `TRK-${2000 + index}`;

    return {
      ...row,
      predictedSongId,
      confidence: passed ? 0.88 + (index % 8) * 0.01 : 0.42 + (index % 4) * 0.04,
      passed,
    };
  });

  const passedCount = results.filter((row) => row.passed).length;
  const falseNegatives = results.filter((row) => row.predictedSongId === "UNKNOWN").length;
  const falsePositives = results.length - passedCount - falseNegatives;

  return {
    accuracy: results.length ? Math.round((passedCount / results.length) * 1000) / 10 : 0,
    falsePositives,
    falseNegatives,
    rows: results,
  };
}

async function readErrorMessage(response: Response): Promise<string | null> {
  try {
    const payload = await response.json();
    if (typeof payload.detail === "string") return payload.detail;
    if (typeof payload.message === "string") return payload.message;
    if (typeof payload.error === "string") return payload.error;
  } catch {
    return null;
  }
  return null;
}

function normalizeHealth(payload: Record<string, unknown>): HealthResponse {
  const rawStatus = String(payload.status ?? payload.system_status ?? "healthy").toLowerCase();
  const status =
    rawStatus === "offline" ? "offline" : rawStatus === "degraded" ? "degraded" : "healthy";

  const songsLoaded = Number(
    payload.songsLoaded ??
      payload.songs_loaded ??
      payload.total_tracks ??
      payload.indexed_tracks ??
      payload.tracks ??
      0,
  );

  return {
    songsLoaded: Number.isFinite(songsLoaded) ? songsLoaded : 0,
    indexReady: Boolean(
      payload.indexReady ??
        payload.index_ready ??
        payload.redis_ready ??
        payload.ready ??
        status === "healthy",
    ),
    status,
    updatedAt: String(payload.updatedAt ?? payload.updated_at ?? new Date().toISOString()),
  };
}

function normalizeIdentify(payload: Record<string, unknown>, clientLatencyMs: number): QueryResponse {
  const hasMatch = payload.match !== null && payload.match !== undefined;
  const confidence = Number(payload.confidence ?? 0);
  const normalizedConfidence = confidence > 1 ? confidence / 100 : confidence;
  
  let latencyValue: number;
  if (typeof payload.latency === "number") {
    latencyValue = payload.latency;
  } else if (payload.latency && typeof payload.latency === "object") {
    latencyValue = Number((payload.latency as any).total || clientLatencyMs);
  } else {
    latencyValue = clientLatencyMs;
  }

  return {
    match: hasMatch ? normalizeSong(payload) : null,
    confidence: Math.max(0, Math.min(1, normalizedConfidence)),
    latencyMs: latencyValue,
    status: hasMatch ? "matched" : "unknown",
  };
}

function normalizeSong(payload: Record<string, unknown>): SongMatch {
  const matchData = (payload.match && typeof payload.match === 'object') 
    ? (payload.match as Record<string, unknown>) 
    : payload;

  return {
    songId: String(matchData.songId ?? matchData.filename ?? "UNKNOWN"),
    title: String(matchData.title ?? matchData.name ?? "Unknown title"),
    artist: String(matchData.artist ?? "Unknown artist"),
    duration: String(matchData.duration ?? matchData.duration_sec ?? "--"),
    genre: String(matchData.genre ?? matchData.type ?? "Unknown genre"),
  };
}

function getObject(value: unknown): Record<string, unknown> | null {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return null;
}
