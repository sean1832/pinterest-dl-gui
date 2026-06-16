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
    import { i18n, setLocale, localeOptions, type Locale } from '$lib/i18n/index.svelte';
    import * as Dialog from '$lib/components/ui/dialog';
    import * as Select from '$lib/components/ui/select';
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { NumberInput } from '$lib/components/ui/number-input';
    import { Label } from '$lib/components/ui/label';
    import { Badge } from '$lib/components/ui/badge';
    import { Separator } from '$lib/components/ui/separator';
    import InfoTooltip from '$lib/components/info-tooltip.svelte';
    import TooltipButton from '$lib/components/tooltip-button.svelte';
    import Settings from '@lucide/svelte/icons/settings';
    import Languages from '@lucide/svelte/icons/languages';
    import KeyRound from '@lucide/svelte/icons/key-round';
    import Film from '@lucide/svelte/icons/film';
    import Gauge from '@lucide/svelte/icons/gauge';
    import FolderOpen from '@lucide/svelte/icons/folder-open';
    import RefreshCw from '@lucide/svelte/icons/refresh-cw';
    import CircleCheck from '@lucide/svelte/icons/circle-check';
    import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
    import LoaderCircle from '@lucide/svelte/icons/loader-circle';
    import CircleQuestionMark from '@lucide/svelte/icons/circle-question-mark';

    // Badge color per status; the label is localized (i18n.settings.ffmpegStatus/cookieStatus).
    const ffmpegStatusClass: Record<FfmpegStatus, string> = {
        found: 'bg-success/10 text-success',
        missing: 'bg-destructive/10 text-destructive',
        checking: 'bg-muted text-muted-foreground',
        unknown: 'bg-muted text-muted-foreground'
    };
    const status = $derived({
        label: i18n.m.settings.ffmpegStatus[settings.ffmpegStatus],
        class: ffmpegStatusClass[settings.ffmpegStatus]
    });

    const cookieStatusClass: Record<CookieStatus, string> = {
        valid: 'bg-success/10 text-success',
        expired: 'bg-destructive/10 text-destructive',
        checking: 'bg-muted text-muted-foreground',
        unknown: 'bg-muted text-muted-foreground'
    };
    const cookie = $derived({
        label: i18n.m.settings.cookieStatus[settings.cookieStatus],
        class: cookieStatusClass[settings.cookieStatus]
    });

    const currentLocaleName = $derived(
        localeOptions.find((o) => o.value === i18n.locale)?.name ?? i18n.locale
    );

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
                {i18n.m.settings.button}
            </Button>
        {/snippet}
    </Dialog.Trigger>

    <Dialog.Content class="sm:max-w-lg">
        <Dialog.Header>
            <Dialog.Title>{i18n.m.settings.title}</Dialog.Title>
            <Dialog.Description>{i18n.m.settings.description}</Dialog.Description>
        </Dialog.Header>

        <div class="flex min-w-0 flex-col gap-6 text-xs">
            <!-- Language -->
            <section class="flex flex-col gap-3">
                {@render sectionLabel(Languages, i18n.m.settings.sections.language)}
                <div class="flex flex-col gap-1.5">
                    <Label for="set-locale">{i18n.m.settings.language.label}</Label>
                    <Select.Root
                        type="single"
                        value={i18n.locale}
                        onValueChange={(value) => setLocale(value as Locale)}
                    >
                        <Select.Trigger id="set-locale" class="w-full">
                            {currentLocaleName}
                        </Select.Trigger>
                        <Select.Content>
                            <Select.Group>
                                {#each localeOptions as option (option.value)}
                                    <Select.Item value={option.value} label={option.name} />
                                {/each}
                            </Select.Group>
                        </Select.Content>
                    </Select.Root>
                </div>
            </section>

            <Separator />

            <!-- Authentication -->
            <section class="flex flex-col gap-3">
                {@render sectionLabel(KeyRound, i18n.m.settings.sections.auth)}
                <div class="flex flex-col gap-1.5">
                    <div class="flex items-center gap-1.5">
                        <Label for="set-cookies">{i18n.m.settings.cookies.label}</Label>
                        <InfoTooltip text={i18n.m.settings.cookies.tooltip} />
                    </div>
                    <div class="flex">
                        <Input
                            id="set-cookies"
                            bind:value={settings.cookies}
                            placeholder={i18n.m.settings.cookies.placeholder}
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
                            tooltip={i18n.m.settings.cookies.captureTooltip}
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
                                    >{i18n.m.settings.cookieMessage.expired}</span
                                >
                            {:else if settings.cookieStatus === 'valid' && settings.cookieExpiry}
                                <span class="text-muted-foreground"
                                    >{i18n.m.settings.cookieMessage.validUntil(
                                        formatExpiry(settings.cookieExpiry)
                                    )}</span
                                >
                            {:else if settings.cookieStatus === 'unknown'}
                                <span class="text-muted-foreground"
                                    >{i18n.m.settings.cookieMessage.unknownExpiry}</span
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
                    {@render sectionLabel(Film, i18n.m.settings.sections.ffmpeg)}
                    <InfoTooltip text={i18n.m.settings.ffmpeg.tooltip} />
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
                            <span class="text-muted-foreground">{i18n.m.settings.ffmpeg.label}</span>
                        </div>
                        <span
                            class="truncate font-mono text-[11px] text-muted-foreground/70"
                            title={settings.ffmpegResolved}
                        >
                            {settings.ffmpegResolved || i18n.m.settings.ffmpeg.notResolved}
                        </span>
                    </div>
                    <TooltipButton
                        tooltip={i18n.m.settings.ffmpeg.recheckTooltip}
                        variant="outline"
                        size="sm"
                        class="shrink-0"
                        onclick={() => checkFfmpeg()}
                    >
                        <RefreshCw />
                    </TooltipButton>
                </div>
                <div class="flex flex-col gap-1.5">
                    <Label for="set-ffmpeg">{i18n.m.settings.ffmpeg.customPathLabel}</Label>

                    <div class="flex">
                        <Input
                            id="set-ffmpeg"
                            bind:value={settings.ffmpegPath}
                            placeholder={i18n.m.settings.ffmpeg.customPathPlaceholder}
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
                {@render sectionLabel(Gauge, i18n.m.settings.sections.network)}
                <div class="flex gap-3">
                    <div class="flex flex-1 flex-col gap-1.5">
                        <div class="flex items-center gap-1.5">
                            <Label for="set-delay">{i18n.m.settings.network.delay.label}</Label>
                            <InfoTooltip text={i18n.m.settings.network.delay.tooltip} />
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
                            <Label for="set-timeout">{i18n.m.settings.network.timeout.label}</Label>
                            <InfoTooltip text={i18n.m.settings.network.timeout.tooltip} />
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
                        <Label for="set-max-workers">{i18n.m.settings.network.maxWorkers.label}</Label>
                        <InfoTooltip text={i18n.m.settings.network.maxWorkers.tooltip} />
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
