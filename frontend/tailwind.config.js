/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        sunrise: "#f97316",
        mint: "#34d399",
        paper: "#fffaf0",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["DM Sans", "sans-serif"],
      },
      boxShadow: {
        card: "0 20px 60px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
};
