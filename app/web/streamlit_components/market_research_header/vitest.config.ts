import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const root = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  resolve: {
    alias: {
      "react/jsx-dev-runtime": resolve(root, "node_modules/react/jsx-dev-runtime.js"),
      "react/jsx-runtime": resolve(root, "node_modules/react/jsx-runtime.js"),
      "react-dom": resolve(root, "node_modules/react-dom"),
      react: resolve(root, "node_modules/react"),
    },
  },
});
