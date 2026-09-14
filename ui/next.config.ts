import type { NextConfig } from "next"

/**
 * `next dev` does not execute api/*.py, so in development the /api routes are
 * proxied to scripts/local_api.py. In production those same paths are real
 * Vercel Python functions and must not be rewritten, which is why the rewrite
 * is gated on NODE_ENV rather than always present.
 */
const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return []
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8787/api/:path*",
      },
    ]
  },
}

export default nextConfig
