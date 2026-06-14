<script lang="ts">
    import { cn } from '$lib/utils';
    import { runStatus, type LogLine } from '$lib/state/runStatus.svelte';
    import { Progress } from '$lib/components/ui/progress';
    import { Badge } from '$lib/components/ui/badge';
    import { ScrollArea } from '$lib/components/ui/scroll-area';
    import Download from '@lucide/svelte/icons/download';
    import Funnel from '@lucide/svelte/icons/funnel';
    import Film from '@lucide/svelte/icons/film';

    const tagClass: Record<string, string> = {
        SYS: 'bg-primary/10 text-primary',
        DL: 'bg-success/10 text-success',
        WARN: 'bg-warning/10 text-warning',
        ERR: 'bg-destructive/10 text-destructive'
    };

    // collapse level + phase on to the existing 4 tags palette
    function logTag(line: LogLine): string {
        if (line.level === 'error') return 'ERR';
        if (line.level === 'warn') return 'WARN';
        if (line.phase === 'download') return 'DL';
        return 'SYS';
    }

    const percent = $derived(
        runStatus.total > 0 ? Math.round((runStatus.current / runStatus.total) * 100) : 0
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
    <div class="grid grid-cols-3 border-b border-border bg-card">
        <div class="flex flex-col gap-1 border-r border-border p-4">
            <span class="text-[28px] leading-none font-semibold tracking-tight">
                {runStatus.counts.downloaded}
            </span>
            <span
                class="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase"
            >
                <Download class="size-3" />
                Downloaded
            </span>
        </div>
        <div class="flex flex-col gap-1 border-r border-border p-4">
            <span
                class="text-[28px] leading-none font-semibold tracking-tight text-muted-foreground"
            >
                {runStatus.counts.filtered}
            </span>
            <span
                class="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase"
            >
                <Funnel class="size-3" />
                Filtered
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
    <ScrollArea orientation="horizontal" class="border-b border-border bg-card">
        <div class="flex min-h-[85px] gap-2 p-4">
            {#each runStatus.previews as preview, i (i)}
                <div class="relative shrink-0">
                    <img
                        src={preview.thumbnail}
                        alt=""
                        loading="lazy"
                        class="size-[52px] rounded-md border border-border object-cover"
                    />
                    {#if preview.isVideo}
                        <span
                            class="absolute right-0.5 bottom-0.5 flex items-center rounded bg-black/70 p-0.5 text-white"
                        >
                            <Film class="size-3" />
                        </span>
                    {/if}
                </div>
            {/each}
        </div>
    </ScrollArea>

    <!-- Log -->
    <ScrollArea class="min-h-0 flex-1">
        <div
            class="flex flex-col gap-1 p-4 font-mono text-[11px] leading-relaxed text-muted-foreground"
        >
            {#each runStatus.logs as log, i (i)}
                <div class="flex items-center gap-2">
                    <time class="shrink-0 text-muted-foreground/60">{log.time}</time>
                    <Badge
                        class={cn(
                            'h-4 shrink-0 border-transparent px-1 text-[10px]',
                            tagClass[logTag(log)]
                        )}
                    >
                        {logTag(log)}
                    </Badge>
                    <span>{log.message}</span>
                </div>
            {/each}
        </div>
    </ScrollArea>
</section>
