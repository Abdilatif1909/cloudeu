import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  base: process.env.VITE_PUBLIC_BASE || '/',
  plugins: [react()],
  server: {
    port: 5173,
  },
});
