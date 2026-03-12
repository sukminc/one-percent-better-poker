import { test, expect } from "@playwright/test";

test.describe("Project cards — desktop hover flip", () => {
  test.use({ viewport: { width: 1280, height: 800 } });

  test("card flips on mouseenter and reverts on mouseleave", async ({
    page,
  }) => {
    await page.goto("/");

    const card = page.locator("[data-testid='project-card']").nth(1);
    await card.scrollIntoViewIfNeeded();

    // Not flipped initially
    await expect(card).toHaveAttribute("data-flipped", "false");

    // Hover → flipped
    await card.hover();
    await expect(card).toHaveAttribute("data-flipped", "true");

    // Move away → back to false
    await page.mouse.move(0, 0);
    await expect(card).toHaveAttribute("data-flipped", "false");
  });
});

test.describe("Project cards — mobile tap flip", () => {
  test.use({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });

  test("card flips on tap and shows close button", async ({ page }) => {
    await page.goto("/");

    const card = page.locator("[data-testid='project-card']").nth(1);
    await card.scrollIntoViewIfNeeded();

    // Not flipped before tap
    await expect(card).toHaveAttribute("data-flipped", "false");

    // Tap to flip
    await card.tap();
    await expect(card).toHaveAttribute("data-flipped", "true");

    // Close button (×) should be visible on mobile
    const closeBtn = card.locator("button[aria-label='Close']");
    await expect(closeBtn).toBeVisible();

    // Tapping close flips card back
    await closeBtn.tap();
    await expect(card).toHaveAttribute("data-flipped", "false");
  });

  test("double-tap does NOT double-toggle (regression guard)", async ({
    page,
  }) => {
    await page.goto("/");

    const card = page.locator("[data-testid='project-card']").nth(1);
    await card.scrollIntoViewIfNeeded();

    // First tap → should flip open
    await card.tap();
    await expect(card).toHaveAttribute("data-flipped", "true");

    // Wait — card must stay flipped (not double-toggle back to false)
    await page.waitForTimeout(500);
    await expect(card).toHaveAttribute("data-flipped", "true");
  });
});

test.describe("Filter pills", () => {
  test("filtering by 'Data' hides non-data projects", async ({ page }) => {
    await page.goto("/");

    const allCards = page.locator("[data-testid='project-card']");
    const initialCount = await allCards.count();
    expect(initialCount).toBe(5);

    // Click Data filter (exact to avoid matching "Automation" etc.)
    await page.getByRole("button", { name: "Data", exact: true }).click();

    // Should show fewer cards
    const filteredCount = await allCards.count();
    expect(filteredCount).toBeLessThan(initialCount);
    expect(filteredCount).toBeGreaterThan(0);
  });

  test("'All' filter restores full list", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: "Data" }).click();
    // Use exact match to avoid partial matching of "All-In" funding tier button
    await page.getByRole("button", { name: "All", exact: true }).click();

    const cards = page.locator("[data-testid='project-card']");
    await expect(cards).toHaveCount(5);
  });

  test("Automation filter shows at least one card", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Automation" }).click();

    const cards = page.locator("[data-testid='project-card']");
    expect(await cards.count()).toBeGreaterThan(0);
  });
});
