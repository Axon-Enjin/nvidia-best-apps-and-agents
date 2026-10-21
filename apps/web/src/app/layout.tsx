import type { Metadata } from "next";
import { connection } from "next/server";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Sentinel Claims", template: "%s · Sentinel Claims" },
  description: "Claim review workspace for prepared hospital claims.",
  icons: { icon: "/favicon.svg" },
  robots: { index: false, follow: false },
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  // Every page renders per request: the CSP nonce needs it, and no page here is public or cacheable.
  await connection();
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
