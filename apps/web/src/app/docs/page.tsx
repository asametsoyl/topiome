import Link from "next/link";
import { ArrowLeft, ArrowRight, Database, GitBranch, ShieldCheck } from "lucide-react";
import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";
import { RuoNotice } from "@/components/ui/ruo-notice";

const gates = [
  ["Task definition", "State exactly what the model receives and predicts: control-cell context, perturbation identity, assay, and response endpoint."],
  ["Leakage-resistant splits", "Hold out whole perturbations or cell contexts. Never split individual cells randomly across train and test when they share the same experiment."],
  ["Strong simple baselines", "Compare against no-change, mean-response, and linear/additive models before adding graph or foundation-model complexity."],
  ["Biological metrics", "Evaluate perturbation-effect correlation, top differentially expressed genes, pathway consistency, distributional response, and calibrated uncertainty."],
  ["Independent experiments", "Public held-out datasets measure computational generalization. They do not replace newly generated experiments for prospective validation."],
];

export default function DocsPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main>
        <section className="border-b border-line bg-[#f8faf8] py-14 md:py-20">
          <div className="container-page max-w-4xl">
            <Link href="/" className="inline-flex items-center gap-2 text-[11px] text-slate hover:text-teal"><ArrowLeft className="size-3.5" /> Home</Link>
            <p className="mono-label mt-7">Research plan · v0.1</p>
            <h1 className="display mt-4 text-5xl text-bone sm:text-6xl">Predicting cellular perturbation responses.</h1>
            <p className="mt-5 max-w-2xl text-sm leading-7 text-bone-dim">
              This page describes the research direction and proposed evaluation. Topiome has not yet trained or validated a perturbation-response model.
            </p>
          </div>
        </section>

        <section className="border-b border-line py-14 md:py-18">
          <div className="container-page grid gap-12 lg:grid-cols-[0.72fr_1.28fr]">
            <div>
              <p className="mono-label">Question</p>
              <h2 className="display mt-4 text-3xl text-bone sm:text-4xl">Can a model predict an intervention it has not seen?</h2>
            </div>
            <div className="space-y-4 text-sm leading-7 text-bone-dim">
              <p>Single-cell perturbation experiments measure how cells respond to defined genetic or chemical interventions. A useful model must predict responses in held-out perturbations or biological contexts, rather than reconstruct examples that resemble its training data.</p>
              <p>The first scope is intentionally narrow: computational prediction of research assay readouts. It is not a virtual organism, a causal mechanism oracle, or a source of treatment recommendations.</p>
            </div>
          </div>
        </section>

        <section id="data" className="scroll-mt-24 border-b border-line bg-white py-14 md:py-18">
          <div className="container-page grid gap-8 md:grid-cols-[0.7fr_1.3fr]">
            <div>
              <p className="mono-label">Data</p>
              <h2 className="display mt-4 text-3xl text-bone sm:text-4xl">Start with experiments already measured.</h2>
            </div>
            <div className="space-y-4">
              <article className="rounded-2xl border border-line-soft bg-[#fbfcfb] p-5">
                <div className="flex items-center gap-2 text-xs font-medium text-bone"><Database className="size-4 text-teal" /> Arc Virtual Cell Atlas</div>
                <p className="mt-2 text-xs leading-6 text-bone-dim">The initial local benchmark uses Arc VCC 2025 H1 hESC CRISPRi data as PIE-preprocessed aggregate effects: 146 training perturbations and 44 held-out perturbations. The original VCC 2025 component is listed as CC0 by Arc; source, checksums, and the limits of the processed mirror are recorded for this experiment.</p>
                <p className="mt-3 text-xs leading-6 text-bone-dim">Later benchmarks use PIE Replogle-Nadig (four cell lines) and PIE X-Atlas/Orion (HCT116 and HEK293T). A simple scaled-transfer baseline passed a pre-registered unseen-context gate on three Replogle-Nadig cell lines, but the independent Orion replication failed the numeric gate in both folds. That line is stopped; the in-dataset result is not presented as independent replication.</p>
                <a className="mt-3 inline-flex items-center gap-1.5 text-[11px] text-teal hover:text-[#125f50]" href="https://arcinstitute.org/tools/virtualcellatlas" target="_blank" rel="noreferrer">Open the data catalog <ArrowRight className="size-3" /></a>
                <a className="ml-4 mt-3 inline-flex items-center gap-1.5 text-[11px] text-teal hover:text-[#125f50]" href="https://huggingface.co/datasets/arcinstitute/PIE_arc_vcc_25" target="_blank" rel="noreferrer">Open the processed dataset card <ArrowRight className="size-3" /></a>
              </article>
              <p className="text-xs leading-6 text-slate">This first subset contains aggregate pseudobulk effects from a single H1 cell line. It tests unseen perturbation targets only; it does not test a new cell context or predict single-cell response distributions. The validation labels are available publicly and do not constitute independent experimental confirmation.</p>
            </div>
          </div>
        </section>

        <section id="benchmark" className="scroll-mt-24 border-b border-line py-14 md:py-18">
          <div className="container-page">
            <p className="mono-label">Evaluation protocol</p>
            <h2 className="display mt-4 max-w-2xl text-3xl text-bone sm:text-4xl">No random-cell split. No unchallenged model claims.</h2>
            <div className="mt-8 grid gap-3 md:grid-cols-2">
              {gates.map(([title, body], index) => (
                <article key={title} className="flex gap-4 rounded-2xl border border-line bg-white p-5">
                  <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-[#edf4ef] font-mono text-[10px] text-teal">0{index + 1}</span>
                  <div>
                    <h3 className="text-xs font-medium text-bone">{title}</h3>
                    <p className="mt-1.5 text-xs leading-6 text-bone-dim">{body}</p>
                  </div>
                </article>
              ))}
            </div>
            <p className="mt-5 flex items-start gap-2 text-[11px] leading-6 text-slate"><GitBranch className="mt-1 size-3.5 shrink-0 text-teal" /> Exact splits, preprocessing, software versions, and metrics will be published before comparing candidate models. A benchmark result is not evidence of prospective experimental utility.</p>
          </div>
        </section>

        <section id="limits" className="scroll-mt-24 border-b border-line bg-[#f8faf8] py-14 md:py-18">
          <div className="container-page grid gap-8 lg:grid-cols-[0.7fr_1.3fr]">
            <div>
              <p className="mono-label">Limits and status</p>
              <h2 className="display mt-4 text-3xl text-bone sm:text-4xl">What this research cannot claim yet.</h2>
            </div>
            <ul className="space-y-3 text-xs leading-6 text-bone-dim">
              <li className="rounded-xl border border-line bg-white p-4">No perturbation-response model has been trained or validated by Topiome.</li>
              <li className="rounded-xl border border-line bg-white p-4">Public benchmark success does not establish causal mechanism, disease translation, or experimental benefit.</li>
              <li className="rounded-xl border border-line bg-white p-4">Predictions depend on perturbation efficiency, cell context, assay, time point, dose, and data quality.</li>
              <li className="rounded-xl border border-line bg-white p-4">Prospective claims require an independent experimental partner and pre-specified readouts.</li>
            </ul>
          </div>
        </section>

        <section className="py-14">
          <div className="container-page max-w-4xl">
            <RuoNotice />
            <p className="mt-5 flex items-start gap-2 text-[11px] leading-6 text-slate"><ShieldCheck className="mt-1 size-3.5 shrink-0 text-teal" /> Historical spatial-transcriptomics code and results remain archived as legacy research. They are not evidence for the new perturbation-response direction.</p>
            <Link href="/pricing" className="mt-6 inline-flex items-center gap-2 text-xs text-teal hover:text-[#125f50]">Research preview status <ArrowRight className="size-3.5" /></Link>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
