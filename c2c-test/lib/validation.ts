import type { EvalRowInput, QueryValidationCode } from "@/lib/types";

const supportedTypes = new Set([
  "audio/mpeg",
  "audio/mp3",
  "audio/wav",
  "audio/x-wav",
  "audio/webm",
  "audio/mp4",
  "audio/aac",
  "audio/ogg",
  "audio/flac",
]);

const supportedExtensions = [".mp3", ".wav", ".webm", ".m4a", ".aac", ".ogg", ".flac"];

export function validateAudioFile(file: File | Blob): QueryValidationCode | null {
  if (file.size === 0) {
    return "empty_file";
  }

  if (file.size < 16_000) {
    return "too_short";
  }

  if (file instanceof File) {
    const name = file.name.toLowerCase();
    const hasSupportedExtension = supportedExtensions.some((ext) => name.endsWith(ext));
    const hasSupportedType = supportedTypes.has(file.type);

    if (!hasSupportedExtension && !hasSupportedType) {
      return "unsupported_format";
    }
  }

  return null;
}

export function getValidationMessage(code: QueryValidationCode): string {
  const messages: Record<QueryValidationCode, string> = {
    empty_file: "The selected audio file is empty.",
    too_short: "The snippet is too short. Upload or record at least 1 second of audio.",
    silent_audio: "The snippet appears silent. Try a clearer recording.",
    unsupported_format: "Unsupported format. Use MP3, WAV, WEBM, M4A, AAC, OGG, or FLAC.",
  };

  return messages[code];
}

export function parseEvaluationCsv(text: string): EvalRowInput[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, index) => {
      const [filename, expectedSongId, ...extra] = line.split(",").map((value) => value.trim());

      if (!filename || !expectedSongId || extra.length > 0) {
        throw new Error(`Malformed CSV row ${index + 1}. Use filename,expected_song_id.`);
      }

      return { filename, expectedSongId };
    });
}
