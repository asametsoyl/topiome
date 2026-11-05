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
    default: "Topiome — Spatial disease atlas platform",
    template: "%s · Topiome",
  },
  description:
    "Topiome turns spatial transcriptomics into validated, shareable tissue atlases: cell composition, spatial domains, target evidence, and uncertainty — for research use only.",
  keywords: [
    "spatial transcriptomics",
    "spatial omics",
    "tissue atlas",
    "deconvolution",
    "Visium",
    "bioinformatics",
    "research use only",
  ],
  openGraph: {
    title: "Topiome — Spatial disease atlas platform",
    description:
      "From spots to story. Validated spatial atlases with visible uncertainty. For research use only.",
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
