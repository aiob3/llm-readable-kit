import type { Metadata } from "next";
import { Oxanium, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// Neural Cartography — Oxanium: geometric sci-fi data-terminal feel
const headingFont = Oxanium({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-heading"
});

// MDS-specified mono: JetBrains Mono for IDs, code, node labels
const monoFont = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["300", "400", "500"],
  variable: "--font-mono"
});

export const metadata: Metadata = {
  title: "canonical::ssot — v1 pilot",
  description: "DSL textual autoral → JSON normalizado → idempotência → event log"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={`${headingFont.variable} ${monoFont.variable}`}>{children}</body>
    </html>
  );
}
