import { expect, test } from "@playwright/test";

test("homepage form sends URL-encoded fields under its Netlify form name", async ({ page }) => {
  let submitted: URLSearchParams | undefined;
  await page.route("**/__forms.html", async (route) => {
    expect(route.request().method()).toBe("POST");
    expect(route.request().headers()["content-type"]).toContain("application/x-www-form-urlencoded");
    submitted = new URLSearchParams(route.request().postData() ?? "");
    await route.fulfill({ status: 200, contentType: "text/plain", body: "Accepted" });
  });

  await page.goto("/#contact");
  const form = page.locator('form[name="contact-home"]');
  await expect(form).toHaveAttribute("data-netlify", "true");
  await expect(form).toHaveAttribute("netlify-honeypot", "bot-field");
  for (const fieldName of ["name", "email", "company", "inquiryType", "message"]) {
    await expect(form.locator(`[name="${fieldName}"]`)).toHaveAttribute("required", "");
  }
  await form.getByLabel("Name").fill("Morgan Example");
  await form.getByLabel("Email").fill("morgan@example.com");
  await form.getByLabel("Company").fill("Example Freight");
  await expect(form.getByLabel("Inquiry type").locator("option")).toHaveText([
    "Select an inquiry type",
    "Investor",
    "Partner",
    "Importer",
    "Other",
  ]);
  await form.getByLabel("Inquiry type").selectOption("Importer");
  await form.getByLabel("Message").fill("Please contact me about invoice recovery.");
  await form.getByRole("button", { name: "Send inquiry" }).click();

  await expect(page.getByRole("status")).toContainText("Thank you");
  expect(submitted).toBeDefined();
  expect(Object.fromEntries(submitted!.entries())).toEqual({
    "form-name": "contact-home",
    name: "Morgan Example",
    email: "morgan@example.com",
    company: "Example Freight",
    inquiryType: "Importer",
    message: "Please contact me about invoice recovery.",
    "bot-field": "",
  });
});

test("contact-page form reports a submission error and preserves Reply-to field name", async ({ page }) => {
  let submitted: URLSearchParams | undefined;
  await page.route("**/__forms.html", async (route) => {
    submitted = new URLSearchParams(route.request().postData() ?? "");
    await route.fulfill({ status: 500, contentType: "text/plain", body: "Unavailable" });
  });

  await page.goto("/contact");
  const form = page.locator('form[name="contact-page"]');
  await form.getByLabel("Name").fill("Avery Example");
  await form.getByLabel("Email").fill("avery@example.com");
  await form.getByLabel("Company").fill("Example Imports");
  await form.getByLabel("Inquiry type").selectOption("Partner");
  await form.getByLabel("Message").fill("I would like to discuss a partnership.");
  await form.getByRole("button", { name: "Send inquiry" }).click();

  await expect(page.locator(".contact-feedback-error")).toContainText("could not send");
  expect(submitted).toBeDefined();
  expect(Object.fromEntries(submitted!.entries())).toMatchObject({
    "form-name": "contact-page",
    email: "avery@example.com",
    inquiryType: "Partner",
    "bot-field": "",
  });
});

test("static Netlify form definitions register both contact forms and fields", async ({ page }) => {
  const response = await page.request.get("/__forms.html");
  expect(response.status()).toBe(200);
  const html = await response.text();
  expect(html.match(/data-netlify="true"/g)).toHaveLength(2);
  for (const formName of ["contact-home", "contact-page"]) {
    const definition = html.match(new RegExp(`<form[^>]*name="${formName}"[^>]*>[\\s\\S]*?<\\/form>`))?.[0];
    expect(definition).toBeDefined();
    for (const fieldName of ["name", "email", "company", "inquiryType", "message", "bot-field"]) {
      expect(definition).toContain(`name="${fieldName}"`);
    }
    expect(definition).toContain(`value="${formName}"`);
  }
});
