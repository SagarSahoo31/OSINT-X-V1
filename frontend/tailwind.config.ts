import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#0f172a",
        surfaceHover: "#1e293b",
        border: "#1e293b",
        primary: {
          DEFAULT: "#0284c7",
          hover: "#0369a1",
          light: "#38bdf8",
        },
        risk: {
          critical: "#dc2626",
          high: "#ea580c",
          medium: "#eab308",
          low: "#16a34a",
          info: "#0284c7",
        },
      },
    },
  },
  plugins: [],
};
export default config;
