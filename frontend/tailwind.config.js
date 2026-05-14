/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        success: '#4CAF50',
        danger: '#f44336',
        warning: '#ff9800',
        info: '#2196F3',
      }
    },
  },
  plugins: [],
}
