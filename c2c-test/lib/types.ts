export type HealthStatus = "healthy" | "degraded" | "offline";

export type HealthResponse = {
  songsLoaded: number;
  indexReady: boolean;
  status: HealthStatus;
  updatedAt: string;
};

export type SongMatch = {
  songId: string;
  title: string;
  artist: string;
  duration: string;
  genre: string;
};

export type QueryResponse = {
  match: SongMatch | null;
  confidence: number;
  latencyMs: number;
  status: "matched" | "unknown";
};

export type QueryValidationCode =
  | "too_short"
  | "silent_audio"
  | "unsupported_format"
  | "empty_file";

export type EvalRowInput = {
  filename: string;
  expectedSongId: string;
};

export type EvalResultRow = EvalRowInput & {
  predictedSongId: string | null;
  confidence: number;
  passed: boolean;
};

export type EvalResponse = {
  accuracy: number;
  falsePositives: number;
  falseNegatives: number;
  rows: EvalResultRow[];
};
