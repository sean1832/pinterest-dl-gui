// App-global settings shared across modes (scrape/search/cache): authentication,
// the FFmpeg toolchain, and network defaults. Lives in a module-level `$state` so the
// config panel, footer, and Settings dialog all read/write one source without prop drilling.

export type FfmpegStatus = "unknown" | "checking" | "found" | "missing";

interface FfmpegResult {
	found: boolean;
	path: string;
}

// The pywebview js_api surface (Python `Api` methods). Absent under `vite dev`.
interface PinterestApi {
	check_ffmpeg(customPath: string | null): Promise<FfmpegResult>;
}

declare global {
	interface Window {
		pywebview?: { api?: PinterestApi };
	}
}

interface Settings {
	cookies: string;
	ffmpegPath: string;
	ffmpegStatus: FfmpegStatus;
	ffmpegResolved: string;
	delay: number;
	timeout: number;
}

const STORAGE_KEY = "pdl.settings";

export const settings = $state<Settings>({
	cookies: "",
	ffmpegPath: "",
	ffmpegStatus: "unknown",
	ffmpegResolved: "",
	delay: 0.2,
	timeout: 10,
});

// Restore durable fields synchronously at module init (before any component renders).
const raw = localStorage.getItem(STORAGE_KEY);
if (raw) {
	try {
		const saved = JSON.parse(raw) as Partial<Settings>;
		if (typeof saved.cookies === "string") settings.cookies = saved.cookies;
		if (typeof saved.ffmpegPath === "string") settings.ffmpegPath = saved.ffmpegPath;
		if (typeof saved.delay === "number") settings.delay = saved.delay;
		if (typeof saved.timeout === "number") settings.timeout = saved.timeout;
	} catch {
		// Corrupt JSON in localStorage - keep defaults rather than failing startup.
	}
}

// Persist only durable fields (not transient ffmpeg status). The root effect lives for
// the app's lifetime, which is the intended scope for global settings.
$effect.root(() => {
	$effect(() => {
		const durable = {
			cookies: settings.cookies,
			ffmpegPath: settings.ffmpegPath,
			delay: settings.delay,
			timeout: settings.timeout,
		};
		localStorage.setItem(STORAGE_KEY, JSON.stringify(durable));
	});
});

// Resolve FFmpeg via the Python bridge. Under `vite dev` (no pywebview) the status stays
// "unknown" so the dev preview still runs; the real check runs inside the packaged app.
export async function checkFfmpeg(): Promise<void> {
	const api = window.pywebview?.api;
	if (!api) {
		settings.ffmpegStatus = "unknown";
		return;
	}
	settings.ffmpegStatus = "checking";
	try {
		const result = await api.check_ffmpeg(settings.ffmpegPath || null);
		settings.ffmpegStatus = result.found ? "found" : "missing";
		settings.ffmpegResolved = result.path;
	} catch {
		// Bridge call failed - surface as missing so the user can fix the path.
		settings.ffmpegStatus = "missing";
		settings.ffmpegResolved = "";
	}
}
