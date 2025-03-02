import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 10000, // Port utilisé sur Render
    strictPort: true,
    host: "0.0.0.0",
  },
  preview: {
    allowedHosts: ["investai-frontend.onrender.com"], // ✅ Ajoute ton domaine Render ici
  },
});
