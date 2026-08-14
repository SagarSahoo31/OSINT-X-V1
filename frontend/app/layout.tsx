import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "OSINT-X — Cybersecurity Intelligence & Exposure Risk Platform",
  description: "Defensive attack-surface discovery, relationship intelligence, and exposure risk assessment.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-slate-100 min-h-screen flex flex-col">
        <Navbar />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-6 overflow-y-auto max-w-[1600px] w-full">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
