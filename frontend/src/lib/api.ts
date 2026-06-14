export interface FfmpegResult {
    found: boolean;
    path: string;
}

export interface PinterestApi {
    get_core_version(): Promise<string>;
    check_ffmpeg(customPath: string | null): Promise<FfmpegResult>;
}

declare global {
    interface Window { 
        pywebview?: { 
            api?: PinterestApi 
        }; 
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