import { expect, test } from "@playwright/test";

const PILOT_CTA = "Request a pilot";
const PII_PATTERN = /jane|example\.com|555000|acme/i;

test("opens a native pilot dialog from each visible CTA and restores focus", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const ctas = page
    .locator('a[href="/pilot"]:visible')
    .filter({ hasText: PILOT_CTA });
  const ctaCount = await ctas.count();
  expect(ctaCount).toBeGreaterThanOrEqual(3);

  for (let index = 0; index < ctaCount; index += 1) {
    const cta = ctas.nth(index);
    await expect(cta).toHaveAccessibleName(PILOT_CTA);
    await cta.scrollIntoViewIfNeeded();
    await cta.click();

    const dialog = page.getByRole("dialog", { name: PILOT_CTA });
    await expect(dialog).toBeVisible();
    await expect(dialog).toHaveAttribute("open", "");
    expect(
      await dialog.evaluate((element) => element instanceof HTMLDialogElement),
    ).toBe(true);
    await expect(dialog.locator("form")).toBeVisible();
    await expect(
      dialog.getByText(/No details are collected|Nothing is transmitted or stored/i),
    ).toBeVisible();

    const fields = dialog.locator("input, select, textarea");
    expect(
      await fields.evaluateAll((elements) =>
        elements.every((element) =>
          (
            element as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
          ).matches(":disabled"),
        ),
      ),
    ).toBe(true);
    await expect(dialog.locator('button[type="submit"]')).toBeDisabled();

    const lockState = await page.evaluate(() => ({
      bodyOverflow: getComputedStyle(document.body).overflowY,
      documentOverflow: getComputedStyle(document.documentElement).overflowY,
    }));
    expect(
      [lockState.bodyOverflow, lockState.documentOverflow].some((value) =>
        ["hidden", "clip"].includes(value),
      ),
    ).toBe(true);

    await expect(dialog.getByRole("button", { name: /close/i })).toBeVisible();
    await dialog.getByRole("button", { name: /close/i }).click();
    await expect(dialog).toBeHidden();
    await expect(cta).toBeFocused();

    const unlockedState = await page.evaluate(() => ({
      bodyOverflow: getComputedStyle(document.body).overflowY,
      documentOverflow: getComputedStyle(document.documentElement).overflowY,
    }));
    expect(
      [unlockedState.bodyOverflow, unlockedState.documentOverflow].some((value) =>
        ["hidden", "clip"].includes(value),
      ),
    ).toBe(false);
  }
});

test("keeps keyboard focus inside the dialog and preserves modified /pilot links", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });
  const cta = page
    .locator('a[href="/pilot"]:visible')
    .filter({ hasText: PILOT_CTA })
    .first();
  await cta.click();

  const dialog = page.getByRole("dialog", { name: PILOT_CTA });
  await expect(dialog).toBeVisible();
  const closeButton = dialog.getByRole("button", { name: /close/i });
  await closeButton.focus();
  await page.keyboard.press("Tab");
  expect(await dialog.evaluate((element) => element.contains(document.activeElement))).toBe(true);
  await page.keyboard.press("Shift+Tab");
  expect(await dialog.evaluate((element) => element.contains(document.activeElement))).toBe(true);
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await expect(cta).toBeFocused();

  const modifiedClick = await cta.evaluate((element) => {
    const anchor = element as HTMLAnchorElement;
    const event = new MouseEvent("click", {
      bubbles: true,
      cancelable: true,
      ctrlKey: true,
      metaKey: true,
      view: window,
    });
    const dispatchResult = anchor.dispatchEvent(event);
    return {
      dispatchResult,
      defaultPrevented: event.defaultPrevented,
      path: new URL(anchor.href).pathname,
    };
  });
  expect(modifiedClick.dispatchResult).toBe(true);
  expect(modifiedClick.defaultPrevented).toBe(false);
  expect(modifiedClick.path).toBe("/pilot");
  await expect(dialog).toBeHidden();
});

// A 720x450 CSS viewport models desktop reflow at 200% zoom on a 1440x900 window.
// CSS body zoom would scale dialog coordinates without updating viewport units.
for (const viewport of [
  { name: "mobile", width: 390, height: 844 },
  { name: "200 percent desktop reflow", width: 720, height: 450 },
]) {
  test(`scrolls the ${viewport.name} pilot dialog without moving the page`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await page.goto("/", { waitUntil: "networkidle" });

    const cta = page
      .locator('a[href="/pilot"]:visible')
      .filter({ hasText: PILOT_CTA })
      .last();
    await cta.scrollIntoViewIfNeeded();
    const pageScrollBeforeOpen = await page.evaluate(() => window.scrollY);
    expect(pageScrollBeforeOpen).toBeGreaterThan(0);
    await cta.click();

    const dialog = page.getByRole("dialog", { name: PILOT_CTA });
    await expect(dialog).toBeVisible();
    const submit = dialog.locator('button[type="submit"]');
    await expect(submit).toBeDisabled();

    const beforeScroll = await dialog.evaluate((element) => {
      const pilotDialog = element as HTMLDialogElement;
      return {
        clientHeight: pilotDialog.clientHeight,
        overflowY: getComputedStyle(pilotDialog).overflowY,
        scrollHeight: pilotDialog.scrollHeight,
        scrollTop: pilotDialog.scrollTop,
      };
    });
    expect(beforeScroll.overflowY).toBe("auto");
    expect(beforeScroll.scrollHeight).toBeGreaterThan(beforeScroll.clientHeight);

    await dialog.evaluate((element) => {
      const pilotDialog = element as HTMLDialogElement;
      pilotDialog.scrollTop = pilotDialog.scrollHeight;
    });

    const afterScroll = await dialog.evaluate((element) => {
      const pilotDialog = element as HTMLDialogElement;
      const submitButton = pilotDialog.querySelector<HTMLButtonElement>(
        'button[type="submit"]',
      );
      if (!submitButton) {
        throw new Error("Pilot dialog submit button is missing");
      }

      const dialogRect = pilotDialog.getBoundingClientRect();
      const submitRect = submitButton.getBoundingClientRect();
      return {
        dialogBottom: Math.min(dialogRect.bottom, window.innerHeight),
        dialogTop: Math.max(dialogRect.top, 0),
        pageScrollY: window.scrollY,
        scrollTop: pilotDialog.scrollTop,
        submitBottom: submitRect.bottom,
        submitTop: submitRect.top,
      };
    });
    expect(afterScroll.scrollTop).toBeGreaterThan(beforeScroll.scrollTop);
    expect(afterScroll.pageScrollY).toBe(pageScrollBeforeOpen);
    expect(afterScroll.submitTop).toBeGreaterThanOrEqual(afterScroll.dialogTop);
    expect(afterScroll.submitBottom).toBeLessThanOrEqual(afterScroll.dialogBottom);

    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(cta).toBeFocused();
    expect(await page.evaluate(() => window.scrollY)).toBe(pageScrollBeforeOpen);
  });
}

test("keeps the disabled /pilot form inert without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({
    javaScriptEnabled: false,
    viewport: { width: 390, height: 900 },
  });
  const page = await context.newPage();
  const requests: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/pilot") {
      requests.push(`${request.method()} ${request.url()}`);
    }
  });

  await page.goto("/pilot", { waitUntil: "load" });
  const form = page.locator("form").filter({ hasText: "Work email" }).first();
  await expect(form).toHaveAttribute("method", "post");
  await expect(form).toHaveAttribute("action", "/api/pilot");
  const fields = form.locator('input:not([type="hidden"]), select, textarea');
  expect(
    await fields.evaluateAll((elements) =>
      elements.every((element) => element.matches(":disabled")),
    ),
  ).toBe(true);
  const submit = form.locator('button[type="submit"]');
  await expect(submit).toBeDisabled();
  await submit.scrollIntoViewIfNeeded();
  await expect(submit).toBeInViewport();
  await submit.click({ force: true });
  expect(requests).toEqual([]);
  await expect(page).toHaveURL(/\/pilot\/?$/);

  await context.close();
});

test("renders a disabled pilot form without transmitting or placing PII in a GET", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  const piiQueryRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.pathname === "/api/pilot") {
      apiRequests.push(`${request.method()} ${url.pathname}`);
    }
    if (PII_PATTERN.test(url.search)) {
      piiQueryRequests.push(url.toString());
    }
  });

  await page.goto("/pilot", { waitUntil: "networkidle" });
  const form = page.locator("form").filter({ hasText: "Work email" }).first();
  await expect(form).toBeVisible();
  await expect(
    form.getByText(/No details are collected|Nothing is transmitted or stored/i),
  ).toBeVisible();

  const fields = form.locator('input:not([type="hidden"]), select, textarea');
  expect(await fields.count()).toBeGreaterThan(0);
  expect(
    await fields.evaluateAll((elements) =>
      elements.every((element) =>
        (
          element as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
        ).matches(":disabled"),
      ),
    ),
  ).toBe(true);
  const submit = form.locator('button[type="submit"]');
  await expect(submit).toBeDisabled();
  await expect(page.getByText(/Pilot request sent/i)).toHaveCount(0);

  await form.evaluate((element) => {
    const fields = element.querySelectorAll<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(
      "input, select, textarea",
    );
    const values = ["Jane Smith", "jane@example.com", "Acme Imports"];
    fields.forEach((field, index) => {
      field.value = values[index] ?? field.value;
    });
    element.dispatchEvent(
      new SubmitEvent("submit", { bubbles: true, cancelable: true }),
    );
  });
  await page.evaluate(() => new Promise<void>((resolve) => queueMicrotask(resolve)));

  expect(apiRequests).toEqual([]);
  expect(piiQueryRequests).toEqual([]);
  await expect(page.getByText(/Pilot request sent/i)).toHaveCount(0);
});

test("renders FAQ answers with native details disclosure", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("/", { waitUntil: "domcontentloaded" });
  const faqItems = page.locator("#trust details");
  expect(await faqItems.count()).toBeGreaterThan(0);
  const firstItem = faqItems.first();
  const firstSummary = firstItem.locator(":scope > summary");
  await expect(firstSummary).toHaveCount(1);
  await firstSummary.click();
  await expect(firstItem).toHaveAttribute("open", "");
  await firstSummary.click();
  await expect(firstItem).not.toHaveAttribute("open", "");
  await context.close();
});
