import Link from "next/link";
import {
  ArrowUpRight,
  Boxes,
  Braces,
  Check,
  CircleDot,
  Dna,
  FileText,
  Layers3,
  Map,
  Microscope,
  ScanLine,
  Sparkles,
  Target,
  Users,
} from "lucide-react";
import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";
import { DemoButton } from "@/components/marketing/demo-button";
import { AtlasVisual } from "@/components/marketing/atlas-visual";
import { Badge } from "@/components/ui/badge";
import { RuoNotice } from "@/components/ui/ruo-notice";
import { cn } from "@/lib/utils";

const packs = [
  {
    name: "Breast",
    id: "breast",
    tissue: "Breast",
    status: "beta",
    color: "#E8B4B8",
    cells: 10,
    zones: 6,
    targets: 6,
    note: "Tumor core, invasive margin, immune aggregates, normal gland.",
  },
  {
    name: "Colorectal",
    id: "colorectal",
    tissue: "Colon",
    status: "beta",
    color: "#7FB77E",
    cells: 9,
    zones: 6,
    targets: 5,
    note: "Tumor glands, invasive front, lymphoid aggregates, mucosa.",
  },
  {
    name: "Lung",
    id: "lung",
    tissue: "Lung",
    status: "draft",
    color: "#8DB6D9",
    cells: 8,
    zones: 6,
    targets: 6,
    note: "Tumor, alveolar and airway compartments, stroma, necrosis.",
  },
  {
    name: "Melanoma",
    id: "melanoma",
    tissue: "Skin",
    status: "draft",
    color: "#B08BBB",
    cells: 8,
    zones: 5,
    targets: 6,
    note: "Tumor, invasive margin, immune infiltrate, skin compartments.",
  },
  {
    name: "Prostate",
    id: "prostate",
    tissue: "Prostate",
    status: "draft",
    color: "#6FA8DC",
    cells: 9,
    zones: 5,
    targets: 6,
    note: "Tumor glands, benign glands, fibromuscular stroma, perineural.",
  },
  {
    name: "Glioblastoma",
    id: "glioblastoma",
    tissue: "Brain",
    status: "beta",
    color: "#C95B7A",
    cells: 7,
    zones: 5,
    targets: 6,
    note: "Pseudopalisading necrosis, microvascular proliferation, leading edge.",
  },
];

const features = [
  {
    icon: Dna,
    title: "Deconvolution with residuals",
    body: "NNLS baseline returns per-spot residual and entropy, combined into a visible uncertainty layer. No black-box proportions.",
    accent: "text-teal",
  },
  {
    icon: Layers3,
    title: "Spatially coherent domains",
    body: "kNN-smoothed composition drives clustering; each domain is labeled by the disease pack's zone markers and reported with its cell-type mix.",
    accent: "text-acid",
  },
  {
    icon: Boxes,
    title: "Disease packs, not scripts",
    body: "Markers, zones, targets, and report sections live in versioned YAML. A new disease is a data and validation task, not a new codebase.",
    accent: "text-amber",
  },
  {
    icon: Target,
    title: "Target evidence, ranked",
    body: "Research prioritization scores by domain and cell type, with evidence levels. A hypothesis generator — not a treatment recommendation.",
    accent: "text-coral",
  },
  {
    icon: Braces,
    title: "Reproducible by default",
    body: "Pipeline version, pack version, parameters, and runtime are recorded for every run. Re-running is a first-class action.",
    accent: "text-teal",
  },
  {
    icon: FileText,
    title: "Reports your team can defend",
    body: "Self-contained HTML with methods, QC, warnings, limitations, and a permanent RUO notice. Print or share without losing context.",
    accent: "text-acid",
  },
];

const benchmarks = [
  {
    label: "Composition JSD",
    value: 0.099,
    display: "0.099",
    min: 0.2,
    target: 0.12,
    lowerIsBetter: true,
  },
  {
    label: "Dominant-type Pearson",
    value: 0.862,
    display: "0.862",
    min: 0.75,
    target: 0.85,
    lowerIsBetter: false,
  },
  {
    label: "Domain ARI",
    value: 0.634,
    display: "0.634",
    min: 0.35,
    target: 0.55,
    lowerIsBetter: false,
  },
];

const steps = [
  {
    icon: Microscope,
    title: "Bring a sample",
    body: "Upload a Space Ranger folder or zip, or start with the synthetic demo sample.",
  },
  {
    icon: Boxes,
    title: "Pick a disease pack",
    body: "Breast, colorectal, lung, melanoma, prostate, or glioblastoma — each with markers and zones.",
  },
  {
    icon: ScanLine,
    title: "Run the pipeline",
    body: "QC, deconvolution, spatial smoothing, domain assignment, target scoring, uncertainty, report.",
  },
  {
    icon: Map,
    title: "Read the atlas",
    body: "Inspect composition, domains, and uncertainty on the tissue map, then share the report.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden border-b border-line">
          <div className="pointer-events-none absolute inset-0 grid-bg opacity-70" />
          <div className="pointer-events-none absolute -left-40 top-20 size-[480px] rounded-full bg-teal/5 blur-3xl" />
          <div className="container-page relative grid gap-14 py-16 md:py-24 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
            <div className="animate-fade-up">
              <div className="flex items-center gap-2">
                <Badge variant="acid">Spatial disease atlas platform</Badge>
                <Badge variant="outline">RUO</Badge>
              </div>
              <h1 className="display mt-6 text-6xl text-bone sm:text-7xl lg:text-[86px]">
                From spots
                <br />
                to <span className="text-acid">story.</span>
              </h1>
              <p className="mt-6 max-w-xl text-sm leading-relaxed text-bone-dim sm:text-base">
                Topiome turns spatial transcriptomics into cell composition, coherent tissue
                domains, and target evidence — with uncertainty visible on every spot and a
                report your team can defend.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3">
                <DemoButton>Explore the live atlas</DemoButton>
                <Link
                  href="#product"
                  className="inline-flex h-12 items-center gap-2 rounded-xl border border-line px-5 text-sm text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
                >
                  See how it works
                  <ArrowUpRight className="size-4" />
                </Link>
              </div>

              <div className="mt-8 flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] text-slate">
                <span className="inline-flex items-center gap-1.5">
                  <Check className="size-3.5 text-teal" />
                  Demo data included
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <Check className="size-3.5 text-teal" />
                  No credit card
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <Check className="size-3.5 text-teal" />
                  Built for Visium
                </span>
              </div>
            </div>

            <div className="animate-fade-up [animation-delay:120ms]">
              <AtlasVisual />
            </div>
          </div>

          <div className="container-page relative pb-8">
            <div className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line md:grid-cols-4">
              {[
                { k: "6", v: "data-rich disease packs" },
                { k: "< 3 min", v: "upload to atlas (demo)" },
                { k: "2×", v: "uncertainty layers per run" },
                { k: "100%", v: "research use only" },
              ].map((item) => (
                <div key={item.v} className="bg-ink-2 px-5 py-4">
                  <p className="font-mono text-2xl tracking-tight text-bone">{item.k}</p>
                  <p className="mt-1 text-[11px] text-slate">{item.v}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Trust strip */}
        <section className="border-b border-line bg-ink-2/40">
          <div className="container-page flex flex-col items-center gap-4 py-6 md:flex-row md:justify-between">
            <p className="mono-label">Built for the spatial biology stack</p>
            <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[11px] text-slate">
              <span>10x Visium</span>
              <span className="text-line">/</span>
              <span>scRNA-seq references</span>
              <span className="text-line">/</span>
              <span>NNLS baseline</span>
              <span className="text-line">/</span>
              <span>Cell2location-ready</span>
              <span className="text-line">/</span>
              <span>HTML reports</span>
            </div>
          </div>
        </section>

        {/* Problem */}
        <section className="border-b border-line py-20">
          <div className="container-page">
            <div className="max-w-2xl">
              <p className="mono-label">The gap</p>
              <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">
                Pretty maps are not evidence.
              </h2>
              <p className="mt-4 max-w-xl text-sm leading-relaxed text-bone-dim">
                Spatial pipelines often stop at a colorful cluster plot. The hard questions —
                how sure are we, what does this region mean, and can someone reproduce it — are
                left to the reader.
              </p>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {[
                {
                  n: "01",
                  title: "Composition you can't audit",
                  body: "Proportions without residuals, reference provenance, or a confidence layer. A single number hides the uncertainty.",
                },
                {
                  n: "02",
                  title: "Domains without a definition",
                  body: "Clusters that look spatial but carry no biological label, no marker evidence, and no stability check.",
                },
                {
                  n: "03",
                  title: "Reports that hide the caveats",
                  body: "Methods and limitations buried in a slide deck — or missing. The result travels further than its context.",
                },
              ].map((item) => (
                <div key={item.n} className="card card-hover p-6">
                  <p className="font-mono text-xs text-coral">{item.n}</p>
                  <h3 className="mt-4 text-sm font-medium text-bone">{item.title}</h3>
                  <p className="mt-2 text-xs leading-relaxed text-slate">{item.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Product */}
        <section id="product" className="scroll-mt-24 border-b border-line py-20">
          <div className="container-page">
            <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
              <div className="max-w-2xl">
                <p className="mono-label">The platform</p>
                <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">
                  One workflow.
                  <br />
                  Every layer visible.
                </h2>
              </div>
              <p className="max-w-sm text-xs leading-relaxed text-slate">
                A disease-agnostic core with versioned disease packs. The same pipeline runs on
                the demo sample and on your Visium data — with the same audit trail.
              </p>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div key={feature.title} className="card card-hover p-6">
                    <span
                      className={cn(
                        "inline-flex size-9 items-center justify-center rounded-lg border border-line bg-ink-3",
                        feature.accent,
                      )}
                    >
                      <Icon className="size-4" />
                    </span>
                    <h3 className="mt-4 text-sm font-medium text-bone">{feature.title}</h3>
                    <p className="mt-2 text-xs leading-relaxed text-slate">{feature.body}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Disease packs */}
        <section id="packs" className="scroll-mt-24 border-b border-line py-20">
          <div className="container-page">
            <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
              <div className="max-w-2xl">
                <p className="mono-label">Disease packs</p>
                <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">
                  Start where the data is rich.
                </h2>
                <p className="mt-4 max-w-xl text-sm leading-relaxed text-bone-dim">
                  Six cancers with deep public spatial and single-cell resources. Each pack
                  carries cell types, zone definitions, target genes, and a report template.
                </p>
              </div>
              <DemoButton variant="secondary" size="md" showArrow={false}>
                Open the pack browser
              </DemoButton>
            </div>

            <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {packs.map((pack) => (
                <div key={pack.id} className="card card-hover overflow-hidden">
                  <div
                    className="h-1 w-full"
                    style={{ background: pack.color, opacity: 0.9 }}
                  />
                  <div className="p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-sm font-medium text-bone">{pack.name}</h3>
                        <p className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.12em] text-slate">
                          {pack.tissue} · {pack.id}
                        </p>
                      </div>
                      <Badge variant={pack.status === "beta" ? "teal" : "outline"}>
                        {pack.status}
                      </Badge>
                    </div>
                    <p className="mt-3 text-xs leading-relaxed text-slate">{pack.note}</p>
                    <div className="mt-4 flex items-center gap-4 border-t border-line pt-3 font-mono text-[10px] text-slate">
                      <span>{pack.cells} cell types</span>
                      <span>{pack.zones} zones</span>
                      <span>{pack.targets} targets</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <p className="mt-5 text-[11px] text-slate">
              Status reflects validation maturity. <span className="text-bone-dim">Beta</span> =
              baseline running, validation incomplete. <span className="text-bone-dim">Draft</span>{" "}
              = under development. No pack is marketed as clinically validated.
            </p>
          </div>
        </section>

        {/* Validation */}
        <section id="validation" className="scroll-mt-24 border-b border-line py-20">
          <div className="container-page grid gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
            <div>
              <p className="mono-label">Validation</p>
              <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">
                Validation,
                <br />
                not vibes.
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-bone-dim">
                Every release is measured against known ground truth before it is called
                validated. Synthetic pseudospots test the estimator; held-out real samples test
                generalization. Neither is a clinical claim.
              </p>

              <ul className="mt-6 space-y-3">
                {[
                  "Pseudospot benchmark with known composition and zones",
                  "Held-out samples from independent studies, not the same patient",
                  "Calibration and stability checks, not just a single score",
                  "Model card for every pack version: data, metrics, limits",
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-xs text-bone-dim">
                    <CircleDot className="mt-0.5 size-3.5 shrink-0 text-acid" />
                    <span className="leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>

              <Link
                href="/docs#validation"
                className="mt-6 inline-flex items-center gap-1.5 text-xs text-acid transition hover:gap-2.5"
              >
                Read the validation method
                <ArrowUpRight className="size-3.5" />
              </Link>
            </div>

            <div className="card overflow-hidden">
              <div className="flex items-center justify-between border-b border-line px-5 py-4">
                <div>
                  <p className="text-sm font-medium text-bone">Synthetic benchmark</p>
                  <p className="mt-0.5 text-xs text-slate">Breast pack · 1,200 spots · seed 42</p>
                </div>
                <Badge variant="teal">Passing</Badge>
              </div>
              <div className="space-y-5 p-5">
                {benchmarks.map((metric) => {
                  const scaleMax = metric.lowerIsBetter ? 0.25 : 1;
                  const fill = Math.max(0.02, Math.min(1, metric.value / scaleMax));
                  const minPos = Math.min(1, metric.min / scaleMax);
                  const targetPos = Math.min(1, metric.target / scaleMax);
                  const passing = metric.lowerIsBetter
                    ? metric.value <= metric.target
                    : metric.value >= metric.target;
                  const minimum = metric.lowerIsBetter
                    ? metric.value <= metric.min
                    : metric.value >= metric.min;
                  return (
                    <div key={metric.label}>
                      <div className="flex items-baseline justify-between">
                        <p className="text-xs text-bone-dim">
                          {metric.label}
                          {metric.lowerIsBetter ? (
                            <span className="ml-1.5 font-mono text-[9px] text-slate">
                              lower is better
                            </span>
                          ) : null}
                        </p>
                        <p
                          className={cn(
                            "font-mono text-sm",
                            passing ? "text-teal" : minimum ? "text-amber" : "text-coral",
                          )}
                        >
                          {metric.display}
                        </p>
                      </div>
                      <div className="relative mt-2 h-2 rounded-full bg-bone/10">
                        <div
                          className={cn(
                            "h-full rounded-full",
                            passing
                              ? "bg-gradient-to-r from-teal to-acid"
                              : minimum
                                ? "bg-amber"
                                : "bg-coral",
                          )}
                          style={{ width: `${fill * 100}%` }}
                        />
                        <span
                          className="absolute top-1/2 h-3.5 w-px -translate-y-1/2 bg-bone/30"
                          style={{ left: `${minPos * 100}%` }}
                          title={`minimum threshold ${metric.min}`}
                        />
                        <span
                          className="absolute top-1/2 h-3.5 w-px -translate-y-1/2 bg-acid/70"
                          style={{ left: `${targetPos * 100}%` }}
                          title={`target threshold ${metric.target}`}
                        />
                      </div>
                      <div className="mt-1 flex justify-between font-mono text-[9px] text-slate">
                        <span>
                          min {metric.lowerIsBetter ? "<" : ">"} {metric.min}
                        </span>
                        <span>
                          target {metric.lowerIsBetter ? "<" : ">"} {metric.target}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="border-t border-line bg-ink-3/60 px-5 py-3">
                <p className="text-[10px] leading-relaxed text-slate">
                  Synthetic ground truth; not a substitute for held-out real-data validation.
                  Metrics are reported with every run, including failures and warnings.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How it works */}
        <section className="border-b border-line py-20">
          <div className="container-page">
            <div className="max-w-2xl">
              <p className="mono-label">Workflow</p>
              <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">
                Four steps to a tissue atlas.
              </h2>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {steps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={step.title} className="relative card p-5">
                    <div className="flex items-center justify-between">
                      <span className="inline-flex size-9 items-center justify-center rounded-lg border border-line bg-ink-3 text-teal">
                        <Icon className="size-4" />
                      </span>
                      <span className="font-mono text-xs text-slate">0{index + 1}</span>
                    </div>
                    <h3 className="mt-4 text-sm font-medium text-bone">{step.title}</h3>
                    <p className="mt-1.5 text-xs leading-relaxed text-slate">{step.body}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Pricing teaser */}
        <section className="border-b border-line py-20">
          <div className="container-page">
            <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
              <div>
                <p className="mono-label">Pricing</p>
                <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">
                  Research-first pricing.
                </h2>
              </div>
              <Link
                href="/pricing"
                className="inline-flex items-center gap-1.5 text-xs text-acid transition hover:gap-2.5"
              >
                Compare plans
                <ArrowUpRight className="size-3.5" />
              </Link>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {[
                {
                  name: "Academic",
                  price: "Free",
                  note: "Approved academic labs",
                  items: ["1 user", "3 projects", "Core packs", "Community support"],
                  featured: false,
                },
                {
                  name: "Lab",
                  price: "$399",
                  suffix: "/ year",
                  note: "For research teams",
                  items: [
                    "3 users",
                    "30 projects",
                    "All beta packs",
                    "Priority support",
                    "Shared reports",
                  ],
                  featured: true,
                },
                {
                  name: "Institution",
                  price: "Custom",
                  note: "On-prem or VPC",
                  items: ["SSO / SAML", "Unlimited projects", "Audit & DPA", "Training"],
                  featured: false,
                },
              ].map((plan) => (
                <div
                  key={plan.name}
                  className={cn(
                    "card p-6",
                    plan.featured && "border-acid/40 bg-acid/[0.04]",
                  )}
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-bone">{plan.name}</p>
                    {plan.featured ? <Badge variant="acid">Popular</Badge> : null}
                  </div>
                  <p className="mt-4 font-mono text-3xl tracking-tight text-bone">
                    {plan.price}
                    {plan.suffix ? (
                      <span className="ml-1 text-xs text-slate">{plan.suffix}</span>
                    ) : null}
                  </p>
                  <p className="mt-1 text-[11px] text-slate">{plan.note}</p>
                  <ul className="mt-5 space-y-2">
                    {plan.items.map((item) => (
                      <li key={item} className="flex items-center gap-2 text-xs text-bone-dim">
                        <Check className="size-3.5 text-teal" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <Link
                    href={plan.name === "Institution" ? "mailto:hello@topiome.com" : "/register"}
                    className={cn(
                      "mt-6 flex h-10 items-center justify-center rounded-xl text-xs font-medium transition",
                      plan.featured
                        ? "bg-acid text-ink hover:bg-[#d6ff6a]"
                        : "border border-line text-bone hover:border-[#3a4d41]",
                    )}
                  >
                    {plan.name === "Institution" ? "Talk to us" : "Start free"}
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="relative overflow-hidden py-24">
          <div className="pointer-events-none absolute inset-0 spot-grid opacity-40" />
          <div className="container-page relative text-center">
            <Sparkles className="mx-auto size-5 text-acid" />
            <h2 className="display mx-auto mt-5 max-w-3xl text-5xl text-bone sm:text-6xl">
              See your tissue as a map.
            </h2>
            <p className="mx-auto mt-4 max-w-lg text-sm leading-relaxed text-bone-dim">
              Start with the synthetic breast sample, explore every layer, then bring your own
              Visium data.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <DemoButton>Launch the demo</DemoButton>
              <Link
                href="mailto:hello@topiome.com"
                className="inline-flex h-12 items-center gap-2 rounded-xl border border-line px-5 text-sm text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
              >
                <Users className="size-4" />
                Talk to the team
              </Link>
            </div>
            <RuoNotice className="mx-auto mt-10 max-w-2xl text-left" />
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
