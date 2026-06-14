import { onRunEvent, type RunEvent } from "$lib/api";
export type RunStatusValue =  "idle" | "running" | "done" | "error";
export type RunPhase = "scrape" | "download";

export interface LogLine {
    time: string;
    level: "info" | "warn" | "error";
    phase: RunPhase | null;  // null for logs not associated with a phase
    message: string;
}

export interface Preview {
    thumbnail: string;  // base64 data URI of the downloaded image, or "" for video streams
    isVideo: boolean;
}

interface RunStatus {
    status: RunStatusValue;
    phase: RunPhase | null;  // null when not running
    current: number;
    total: number;
    logs: LogLine[];
    previews: Preview[];
    counts: {
        downloaded: number;
        videos: number;
        saved: number;  // records written to a metadata cache; drives the "Saved" tile
    }
    startedAt: number;
}
export const runStatus = $state<RunStatus>({
    status: "idle",
    phase: null,
    current: 0,
    total: 0,
    logs: [],
    previews: [],
    counts: { downloaded: 0, videos: 0, saved: 0 },
    startedAt: 0,
});

/** Clear prior state and arm a fresh run. Called by ConfigPanel on Execute, before start_run. */
export function resetRun(): void {
    runStatus.status = "running";
    runStatus.phase = "scrape";
    runStatus.current = 0;
    runStatus.total = 0;
    runStatus.logs = [];
    runStatus.previews = [];
    runStatus.counts = { downloaded: 0, videos: 0, saved: 0 };
    runStatus.startedAt = Date.now();  // log timestamps are relative to this
}

// [mm:ss] since the run armed -- the frontend owns timestamps (Python sends none).
function elapsed(): string {
    const seconds = Math.floor((Date.now() - runStatus.startedAt) / 1000);
    const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
    const ss = String(seconds % 60).padStart(2, "0");
    return `[${mm}:${ss}]`;
}

/** Apply a run event to the status. Subscribed once at module level for the app's lifetime. */
function apply(event: RunEvent): void {
    switch (event.type) {
        case "progress":
            runStatus.phase = event.phase;
            runStatus.current = event.current;
            runStatus.total = event.total;
            // Downloaded tile is driven by download-phase progress; done reconciles it.
            if (event.phase === "download") runStatus.counts.downloaded = event.current;
            break;
        case "log":
            runStatus.logs.push({
                time: elapsed(),
                level: event.level,
                phase: runStatus.phase,  // tag the line with whatever phase is live
                message: event.message,
            });
            break;
        case "media":
            runStatus.previews.push({ thumbnail: event.thumbnail, isVideo: event.isVideo });
            if (event.isVideo) runStatus.counts.videos += 1;  // live tally as files download
            break;
        case "done":
            runStatus.status = "done";
            runStatus.phase = null;
            // Authoritative final counts replace the live estimates.
            runStatus.counts = {
                downloaded: event.downloaded,
                videos: event.videos,
                saved: event.saved,
            };
            break;
        case "error":
            runStatus.status = "error";
            runStatus.phase = null;
            runStatus.logs.push({ time: elapsed(), level: "error", phase: null, message: event.message });
            break;
        default:
            event satisfies never;  // compile-time exhaustiveness: a new variant won't compile until handled
    }
}

// Subscribe once for the app's lifetime; no teardown needed for a module-level singleton.
onRunEvent(apply);