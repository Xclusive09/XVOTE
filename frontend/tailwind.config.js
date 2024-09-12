/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../templates/*.html',
    '../**/templates/*.html',
    '../**/templates/**/*.html',
    '../../templates/**/*.html', // Add this line to include templates in the root templates directory
  ],
  theme: {
    extend: {
      colors: {
        'dark-green': '#064e3b', // Custom dark-green color
      },
    },
  },
  plugins: [],
}