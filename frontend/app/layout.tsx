import type { Metadata } from "next";

import "./globals.css";

import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export const metadata: Metadata = {
  title: "CommunityOS",
  description:
    "Community intelligence and operations platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-zinc-50 text-zinc-950 antialiased">

        <div className="flex min-h-screen">

          <Sidebar />

          <div className="ml-64 flex min-h-screen flex-1 flex-col">

            <Header />

            <main className="min-h-[calc(100vh-4rem)] flex-1 bg-zinc-50 p-8">
              {children}
            </main>

          </div>

        </div>

      </body>
    </html>
  );
}