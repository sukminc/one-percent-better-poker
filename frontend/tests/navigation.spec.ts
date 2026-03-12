import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("nav links are present on home page", async ({ page }) => {
    await page.goto("/");
    // Verify primary nav links exist
    await expect(page.locator("a[href='/about']").first()).toBeVisible();
    await expect(page.locator("a[href='/activity']").first()).toBeVisible();
  });

  test("clicking About nav link navigates to /about", async ({ page }) => {
    await page.goto("/");
    await page.locator("a[href='/about']").first().click();
    await expect(page).toHaveURL(/\/about/);
    await expect(page.locator("body")).toContainText("Chris");
  });

  test("clicking Activity nav link navigates to /activity", async ({
    page,
  }) => {
    await page.goto("/");
    await page.locator("a[href='/activity']").first().click();
    await expect(page).toHaveURL(/\/activity/);
  });

  test("logo / site name links back to /", async ({ page }) => {
    await page.goto("/about");
    await page.locator("a[href='/']").first().click();
    await expect(page).toHaveURL(/\/$/);
    await expect(page.locator("body")).toContainText("Marginal gains");
  });

  test("all internal links resolve without 404", async ({ page }) => {
    const paths = ["/", "/about", "/activity"];
    for (const path of paths) {
      const response = await page.goto(path);
      expect(response?.status(), `${path} returned non-200`).toBe(200);
    }
  });
});
