# Frontend Build Plan

> From all 18 issues, only **7 touch the frontend directly**. The rest are backend concerns. This document covers the complete frontend build — two pages, one persistent layout, three API endpoints.

---

## Two Pages + One Persistent Layout

---

### `app/layout.tsx` — Persistent Status Bar
**Issues covered: 1, 18**

A sticky top bar that polls `GET /health` every 5–10 seconds. Shows three things:

- Number of songs loaded
- Index ready / not ready
- Red/green system indicator

Keep it minimal — one line across the top. Use React Bits' `<ShinyText>` on the "ready" badge for a subtle alive-system feel.

---

### `app/page.tsx` — Query Page
**Issues covered: 5, 9, 12, 13**

The entire core interaction. Three vertical zones:

**1. Upload / Record Zone**
A drag-and-drop area plus a mic button. On submit, `POST /query` with the audio as `multipart/form-data`. Client-side validation runs before the request fires (Issue 12).

**2. Validation Feedback**
A red error banner below the upload zone, conditionally rendered. Covers three distinct cases — each returns a specific message from the backend, surfaced here:
- File too short
- Silent audio
- Wrong format

**3. Result Card**
Slides in after a successful response. Displays:
- Matched song metadata
- Confidence percentage with a progress bar
- End-to-end latency in milliseconds (pulled from response or measured with `performance.now()`)

---

### `app/eval/page.tsx` — Evaluation Page
**Issue covered: 14**

A separate route — not linked from main nav. Evaluators navigate directly. Three sections:

- **CSV upload area** — each row is `filename,expected_song_id`
- **"Run evaluation" button** — posts the batch
- **Results panel** — shows accuracy %, false positive count, false negative count, and a per-query pass/fail table

---

## API Surface

These are the only three endpoints the frontend needs to wire up:

| Endpoint | Method | Used by |
|---|---|---|
| `/health` | GET | Status bar — Issues 1, 18 |
| `/query` | POST | Query page — Issues 5, 9, 12, 13 |
| `/eval` | POST | Eval page — Issue 14 |

---

## File Structure

```
app/
  layout.tsx          ← status bar lives here
  page.tsx            ← query page
  eval/
    page.tsx          ← evaluation page

components/
  StatusBar.tsx       ← health polling + indicators
  AudioDropzone.tsx   ← upload + mic record
  ResultCard.tsx      ← match result, confidence, latency
  ValidationBanner.tsx
  EvalResults.tsx     ← table + metric cards

lib/
  api.ts              ← typed fetch wrappers for all 3 endpoints
```

---

## Key Implementation Notes

**Mic recording**
Use the native `MediaRecorder` API — no library needed. Record to a `Blob`, send as `audio/webm`. The backend handles format conversion.

**Latency display (Issue 13)**
Measure on the client with `performance.now()` around the fetch call. Cross-reference with whatever the backend logs. Display as `42 ms` inline next to the result — don't hide it in a tooltip.

**Eval CSV parsing (Issue 14)**
Parse client-side with a simple line-split before submitting. Show a row count preview (`"18 queries loaded"`) and catch malformed files before the network request goes out.

**Status bar polling (Issue 18)**
Use `setInterval` inside a `useEffect` with proper cleanup. No SWR — it's overkill for a health ping. Just `fetch('/health')` every 8 seconds.