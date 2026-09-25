/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg:               '#0A0A0A',
        surface:          '#111111',
        card:             '#1A1A1A',
        border:           '#2A2A2A',
        gold:             '#C9A84C',
        'gold-dark':      '#2A2000',
        'gold-bright':    '#E0B85C',
        'text-primary':   '#F5F5F5',
        'text-secondary': '#888888',
        muted:            '#555555',
        error:            '#E53E3E',
        success:          '#38A169',
        'hover-bg':       '#222222',
      },
    },
  },
  plugins: [],
};
