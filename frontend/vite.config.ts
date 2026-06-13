import path from "path";
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
    plugins: [svelte()],
    base: "./", // Ensure relative paths for assets (important for pywebview)
    resolve: {
        alias: {
            $lib: path.resolve("./src/lib"),
        },
    },
    build: {
        outDir: "../web",
        emptyOutDir: true,
    },
});