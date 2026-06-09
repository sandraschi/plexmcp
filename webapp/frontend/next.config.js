/** @type {import('next').NextConfig} */
const isTauri = process.env.TAURI_BUILD === "1";

const nextConfig = {
	reactStrictMode: true,
	trailingSlash: isTauri,
	images: { unoptimized: isTauri },
	...(isTauri ? { output: "export" } : { output: "standalone" }),
	async rewrites() {
		if (isTauri) return [];
		return [
			{
				source: "/api/:path*",
				destination: "http://127.0.0.1:10740/api/:path*",
			},
			{
				source: "/image/:path*",
				destination: "http://127.0.0.1:10740/image/:path*",
			},
			{
				source: "/docs",
				destination: "http://127.0.0.1:10740/docs",
			},
			{
				source: "/docs/:path*",
				destination: "http://127.0.0.1:10740/docs/:path*",
			},
			{
				source: "/openapi.json",
				destination: "http://127.0.0.1:10740/openapi.json",
			},
			{
				source: "/redoc",
				destination: "http://127.0.0.1:10740/redoc",
			},
		];
	},
};

module.exports = nextConfig;
