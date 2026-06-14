// Per-run configuration for the active mode (scrape/search/cache): the target, output,
// extraction options, and engine. Lives in a module-level `$state` so the config panel and
// status footer read/write one source without prop drilling, mirroring `settings.svelte.ts`.

interface RunConfig {
	mode: string;
	source: string;
	output: string;
	limit: number;
	fetchVideos: boolean;
	resW: number;
	resH: number;
	caption: string;
	client: string;
	incognito: boolean;
	strictAlt: boolean;
}

export const run = $state<RunConfig>({
	mode: "scrape",
	source: "https://www.pinterest.com/g/concept-art/",
	output: "./downloads/concept-art",
	limit: 100,
	fetchVideos: false,
	resW: 0,
	resH: 0,
	caption: "none",
	client: "api",
	incognito: true,
	strictAlt: false,
});

export const captionItems: { value: string; label: string }[] = [
	{ value: "none", label: "None" },
	{ value: "txt", label: "TXT Sidecar" },
	{ value: "json", label: "JSON Sidecar" },
	{ value: "metadata", label: "Embed EXIF" },
];

export const clientItems: { value: string; label: string }[] = [
	{ value: "api", label: "API (Default)" },
	{ value: "chromium", label: "Chromium" },
	{ value: "firefox", label: "Firefox" },
];

// Search is API-only in pinterest-dl; keep the engine consistent with the mode. The
// invariant lives with the state so it holds regardless of which component is mounted.
$effect.root(() => {
	$effect(() => {
		if (run.mode === "search") run.client = "api";
	});
});
