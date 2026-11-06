import type { NextConfig } from "next";

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

// The repo lives on an exFAT disk, where macOS writes "._*" AppleDouble files next to
// every file. Turbopack's on-disk cache cannot parse those names and the build fails
// with "Failed to open database". Keep the cache off unless explicitly enabled.
const turbopackFsCache = process.env.TOPIOME_TURBOPACK_FS_CACHE === "1";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Docker images use the self-contained server (infra/docker/web.Dockerfile).
  ...(process.env.NEXT_OUTPUT === "standalone" ? { output: "standalone" as const } : {}),
  experimental: {
    turbopackFileSystemCacheForDev: turbopackFsCache,
    turbopackFileSystemCacheForBuild: turbopackFsCache,
  },
  poweredByHeader: false,
  allowedDevOrigins: ["127.0.0.1", "localhost"],
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_URL}/api/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },
};

export default nextConfig;
