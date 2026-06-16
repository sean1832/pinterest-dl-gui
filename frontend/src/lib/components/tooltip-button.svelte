<script lang="ts">
	import * as Tooltip from "$lib/components/ui/tooltip";
	import { Button, type ButtonProps } from "$lib/components/ui/button";

	let { tooltip, children, ...rest }: ButtonProps & { tooltip: string } = $props();
</script>

<Tooltip.Provider>
	<Tooltip.Root>
		<Tooltip.Trigger>
			{#snippet child({ props })}
				<Button {...props} {...rest}>{@render children?.()}</Button>
			{/snippet}
		</Tooltip.Trigger>
		<Tooltip.Content sideOffset={6}>{tooltip}</Tooltip.Content>
	</Tooltip.Root>
</Tooltip.Provider>
