"use client";

import { Mic, Pause, Send, UploadCloud, X } from "lucide-react";
import { ChangeEvent, DragEvent, useRef, useState } from "react";
import { validateAudioFile } from "@/lib/validation";
import type { QueryValidationCode } from "@/lib/types";

type AudioDropzoneProps = {
  disabled?: boolean;
  onSubmit: (file: File | Blob) => void;
  onValidationError: (code: QueryValidationCode) => void;
};

export function AudioDropzone({ disabled, onSubmit, onValidationError }: AudioDropzoneProps) {
  const [selected, setSelected] = useState<File | Blob | null>(null);
  const [selectedName, setSelectedName] = useState<string>("No snippet selected");
  const [isDragging, setIsDragging] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  function acceptFile(file: File | Blob, name = "Recorded snippet.webm") {
    const validation = validateAudioFile(file);
    if (validation) {
      onValidationError(validation);
      return;
    }

    setSelected(file);
    setSelectedName(file instanceof File ? file.name : name);
  }

  function handleInput(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      acceptFile(file);
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) {
      acceptFile(file);
    }
  }

  async function toggleRecording() {
    if (isRecording) {
      recorderRef.current?.stop();
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      onValidationError("unsupported_format");
      return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    chunksRef.current = [];
    recorderRef.current = recorder;

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };

    recorder.onstop = () => {
      stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
      acceptFile(new Blob(chunksRef.current, { type: "audio/webm" }));
    };

    recorder.start();
    setIsRecording(true);
  }

  function submit() {
    if (!selected) {
      onValidationError("empty_file");
      return;
    }

    onSubmit(selected);
  }

  return (
    <section className="space-y-4">
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`relative overflow-hidden rounded-lg border p-6 transition ${
          isDragging
            ? "border-cyan bg-cyan/10"
            : "border-line bg-white/[0.035] hover:border-cyan/45"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="audio/*,.mp3,.wav,.webm,.m4a,.aac,.ogg,.flac"
          className="hidden"
          onChange={handleInput}
        />
        <div className="pointer-events-none absolute inset-x-6 top-5 h-px bg-gradient-to-r from-transparent via-cyan/60 to-transparent" />
        <div className="relative flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg border border-line bg-ink">
              <UploadCloud className="h-5 w-5 text-cyan" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Identify an audio source</h2>
              <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
                Drop a noisy 3-10 second snippet, upload a clean sample, or record from the mic.
              </p>
              <p className="mt-3 max-w-full truncate font-mono text-xs text-slate-300">{selectedName}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="inline-flex h-10 items-center gap-2 rounded-lg border border-line bg-white/[0.05] px-4 text-sm font-semibold text-slate-100 transition hover:border-cyan/45"
            >
              <UploadCloud className="h-4 w-4" aria-hidden="true" />
              Upload
            </button>
            <button
              type="button"
              onClick={toggleRecording}
              className={`inline-flex h-10 items-center gap-2 rounded-lg border px-4 text-sm font-semibold transition ${
                isRecording
                  ? "border-rose/50 bg-rose/15 text-rose"
                  : "border-line bg-white/[0.05] text-slate-100 hover:border-mint/45"
              }`}
            >
              {isRecording ? <Pause className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              {isRecording ? "Stop" : "Record"}
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          type="button"
          onClick={() => {
            setSelected(null);
            setSelectedName("No snippet selected");
          }}
          className="inline-flex h-10 items-center gap-2 rounded-lg border border-line px-4 text-sm text-slate-300 transition hover:border-rose/45 hover:text-rose"
        >
          <X className="h-4 w-4" aria-hidden="true" />
          Clear
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={submit}
          className="inline-flex h-11 items-center gap-2 rounded-lg bg-cyan px-5 text-sm font-bold text-ink transition hover:bg-mint disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Send className="h-4 w-4" aria-hidden="true" />
          {disabled ? "Listening..." : "Run identification"}
        </button>
      </div>
    </section>
  );
}
