/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        olive: {
          DEFAULT: '#3F4A32',
          50: '#F5F7F3',
          100: '#E8ECE2',
          200: '#D2DBC6',
          300: '#B0BF9E',
          400: '#7B9164',
          500: '#3F4A32', // Deep Olive
          600: '#353E2A',
          700: '#2A3222',
          800: '#20261A',
          900: '#161A12',
        },
        sand: {
          DEFAULT: '#D8C7A3',
          50: '#FAF8F4',
          100: '#F4EFE6',
          200: '#E8DDC8',
          300: '#D8C7A3', // Warm Sand
          400: '#C5B085',
          500: '#AD9668',
        },
        offwhite: {
          DEFAULT: '#F7F5EF', // Warm Off-White
          50: '#FDFCFB',
          100: '#FAF8F4',
          200: '#F7F5EF',
        },
        paper: {
          DEFAULT: '#FFFFFF',    // Paper White
        },
        terracotta: {
          DEFAULT: '#B66A4C', // Muted Terracotta
          50: '#FBF5F3',
          100: '#F6E9E4',
          200: '#EDD3C9',
          500: '#B66A4C',
          600: '#9E583C',
          700: '#84472F',
        },
        natgreen: {
          DEFAULT: '#607A4A', // Natural Green
          50: '#F4F7F2',
          100: '#E6EDE1',
          200: '#CFDEC6',
          500: '#607A4A',
          600: '#4F653D',
        },
        charcoal: {
          DEFAULT: '#292925', // Charcoal Text
          50: '#F6F6F5',
          100: '#E7E7E5',
          200: '#D1D0CC',
          300: '#A9A8A3',
          400: '#8B8982',
          500: '#716F67', // Warm Gray Secondary Text
          600: '#55544E',
          700: '#42413C',
          800: '#32312D',
          900: '#292925',
        },
        warmgray: {
          DEFAULT: '#716F67',
          50: '#F8F8F7',
          100: '#ECEBE9',
          200: '#DAD8D4',
          500: '#716F67',
        },
        bordercolor: '#DEDACF', // Soft Beige Gray
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        DEFAULT: '8px',
        md: '8px',
        lg: '10px',
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(41, 41, 37, 0.04)',
        card: '0 1px 3px 0 rgba(41, 41, 37, 0.05), 0 1px 2px -1px rgba(41, 41, 37, 0.03)',
      }
    },
  },
  plugins: [],
}
