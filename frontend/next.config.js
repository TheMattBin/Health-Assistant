/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  trailingSlash: true,
  output: 'standalone',
  experimental: {
    ssr: true
  },
  generateEtags: false,
  poweredByHeader: false,
}

module.exports = nextConfig