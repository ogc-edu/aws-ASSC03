/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aws: {
          dark: '#161e2e',
          squid: '#232f3e',
          orange: '#ff9900',
          hoverOrange: '#ec7211',
          blue: '#0073bb',
          lightBg: '#f8fafc'
        }
      }
    },
  },
  plugins: [],
}
