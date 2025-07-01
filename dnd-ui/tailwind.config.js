/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'parchment': {
          50: '#fefcf8',
          100: '#fdf8f0',
          200: '#faf0d8',
          300: '#f5e4b8',
          400: '#eed394',
          500: '#e6c06d',
          600: '#d9a94a',
          700: '#c18f3a',
          800: '#9e7232',
          900: '#805e2e',
        },
        'scroll': {
          50: '#f8f9fa',
          100: '#e9ecef',
          200: '#dee2e6',
          300: '#ced4da',
          400: '#adb5bd',
          500: '#6c757d',
          600: '#495057',
          700: '#343a40',
          800: '#212529',
          900: '#1a1d20',
        },
        'ink': {
          50: '#f8f9fa',
          100: '#e9ecef',
          200: '#dee2e6',
          300: '#ced4da',
          400: '#adb5bd',
          500: '#6c757d',
          600: '#495057',
          700: '#343a40',
          800: '#212529',
          900: '#0d1117',
        }
      },
      fontFamily: {
        'serif': ['Georgia', 'serif'],
        'fantasy': ['Cinzel', 'Georgia', 'serif'],
      },
      backgroundImage: {
        'parchment-texture': "url('data:image/svg+xml,%3Csvg width=\"100\" height=\"100\" viewBox=\"0 0 100 100\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cfilter id=\"noise\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.9\" numOctaves=\"4\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"100\" height=\"100\" filter=\"url(%23noise)\" opacity=\"0.05\"/%3E%3C/svg%3E')",
      }
    },
  },
  plugins: [],
} 