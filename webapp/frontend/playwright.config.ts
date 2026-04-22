import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
	testDir: "e2e",
	fullyParallel: true,
	forbidOnly: Boolean(process.env.CI),
	retries: process.env.CI ? 1 : 0,
	workers: process.env.CI ? 1 : undefined,
	use: {
		...devices["Desktop Chrome"],
		baseURL: "http://127.0.0.1:10741",
		trace: "on-first-retry",
	},
	webServer: {
		command: "npm run dev",
		url: "http://127.0.0.1:10741",
		reuseExistingServer: !process.env.CI,
		timeout: 180_000,
	},
});
