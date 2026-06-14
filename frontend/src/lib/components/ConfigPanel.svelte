<script lang="ts">
    import { cn } from '$lib/utils';
    import { run, captionItems } from '$lib/state/run.svelte';
    import { OptionRow, OptionGroup, OptionGroupSub } from '$lib/components/ui/option-row';
    import SettingsDialog from '$lib/components/SettingsDialog.svelte';
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { NumberInput } from '$lib/components/ui/number-input';
    import { Label } from '$lib/components/ui/label';
    import { Switch } from '$lib/components/ui/switch';
    import { ScrollArea } from '$lib/components/ui/scroll-area';
    import { ToggleGroup, ToggleGroupItem } from '$lib/components/ui/toggle-group';
    import * as Select from '$lib/components/ui/select';
    import Download from '@lucide/svelte/icons/download';
    import Search from '@lucide/svelte/icons/search';
    import FileDown from '@lucide/svelte/icons/file-down';
    import FolderOpen from '@lucide/svelte/icons/folder-open';
    import Play from '@lucide/svelte/icons/play';
    import Square from '@lucide/svelte/icons/square';
    import { getApi } from '$lib/api';
    import { runStatus, resetRun } from '$lib/state/runStatus.svelte';
    import { settings } from '$lib/state/settings.svelte';

    // Width is owned by the shell's resizable split and passed down explicitly.
    let { width }: { width: number } = $props();

    const showLimit = $derived(run.mode !== 'download');
    const showBrowseSource = $derived(run.mode === 'download');
    const captionLabel = $derived(
        captionItems.find((i) => i.value === run.caption)?.label ?? 'Select'
    );

    const isRunning = $derived(runStatus.status === 'running');

    // The cache path tracks the output directory until the user overrides it (by typing
    // or picking a file); after that it stays put. The timestamp default is resolved in
    // Python only as a fallback when the field is left empty.
    let cachePathEdited = $state(false);

    function defaultCachePath(output: string): string {
        const dir = output.trim().replace(/[\\/]+$/, '');
        return dir ? `${dir}/metadata.json` : 'metadata.json';
    }

    $effect(() => {
        if (!cachePathEdited) run.cachePath = defaultCachePath(run.output);
    });

    async function browseCacheFile(): Promise<void> {
        const api = getApi();
        if (!api) return;
        try {
            const picked = await api.select_cache_file(run.cachePath);
            if (picked) {
                run.cachePath = picked;
                cachePathEdited = true;
            }
        } catch {
            // a bridge error on the file dialog is harmless; keep the current path
        }
    }

    async function browseOutput(): Promise<void> {
        const api = getApi();
        if (!api) return;
        try {
            const picked = await api.select_folder(run.output);
            if (picked) run.output = picked;
        } catch {
            // a bridge error on the folder dialog is harmless; keep the current path
        }
    }

    async function browseSource(): Promise<void> {
        const api = getApi();
        if (!api) return;
        try {
            const picked = await api.select_json_file(run.source);
            if (picked) run.source = picked;
        } catch {
            // a bridge error on the file dialog is harmless; keep the current path
        }
    }

    function execute(): void {
        const api = getApi();
        if (!api) return; // no bridge under `vite dev`; should be impossible to reach the button in this state
        resetRun(); // clear prior run + set timestamp before events arrive
        api.start_run({
            url: run.source,
            mode: run.mode,
            num: run.limit,
            output_dir: run.output,
            min_resolution: [run.resW, run.resH],
            delay: settings.delay,
            download_streams: run.fetchVideos,
            skip_remux: false,
            caption_from_title: false,
            save_cache: run.saveCache,
            cache_path: run.cachePath,
            // skip-download only makes sense with a cache; guard against stale state
            // left over from toggling Save Metadata Cache off.
            skip_download: run.saveCache && run.skipDownload
        }).catch((error: unknown) => {
            // Bridge-level failure
            console.error('Failed to start run:', error);
        });
    }

    function terminate(): void {
        // chain short-circuits with no bridge.
        getApi()
            ?.terminate()
            .catch(() => {
                // a bridge error on terminate is harmless
            });
    }
</script>

{#snippet groupLabel(text: string)}
    <span class="text-[11px] font-semibold tracking-wide text-muted-foreground uppercase"
        >{text}</span
    >
{/snippet}

<section class="flex min-h-0 shrink-0 flex-col bg-background" style="width: {width}px">
    <ScrollArea class="min-h-0 flex-1">
        <div class="flex flex-col gap-6 p-6">
            <!-- Mode -->
            <ToggleGroup
                type="single"
                bind:value={run.mode}
                class="w-full rounded-md border border-border bg-card p-1"
            >
                <ToggleGroupItem
                    value="scrape"
                    class="flex-1 gap-1.5 text-muted-foreground data-[state=on]:bg-muted data-[state=on]:text-foreground data-[state=on]:shadow-sm"
                >
                    <Download class="size-3.5" />
                    Scrape
                </ToggleGroupItem>
                <ToggleGroupItem
                    value="search"
                    class="flex-1 gap-1.5 text-muted-foreground data-[state=on]:bg-muted data-[state=on]:text-foreground data-[state=on]:shadow-sm"
                >
                    <Search class="size-3.5" />
                    Search
                </ToggleGroupItem>
                <ToggleGroupItem
                    value="download"
                    class="flex-1 gap-1.5 text-muted-foreground data-[state=on]:bg-muted data-[state=on]:text-foreground data-[state=on]:shadow-sm"
                >
                    <FileDown class="size-3.5" />
                    Download
                </ToggleGroupItem>
            </ToggleGroup>

            <!-- Target -->
            <div class="flex flex-col gap-3">
                {@render groupLabel('Target')}
                <div class="flex flex-col gap-1.5">
                    <Label for="source"
                        >{run.mode === 'search'
                            ? 'Search Query'
                            : run.mode === 'download'
                              ? 'Cache File'
                              : 'Source URL'}</Label
                    >
                    <div class="flex">
                        <Input
                            id="source"
                            placeholder={run.mode === 'search'
                                ? 'cats'
                                : run.mode === 'download'
                                  ? './metadata.json'
                                  : 'https://www.pinterest.com/pin/1234567890/'}
                            bind:value={run.source}
                            class={cn(
                                'flex-1 font-mono',
                                showBrowseSource && 'rounded-r-none border-r-0'
                            )}
                        />
                        {#if showBrowseSource}
                            <Button
                                variant="outline"
                                class="shrink-0 rounded-l-none"
                                onclick={browseSource}
                            >
                                <FolderOpen />
                            </Button>
                        {/if}
                    </div>
                </div>
                <div class="flex gap-3">
                    <div class="flex flex-2 flex-col gap-1.5">
                        <Label for="output">Output Directory</Label>
                        <div class="flex">
                            <Input
                                id="output"
                                placeholder="./downloads"
                                bind:value={run.output}
                                class="flex-1 rounded-r-none border-r-0 font-mono"
                            />
                            <Button
                                variant="outline"
                                class="shrink-0 rounded-l-none"
                                onclick={browseOutput}
                            >
                                <FolderOpen />
                            </Button>
                        </div>
                    </div>
                    {#if showLimit}
                        <div class="flex flex-1 flex-col gap-1.5">
                            <Label for="limit">Limit</Label>
                            <NumberInput
                                id="limit"
                                bind:value={run.limit}
                                min={1}
                                max={5000}
                            />
                        </div>
                    {/if}
                </div>
            </div>

            <!-- Extraction options -->
            <div class="flex flex-col gap-3">
                {@render groupLabel('Extraction Options')}
                <div class="flex flex-col gap-2">
                    <OptionRow
                        title="Fetch Videos"
                        desc="Download HLS video segments and mux to MP4."
                    >
                        <Switch bind:checked={run.fetchVideos} />
                    </OptionRow>

                    <OptionRow
                        title="Minimum Resolution"
                        desc="Discard assets smaller than dimensions (0 disables)."
                    >
                        <div class="flex items-center gap-2">
                            <NumberInput
                                bind:value={run.resW}
                                min={0}
                                class="w-28"
                            />
                            <span class="text-muted-foreground">x</span>
                            <NumberInput
                                bind:value={run.resH}
                                min={0}
                                class="w-28"
                            />
                        </div>
                    </OptionRow>

                    <OptionRow
                        title="Metadata Strategy"
                        desc="Format for accompanying alt text/captions."
                    >
                        <Select.Root type="single" bind:value={run.caption}>
                            <Select.Trigger class="w-[150px]">{captionLabel}</Select.Trigger>
                            <Select.Content>
                                <Select.Group>
                                    {#each captionItems as item (item.value)}
                                        <Select.Item value={item.value} label={item.label} />
                                    {/each}
                                </Select.Group>
                            </Select.Content>
                        </Select.Root>
                    </OptionRow>

                    <OptionRow
                        title="Strict Alt-Text"
                        desc="Drop assets lacking valid captions."
                    >
                        <Switch bind:checked={run.strictAlt} />
                    </OptionRow>
                </div>
            </div>

            <!-- Metadata cache (scrape/search only; download mode already has the records) -->
            {#if run.mode !== 'download'}
                <div class="flex flex-col gap-3">
                    {@render groupLabel('Metadata Cache')}
                    <div class="flex flex-col gap-2">
                        <OptionGroup>
                            <OptionRow
                                flat
                                title="Save Metadata Cache"
                                desc="Write scraped records to a JSON file for reuse in Download mode."
                            >
                                <Switch bind:checked={run.saveCache} />
                            </OptionRow>

                            {#if run.saveCache}
                                <OptionGroupSub>
                                    <div class="flex flex-col gap-1.5 p-3">
                                        <Label for="cachePath">Cache Path</Label>
                                        <div class="flex">
                                            <Input
                                                id="cachePath"
                                                bind:value={run.cachePath}
                                                oninput={() => {
                                                    cachePathEdited = true;
                                                }}
                                                class="flex-1 rounded-r-none border-r-0 font-mono"
                                            />
                                            <Button
                                                variant="outline"
                                                class="shrink-0 rounded-l-none"
                                                onclick={browseCacheFile}
                                            >
                                                <FolderOpen />
                                            </Button>
                                        </div>
                                        <p class="text-xs text-muted-foreground">
                                            Follows the output directory until you change it.
                                        </p>
                                    </div>
                                    <OptionRow
                                        flat
                                        title="Skip Download"
                                        desc="Save metadata only; don't download media."
                                    >
                                        <Switch bind:checked={run.skipDownload} />
                                    </OptionRow>
                                </OptionGroupSub>
                            {/if}
                        </OptionGroup>
                    </div>
                </div>
            {/if}
        </div>
    </ScrollArea>

    <!-- Action bar -->
    <div class="flex items-center justify-between gap-3 border-t border-border bg-card px-6 py-4">
        <SettingsDialog />
        <div class="flex gap-3">
            <Button variant="destructive" disabled={!isRunning} onclick={terminate}>
                <Square />
                Terminate
            </Button>
            <Button disabled={isRunning} onclick={execute}>
                <Play />
                Execute
            </Button>
        </div>
    </div>
</section>
