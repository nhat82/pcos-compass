/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        // Defined Colors
        'dark-text': '#364051',
        'light-text': '#6b7280',
        
        // Primary (Treatment) Palette
        'primary': '#E618E7',
        'primary-light': '#E9D5FF',
        'primary-lighter': '#F3E8FF',
        'primary-text': '#886388',
        'primary-dark': '#c416c4',
        
        // Secondary (Problem) Palette
        'secondary': '#BE123C',
        'secondary-light': '#FFE4E6',
        'secondary-lighter': '#FECDD3',

        // Calendar specific colors
        'background': '#fcfcff',
        'surface': '#ffffff',
        'border': '#f4f0f4',
        'border-dark': '#e5dce5',
        'gray-light': '#faf7fa',
      },
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}