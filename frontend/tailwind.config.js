/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sentinel: {
          bg: "#060414",
          surface: "#0B0826",
          card: "#120D36",
          border: "rgba(168, 85, 247, 0.22)",
          "border-subtle": "rgba(255, 255, 255, 0.08)",
          cyan: "#00F0FF",
          purple: "#A855F7",
          pink: "#EC4899",
          magenta: "#D946EF",
          amber: "#F59E0B",
          emerald: "#10B981",
          muted: "#94A3B8"
        }
      },
      fontFamily: {
        display: ["Syne", "Space Grotesk", "sans-serif"],
        sans: ["Space Grotesk", "Inter", "sans-serif"],
        mono: ["Space Grotesk", "monospace"],
      },
      boxShadow: {
        glow: "0 0 25px -5px rgba(168, 85, 247, 0.35)",
        "glow-cyan": "0 0 25px -5px rgba(0, 240, 255, 0.4)",
        "glow-pink": "0 0 35px -5px rgba(236, 72, 153, 0.4)",
        "glow-amber": "0 0 25px -5px rgba(245, 158, 11, 0.4)",
      },
      animation: {
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float-orb": "floatOrb 8s ease-in-out infinite",
        "spin-slow": "spin 20s linear infinite",
      },
      keyframes: {
        floatOrb: {
          "0%, 100%": { transform: "translateY(0px) scale(1)" },
          "50%": { transform: "translateY(-12px) scale(1.02)" },
        }
      }
    },
  },
  plugins: [],
};
