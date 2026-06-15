import { getApi, onBridgeReady } from "$lib/api";

export type FfmpegStatus = "unknown" | "checking" | "found" | "missing";
export type CookieStatus = "unknown" | "checking" | "valid" | "expired";

interface Settings {
	cookies: string;
	cookieStatus: CookieStatus;
	cookieExpiry: number | null; // Unix seconds of the earliest-expiring cookie, or null when unknown
	ffmpegPath: string;
	ffmpegStatus: FfmpegStatus;
	ffmpegResolved: string;
	delay: number;
	timeout: number;
}

const STORAGE_KEY = "pdl.settings";

export const settings = $state<Settings>({
	cookies: "",
	cookieStatus: "unknown",
	cookieExpiry: null,
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

// Auto-check on bridge ready so the dialog never opens showing "Unknown" for the first time.
// Cookies are restored from localStorage synchronously above, so the path is set by now.
onBridgeReady(() => {
	checkFfmpeg();
	checkCookieStatus();
});

// Resolve FFmpeg via the Python bridge. Under `vite dev` (no pywebview) the status stays
// "unknown" so the dev preview still runs; the real check runs inside the packaged app.
export async function checkFfmpeg(): Promise<void> {
	const api = getApi();
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

// Check the saved cookies file's expiry via the Python bridge. With no path set (or under
// `vite dev` without pywebview) the status stays "unknown" so no badge is shown.
export async function checkCookieStatus(): Promise<void> {
	const api = getApi();
	if (!api || !settings.cookies.trim()) {
		settings.cookieStatus = "unknown";
		settings.cookieExpiry = null;
		return;
	}
	settings.cookieStatus = "checking";
	try {
		const result = await api.check_cookie_status(settings.cookies);
		settings.cookieStatus = result.state;
		settings.cookieExpiry = result.expiry;
	} catch {
		// Bridge call failed - fall back to unknown rather than a false "expired".
		settings.cookieStatus = "unknown";
		settings.cookieExpiry = null;
	}
}
