/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: false,
  },
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    return [
      { source: "/proxy/:path*", destination: `${api}/:path*` },
    ];
  },
};

module.exports = nextConfig;
