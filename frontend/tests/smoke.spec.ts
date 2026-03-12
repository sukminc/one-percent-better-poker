import { test, expect } from "@playwright/test";

test.describe("Page smoke tests", () => {
  test("/ — loads and shows hero", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));

    await page.goto("/");
    await expect(page.locator("body")).toContainText("Marginal gains");
    await expect(page.locator("body")).toContainText("Exponential results");

    expect(errors.filter((e) => !e.includes("favicon"))).toHaveLength(0);
  });

  test("/ — shows all 5 project cards", async ({ page }) => {
    await page.goto("/");
    const cards = page.locator("[data-testid='project-card']");
    await expect(cards).toHaveCount(5);
  });

  test("/about — loads with Chris's name", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));

    await page.goto("/about");
    await expect(page.locator("body")).toContainText("Chris");

    expect(errors.filter((e) => !e.includes("favicon"))).toHaveLength(0);
  });

  test("/activity — loads build log", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));

    await page.goto("/activity");
    await expect(page.locator("body")).toContainText("build log", {
      ignoreCase: true,
    });

    expect(errors.filter((e) => !e.includes("favicon"))).toHaveLength(0);
  });
});
