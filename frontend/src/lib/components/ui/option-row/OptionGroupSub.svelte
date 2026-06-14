<script lang="ts">
    import type { Snippet } from 'svelte';

    let { children }: { children: Snippet } = $props();
</script>

<div class="divide-y divide-border bg-muted/40">
    {@render children()}
</div>
