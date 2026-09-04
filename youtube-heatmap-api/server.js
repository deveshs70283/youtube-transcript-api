const express = require('express');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const app = express();
const PORT = process.env.PORT || 3000;
const CACHE_DIR = path.join(__dirname, 'cache');

// Make sure the cache directory exists before we accept any requests
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

app.use(express.json());

// Pulls the 11-char video ID out of either youtube.com/watch?v= or youtu.be/ URLs
function extractVideoId(url) {
  if (typeof url !== 'string') return null;

  const watchMatch = url.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
  if (watchMatch) return watchMatch[1];

  const shortMatch = url.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
  if (shortMatch) return shortMatch[1];

  return null;
}

app.get('/', (req, res) => {
  res.json({ status: 'running', service: 'youtube-heatmap-api' });
});

app.post('/extract-heatmap', async (req, res) => {
  const { url } = req.body || {};

  if (!url) {
    return res.status(400).json({ error: 'Missing "url" in request body' });
  }

  const videoId = extractVideoId(url);
  if (!videoId) {
    return res.status(400).json({ error: 'Invalid YouTube URL' });
  }

  const cachePath = path.join(CACHE_DIR, `${videoId}.json`);

  // Cache-first: never launch Playwright if we already have this video
  if (fs.existsSync(cachePath)) {
    const cached = JSON.parse(fs.readFileSync(cachePath, 'utf-8'));
    return res.json({ ...cached, cached: true });
  }

  let browser;
  try {
    // --no-sandbox/--disable-dev-shm-usage are required for Chromium to run
    // reliably inside a container (Render, Docker, etc.)
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    });
    const page = await browser.newPage({ locale: 'en-US' });

    await page.goto(url, { waitUntil: 'domcontentloaded' });

    // Cloud/datacenter IPs are often served a cookie-consent interstitial
    // instead of the video page — dismiss it if present before continuing.
    try {
      await page.getByRole('button', { name: /accept all|i agree/i }).click({ timeout: 5000 });
    } catch {
      // No consent dialog shown — nothing to do.
    }

    // The heatmap only renders once the player chrome and progress bar are ready
    await page.waitForSelector('.ytp-chrome-bottom', { timeout: 45000 });
    await page.waitForSelector('.ytp-progress-bar');
    await page.hover('.ytp-progress-bar');

    const heatmapHandle = await page.waitForSelector('.ytp-heat-map-container');
    const heatmapHtml = await heatmapHandle.evaluate((el) => el.outerHTML);

    const title = await page.evaluate(() => {
      const meta = document.querySelector('meta[name="title"]');
      return meta ? meta.getAttribute('content') : null;
    });

    const duration = await page.evaluate(() => {
      const video = document.querySelector('video');
      return video && !Number.isNaN(video.duration) ? Math.round(video.duration) : null;
    });

    const result = {
      videoId,
      url,
      title,
      duration,
      heatmapHtml,
      createdAt: new Date().toISOString(),
      cached: false,
    };

    fs.writeFileSync(cachePath, JSON.stringify(result, null, 2));

    return res.json(result);
  } catch (err) {
    return res.status(500).json({ error: 'Failed to extract heatmap', details: err.message });
  } finally {
    if (browser) await browser.close();
  }
});

app.listen(PORT, () => {
  console.log(`youtube-heatmap-api listening on port ${PORT}`);
});
