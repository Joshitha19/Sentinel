import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
const wsBackendUrl = backendUrl.replace(/^http/, "ws");

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: backendUrl,
        changeOrigin: true,
      },
      "/ws": {
        target: wsBackendUrl,
        ws: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom", "framer-motion", "lucide-react"],
          charts: ["recharts"],
        },
      },
    },
  },
});
