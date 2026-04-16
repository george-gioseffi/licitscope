import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: {
        "2xl": "1440px",
      },
    },
    extend: {
      colors: {
        ink: {
          50:  "#f5f7fa",
          100: "#e4e9f0",
          200: "#c6cfdd",
          300: "#9aa6ba",
          400: "#6b7891",
          500: "#475571",
          600: "#334057",
          700: "#232d42",
          800: "#161d2f",
          900: "#0b1020",
        },
        brand: {
          50:  "#eef5ff",
          100: "#d9e8ff",
          200: "#b4d0ff",
          300: "#84b1ff",
          400: "#528aff",
          500: "#2b65f5",
          600: "#1a49d0",
          700: "#1539a0",
          800: "#122d7c",
          900: "#0e2159",
        },
        accent: {
          mint: "#2dd4bf",
          amber: "#f59e0b",
          rose: "#f43f5e",
          violet: "#8b5cf6",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 1px 0 0 rgb(255 255 255 / 0.04) inset, 0 1px 2px 0 rgb(10 12 20 / 0.4), 0 8px 20px -12px rgb(20 40 100 / 0.45)",
        glow: "0 0 0 1px rgba(43,101,245,0.35), 0 8px 32px -4px rgba(43,101,245,0.35)",
      },
      backgroundImage: {
        "grid": "linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
