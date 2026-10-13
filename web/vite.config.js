import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// base: '/NiHao/' for GitHub Pages; '/' for Capacitor native builds (CAP_BUILD=1)
export default defineConfig({
  plugins: [
    react(),
    // PWA is web-only: service workers aren't supported on capacitor:// and
    // native builds bundle their assets (offline by construction).
    ...(process.env.CAP_BUILD ? [] : [VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: 'NiHao — HSK1 Vocabulary Trainer',
        short_name: 'NiHao',
        description: 'Learn HSK1 Chinese vocabulary with quizzes, flashcards, and audio pronunciation.',
        theme_color: '#dc2626',
        background_color: '#f9fafb',
        display: 'standalone',
        orientation: 'portrait',
        icons: [
          {
            src: 'pwa-192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: 'pwa-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        // App is fully offline-capable: cache all built assets
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        navigateFallback: 'index.html',
      },
    })]),
  ],
  base: process.env.CAP_BUILD ? '/' : '/NiHao/',
})
