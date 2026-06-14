<script lang="ts">
  import type { Snippet } from "svelte";

  let {
    title,
    desc,
    children,
  }: { title: string; desc: string; children: Snippet } = $props();
</script>

<div
  class="flex items-center justify-between gap-3 rounded-md border border-border bg-card p-3"
>
  <div class="flex flex-col gap-1">
    <strong class="text-xs font-medium text-foreground">{title}</strong>
    <span class="text-xs text-muted-foreground">{desc}</span>
  </div>
  {@render children()}
</div>
