<script lang="ts">
    import type { Snippet } from 'svelte';
    import { cn } from '$lib/utils';

    let {
        title,
        desc,
        flat = false,
        children,
    }: { title: string; desc: string; flat?: boolean; children: Snippet } = $props();
</script>

<div
    class={cn(
        'flex items-center justify-between gap-3 p-3 transition-colors hover:bg-card/70',
        !flat && 'rounded-md border border-border bg-card'
    )}
>
    <div class="flex flex-col gap-1">
        <strong class="text-xs font-medium text-foreground">{title}</strong>
        <span class="text-xs text-muted-foreground">{desc}</span>
    </div>
    {@render children()}
</div>
