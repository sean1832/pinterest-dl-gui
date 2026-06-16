import type { Messages, PartialMessages } from "./en";

// Chinese translation. This file is intentionally PARTIAL: any key omitted here falls back
// to the English string at runtime, so you can translate incrementally. To expand it,
// follow the shape of `en` in ./en.ts and fill in more keys -- TypeScript checks that each
// key you add exists in English and has the right type.
export const zh: PartialMessages<Messages> = {
	common: {
		select: "选择",
	},
	mode: {
		scrape: "抓取",
		search: "搜索",
		download: "下载",
	},
	config: {
		groups: {
			target: "目标",
			extraction: "提取选项",
			metadataCache: "元数据缓存",
		},
		// The single source field is relabelled per mode.
		sourceLabel: {
			url: "目标链接",
			query: "搜索关键词",
			cacheFile: "缓存文件",
		},
		outputDir: "输出目录",
		num: "最大数量",
		fetchVideos: {
			title: "下载视频",
			desc: "下载 HLS 视频片段并合并为 MP4。",
		},
		minResolution: {
			title: "最小分辨率",
			desc: "过滤小于该尺寸的图片, 设为 0 则关闭。",
		},
		metadataStrategy: {
			title: "文字描述",
			desc: "如何保存图片的标题、描述等文字信息。",
		},
		strictAlt: {
			title: "过滤无描述内容",
			desc: "仅下载包含标题或描述的图片, 舍弃无文字信息的内容。",
		},
		// Keyed by the caption `value` in run.svelte.ts (captionValues).
		captions: {
			none: "不保存",
			txt: "保存为 TXT",
			json: "保存为 JSON",
			metadata: "嵌入 EXIF",
		},
		saveCache: {
			title: "保存元数据",
			desc: "将抓取结果保存为 JSON 文件, 供下载模式复用。",
		},
		cachePath: "缓存文件路径",
		cachePathHint: "跟随输出目录, 手动修改后不再自动同步。",
		skipDownload: {
			title: "跳过下载",
			desc: "仅保存元数据, 不下载媒体文件。",
		},
		execute: "执行",
		terminate: "终止",
	},
	settings: {
		button: "设置",
		title: "设置",
		description: "全局配置, 所有模式共用。",
		sections: {
			language: "语言",
			auth: "认证",
			ffmpeg: "视频 / FFmpeg",
			network: "网络设置",
		},
		language: {
			label: "界面语言",
		},
		cookies: {
			label: "Cookie 文件",
			tooltip:
				"抓取与搜索模式共用。公开内容无需登录, 仅访问私有画板时需要。",
			placeholder: "未选择文件",
			captureTooltip:
				"通过内嵌浏览器登录 Pinterest, 自动获取 Cookie。",
		},
		cookieStatus: {
			valid: "有效",
			expired: "已过期",
			checking: "检查中",
			unknown: "未知",
		},
		cookieMessage: {
			expired: "登录已过期, 请重新获取。",
			validUntil: (date: string) => `有效期至 ${date}`,
			unknownExpiry: "无法检测有效期, 状态未知。",
		},
		ffmpeg: {
			label: "FFmpeg",
			tooltip:
				"用于将 HLS 视频合并为 MP4。若未检测到, 视频将以原始 .ts 片段保存。",
			notResolved: "未找到",
			recheckTooltip: "重新检测 FFmpeg",
			customPathLabel: "自定义路径",
			customPathPlaceholder: "留空则使用系统 PATH",
		},
		ffmpegStatus: {
			found: "已找到",
			missing: "未找到",
			checking: "检查中",
			unknown: "未知",
		},
		network: {
			delay: {
				label: "请求间隔（秒）",
				tooltip:
					"每次请求之间的等待时间。间隔越长对 Pinterest 越友好, 可降低限流风险。",
			},
			timeout: {
				label: "请求超时（秒）",
				tooltip:
					"单个请求的最长等待时间, 超时后自动中止。",
			},
			maxWorkers: {
				label: "最大并发下载数",
				tooltip:
					"同时下载的文件数量。数值越大速度越快, 但限流风险也越高。范围 1-16, 默认 8。",
			},
		},
	},
	console: {
		saved: "已缓存",
		downloaded: "已下载",
		videos: "视频",
		phase: {
			idle: "空闲",
			done: "完成",
			error: "错误",
			downloading: "下载中",
			scraping: "抓取中",
		},
	},
	statusBar: {
		ready: "就绪",
		ffmpeg: "FFMPEG",
	},
};
