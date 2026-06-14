<script lang="ts">
	import * as Tooltip from "$lib/components/ui/tooltip";
	import Info from "@lucide/svelte/icons/info";

	let { text }: { text: string } = $props();
</script>

<Tooltip.Provider>
	<Tooltip.Root>
		<Tooltip.Trigger>
			{#snippet child({ props })}
				<span
					{...props}
					tabindex="-1"
					class="inline-flex cursor-default items-center text-muted-foreground/50 transition-colors hover:text-muted-foreground"
				>
					<Info class="size-3.5" />
				</span>
			{/snippet}
		</Tooltip.Trigger>
		<Tooltip.Content sideOffset={6}>
			{text}
		</Tooltip.Content>
	</Tooltip.Root>
</Tooltip.Provider>
