/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#0F766E',
          light: '#14B8A6',
          lighter: '#CCFBF1',
          dark: '#115E59'
        },
        income: '#10B981',
        expense: '#EF4444',
        ai: '#F59E0B',
        info: '#3B82F6',
        surface: '#FFFFFF',
        bg: '#F8FAFC',
        divider: '#E2E8F0',
        'text-primary': '#1E293B',
        'text-secondary': '#64748B',
        'text-muted': '#94A3B8',
        'dark-bg': '#0F172A',
        'dark-surface': '#1E293B',
        'dark-divider': '#334155'
      },
      fontFamily: {
        sans: ['Inter', '"Noto Sans SC"', '-apple-system', 'sans-serif']
      },
      fontSize: {
        display: ['36px', { lineHeight: '1.2', fontWeight: '700' }],
        h1: ['24px', { lineHeight: '1.3', fontWeight: '600' }],
        h2: ['18px', { lineHeight: '1.4', fontWeight: '600' }],
        body: ['15px', { lineHeight: '1.5', fontWeight: '400' }],
        caption: ['13px', { lineHeight: '1.4', fontWeight: '400' }],
        data: ['28px', { lineHeight: '1.1', fontWeight: '600' }]
      },
      spacing: {
        'space-1': '4px',
        'space-2': '8px',
        'space-3': '12px',
        'space-4': '16px',
        'space-5': '20px',
        'space-6': '24px',
        'space-8': '32px'
      },
      borderRadius: {
        'card': '16px',
        'card-sm': '12px',
        'tag': '8px'
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03)',
        'card-hover': '0 4px 6px rgba(0,0,0,0.07)',
        'btn': '0 1px 3px rgba(15,118,110,0.2)',
        'fab': '0 4px 12px rgba(15,118,110,0.35)'
      }
    }
  },
  plugins: []
}
