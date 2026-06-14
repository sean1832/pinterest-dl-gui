// Per-run configuration for the active mode (scrape/search/cache): the target, output,
// and extraction options. Lives in a module-level `$state` so the config panel and
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
	strictAlt: boolean;
}

export const run = $state<RunConfig>({
	mode: "scrape",
	source: "",
	output: "./downloads",
	limit: 1,
	fetchVideos: false,
	resW: 0,
	resH: 0,
	caption: "none",
	strictAlt: false,
});

export const captionItems: { value: string; label: string }[] = [
	{ value: "none", label: "None" },
	{ value: "txt", label: "TXT Sidecar" },
	{ value: "json", label: "JSON Sidecar" },
	{ value: "metadata", label: "Embed EXIF" },
];
