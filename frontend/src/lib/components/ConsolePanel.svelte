<script lang="ts">
	import { cn } from "$lib/utils";
	import { Progress } from "$lib/components/ui/progress";
	import { Badge } from "$lib/components/ui/badge";
	import { ScrollArea } from "$lib/components/ui/scroll-area";
	import Download from "@lucide/svelte/icons/download";
	import Funnel from "@lucide/svelte/icons/funnel";
	import Film from "@lucide/svelte/icons/film";

	// Cosmetic placeholders for the console preview (no real scraping wired up yet).
	const assets = Array.from({ length: 12 }, (_, i) => `https://picsum.photos/seed/pdl${i}/100/100`);
	const tagClass: Record<string, string> = {
		SYS: "bg-primary/10 text-primary",
		DL: "bg-success/10 text-success",
		WARN: "bg-warning/10 text-warning",
		ERR: "bg-destructive/10 text-destructive",
	};
	const logs = [
		{ time: "[00:00]", tag: "SYS", msg: "Ready for initialization." },
		{ time: "[00:01]", tag: "SYS", msg: "Engine initialized sequence for mode: scrape" },
		{ time: "[00:02]", tag: "DL", msg: "Wrote chunk to disk (32/100)" },
		{ time: "[00:03]", tag: "WARN", msg: "Asset skipped: resolution below threshold." },
		{ time: "[00:04]", tag: "DL", msg: "Wrote chunk to disk (64/100)" },
	];
</script>

<section class="flex min-h-0 min-w-0 flex-1 flex-col bg-background">
	<!-- Telemetry -->
	<div class="grid grid-cols-3 border-b border-border bg-card">
		<div class="flex flex-col gap-1 border-r border-border p-4">
			<span class="text-[28px] leading-none font-semibold tracking-tight">0</span>
			<span class="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
				<Download class="size-3" />
				Downloaded
			</span>
		</div>
		<div class="flex flex-col gap-1 border-r border-border p-4">
			<span class="text-[28px] leading-none font-semibold tracking-tight text-muted-foreground">0</span>
			<span class="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
				<Funnel class="size-3" />
				Filtered
			</span>
		</div>
		<div class="flex flex-col gap-1 p-4">
			<span class="text-[28px] leading-none font-semibold tracking-tight text-primary">0</span>
			<span class="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
				<Film class="size-3" />
				Videos
			</span>
		</div>
	</div>

	<!-- Progress -->
	<div class="border-b border-border bg-card p-4">
		<div class="mb-2 flex justify-between text-xs text-muted-foreground">
			<span>Idle</span>
			<span>0%</span>
		</div>
		<Progress value={0} />
	</div>

	<!-- Asset previews -->
	<ScrollArea orientation="horizontal" class="border-b border-border bg-card">
		<div class="flex min-h-[85px] gap-2 p-4">
			{#each assets as asset (asset)}
				<img
					src={asset}
					alt=""
					loading="lazy"
					class="size-[52px] shrink-0 rounded-md border border-border object-cover"
				/>
			{/each}
		</div>
	</ScrollArea>

	<!-- Log -->
	<ScrollArea class="min-h-0 flex-1">
		<div class="flex flex-col gap-1 p-4 font-mono text-[11px] leading-relaxed text-muted-foreground">
			{#each logs as log}
				<div class="flex items-center gap-2">
					<time class="shrink-0 text-muted-foreground/60">{log.time}</time>
					<Badge class={cn("h-4 shrink-0 border-transparent px-1 text-[10px]", tagClass[log.tag])}>
						{log.tag}
					</Badge>
					<span>{log.msg}</span>
				</div>
			{/each}
		</div>
	</ScrollArea>
</section>
