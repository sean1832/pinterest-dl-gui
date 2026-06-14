<script lang="ts">
	import { cn } from "$lib/utils";
	import { settings, checkFfmpeg, type FfmpegStatus } from "$lib/state/settings.svelte";
	import * as Dialog from "$lib/components/ui/dialog";
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
	import { Label } from "$lib/components/ui/label";
	import { Badge } from "$lib/components/ui/badge";
	import Settings from "@lucide/svelte/icons/settings";
	import KeyRound from "@lucide/svelte/icons/key-round";
	import Film from "@lucide/svelte/icons/film";
	import Gauge from "@lucide/svelte/icons/gauge";
	import FolderOpen from "@lucide/svelte/icons/folder-open";
	import RefreshCw from "@lucide/svelte/icons/refresh-cw";
	import CircleCheck from "@lucide/svelte/icons/circle-check";
	import TriangleAlert from "@lucide/svelte/icons/triangle-alert";
	import LoaderCircle from "@lucide/svelte/icons/loader-circle";
	import CircleQuestionMark from "@lucide/svelte/icons/circle-question-mark";

	const statusMeta: Record<FfmpegStatus, { label: string; class: string }> = {
		found: { label: "Found", class: "bg-success/10 text-success" },
		missing: { label: "Not found", class: "bg-destructive/10 text-destructive" },
		checking: { label: "Checking", class: "bg-muted text-muted-foreground" },
		unknown: { label: "Unknown", class: "bg-muted text-muted-foreground" },
	};
	const status = $derived(statusMeta[settings.ffmpegStatus]);

	// Cosmetic stand-in for the `login` capture flow until the bridge is wired.
	function captureCookies() {
		settings.cookies = "./cookies/session.json";
	}
</script>

{#snippet sectionLabel(icon: typeof Settings, text: string)}
	{@const Icon = icon}
	<div class="flex items-center gap-2 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
		<Icon class="size-3.5" />
		<span>{text}</span>
	</div>
{/snippet}

<Dialog.Root>
	<Dialog.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="outline" size="sm">
				<Settings />
				Settings
			</Button>
		{/snippet}
	</Dialog.Trigger>

	<Dialog.Content class="sm:max-w-lg">
		<Dialog.Header>
			<Dialog.Title>Settings</Dialog.Title>
			<Dialog.Description>Global configuration shared across all modes.</Dialog.Description>
		</Dialog.Header>

		<div class="flex min-w-0 flex-col gap-6 text-xs">
			<!-- Authentication -->
			<section class="flex flex-col gap-3">
				{@render sectionLabel(KeyRound, "Authentication")}
				<div class="flex flex-col gap-1.5">
					<Label for="set-cookies">Session Cookies File</Label>
					<div class="flex">
						<Input
							id="set-cookies"
							bind:value={settings.cookies}
							placeholder="No file loaded"
							class="flex-1 rounded-r-none border-r-0 font-mono"
						/>
						<Button variant="outline" class="shrink-0 rounded-l-none" onclick={captureCookies}>
							<KeyRound />
							Capture
						</Button>
					</div>
				</div>
				<p class="rounded-md bg-muted/40 p-2 leading-relaxed text-muted-foreground">
					Shared by Scrape and Search. Required only for private boards; public endpoints operate
					without session state.
				</p>
			</section>

			<!-- Video / FFmpeg -->
			<section class="flex flex-col gap-3">
				{@render sectionLabel(Film, "Video / FFmpeg")}
				<div class="flex items-center justify-between gap-3 rounded-md border border-border bg-card p-3">
					<div class="flex min-w-0 flex-col gap-1">
						<div class="flex items-center gap-2">
							<Badge class={cn("border-transparent", status.class)}>
								{#if settings.ffmpegStatus === "found"}
									<CircleCheck />
								{:else if settings.ffmpegStatus === "missing"}
									<TriangleAlert />
								{:else if settings.ffmpegStatus === "checking"}
									<LoaderCircle class="animate-spin" />
								{:else}
									<CircleQuestionMark />
								{/if}
								{status.label}
							</Badge>
							<span class="text-muted-foreground">FFmpeg</span>
						</div>
						<span
							class="truncate font-mono text-[11px] text-muted-foreground/70"
							title={settings.ffmpegResolved}
						>
							{settings.ffmpegResolved || "Not resolved"}
						</span>
					</div>
					<Button variant="outline" size="sm" class="shrink-0" onclick={() => checkFfmpeg()}>
						<RefreshCw />
						Test
					</Button>
				</div>
				<div class="flex flex-col gap-1.5">
					<Label for="set-ffmpeg">Custom FFmpeg Path</Label>
					<div class="flex">
						<Input
							id="set-ffmpeg"
							bind:value={settings.ffmpegPath}
							placeholder="Leave empty to use PATH"
							class="flex-1 rounded-r-none border-r-0 font-mono"
						/>
						<Button variant="outline" class="shrink-0 rounded-l-none">
							<FolderOpen />
							Browse
						</Button>
					</div>
				</div>
				<p class="rounded-md bg-muted/40 p-2 leading-relaxed text-muted-foreground">
					Required to remux HLS video into MP4. Without it, videos are saved as raw .ts segments.
				</p>
			</section>

			<!-- Network -->
			<section class="flex flex-col gap-3">
				{@render sectionLabel(Gauge, "Network Defaults")}
				<div class="flex gap-3">
					<div class="flex flex-1 flex-col gap-1.5">
						<Label for="set-delay">Request Delay (s)</Label>
						<Input id="set-delay" type="number" bind:value={settings.delay} step="0.1" min="0" />
					</div>
					<div class="flex flex-1 flex-col gap-1.5">
						<Label for="set-timeout">Timeout (s)</Label>
						<Input id="set-timeout" type="number" bind:value={settings.timeout} step="1" min="0" />
					</div>
				</div>
				<p class="rounded-md bg-muted/40 p-2 leading-relaxed text-muted-foreground">
					Applied to every run. Higher delay is gentler on Pinterest and reduces rate-limiting.
				</p>
			</section>
		</div>
	</Dialog.Content>
</Dialog.Root>
