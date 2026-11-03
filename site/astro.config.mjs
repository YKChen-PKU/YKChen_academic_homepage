// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://yankechen.xyz',
  integrations: [sitemap()],
  build: { format: 'directory' },
});
