<script lang="ts">
    import { cn } from '$lib/utils';
    import { getApi } from '$lib/api';
    import {
        settings,
        checkFfmpeg,
        checkCookieStatus,
        type FfmpegStatus,
        type CookieStatus
    } from '$lib/state/settings.svelte';
    import * as Dialog from '$lib/components/ui/dialog';
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { NumberInput } from '$lib/components/ui/number-input';
    import { Label } from '$lib/components/ui/label';
    import { Badge } from '$lib/components/ui/badge';
    import { Separator } from '$lib/components/ui/separator';
    import InfoTooltip from '$lib/components/info-tooltip.svelte';
    import TooltipButton from '$lib/components/tooltip-button.svelte';
    import Settings from '@lucide/svelte/icons/settings';
    import KeyRound from '@lucide/svelte/icons/key-round';
    import Film from '@lucide/svelte/icons/film';
    import Gauge from '@lucide/svelte/icons/gauge';
    import FolderOpen from '@lucide/svelte/icons/folder-open';
    import RefreshCw from '@lucide/svelte/icons/refresh-cw';
    import CircleCheck from '@lucide/svelte/icons/circle-check';
    import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
    import LoaderCircle from '@lucide/svelte/icons/loader-circle';
    import CircleQuestionMark from '@lucide/svelte/icons/circle-question-mark';

    const statusMeta: Record<FfmpegStatus, { label: string; class: string }> = {
        found: { label: 'Found', class: 'bg-success/10 text-success' },
        missing: { label: 'Not found', class: 'bg-destructive/10 text-destructive' },
        checking: { label: 'Checking', class: 'bg-muted text-muted-foreground' },
        unknown: { label: 'Unknown', class: 'bg-muted text-muted-foreground' }
    };
    const status = $derived(statusMeta[settings.ffmpegStatus]);

    const cookieMeta: Record<CookieStatus, { label: string; class: string }> = {
        valid: { label: 'Valid', class: 'bg-success/10 text-success' },
        expired: { label: 'Expired', class: 'bg-destructive/10 text-destructive' },
        checking: { label: 'Checking', class: 'bg-muted text-muted-foreground' },
        unknown: { label: 'Unknown', class: 'bg-muted text-muted-foreground' }
    };
    const cookie = $derived(cookieMeta[settings.cookieStatus]);

    function formatExpiry(unixSeconds: number): string {
        return new Date(unixSeconds * 1000).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    let capturing = $state(false); // disable capture button + show spinner while in progress

    async function browseCookies() {
        const api = getApi();
        if (!api) return;
        const path = await api.select_json_file(settings.cookies);
        if (path) {
            settings.cookies = path;
            await checkCookieStatus();
        }
    }

    async function captureCookies() {
        const api = getApi();
        if (!api) return;
        capturing = true;
        try {
            const result = await api.capture_cookies();
            if (result.success) {
                settings.cookies = result.path;
                await checkCookieStatus();
            } else {
                console.warn(`Cookie capture failed: ${result.message}`); // non-critical, so just log it
            }
        } catch (err) {
            console.error(`Unexpected error: ${err instanceof Error ? err.message : String(err)}`);
        } finally {
            capturing = false; // re-enable button regardless of outcome
        }
    }

    async function browseFfmpeg() {
        const api = getApi();
        if (!api) return;
        const path = await api.select_file(settings.ffmpegPath);
        if (path) {
            settings.ffmpegPath = path;
            await checkFfmpeg();
        }
    }
</script>

{#snippet sectionLabel(icon: typeof Settings, text: string)}
    {@const Icon = icon}
    <div
        class="flex items-center gap-2 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase"
    >
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
                {@render sectionLabel(KeyRound, 'Authentication')}
                <div class="flex flex-col gap-1.5">
                    <div class="flex items-center gap-1.5">
                        <Label for="set-cookies">Session Cookies File</Label>
                        <InfoTooltip
                            text="Shared by Scrape and Search. Required only for private boards; public endpoints operate without session state."
                        />
                    </div>
                    <div class="flex">
                        <Input
                            id="set-cookies"
                            bind:value={settings.cookies}
                            placeholder="No file loaded"
                            class="flex-1 rounded-r-none border-r-0 font-mono"
                        />
                        <Button
                            variant="outline"
                            class="shrink-0 rounded-none"
                            onclick={browseCookies}
                        >
                            <FolderOpen />
                        </Button>
                        <TooltipButton
                            tooltip="Capture a new cookies from Pinterest by logging in through an embedded browser window."
                            variant="outline"
                            class="shrink-0 rounded-l-none"
                            onclick={captureCookies}
                            disabled={capturing}
                        >
                            {#if capturing}
                                <LoaderCircle class="animate-spin" />
                            {:else}
                                <KeyRound />
                            {/if}
                        </TooltipButton>
                    </div>

                    {#if settings.cookies}
                        <div class="flex items-center gap-2">
                            <Badge class={cn('border-transparent', cookie.class)}>
                                {#if settings.cookieStatus === 'valid'}
                                    <CircleCheck />
                                {:else if settings.cookieStatus === 'expired'}
                                    <TriangleAlert />
                                {:else if settings.cookieStatus === 'checking'}
                                    <LoaderCircle class="animate-spin" />
                                {:else}
                                    <CircleQuestionMark />
                                {/if}
                                {cookie.label}
                            </Badge>
                            {#if settings.cookieStatus === 'expired'}
                                <span class="text-destructive"
                                    >Session expired - recapture to refresh.</span
                                >
                            {:else if settings.cookieStatus === 'valid' && settings.cookieExpiry}
                                <span class="text-muted-foreground"
                                    >Valid until {formatExpiry(settings.cookieExpiry)}</span
                                >
                            {:else if settings.cookieStatus === 'unknown'}
                                <span class="text-muted-foreground"
                                    >No expiry info - validity unknown.</span
                                >
                            {/if}
                        </div>
                    {/if}
                </div>
            </section>

            <Separator />

            <!-- Video / FFmpeg -->
            <section class="flex flex-col gap-3">
                <div class="flex items-center gap-1.5">
                    {@render sectionLabel(Film, 'Video / FFmpeg')}
                    <InfoTooltip
                        text="Required to remux HLS video into MP4. Without it, videos are saved as raw .ts segments."
                    />
                </div>
                <div
                    class="flex items-center justify-between gap-3 rounded-md border border-border bg-card p-3"
                >
                    <div class="flex min-w-0 flex-col gap-1">
                        <div class="flex items-center gap-2">
                            <Badge class={cn('border-transparent', status.class)}>
                                {#if settings.ffmpegStatus === 'found'}
                                    <CircleCheck />
                                {:else if settings.ffmpegStatus === 'missing'}
                                    <TriangleAlert />
                                {:else if settings.ffmpegStatus === 'checking'}
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
                            {settings.ffmpegResolved || 'Not resolved'}
                        </span>
                    </div>
                    <TooltipButton
                        tooltip="Re-check FFmpeg availability"
                        variant="outline"
                        size="sm"
                        class="shrink-0"
                        onclick={() => checkFfmpeg()}
                    >
                        <RefreshCw />
                    </TooltipButton>
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
                        <Button
                            variant="outline"
                            class="shrink-0 rounded-l-none"
                            onclick={browseFfmpeg}
                        >
                            <FolderOpen />
                        </Button>
                    </div>
                </div>
            </section>

            <Separator />

            <!-- Network -->
            <section class="flex flex-col gap-3">
                {@render sectionLabel(Gauge, 'Network Defaults')}
                <div class="flex gap-3">
                    <div class="flex flex-1 flex-col gap-1.5">
                        <div class="flex items-center gap-1.5">
                            <Label for="set-delay">Request Delay (s)</Label>
                            <InfoTooltip
                                text="Applied per request. Higher delay is gentler on Pinterest and reduces rate-limiting."
                            />
                        </div>
                        <NumberInput
                            id="set-delay"
                            bind:value={settings.delay}
                            step={0.1}
                            min={0}
                        />
                    </div>
                    <div class="flex flex-1 flex-col gap-1.5">
                        <div class="flex items-center gap-1.5">
                            <Label for="set-timeout">Timeout (s)</Label>
                            <InfoTooltip
                                text="Maximum wait time per request before it is aborted. Applied to every run."
                            />
                        </div>
                        <NumberInput
                            id="set-timeout"
                            bind:value={settings.timeout}
                            step={1}
                            min={0}
                        />
                    </div>
                </div>
                <div class="flex flex-col gap-1.5">
                    <div class="flex items-center gap-1.5">
                        <Label for="set-max-workers">Max Concurrent Downloads</Label>
                        <InfoTooltip
                            text="How many files download in parallel. Higher is faster but higher risk of rate-limiting. (1-16, defaults to 8)"
                        />
                    </div>
                    <NumberInput
                        id="set-max-workers"
                        bind:value={settings.maxWorkers}
                        step={1}
                        min={1}
                        max={16}
                    />
                </div>
            </section>
        </div>
    </Dialog.Content>
</Dialog.Root>
