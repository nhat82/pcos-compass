/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        // --- Custom Utility Colors from <style> block ---
        'pcos-pink': '#E618E7',           // Equivalent to .text-pcos-pink, .bg-pcos-pink
        'pcos-pink-700': '#c015c1',       // Equivalent to .hover:bg-pcos-pink-700
        'pcos-light-pink': '#FCE8FC',     // Equivalent to .bg-pcos-light-pink

        // --- Core/System Colors ---
        'dark-text': '#364051',
        'light-text': '#6b7280',
        
        // --- Primary (Treatment) Palette ---
        'primary': '#E618E7',             // Main primary color
        'primary-light': '#E9D5FF',
        'primary-lighter': '#F3E8FF',
        'primary-text': '#886388',
        'primary-dark': '#c416c4',
        
        // --- Secondary (Problem) Palette ---
        'secondary': '#BE123C',
        'secondary-light': '#FFE4E6',
        'secondary-lighter': '#FECDD3',

        // --- Calendar/Background specific colors ---
        'background': '#f7fafc',
        'surface': '#ffffff',
        'border': '#f4f0f4',
        'border-dark': '#e5dce5',
        'gray-light': '#faf7fa',
      },
      fontFamily: {
        // You only need 'inter' here since 'sans-serif' is the fallback
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}