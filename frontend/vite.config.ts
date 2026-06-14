import path from "path";
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import tailwindcss from "@tailwindcss/vite";
import { readFileSync } from "fs";

const pkg = JSON.parse(readFileSync("./package.json", "utf-8")) as {
    version: string;
}

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
    define: {
        __APP_VERSION__: JSON.stringify(pkg.version),
    },
});