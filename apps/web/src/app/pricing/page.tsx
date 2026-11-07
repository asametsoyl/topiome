import Link from "next/link";
import { ArrowRight, Beaker, CircleHelp, Users } from "lucide-react";
import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";
import { RuoNotice } from "@/components/ui/ruo-notice";

export default function PricingPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main>
        <section className="border-b border-line bg-[#f8faf8] py-16 md:py-24">
          <div className="container-page max-w-4xl">
            <p className="mono-label">Access</p>
            <h1 className="display mt-5 text-5xl text-bone sm:text-6xl">Research preview.</h1>
            <p className="mt-5 max-w-2xl text-sm leading-7 text-bone-dim">
              Topiome is at the beginning of a new research direction. We are not offering paid plans or model access while the perturbation benchmark and scientific scope are being established.
            </p>
            <a href="mailto:hello@topiome.com?subject=Topiome%20research%20preview" className="mt-8 inline-flex h-11 items-center gap-2 rounded-xl bg-teal px-4 text-xs font-medium text-white hover:bg-[#125f50]">
              Discuss a research collaboration <ArrowRight className="size-3.5" />
            </a>
          </div>
        </section>
        <section className="border-b border-line py-16 md:py-20">
          <div className="container-page grid gap-4 md:grid-cols-3">
            {[
              { icon: Beaker, title: "Current stage", text: "Public-data curation and a locked, baseline-first benchmark." },
              { icon: Users, title: "Collaboration", text: "Experimental partners will be needed to test predictions prospectively." },
              { icon: CircleHelp, title: "Access", text: "There is no validated prediction service, subscription, or pricing yet." },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <article key={item.title} className="card p-6">
                  <Icon className="size-4 text-teal" />
                  <h2 className="mt-6 text-sm font-medium text-bone">{item.title}</h2>
                  <p className="mt-2 text-xs leading-6 text-bone-dim">{item.text}</p>
                </article>
              );
            })}
          </div>
        </section>
        <section className="py-16">
          <div className="container-page max-w-4xl">
            <RuoNotice />
            <Link href="/docs" className="mt-6 inline-flex items-center gap-2 text-xs text-teal hover:text-[#125f50]">Read the research plan <ArrowRight className="size-3.5" /></Link>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
