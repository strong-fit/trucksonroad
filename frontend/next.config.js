/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL || '',
  },
  allowedDevOrigins: ['*.preview.emergentagent.com', '*.preview.emergentcf.cloud'],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8001/api/:path*',
      },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: '**.emergentagent.com' },
    ],
    unoptimized: true,
  },
};

module.exports = nextConfig;
