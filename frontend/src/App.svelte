<script lang="ts">
    import { onMount } from 'svelte';
    import { cn } from '$lib/utils';
    import { checkFfmpeg } from '$lib/state/settings.svelte';
    import ConfigPanel from '$lib/components/ConfigPanel.svelte';
    import ConsolePanel from '$lib/components/ConsolePanel.svelte';
    import { onBridgeReady, getApi } from '$lib/api';

    let coreVersion = $state('unknown');
    async function loadCoreVersion() {
        const api = getApi();
        if (!api) return 'unknown';
        coreVersion = await api.get_core_version();
    }

    // Resolve FFmpeg once on startup.
    onMount(() => {
        onBridgeReady(() => {
            void checkFfmpeg();
            void loadCoreVersion();
        });
    });

    // --- Resizable left config pane (horizontal split) ------------------------
    const DEFAULT_LEFT = 480;
    const MIN_LEFT = 420;
    const MAX_LEFT = 720;
    const LEFT_WIDTH_KEY = 'pdl.leftWidth';

    function clampLeft(px: number): number {
        return Math.min(MAX_LEFT, Math.max(MIN_LEFT, px));
    }

    let leftWidth = $state(clampLeft(Number(localStorage.getItem(LEFT_WIDTH_KEY)) || DEFAULT_LEFT));
    let dragging = $state(false);

    function persistLeftWidth() {
        localStorage.setItem(LEFT_WIDTH_KEY, String(leftWidth));
    }
    function onDividerPointerDown(e: PointerEvent) {
        dragging = true;
        (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    }
    function onDividerPointerMove(e: PointerEvent) {
        if (!dragging) return;
        // The workspace starts at viewport x=0, so clientX is the desired left width.
        leftWidth = clampLeft(e.clientX);
    }
    function onDividerPointerUp(e: PointerEvent) {
        if (!dragging) return;
        dragging = false;
        (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
        persistLeftWidth();
    }
    function onDividerKeydown(e: KeyboardEvent) {
        if (e.key === 'ArrowLeft') leftWidth = clampLeft(leftWidth - 16);
        else if (e.key === 'ArrowRight') leftWidth = clampLeft(leftWidth + 16);
        else return;
        e.preventDefault();
        persistLeftWidth();
    }
</script>

<div class="flex h-full w-full flex-col overflow-hidden bg-background text-xs text-foreground">
    <!-- Workspace -->
    <main class="flex min-h-0 flex-1" class:select-none={dragging}>
        <ConfigPanel width={leftWidth} />

        <!-- Resize divider: a focusable window-splitter (separator + aria-valuenow),
		     which legitimately needs pointer/keyboard handlers and a tab stop. -->
        <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
        <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
        <div
            role="separator"
            aria-orientation="vertical"
            aria-label="Resize panels"
            aria-valuemin={MIN_LEFT}
            aria-valuemax={MAX_LEFT}
            aria-valuenow={leftWidth}
            tabindex="0"
            class="group relative z-10 w-px shrink-0 cursor-col-resize bg-border outline-none"
            onpointerdown={onDividerPointerDown}
            onpointermove={onDividerPointerMove}
            onpointerup={onDividerPointerUp}
            onpointercancel={onDividerPointerUp}
            onkeydown={onDividerKeydown}
        >
            <div
                class={cn(
                    'absolute inset-y-0 -right-1 -left-1 transition-colors group-hover:bg-primary/20 group-focus-visible:bg-primary/30',
                    dragging && 'bg-primary/40'
                )}
            ></div>
        </div>

        <ConsolePanel />
    </main>

    <!-- Status bar -->
    <footer
        class="flex h-8 shrink-0 items-center justify-between border-t border-border bg-card px-4 font-mono text-[11px] text-muted-foreground"
    >
        <div class="flex gap-2">
            <div class="flex items-center gap-2">
                <span class="size-2 rounded-full bg-green-500"></span>
                <span>READY</span>
            </div>
            |
            <div class="flex items-center gap-2">
                <span class="size-2 rounded-full bg-green-500"></span>
                <span>FFMPEG</span>
            </div>
        </div>

        <div>pinterest-dl v{coreVersion} | GUI v{__APP_VERSION__}</div>
    </footer>
</div>
