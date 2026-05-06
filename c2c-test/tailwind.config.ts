import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#07090f",
        panel: "#0d111b",
        line: "rgba(255, 255, 255, 0.1)",
        mint: "#6ee7b7",
        cyan: "#67e8f9",
        amber: "#f6c76f",
        rose: "#fb7185",
      },
      boxShadow: {
        glow: "0 0 44px rgba(103, 232, 249, 0.18)",
      },
    },
  },
  plugins: [],
};

export default config;
