import { expect, test } from "@playwright/test";

test.describe("Hook tracker", () => {
  test("/counter — loads tracker shell", async ({ page }) => {
    await page.goto("/counter");

    await expect(page.locator("body")).toContainText("1% Better Counter");
    await expect(page.locator("body")).toContainText("Session");
    await expect(page.locator("body")).toContainText(
      "What do you want to make 1% better this session?"
    );
  });

  test("/counter — starts a self-reflection session and pushes past the goal", async ({
    page,
  }) => {
    await page.goto("/counter");

    await page.getByRole("button", { name: "Raise" }).click();
    await page.getByRole("button", { name: "More" }).click();
    await page.getByLabel("Goal target").evaluate((element) => {
      const input = element as HTMLInputElement;
      input.value = "2";
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });

    await expect(page.locator("body")).toContainText(
      "You will RAISE more than 2 times."
    );
    await page.getByRole("button", { name: "Start counting" }).click();

    const tapButton = page.getByRole("button", { name: "Tap to count" });
    await tapButton.click();
    await tapButton.click();
    await tapButton.click();

    await expect(page.locator("body")).toContainText("Momentum");
    await expect(page.locator("body")).toContainText("+1 over");

    await page.getByRole("button", { name: "Finish" }).click();

    await expect(page.locator("body")).toContainText("Goal crushed.");
    await expect(page.locator("body")).toContainText(
      "You went past the line. That is a real 1% session."
    );
    await expect(page.locator("body")).toContainText("GGPoker hands");
  });

  test("/counter — celebrates a clean less-than-zero session", async ({ page }) => {
    await page.goto("/counter");

    await page.getByRole("button", { name: "Call" }).click();
    await page.getByRole("button", { name: "Less" }).click();
    await page.getByLabel("Goal target").evaluate((element) => {
      const input = element as HTMLInputElement;
      input.value = "0";
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });

    await expect(page.locator("body")).toContainText(
      "You will keep CALL at 0."
    );
    await page.getByRole("button", { name: "Start counting" }).click();
    await expect(page.locator("body")).toContainText("Perfect clean sheet");
    await expect(page.locator("body")).toContainText("0 left");

    await page.getByRole("button", { name: "Finish" }).click();

    await expect(page.locator("body")).toContainText("Perfect clean sheet.");
    await expect(page.locator("body")).toContainText(
      "Zero all the way through. Strong discipline."
    );
  });

  test("/counter — missing the line still encourages the next session", async ({ page }) => {
    await page.goto("/counter");

    await page.getByRole("button", { name: "Fold" }).click();
    await page.getByRole("button", { name: "More" }).click();
    await page.getByLabel("Goal target").evaluate((element) => {
      const input = element as HTMLInputElement;
      input.value = "4";
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
    await page.getByRole("button", { name: "Start counting" }).click();

    const tapButton = page.getByRole("button", { name: "Tap to count" });
    await tapButton.click();
    await tapButton.click();
    await page.getByRole("button", { name: "Finish" }).click();

    await expect(page.locator("body")).toContainText("Good rep.");
    await expect(page.locator("body")).toContainText(
      "Missing the line is not the point. Logging the attempt is how the habit starts to change."
    );
    await expect(page.locator("body")).toContainText(
      "Not this session. The rep still counts. Show up again and run it back next session."
    );
    await expect(page.getByRole("button", { name: "Try next session" })).toBeVisible();
  });

  test("/counter — fold only allows more", async ({ page }) => {
    await page.goto("/counter");

    await page.getByRole("button", { name: "Fold" }).click();

    await expect(page.getByRole("button", { name: "More" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Less" })).toHaveCount(0);
  });

  test("/counter — can add a hidden position focus", async ({ page }) => {
    await page.goto("/counter");

    await page.getByRole("button", { name: "Call" }).click();
    await page.getByRole("button", { name: "Add" }).click();
    await page.getByRole("button", { name: "Button" }).click();
    await page.getByRole("button", { name: "More" }).click();

    await expect(page.locator("body")).toContainText("Focused on Button");
    await expect(page.locator("body")).toContainText(
      "You will CALL from Button more than 3 times."
    );
  });

  test("/counter — shows time structure as in progress", async ({ page }) => {
    await page.goto("/counter");

    await page.getByRole("button", { name: "Raise" }).click();

    await expect(page.locator("body")).toContainText("Time Structure");
    await expect(page.locator("body")).toContainText("In progress");
  });

  test("/hook — redirects to /counter", async ({ page }) => {
    await page.goto("/hook");
    await expect(page).toHaveURL(/\/counter$/);
  });
});
