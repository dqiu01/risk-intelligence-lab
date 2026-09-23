import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

try {
  await page.goto("http://127.0.0.1:8000/web/", { waitUntil: "domcontentloaded", timeout: 30000 });

  await page.waitForFunction(
    () => document.querySelector("#boot")?.style.display === "none",
    { timeout: 180000 }
  );

  await page.click('[data-engine="01"]');
  await page.waitForSelector("#kpi-grid .kpi", { timeout: 120000 });

  const count = await page.locator("#kpi-grid .kpi").count();
  if (count < 4) throw new Error(`Expected at least four KPI cards, found ${count}`);

  const summary = (await page.locator("#interpretation").textContent())?.trim();
  if (!summary || summary.includes("could not complete")) {
    throw new Error("Engine 01 did not return a valid interpretation");
  }

  await page.screenshot({ path: "/tmp/risk-intelligence-lab.png", fullPage: true });
  console.log("Browser smoke test passed:", summary);
} finally {
  await browser.close();
}
