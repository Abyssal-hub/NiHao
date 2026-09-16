import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base must match the GitHub Pages subpath: <user>.github.io/NiHao/
export default defineConfig({
  plugins: [react()],
  base: '/NiHao/',
})
