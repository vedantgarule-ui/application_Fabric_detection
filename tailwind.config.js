/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: '#FAF7EE',
          deep: '#E8E1CD',
          subtle: '#F5EFEB',
          card: '#FFFFFF',
          dark: '#181512',
          'dark-card': '#231F1B',
          'dark-border': '#3D362F',
        },
        ink: {
          DEFAULT: '#26211C',
          soft: '#5B5347',
          light: '#8C8275',
          faint: '#B2A899',
        },
        tan: {
          DEFAULT: '#B7A98A',
          light: '#DDD5C0',
          faint: '#EFE9DC',
        },
        eco: {
          DEFAULT: '#54683C',
          bg: '#E3E8D6',
          border: '#A2B58B',
          dark: '#3A4928',
        },
        synthetic: {
          DEFAULT: '#4B4F92',
          bg: '#E1E1F0',
          border: '#9EA1D4',
        },
        rust: {
          DEFAULT: '#A8451F',
          light: '#F5DFD6',
          dark: '#853414',
        },
      },
      fontFamily: {
        serif: ['Fraunces', 'Playfair Display', 'Georgia', 'serif'],
        sans: ['IBM Plex Sans', 'Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(38, 33, 28, 0.06)',
        'lift': '0 12px 30px -4px rgba(38, 33, 28, 0.12)',
        'tag': '0 2px 8px 0 rgba(38, 33, 28, 0.08)',
      },
      animation: {
        'scan-beam': 'scanBeam 2.4s ease-in-out infinite',
        'fade-in': 'fadeIn 0.35s ease-out forwards',
        'scale-in': 'scaleIn 0.3s ease-out forwards',
        'pulse-subtle': 'pulseSubtle 2s infinite ease-in-out',
      },
      keyframes: {
        scanBeam: {
          '0%, 100%': { transform: 'translateY(0%)', opacity: '0.4' },
          '50%': { transform: 'translateY(100%)', opacity: '0.9' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
    },
  },
  plugins: [],
}
