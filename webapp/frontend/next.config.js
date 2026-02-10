const path = require("path");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  turbopack: {
    root: path.resolve(__dirname),
  },
};

module.exports = nextConfig;
