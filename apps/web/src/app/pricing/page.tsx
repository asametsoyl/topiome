import Link from "next/link";
import { ArrowUpRight, Check, Minus } from "lucide-react";
import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";
import { DemoButton } from "@/components/marketing/demo-button";
import { Badge } from "@/components/ui/badge";
import { RuoNotice } from "@/components/ui/ruo-notice";
import { cn } from "@/lib/utils";

const plans = [
  {
    name: "Academic",
    price: "Free",
    suffix: "",
    note: "For approved academic labs and students.",
    cta: "Apply for access",
    href: "/register",
    featured: false,
    features: [
      "1 user",
      "3 active projects",
      "Demo + breast / colorectal packs",
      "Uncertainty layer and HTML report",
      "Community support",
      "RUO terms apply",
    ],
    missing: ["Team collaboration", "Audit log export", "On-prem"],
  },
  {
    name: "Lab",
    price: "$399",
    suffix: "/ year",
    note: "For research teams running spatial studies.",
    cta: "Start 14-day trial",
    href: "/register",
    featured: true,
    features: [
      "3 users (add seats anytime)",
      "30 active projects",
      "All beta disease packs",
      "Sample comparison (coming)",
      "Priority support",
      "Shared reports and audit log",
      "API access (beta)",
    ],
    missing: ["SSO / SAML", "On-prem"],
  },
  {
    name: "Institution",
    price: "Custom",
    suffix: "",
    note: "For core facilities, hospitals, and biotech.",
    cta: "Talk to us",
    href: "mailto:hello@topiome.com",
    featured: false,
    features: [
      "Unlimited users and projects",
      "On-prem or private VPC",
      "SSO / SAML",
      "Custom disease packs",
      "DPA and security review",
      "Training and onboarding",
      "Named support contact",
    ],
    missing: [],
  },
];

const faqs = [
  {
    q: "Is Topiome a clinical diagnostic tool?",
    a: "No. Topiome is for research use only. It does not diagnose, predict prognosis, select treatment, or support clinical decision-making. Every report carries this notice.",
  },
  {
    q: "What data can I upload?",
    a: "Phase 1 supports 10x Visium Space Ranger output (matrix, barcodes, features, tissue positions) as a folder or zip. Visium HD, Xenium, and CosMx are on the roadmap. Demo data is synthetic and clearly labeled.",
  },
  {
    q: "How is accuracy validated?",
    a: "We benchmark deconvolution and domain assignment against synthetic pseudospots with known ground truth, then against held-out real samples from independent studies. Thresholds and current results are public in the docs. A synthetic benchmark is not a clinical validation.",
  },
  {
    q: "Can I use my own single-cell reference?",
    a: "Yes. The pipeline accepts an .h5ad reference with a cell_type column. Without a reference, Topiome falls back to a marker-score composition and labels the run accordingly.",
  },
  {
    q: "What happens to my data?",
    a: "Data is isolated per organization, stored in your workspace, and never used to train shared models without explicit agreement. You can delete a project and its files at any time. See the privacy page for details.",
  },
  {
    q: "Do you offer on-prem?",
    a: "Yes, on the Institution plan. We deploy the same web app and analysis service into your VPC or server, with your storage and database. Contact us for requirements.",
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main>
        <section className="relative overflow-hidden border-b border-line py-16 md:py-24">
          <div className="pointer-events-none absolute inset-0 grid-bg opacity-60" />
          <div className="container-page relative text-center">
            <Badge variant="acid">Pricing</Badge>
            <h1 className="display mx-auto mt-6 max-w-3xl text-5xl text-bone sm:text-6xl">
              Research-first pricing.
            </h1>
            <p className="mx-auto mt-4 max-w-xl text-sm leading-relaxed text-bone-dim">
              Start free with the demo. Upgrade when your lab needs more projects, seats, or
              validation depth. No per-sample surprise fees.
            </p>
            <div className="mt-7 flex justify-center">
              <DemoButton variant="secondary" size="md">
                Try the demo first
              </DemoButton>
            </div>
          </div>
        </section>

        <section className="border-b border-line py-16">
          <div className="container-page grid gap-4 lg:grid-cols-3">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={cn(
                  "card flex flex-col p-6",
                  plan.featured && "border-acid/40 bg-acid/[0.04]",
                )}
              >
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-medium text-bone">{plan.name}</h2>
                  {plan.featured ? <Badge variant="acid">Most popular</Badge> : null}
                </div>
                <p className="mt-4 font-mono text-4xl tracking-tight text-bone">
                  {plan.price}
                  {plan.suffix ? (
                    <span className="ml-1 text-xs text-slate">{plan.suffix}</span>
                  ) : null}
                </p>
                <p className="mt-2 text-xs leading-relaxed text-slate">{plan.note}</p>

                <ul className="mt-6 flex-1 space-y-2.5">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-xs text-bone-dim">
                      <Check className="mt-0.5 size-3.5 shrink-0 text-teal" />
                      <span className="leading-relaxed">{feature}</span>
                    </li>
                  ))}
                  {plan.missing.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-xs text-slate/70">
                      <Minus className="mt-0.5 size-3.5 shrink-0" />
                      <span className="leading-relaxed line-through decoration-slate/30">
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.href}
                  className={cn(
                    "mt-7 flex h-11 items-center justify-center gap-1.5 rounded-xl text-xs font-medium transition",
                    plan.featured
                      ? "bg-acid text-ink hover:bg-[#d6ff6a]"
                      : "border border-line text-bone hover:border-[#3a4d41]",
                  )}
                >
                  {plan.cta}
                  <ArrowUpRight className="size-3.5" />
                </Link>
              </div>
            ))}
          </div>

          <div className="container-page mt-6">
            <p className="text-[11px] leading-relaxed text-slate">
              Prices in USD, billed annually. Academic eligibility requires an institutional
              email and approval. All plans are Research Use Only. Taxes may apply. Pilot
              pricing is available for the first three institutions per region.
            </p>
          </div>
        </section>

        <section className="border-b border-line py-16">
          <div className="container-page">
            <h2 className="display text-4xl text-bone">Questions, answered.</h2>
            <div className="mt-8 grid gap-4 md:grid-cols-2">
              {faqs.map((faq) => (
                <div key={faq.q} className="card p-5">
                  <h3 className="text-sm font-medium text-bone">{faq.q}</h3>
                  <p className="mt-2 text-xs leading-relaxed text-slate">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16">
          <div className="container-page">
            <RuoNotice />
            <div className="mt-8 flex flex-col items-start justify-between gap-4 rounded-2xl border border-line bg-ink-2 p-6 md:flex-row md:items-center">
              <div>
                <h2 className="display text-3xl text-bone">Need a custom pack?</h2>
                <p className="mt-2 max-w-xl text-xs leading-relaxed text-slate">
                  We build and validate disease packs with your team: marker review, zone
                  definitions, benchmark data, and a model card. Typical timeline: 6–10 weeks.
                </p>
              </div>
              <Link
                href="mailto:hello@topiome.com"
                className="inline-flex h-11 shrink-0 items-center gap-2 rounded-xl bg-acid px-5 text-xs font-medium text-ink transition hover:bg-[#d6ff6a]"
              >
                hello@topiome.com
                <ArrowUpRight className="size-3.5" />
              </Link>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
