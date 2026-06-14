<script lang="ts">
    import type { Snippet } from 'svelte';

    let { children }: { children: Snippet } = $props();
</script>

<div class="divide-y divide-border overflow-hidden rounded-md border border-border bg-card">
    {@render children()}
</div>
