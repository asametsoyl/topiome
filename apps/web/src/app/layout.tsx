import type { Metadata } from "next";
import { Instrument_Serif } from "next/font/google";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";
import { Providers } from "./providers";

const instrument = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-instrument",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.APP_URL ?? "http://localhost:3000"),
  title: {
    default: "Topiome — Cellular perturbation research",
    template: "%s · Topiome",
  },
  description:
    "Topiome is a research program exploring predictions of cellular responses to defined genetic perturbations, with benchmark-first evaluation and uncertainty made explicit.",
  keywords: [
    "single-cell perturbation",
    "Perturb-seq",
    "cellular response prediction",
    "virtual cell research",
    "CRISPR perturbation",
    "bioinformatics",
    "research use only",
  ],
  openGraph: {
    title: "Topiome — Cellular perturbation research",
    description:
      "Researching how cells respond to defined interventions. Benchmark-first, transparent about uncertainty, for research use only.",
    type: "website",
    siteName: "Topiome",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable} ${instrument.variable}`}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
