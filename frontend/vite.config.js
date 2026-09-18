import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dashboard always calls the API through the "/api" prefix.
// In development Vite forwards those calls to the FastAPI server on port 8000,
// so the browser never has to deal with cross-origin requests.
// Change the target if you start the backend on a different port.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        ws: true,
      },
    },
  },
});