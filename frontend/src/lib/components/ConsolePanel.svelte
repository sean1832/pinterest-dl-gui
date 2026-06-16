<script lang="ts">
    import { cn } from '$lib/utils';
    import { runStatus, type LogLine } from '$lib/state/runStatus.svelte';
    import { Progress } from '$lib/components/ui/progress';
    import { Badge } from '$lib/components/ui/badge';
    import { ScrollArea } from '$lib/components/ui/scroll-area';
    import Download from '@lucide/svelte/icons/download';
    import Film from '@lucide/svelte/icons/film';
    import Save from '@lucide/svelte/icons/save';

    const tagClass: Record<string, string> = {
        SYS: 'bg-primary/10 text-primary',
        OK: 'bg-success/10 text-success',
        WARN: 'bg-warning/10 text-warning',
        ERR: 'bg-destructive/10 text-destructive'
    };

    // collapse level + phase on to the existing 4 tags palette
    function logTag(line: LogLine): string {
        if (line.level === 'error') return 'ERR';
        if (line.level === 'warn') return 'WARN';
        if (line.phase === 'download') return 'OK';
        return 'SYS';
    }

    const percent = $derived(
        runStatus.total > 0 ? Math.round((runStatus.current / runStatus.total) * 100) : 0
    );

    // A metadata-only run downloads nothing; show what it saved instead of a bare 0.
    const savedOnly = $derived(
        runStatus.counts.downloaded === 0 && runStatus.counts.saved > 0
    );

    const phaseLabel = $derived.by(() => {
        if (runStatus.status === 'idle') return 'Idle';
        if (runStatus.status === 'done') return 'Done';
        if (runStatus.status === 'error') return 'Error';
        return runStatus.phase === 'download' ? 'Downloading' : 'Scraping';
    });
</script>

<section class="flex min-h-0 min-w-0 flex-1 flex-col bg-background">
    <!-- Telemetry -->
    <div class="grid grid-cols-2 border-b border-border bg-card">
        <div class="flex flex-col gap-1 border-r border-border p-4">
            <span class="text-[28px] leading-none font-semibold tracking-tight">
                {savedOnly ? runStatus.counts.saved : runStatus.counts.downloaded}
            </span>
            <span
                class="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase"
            >
                {#if savedOnly}
                    <Save class="size-3" />
                    Saved
                {:else}
                    <Download class="size-3" />
                    Downloaded
                {/if}
            </span>
        </div>
        <div class="flex flex-col gap-1 p-4">
            <span class="text-[28px] leading-none font-semibold tracking-tight text-primary">
                {runStatus.counts.videos}
            </span>
            <span
                class="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase"
            >
                <Film class="size-3" />
                Videos
            </span>
        </div>
    </div>

    <!-- Progress -->
    <div class="border-b border-border bg-card p-4">
        <div class="mb-2 flex justify-between text-xs text-muted-foreground">
            <span>{phaseLabel}</span>
            <span>{percent}%</span>
        </div>
        <Progress value={percent} />
    </div>

    <!-- Asset previews -->
    <!-- type="auto" so the bar shows on overflow; the default "hover" hides it until the cursor enters. -->
    <ScrollArea type="auto" orientation="horizontal" class="border-b border-border bg-card">
        <div class="flex min-h-[85px] gap-2 p-4">
            {#each runStatus.previews as preview, i (i)}
                <div class="shrink-0">
                    {#if preview.thumbnail}
                        <img
                            src={preview.thumbnail}
                            alt=""
                            loading="lazy"
                            class="size-[52px] rounded-md border border-border object-cover"
                        />
                    {:else}
                        <!-- Video streams (and any image we couldn't decode) have no still to show. -->
                        <div
                            class="flex size-[52px] items-center justify-center rounded-md border border-border bg-muted text-muted-foreground"
                        >
                            {#if preview.isVideo}
                                <Film class="size-5" />
                            {/if}
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    </ScrollArea>

    <!-- Log -->
    <ScrollArea class="min-h-0 flex-1">
        <div
            class="flex flex-col gap-0.5 p-3 font-mono text-[11px] leading-relaxed text-muted-foreground select-text"
        >
            {#each runStatus.logs as log, i (i)}
                <div
                    class="flex items-center gap-2 rounded px-1.5 py-0.5 transition-colors duration-75 hover:bg-muted/70"
                >
                    <time class="shrink-0 text-muted-foreground/60 select-none">{log.time}</time>
                    <Badge
                        class={cn(
                            'h-4 shrink-0 border-transparent px-1 text-[10px] select-none',
                            tagClass[logTag(log)]
                        )}
                    >
                        {logTag(log)}
                    </Badge>
                    <span class="break-all">{log.message}</span>
                </div>
            {/each}
        </div>
    </ScrollArea>
</section>
