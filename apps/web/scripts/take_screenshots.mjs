#!/usr/bin/env node
/**
 * Take demo screenshots of the LicitScope web UI.
 *
 * Prerequisites:
 *   - The full stack is running locally (make up) OR
 *   - api on http://localhost:8000 and web on http://localhost:3000
 *   - Playwright is installed:
 *       npm i -D @playwright/test
 *       npx playwright install chromium
 *
 * Usage:
 *   node scripts/take_screenshots.mjs [--base=http://localhost:3000] [--out=docs/screenshots]
 *
 * The script navigates through the walkthrough documented in
 * docs/SCREENSHOTS.md and writes a numbered PNG per page.
 */

import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { argv } from "node:process";

const args = Object.fromEntries(
  argv
    .slice(2)
    .filter((a) => a.startsWith("--"))
    .map((a) => {
      const [k, v] = a.slice(2).split("=");
      return [k, v ?? true];
    }),
);

const BASE = args.base || "http://localhost:3000";
const OUT = resolve(args.out || "docs/screenshots");
const VIEWPORT = { width: 1440, height: 900 };

// The full list is the portfolio walkthrough defined in docs/SCREENSHOTS.md.
// Keep the order stable so reviewers always see the same narrative arc.
const SHOTS = [
  { name: "01-dashboard",        path: "/" },
  { name: "02-opportunities",    path: "/opportunities?state=SP&sort=value_desc" },
  { name: "03-search",           path: "/search?q=medicamentos" },
  { name: "04-contracts-pricing", path: "/contracts" },
  { name: "05-agencies",         path: "/agencies" },
  { name: "06-watchlists",       path: "/watchlists" },
  { name: "07-health",           path: "/health" },
  { name: "08-about",            path: "/about" },
];

async function main() {
  mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: VIEWPORT,
    colorScheme: "dark",
    deviceScaleFactor: 2,
    locale: "pt-BR",
  });
  const page = await ctx.newPage();

  for (const shot of SHOTS) {
    const url = `${BASE}${shot.path}`;
    process.stdout.write(`→ ${shot.name.padEnd(22)} ${url}\n`);
    await page.goto(url, { waitUntil: "networkidle" });
    // Give charts and lazy-loaded queries a beat to settle.
    await page.waitForTimeout(800);
    const file = resolve(OUT, `${shot.name}.png`);
    await page.screenshot({ path: file, fullPage: true });
  }

  // Bonus: one opportunity detail screenshot using the first card on the feed.
  await page.goto(`${BASE}/opportunities`, { waitUntil: "networkidle" });
  const firstHref = await page
    .locator('a[href^="/opportunities/"]')
    .first()
    .getAttribute("href");
  if (firstHref) {
    await page.goto(`${BASE}${firstHref}`, { waitUntil: "networkidle" });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: resolve(OUT, "09-opportunity-detail.png"),
      fullPage: true,
    });
    process.stdout.write(`→ 09-opportunity-detail   ${BASE}${firstHref}\n`);
  }

  await browser.close();
  process.stdout.write(`\nWrote screenshots to ${OUT}\n`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
