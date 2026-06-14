export interface FfmpegResult {
    found: boolean;
    path: string;
}

export type RunEvent = 
    | { type: "progress"; phase: "scrape" | "download"; current: number; total: number }
    | { type: "log"; level: "info" | "warn" | "error"; message: string }
    | { type: "media"; thumbnail: string; isVideo: boolean }
    | { type: "done"; scraped: number; downloaded: number; videos: number; filtered: number }
    | { type: "error"; message: string };

// match the shape of ScrapeConfig in core/scrape_config.py
export interface RunPayload {
    client: string;
    url: string;
    num: number;
    output_dir: string;
    min_resolution: [number, number];
    delay: number;
    download_streams: boolean;
    skip_remux?: boolean;
    caption_from_title?: boolean;
}

export interface PinterestApi {
    get_core_version(): Promise<string>;
    check_ffmpeg(customPath: string | null): Promise<FfmpegResult>;
    start_run(config: RunPayload): Promise<{ started: boolean;}>;
    terminate(): Promise<void>;
}

declare global {
    interface Window { 
        pywebview?: { 
            api?: PinterestApi 
        }; 
        __pdl_emit?: (raw: string) => void;
    }
}

export function getApi(): PinterestApi | null {
    return window.pywebview?.api ?? null;
}

export function onBridgeReady(fn: () => void): void {
    if (window.pywebview?.api){
        fn();
        return;
    }
    window.addEventListener('pywebviewready', fn, { once: true });
}

type RunEventHandler = (event: RunEvent) => void;

const runEventHandlers = new Set<RunEventHandler>();

/** Subscribe to live run events; returns an unsubscribe fn. */
export function onRunEvent(handler: RunEventHandler): () => void {
    runEventHandlers.add(handler);
    return () => {
        runEventHandlers.delete(handler); // block body so the boolean return doesn't leak to the caller
    };
}

// python calls window.__pdl_emit("<json>") per event. The payload is a JSON string
// (double-encoded on the python side), so parse once and fan out to all subscribers.
window.__pdl_emit = (raw: string) => {
    const event = JSON.parse(raw) as RunEvent;
    for (const handler of runEventHandlers) handler(event);
};