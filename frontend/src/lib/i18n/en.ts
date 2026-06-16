// English is the source of truth for every user-facing string.

// Conventions:
// - Group keys by the UI region they appear in (mode / config / settings / console / ...).
// - Keep paired strings together: an option's `title` and `desc` live in one object so
//   neither can go missing without the other.
// - Interpolated strings are functions, not "{placeholder}" templates, so the argument is
//   type-checked at every call site.
// - Technical tokens (log tags, file paths, example URLs) stay inline in components; they
//   are not translated.

export const en = {
	common: {
		select: "Select",
	},
	mode: {
		scrape: "Scrape",
		search: "Search",
		download: "Download",
	},
	config: {
		groups: {
			target: "Target",
			extraction: "Extraction Options",
			metadataCache: "Metadata Cache",
		},
		// The single source field is relabelled per mode.
		sourceLabel: {
			url: "Source URL",
			query: "Search Query",
			cacheFile: "Cache File",
		},
		outputDir: "Output Directory",
		num: "Max Items",
		fetchVideos: {
			title: "Fetch Videos",
			desc: "Download HLS video segments and mux to MP4.",
		},
		minResolution: {
			title: "Minimum Resolution",
			desc: "Discard assets smaller than dimensions (0 disables).",
		},
		metadataStrategy: {
			title: "Metadata Strategy",
			desc: "Format for accompanying alt text/captions.",
		},
		strictAlt: {
			title: "Strict Alt-Text",
			desc: "Drop assets lacking valid captions.",
		},
		// Keyed by the caption `value` in run.svelte.ts (captionValues).
		captions: {
			none: "None",
			txt: "TXT Sidecar",
			json: "JSON Sidecar",
			metadata: "Embed EXIF",
		},
		saveCache: {
			title: "Save Metadata Cache",
			desc: "Write scraped records to a JSON file for reuse in Download mode.",
		},
		cachePath: "Cache Path",
		cachePathHint: "Follows the output directory until you change it.",
		skipDownload: {
			title: "Skip Download",
			desc: "Save metadata only; don't download media.",
		},
		execute: "Execute",
		terminate: "Terminate",
	},
	settings: {
		button: "Settings",
		title: "Settings",
		description: "Global configuration shared across all modes.",
		sections: {
			language: "Language",
			auth: "Authentication",
			ffmpeg: "Video / FFmpeg",
			network: "Network Defaults",
		},
		language: {
			label: "Interface Language",
		},
		cookies: {
			label: "Session Cookies File",
			tooltip:
				"Shared by Scrape and Search. Required only for private boards; public endpoints operate without session state.",
			placeholder: "No file loaded",
			captureTooltip:
				"Capture a new cookies from Pinterest by logging in through an embedded browser window.",
		},
		cookieStatus: {
			valid: "Valid",
			expired: "Expired",
			checking: "Checking",
			unknown: "Unknown",
		},
		cookieMessage: {
			expired: "Session expired - recapture to refresh.",
			validUntil: (date: string) => `Valid until ${date}`,
			unknownExpiry: "No expiry info - validity unknown.",
		},
		ffmpeg: {
			label: "FFmpeg",
			tooltip:
				"Required to remux HLS video into MP4. Without it, videos are saved as raw .ts segments.",
			notResolved: "Not resolved",
			recheckTooltip: "Re-check FFmpeg availability",
			customPathLabel: "Custom FFmpeg Path",
			customPathPlaceholder: "Leave empty to use PATH",
		},
		ffmpegStatus: {
			found: "Found",
			missing: "Not found",
			checking: "Checking",
			unknown: "Unknown",
		},
		network: {
			delay: {
				label: "Request Delay (s)",
				tooltip:
					"Applied per request. Higher delay is gentler on Pinterest and reduces rate-limiting.",
			},
			timeout: {
				label: "Timeout (s)",
				tooltip:
					"Maximum wait time per request before it is aborted. Applied to every run.",
			},
			maxWorkers: {
				label: "Max Concurrent Downloads",
				tooltip:
					"How many files download in parallel. Higher is faster but higher risk of rate-limiting. (1-16, defaults to 8)",
			},
		},
	},
	console: {
		saved: "Saved",
		downloaded: "Downloaded",
		videos: "Videos",
		phase: {
			idle: "Idle",
			done: "Done",
			error: "Error",
			downloading: "Downloading",
			scraping: "Scraping",
		},
	},
	statusBar: {
		ready: "READY",
		ffmpeg: "FFMPEG",
	},
};

// The translation contract. Other locales must match this shape (see PartialMessages).
export type Messages = typeof en;

// A locale may translate any subset of the tree; omitted keys fall back to English at
// runtime (see mergeMessages in index.svelte.ts). Functions and primitives are leaves:
// they are replaced wholesale, never merged, so an interpolation function stays callable.
export type PartialMessages<T> = {
	[K in keyof T]?: T[K] extends (...args: never[]) => unknown
		? T[K]
		: T[K] extends object
			? PartialMessages<T[K]>
			: T[K];
};
