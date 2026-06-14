import path from "path";
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
    plugins: [tailwindcss(), svelte()],
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