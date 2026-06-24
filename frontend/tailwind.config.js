/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#0F3460',
        teal: {
          DEFAULT: '#1D9E75',
          600: '#1D9E75',
        },
        amber: {
          DEFAULT: '#E07B20',
          600: '#E07B20',
        },
        surface: '#F7F8FA',
        ink: '#2C2C2A',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
