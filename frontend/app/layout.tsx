import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Roboto_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const robotoMono = Roboto_Mono({
  variable: "--font-roboto-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://onepercentbetter.poker"),
  title: "onepercentbetter.poker — GTO Defends. We Exploit.",
  description:
    "I built a full-stack poker analytics platform using AI. It parses GGPoker hand histories, quantifies opponent GTO deviations, and surfaces actionable bb/100 exploit edges. Built by Sukmin Yoon.",
  openGraph: {
    title: "onepercentbetter.poker — GTO Defends. We Exploit.",
    description:
      "Full-stack poker exploit engine built with AI. Parses GGPoker hand histories to quantify GTO deviations and surface bb/100 edges. Built by Sukmin Yoon.",
    url: "https://onepercentbetter.poker",
    siteName: "onepercentbetter.poker",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "onepercentbetter.poker — GTO Defends. We Exploit.",
    description:
      "Full-stack poker exploit engine built with AI. Parses GGPoker hand histories to quantify GTO deviations and surface bb/100 edges.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.variable} ${robotoMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
