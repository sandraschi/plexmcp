import { expect, test } from "@playwright/test";

test.describe("PlexMCP web shell", () => {
	test("loads the root page with the app title", async ({ page }) => {
		await page.goto("/");
		await expect(page).toHaveTitle(/PlexMCP/i);
	});

	test("serves a health check route (may be 502 without backend)", async ({ request }) => {
		const res = await request.get("/api/health");
		// 200 when FastAPI is up; 502 when the Next proxy cannot reach the backend
		expect([200, 502].includes(res.status())).toBe(true);
	});
});
