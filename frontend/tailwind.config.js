/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      borderRadius: {
        'button': '20px',
        'card': '24px',
      },
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#1f89ecff',
          600: '#1E40AF',
          700: '#2043B2',
        },
        text: {
          
          50: '#f9fafb',
          500: '#374151', 
          600: '#1f2937',
        },
        
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        }
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'shake': 'shake 0.5s ease-in-out',
        'flip-in': 'flipIn 1s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-5px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(5px)' },
        },
        flipIn: {
          '0%': { 
            transform: 'perspective(400px) rotateY(-90deg)',
            opacity: '0',
          },
          '100%': { 
            transform: 'perspective(400px) rotateY(0deg)',
            opacity: '1',
          },
        },
      },
    },
  },
  plugins: [],
}