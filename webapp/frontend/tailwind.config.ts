import type { Config } from "tailwindcss";

const config: Config = {
	content: [
		"./app/**/*.{js,ts,jsx,tsx,mdx}",
		"./components/**/*.{js,ts,jsx,tsx,mdx}",
	],
	theme: {
		extend: {
			colors: {
				background: "var(--background)",
				foreground: "var(--foreground)",
				// Do not set `slate` or `amber` to a single hex string here: that replaces the
				// entire default color scale and breaks utilities like `text-slate-100`,
				// `bg-slate-800`, `border-amber-800` (appears as a blank / “black” UI).
			},
		},
	},
	plugins: [],
};
export default config;
