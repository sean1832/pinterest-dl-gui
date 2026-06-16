// Per-run configuration for the active mode (scrape/search/download): the target, output,
// and extraction options. Lives in a module-level `$state` so the config panel and
// status footer read/write one source without prop drilling, mirroring `settings.svelte.ts`.

interface RunConfig {
	mode: string;
	sourceByMode: Record<string, string>;
	source: string;
	output: string;
	limit: number;
	fetchVideos: boolean;
	resW: number;
	resH: number;
	caption: string;
	strictAlt: boolean;
	// Output: scrape/search can persist records to a cache JSON, and optionally stop there.
	saveCache: boolean;
	cachePath: string; // empty -> auto metadata_<timestamp>.json under the output dir
	skipDownload: boolean;
}

export const run = $state<RunConfig>({
	mode: "scrape",
	sourceByMode: { scrape: "", search: "", download: "" },
	source: "",
	output: "./downloads",
	limit: 1,
	fetchVideos: false,
	resW: 0,
	resH: 0,
	caption: "none",
	strictAlt: false,
	saveCache: false,
	cachePath: "",
	skipDownload: false,
});

// Caption strategy values. Labels are localized via i18n (config.captions, keyed by value).
export const captionValues = ["none", "txt", "json", "metadata"] as const;
