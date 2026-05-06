import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { StatusBar } from "@/components/StatusBar";

export const metadata: Metadata = {
  title: "EchoTrace Audio Identification",
  description: "Identify noisy or partial song snippets with confidence and latency telemetry.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <StatusBar />
        {children}
      </body>
    </html>
  );
}
