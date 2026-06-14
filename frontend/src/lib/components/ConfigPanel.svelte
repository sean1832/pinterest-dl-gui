<script lang="ts">
    import { cn } from '$lib/utils';
    import { run, captionItems, clientItems } from '$lib/state/run.svelte';
    import OptionRow from '$lib/components/OptionRow.svelte';
    import SettingsDialog from '$lib/components/SettingsDialog.svelte';
    import { Button } from '$lib/components/ui/button';
    import { Input } from '$lib/components/ui/input';
    import { Label } from '$lib/components/ui/label';
    import { Switch } from '$lib/components/ui/switch';
    import { ScrollArea } from '$lib/components/ui/scroll-area';
    import { ToggleGroup, ToggleGroupItem } from '$lib/components/ui/toggle-group';
    import * as Select from '$lib/components/ui/select';
    import * as Accordion from '$lib/components/ui/accordion';
    import Download from '@lucide/svelte/icons/download';
    import Search from '@lucide/svelte/icons/search';
    import Database from '@lucide/svelte/icons/database';
    import FolderOpen from '@lucide/svelte/icons/folder-open';
    import Play from '@lucide/svelte/icons/play';
    import Square from '@lucide/svelte/icons/square';
    import { getApi } from '$lib/api';
    import { runStatus, resetRun } from '$lib/state/runStatus.svelte';
    import { settings } from '$lib/state/settings.svelte';

    // Width is owned by the shell's resizable split and passed down explicitly.
    let { width }: { width: number } = $props();

    const showLimit = $derived(run.mode !== 'cache');
    const showBrowseSource = $derived(run.mode === 'cache');
    const clientDisabled = $derived(run.mode === 'search' || run.mode === 'cache');
    // Incognito is a browser-only flag; hide it for the API client (and cache mode).
    const showIncognito = $derived(run.client === 'chromium' || run.client === 'firefox');
    const captionLabel = $derived(
        captionItems.find((i) => i.value === run.caption)?.label ?? 'Select'
    );
    const clientLabel = $derived(
        clientItems.find((i) => i.value === run.client)?.label ?? 'Select'
    );

    const isRunning = $derived(runStatus.status === 'running');

    function execute(): void {
        const api = getApi();
        if (!api) return; // no bridge under `vite dev`; should be impossible to reach the button in this state
        resetRun(); // clear prior run + set timestamp before events arrive
        api.start_run({
            client: run.client,
            url: run.source,
            num: run.limit,
            output_dir: run.output,
            min_resolution: [run.resW, run.resH],
            delay: settings.delay,
            download_streams: run.fetchVideos,
            skip_remux: false,
            caption_from_title: false
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
                    value="cache"
                    class="flex-1 gap-1.5 text-muted-foreground data-[state=on]:bg-muted data-[state=on]:text-foreground data-[state=on]:shadow-sm"
                >
                    <Database class="size-3.5" />
                    Cache
                </ToggleGroupItem>
            </ToggleGroup>

            <!-- Target -->
            <div class="flex flex-col gap-3">
                {@render groupLabel('Target')}
                <div class="flex flex-col gap-1.5">
                    <Label for="source"
                        >{run.mode === 'search' ? 'Search Query' : 'Source URL'}</Label
                    >
                    <div class="flex">
                        <Input
                            id="source"
                            placeholder={run.mode === 'search'
                                ? 'cats'
                                : 'https://www.pinterest.com/pin/1234567890/'}
                            bind:value={run.source}
                            class={cn(
                                'flex-1 font-mono',
                                showBrowseSource && 'rounded-r-none border-r-0'
                            )}
                        />
                        {#if showBrowseSource}
                            <Button variant="outline" class="shrink-0 rounded-l-none">
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
                            <Button variant="outline" class="shrink-0 rounded-l-none">
                                <FolderOpen />
                            </Button>
                        </div>
                    </div>
                    {#if showLimit}
                        <div class="flex flex-1 flex-col gap-1.5">
                            <Label for="limit">Limit</Label>
                            <Input
                                id="limit"
                                type="number"
                                bind:value={run.limit}
                                min="1"
                                max="5000"
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
                            <Input
                                type="number"
                                bind:value={run.resW}
                                min="0"
                                class="w-16 font-mono"
                            />
                            <span class="text-muted-foreground">x</span>
                            <Input
                                type="number"
                                bind:value={run.resH}
                                min="0"
                                class="w-16 font-mono"
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
                </div>
            </div>

            <!-- Advanced -->
            <div class="flex flex-col gap-3">
                {@render groupLabel('Advanced')}
                <Accordion.Root type="multiple" class="flex flex-col gap-2">
                    <Accordion.Item
                        value="engine"
                        class="rounded-md border border-border bg-card px-3"
                    >
                        <Accordion.Trigger>Engine</Accordion.Trigger>
                        <Accordion.Content class="flex flex-col gap-3 border-t border-border pt-3">
                            <div class="flex flex-col gap-1.5">
                                <Label>Client Engine</Label>
                                <Select.Root
                                    type="single"
                                    bind:value={run.client}
                                    disabled={clientDisabled}
                                >
                                    <Select.Trigger class="w-full">{clientLabel}</Select.Trigger>
                                    <Select.Content>
                                        <Select.Group>
                                            {#each clientItems as item (item.value)}
                                                <Select.Item
                                                    value={item.value}
                                                    label={item.label}
                                                />
                                            {/each}
                                        </Select.Group>
                                    </Select.Content>
                                </Select.Root>
                            </div>
                            {#if showIncognito}
                                <OptionRow
                                    title="Incognito Context"
                                    desc="Isolate browser session state."
                                >
                                    <Switch bind:checked={run.incognito} />
                                </OptionRow>
                            {/if}
                            <OptionRow
                                title="Strict Alt-Text"
                                desc="Drop assets lacking valid captions."
                            >
                                <Switch bind:checked={run.strictAlt} />
                            </OptionRow>
                        </Accordion.Content>
                    </Accordion.Item>
                </Accordion.Root>
            </div>
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
