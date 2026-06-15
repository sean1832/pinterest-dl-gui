export interface FfmpegResult {
    found: boolean;
    path: string;
}

export interface CaptureCookiesResult {
    success: boolean;
    path: string;
    message: string;
}

export type RunEvent = 
    | { type: "progress"; phase: "scrape" | "download"; current: number; total: number }
    | { type: "log"; level: "info" | "warn" | "error"; message: string }
    | { type: "media"; thumbnail: string; isVideo: boolean }
    | { type: "done"; scraped: number; downloaded: number; videos: number; saved: number }
    | { type: "error"; message: string };

// match the shape of ScrapeConfig in core/scrape_config.py
export interface RunPayload {
    url: string;
    mode: string;
    num: number;
    output_dir: string;
    min_resolution: [number, number];
    delay: number;
    timeout?: number;
    cookies?: string;
    ensure_alt?: boolean;
    ffmpeg_path?: string;
    download_streams: boolean;
    skip_remux?: boolean;
    caption?: string;
    caption_from_title?: boolean;
    save_cache?: boolean;
    cache_path?: string;
    skip_download?: boolean;
}

export interface PinterestApi {
    get_core_version(): Promise<string>;
    check_ffmpeg(customPath: string | null): Promise<FfmpegResult>;
    capture_cookies(): Promise<CaptureCookiesResult>;
    start_run(config: RunPayload): Promise<{ started: boolean;}>;
    terminate(): Promise<void>;
    select_cache_file(defaultPath: string): Promise<string>;
    select_json_file(defaultPath: string): Promise<string>;
    select_folder(defaultPath: string): Promise<string>;
    select_file(defaultPath: string): Promise<string>;
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