<script lang="ts">
    import { cn } from '$lib/utils';
    import ChevronUp from '@lucide/svelte/icons/chevron-up';
    import ChevronDown from '@lucide/svelte/icons/chevron-down';

    interface Props {
        value?: number;
        min?: number;
        max?: number;
        step?: number;
        disabled?: boolean;
        class?: string;
        id?: string;
    }

    let {
        value = $bindable(0),
        min,
        max,
        step = 1,
        disabled = false,
        class: className,
        id,
    }: Props = $props();

    function clamp(v: number): number {
        let result = v;
        if (min !== undefined && result < min) result = min;
        if (max !== undefined && result > max) result = max;
        return result;
    }

    function decrement() {
        value = clamp(value - step);
    }

    function increment() {
        value = clamp(value + step);
    }

    function onblur() {
        if (!Number.isNaN(value)) value = clamp(value);
    }

    const atMin = $derived(min !== undefined && value <= min);
    const atMax = $derived(max !== undefined && value >= max);
</script>

<div
    class={cn(
        'dark:bg-input/30 border-input focus-within:border-ring focus-within:ring-ring/50 focus-within:ring-1 flex h-8 items-stretch overflow-hidden rounded-md border bg-transparent transition-colors',
        disabled && 'pointer-events-none opacity-50',
        className
    )}
>
    <input
        {id}
        type="number"
        bind:value
        {min}
        {max}
        {step}
        {disabled}
        {onblur}
        class="w-full min-w-0 bg-transparent pl-2.5 pr-1 text-xs font-mono outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
    />
    <div class="flex shrink-0 flex-col border-l border-border">
        <button
            type="button"
            onclick={increment}
            disabled={disabled || atMax}
            tabindex="-1"
            class="flex flex-1 w-5 items-center justify-center text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
        >
            <ChevronUp class="size-3" />
        </button>
        <div class="border-t border-border"></div>
        <button
            type="button"
            onclick={decrement}
            disabled={disabled || atMin}
            tabindex="-1"
            class="flex flex-1 w-5 items-center justify-center text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
        >
            <ChevronDown class="size-3" />
        </button>
    </div>
</div>
