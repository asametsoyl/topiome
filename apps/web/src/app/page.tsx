import Link from "next/link";
import {
  ArrowDown,
  ArrowRight,
  Atom,
  CircleHelp,
  Dna,
  FlaskConical,
  GitBranch,
  ShieldCheck,
  Waypoints,
} from "lucide-react";
import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";
import { RuoNotice } from "@/components/ui/ruo-notice";

const researchGoals = [
  {
    icon: Dna,
    number: "01",
    title: "Model an intervention",
    body: "Estimate how a defined genetic perturbation may change a measured cellular state.",
  },
  {
    icon: Waypoints,
    number: "02",
    title: "Test transfer",
    body: "Measure what holds when the perturbation or cellular context was not seen during training.",
  },
  {
    icon: ShieldCheck,
    number: "03",
    title: "Show the limits",
    body: "Report uncertainty, unsupported contexts, data provenance, and baseline comparisons with every result.",
  },
];

const validationSteps = [
  "Start with public perturbation measurements and documented data rights.",
  "Lock splits by perturbation and biological context before model selection.",
  "Compare against no-change, mean-response, and simple statistical baselines.",
  "Require independent experimental results before making biological claims.",
];

function ResponseConcept() {
  const control = [18, 30, 24, 42, 28, 35, 16, 30, 47, 25, 37, 21, 42, 31, 18, 36, 27, 45, 20, 32, 39, 23, 34, 17];
  const perturbed = [24, 18, 39, 30, 46, 21, 33, 44, 20, 36, 27, 48, 19, 40, 28, 22, 45, 31, 37, 18, 43, 26, 34, 20];
  return (
    <div className="relative overflow-hidden rounded-[28px] border border-line bg-white p-5 shadow-[0_24px_80px_rgba(30,60,43,0.09)] sm:p-7">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[#73a98c] via-[#9ac4a8] to-[#d6b078]" />
      <div className="flex items-start justify-between gap-3 border-b border-line-soft pb-5">
        <div>
          <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-slate">Research concept</p>
          <h2 className="mt-1 text-sm font-medium text-bone">Perturbation response</h2>
        </div>
        <span className="rounded-full border border-amber/30 bg-amber/[0.07] px-2.5 py-1 font-mono text-[9px] uppercase tracking-wide text-amber">Illustrative · not a result</span>
      </div>

      <div className="mt-6 grid grid-cols-[1fr_auto_1fr] items-center gap-3 sm:gap-5">
        <div className="rounded-2xl border border-line-soft bg-[#fafcfb] p-3 sm:p-4">
          <p className="font-mono text-[9px] uppercase tracking-[0.13em] text-slate">Baseline</p>
          <p className="mt-1 text-xs font-medium text-bone">Control cells</p>
          <div className="mt-4 grid grid-cols-6 gap-1.5" aria-label="Illustrative control state visualization">
            {control.map((value, index) => (
              <span key={index} className="aspect-square rounded-full" style={{ backgroundColor: `rgba(69, 130, 99, ${value / 60})` }} />
            ))}
          </div>
        </div>
        <ArrowRight className="size-4 text-slate" aria-hidden="true" />
        <div className="rounded-2xl border border-[#e6d9c4] bg-[#fdfaf5] p-3 sm:p-4">
          <p className="font-mono text-[9px] uppercase tracking-[0.13em] text-amber">Intervention</p>
          <p className="mt-1 text-xs font-medium text-bone">Defined perturbation</p>
          <div className="mt-4 grid grid-cols-6 gap-1.5" aria-label="Illustrative perturbation state visualization">
            {perturbed.map((value, index) => (
              <span key={index} className="aspect-square rounded-full" style={{ backgroundColor: `rgba(182, 126, 53, ${value / 60})` }} />
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl bg-[#f4f7f4] px-3.5 py-3">
        <div className="flex items-center gap-2 text-[10px] text-bone-dim">
          <Atom className="size-3.5 text-teal" />
          <span>Response distribution + uncertainty</span>
        </div>
        <span className="font-mono text-[9px] text-slate">Concept only · no model output</span>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-ink">
      <SiteHeader />
      <main>
        <section className="relative overflow-hidden border-b border-line bg-[#f8faf8]">
          <div className="pointer-events-none absolute -right-40 -top-24 size-[560px] rounded-full bg-[#dcebe0]/70 blur-[100px]" />
          <div className="container-page relative grid gap-12 py-16 md:py-24 lg:grid-cols-[0.92fr_1.08fr] lg:items-center lg:gap-14 lg:py-28">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <span className="inline-flex items-center gap-2 rounded-full border border-teal/20 bg-teal/[0.06] px-3 py-1.5 font-mono text-[9px] uppercase tracking-[0.15em] text-teal">
                  <span className="size-1.5 rounded-full bg-teal" />
                  Perturbation response research
                </span>
                <span className="font-mono text-[9px] uppercase tracking-[0.15em] text-slate">RUO</span>
              </div>
              <h1 className="display mt-7 max-w-2xl text-[3.25rem] text-bone sm:text-6xl lg:text-[72px]">
                What changes when a cell is <span className="text-teal">perturbed?</span>
              </h1>
              <p className="mt-6 max-w-xl text-sm leading-7 text-bone-dim sm:text-base sm:leading-8">
                Topiome is beginning a research program to predict cellular responses to defined genetic interventions — and to test those predictions on perturbations and contexts the model has not seen.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link href="#research" className="inline-flex h-11 items-center gap-2 rounded-xl bg-teal px-4.5 text-xs font-medium text-white transition hover:bg-[#125f50]">
                  Explore the research <ArrowDown className="size-3.5" />
                </Link>
                <Link href="/docs" className="inline-flex h-11 items-center gap-2 rounded-xl border border-line bg-white px-4.5 text-xs text-bone-dim transition hover:border-teal/40 hover:text-bone">
                  Read the validation plan
                </Link>
              </div>
              <div className="mt-8 flex items-center gap-2 border-t border-line pt-5 text-[10px] text-slate">
                <CircleHelp className="size-3.5 text-amber" />
                <span>Research direction in development. No validated prediction model is available yet.</span>
              </div>
            </div>
            <ResponseConcept />
          </div>
        </section>

        <section id="research" className="scroll-mt-24 border-b border-line py-20 md:py-24">
          <div className="container-page">
            <div className="max-w-2xl">
              <p className="mono-label">The scientific question</p>
              <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">Move from describing cells to testing interventions.</h2>
              <p className="mt-5 text-sm leading-7 text-bone-dim">
                Single-cell perturbation experiments reveal how cells respond to gene knockdown, activation, or other defined interventions. Measuring every intervention in every context is expensive. The research question is whether computational models can predict useful responses beyond the experiments used to build them.
              </p>
            </div>
            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {researchGoals.map((item) => {
                const Icon = item.icon;
                return (
                  <article key={item.number} className="card p-6">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[10px] text-slate">{item.number}</span>
                      <Icon className="size-4 text-teal" />
                    </div>
                    <h3 className="mt-7 text-sm font-medium text-bone">{item.title}</h3>
                    <p className="mt-2 text-xs leading-6 text-bone-dim">{item.body}</p>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section id="method" className="scroll-mt-24 border-b border-line bg-white py-20 md:py-24">
          <div className="container-page grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
            <div>
              <p className="mono-label">Evidence before confidence</p>
              <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">A prediction only matters if it survives a hard test.</h2>
              <p className="mt-5 text-sm leading-7 text-bone-dim">
                Randomly holding out cells can leak the same biological context into training and testing. We will separate entire perturbations and contexts, compare simple baselines, and keep independent experiments as the final scientific gate.
              </p>
              <Link href="/docs" className="mt-6 inline-flex items-center gap-2 text-xs font-medium text-teal hover:text-[#125f50]">
                See the proposed evaluation <ArrowRight className="size-3.5" />
              </Link>
            </div>
            <ol className="space-y-3">
              {validationSteps.map((step, index) => (
                <li key={step} className="flex gap-4 rounded-2xl border border-line-soft bg-[#fbfcfb] p-4 sm:p-5">
                  <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-[#eaf2ec] font-mono text-[10px] text-teal">{index + 1}</span>
                  <p className="pt-1 text-xs leading-6 text-bone-dim">{step}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="status" className="scroll-mt-24 border-b border-line py-20 md:py-24">
          <div className="container-page">
            <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
              <div className="max-w-2xl">
                <p className="mono-label">Current status</p>
                <h2 className="display mt-4 text-4xl text-bone sm:text-5xl">A research program, not a finished product.</h2>
              </div>
              <p className="max-w-md text-xs leading-6 text-bone-dim">An initial public perturbation dataset is curated and simple baselines are being measured. Prospective biological validation will require an experimental research partner.</p>
            </div>
            <div className="mt-9 grid gap-3 sm:grid-cols-3">
              {[
                { title: "Public data", state: "Initial set curated", icon: FlaskConical },
                { title: "Prediction benchmark", state: "Baseline stage", icon: GitBranch },
                { title: "Independent experiments", state: "Partner required", icon: ShieldCheck },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.title} className="flex items-start gap-3 rounded-2xl border border-line bg-white p-5">
                    <span className="flex size-9 items-center justify-center rounded-xl bg-[#edf4ef] text-teal"><Icon className="size-4" /></span>
                    <div>
                      <p className="text-xs font-medium text-bone">{item.title}</p>
                      <p className="mt-1 font-mono text-[10px] text-slate">{item.state}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-7 max-w-3xl"><RuoNotice /></div>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/docs" className="inline-flex h-10 items-center gap-2 rounded-xl border border-line bg-white px-4 text-xs text-bone-dim hover:border-teal/40 hover:text-bone">Research and validation plan <ArrowRight className="size-3.5" /></Link>
              <a href="mailto:hello@topiome.com?subject=Topiome%20research%20collaboration" className="inline-flex h-10 items-center rounded-xl px-3 text-xs text-teal hover:bg-teal/[0.05]">Discuss a research collaboration</a>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
