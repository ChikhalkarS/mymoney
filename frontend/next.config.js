/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Enable standalone output for Docker – produces a self-contained server.js
  output: "standalone",
  // When BACKEND_URL is set (e.g. in Docker Compose), proxy /api/* to the
  // backend service so the browser only ever needs to know the frontend URL.
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL;
    if (!backendUrl) return [];
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
