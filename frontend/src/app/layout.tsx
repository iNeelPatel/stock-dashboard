import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Investment Terminal — Indian Equities Research & Paper Trading",
  description: "Production-grade AI-powered Indian stock market research, analysis, and paper trading terminal inspired by Google Finance and Warren Buffett principles.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen selection:bg-slate-900 selection:text-white dark:selection:bg-white dark:selection:text-slate-900">
        {children}
      </body>
    </html>
  );
}
