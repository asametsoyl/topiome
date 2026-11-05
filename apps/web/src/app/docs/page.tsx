import Link from "next/link";
import { ArrowUpRight, Check, CircleDot } from "lucide-react";
import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";
import { DemoButton } from "@/components/marketing/demo-button";
import { Badge } from "@/components/ui/badge";
import { RuoNotice } from "@/components/ui/ruo-notice";

const nav = [
  { href: "#overview", label: "Overview" },
  { href: "#data", label: "Data formats" },
  { href: "#pipeline", label: "Pipeline" },
  { href: "#validation", label: "Validation" },
  { href: "#packs", label: "Disease packs" },
  { href: "#reproducibility", label: "Reproducibility" },
  { href: "#limitations", label: "Limitations" },
  { href: "#ruo", label: "RUO policy" },
];

const metrics = [
  ["Composition JSD", "0.099", "< 0.20", "< 0.12", "Pass"],
  ["Dominant-type Pearson", "0.862", "> 0.75", "> 0.85", "Pass"],
  ["Composition RMSE", "0.017", "—", "—", "Reported"],
  ["Domain ARI", "0.634", "> 0.35", "> 0.55", "Pass"],
  ["Domain NMI", "0.783", "—", "—", "Reported"],
  ["QC pass rate", "100%", "> 90%", "> 95%", "Pass"],
];

const packs = [
  ["Breast", "beta", "High", "10", "6", "6", "0.099", "0.862", "0.634"],
  ["Colorectal", "beta", "High", "9", "6", "5", "0.098", "0.907", "0.623"],
  ["Lung", "draft", "High", "8", "6", "6", "0.089", "0.951", "0.655"],
  ["Melanoma", "draft", "Medium", "8", "5", "6", "0.085", "0.945", "0.966"],
  ["Prostate", "draft", "Medium", "9", "5", "6", "0.099", "0.889", "0.967"],
  ["Glioblastoma", "beta", "Medium", "7", "5", "6", "0.076", "0.851", "0.602"],
];

export default function DocsPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main>
        <section className="border-b border-line py-14">
          <div className="container-page">
            <Badge variant="teal">Documentation</Badge>
            <h1 className="display mt-5 max-w-3xl text-5xl text-bone sm:text-6xl">
              Method, metrics, and honest limits.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-relaxed text-bone-dim">
              This page documents what Topiome computes, how it is benchmarked, and where it
              should not be used. The short version: research use only, uncertainty visible,
              validation before claims.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <DemoButton size="md">Open a live run</DemoButton>
              <Link
                href="/pricing"
                className="inline-flex h-10 items-center gap-2 rounded-xl border border-line px-4 text-xs text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
              >
                Pricing
                <ArrowUpRight className="size-3.5" />
              </Link>
            </div>
          </div>
        </section>

        <div className="container-page grid gap-10 py-12 lg:grid-cols-[220px_1fr]">
          <aside className="hidden lg:block">
            <nav className="sticky top-24 space-y-1">
              {nav.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  className="block rounded-lg px-3 py-2 text-xs text-slate transition hover:bg-bone/5 hover:text-bone"
                >
                  {item.label}
                </a>
              ))}
            </nav>
          </aside>

          <div className="min-w-0 space-y-16">
            <section id="overview" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">Overview</h2>
              <div className="mt-4 space-y-4 text-sm leading-relaxed text-bone-dim">
                <p>
                  Topiome is a multi-tenant web application with a Python analysis service. A
                  run takes a spatial transcriptomics sample and a versioned disease pack, then
                  produces a JSON result payload, a spatial viewer, and a self-contained HTML
                  report.
                </p>
                <p>
                  The platform core is disease-agnostic. Disease knowledge — cell types,
                  markers, zones, target genes, report sections — lives in YAML packs. A pack
                  cannot be marked <span className="font-mono text-teal">validated</span> until
                  its benchmark thresholds and expert review are complete.
                </p>
              </div>
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                {[
                  ["Core", "Disease-agnostic pipeline"],
                  ["Packs", "Versioned YAML knowledge"],
                  ["Output", "Result JSON + HTML report"],
                ].map(([k, v]) => (
                  <div key={k} className="card p-4">
                    <p className="mono-label">{k}</p>
                    <p className="mt-2 text-xs text-bone-dim">{v}</p>
                  </div>
                ))}
              </div>
            </section>

            <section id="data" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">Data formats</h2>
              <p className="mt-3 text-sm leading-relaxed text-bone-dim">
                Phase 1 accepts 10x Visium Space Ranger output as a folder or zip. The loader
                checks for the required files, matches barcodes to tissue positions, and keeps
                only spots with finite coordinates.
              </p>
              <pre className="mt-5 overflow-x-auto rounded-xl border border-line bg-ink-2 p-4 font-mono text-[11px] leading-relaxed text-bone-dim">
{`sample/
├── matrix.mtx.gz
├── barcodes.tsv.gz
├── features.tsv.gz
├── tissue_positions.csv
├── scalefactors_json.json
└── tissue_hires_image.png   (optional)

reference.h5ad                (optional)
└── obs["cell_type"]          required for reference-based deconvolution`}
              </pre>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-line bg-ink-2 p-4">
                  <p className="text-xs font-medium text-bone">No reference?</p>
                  <p className="mt-1.5 text-xs leading-relaxed text-slate">
                    Topiome falls back to a marker-score composition and labels the run
                    <span className="font-mono text-amber"> method=marker_score</span>. It is
                    not full deconvolution and is treated as such in the report.
                  </p>
                </div>
                <div className="rounded-xl border border-line bg-ink-2 p-4">
                  <p className="text-xs font-medium text-bone">Minimum sample size</p>
                  <p className="mt-1.5 text-xs leading-relaxed text-slate">
                    Runs below 100 spots are rejected; below 500 spots produce a warning. The
                    demo sample uses 1,200 synthetic spots.
                  </p>
                </div>
              </div>
            </section>

            <section id="pipeline" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">Pipeline</h2>
              <div className="mt-5 space-y-3">
                {[
                  {
                    n: "01",
                    title: "QC",
                    body: "Per-spot total counts, detected genes, and mitochondrial fraction. Failed spots are flagged, not silently deleted. If fewer than 50 spots pass, modeling continues on all spots with an explicit warning.",
                  },
                  {
                    n: "02",
                    title: "Normalization",
                    body: "Library-size normalization to 10,000 counts per spot. NNLS uses the linear scale; marker scores and target ranking use log1p.",
                  },
                  {
                    n: "03",
                    title: "Deconvolution",
                    body: "Non-negative least squares per spot against reference signatures. Signatures are built from library-size-normalized reference cells, averaged by cell type, and row-scaled. Output: a composition vector and a relative residual for every spot.",
                  },
                  {
                    n: "04",
                    title: "Spatial smoothing",
                    body: "A k-nearest-neighbor graph over spot coordinates smooths the composition (default k=6, alpha=0.45), preserving boundaries while reducing speckle.",
                  },
                  {
                    n: "05",
                    title: "Domains",
                    body: "KMeans on smoothed composition plus a small coordinate term. Each cluster is labeled by the disease pack's zone marker scores; clusters are one-to-one where possible.",
                  },
                  {
                    n: "06",
                    title: "Target scoring",
                    body: "For each pack target gene, a scaled expression score overall, by domain, and by cell type. Evidence level (established / emerging / exploratory) comes from the pack.",
                  },
                  {
                    n: "07",
                    title: "Uncertainty",
                    body: "Per-spot uncertainty combines normalized entropy of the composition (65%) with the NNLS relative residual (35%). Values are shown on the map and in the report.",
                  },
                  {
                    n: "08",
                    title: "Report",
                    body: "A self-contained HTML report with the domain map, composition, domain summary, target evidence, QC, benchmark metrics, warnings, versions, and the RUO notice.",
                  },
                ].map((step) => (
                  <div key={step.n} className="card p-5">
                    <div className="flex items-baseline gap-3">
                      <span className="font-mono text-[10px] text-acid">{step.n}</span>
                      <h3 className="text-sm font-medium text-bone">{step.title}</h3>
                    </div>
                    <p className="mt-2 pl-7 text-xs leading-relaxed text-slate">{step.body}</p>
                  </div>
                ))}
              </div>
            </section>

            <section id="validation" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">Validation</h2>
              <p className="mt-3 text-sm leading-relaxed text-bone-dim">
                The table below is the current synthetic benchmark for the breast pack: 1,200
                pseudospots generated from reference profiles with known composition and zone
                labels. It tests the estimator, not clinical performance.
              </p>

              <div className="mt-5 overflow-x-auto rounded-xl border border-line">
                <table className="w-full min-w-[640px] text-left text-xs">
                  <thead className="border-b border-line bg-ink-2">
                    <tr className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                      <th className="px-4 py-3 font-normal">Metric</th>
                      <th className="px-4 py-3 font-normal">Current</th>
                      <th className="px-4 py-3 font-normal">Minimum</th>
                      <th className="px-4 py-3 font-normal">Target</th>
                      <th className="px-4 py-3 font-normal">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.map(([name, current, min, target, status]) => (
                      <tr key={name} className="border-b border-line-soft last:border-0">
                        <td className="px-4 py-3 text-bone-dim">{name}</td>
                        <td className="px-4 py-3 font-mono text-bone">{current}</td>
                        <td className="px-4 py-3 font-mono text-slate">{min}</td>
                        <td className="px-4 py-3 font-mono text-slate">{target}</td>
                        <td className="px-4 py-3">
                          <span
                            className={
                              status === "Pass"
                                ? "font-mono text-[10px] uppercase tracking-wider text-teal"
                                : "font-mono text-[10px] uppercase tracking-wider text-slate"
                            }
                          >
                            {status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-5 rounded-xl border border-amber/25 bg-amber/[0.06] p-4">
                <p className="text-xs font-medium text-amber">What this does not prove</p>
                <p className="mt-1.5 text-xs leading-relaxed text-amber/80">
                  Synthetic pseudospots share the reference profiles used by the estimator, so
                  they measure numerical recovery, not biological generalization. A pack is not
                  validated until it passes held-out samples from independent studies, marker
                  enrichment, calibration, stability, and expert review.
                </p>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {[
                  ["Pseudospot", "Known composition; JSD, RMSE, dominant-type correlation."],
                  ["Held-out", "Independent studies; ARI/NMI where annotations exist."],
                  ["Calibration", "Do 0.9-confidence spots match ~90% accuracy?"],
                  ["Stability", "Downsampling and noise perturbation; coefficient of variation."],
                ].map(([title, body]) => (
                  <div key={title} className="flex gap-2.5 rounded-xl border border-line bg-ink-2 p-4">
                    <CircleDot className="mt-0.5 size-3.5 shrink-0 text-teal" />
                    <div>
                      <p className="text-xs font-medium text-bone">{title}</p>
                      <p className="mt-1 text-xs leading-relaxed text-slate">{body}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section id="packs" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">Disease packs</h2>
              <p className="mt-3 text-sm leading-relaxed text-bone-dim">
                Six data-rich cancers are in the initial set. Status is deliberately
                conservative: a pack stays beta or draft until its validation gate is complete.
                The numbers are the same synthetic benchmark, run per pack.
              </p>

              <div className="mt-5 overflow-x-auto rounded-xl border border-line">
                <table className="w-full min-w-[760px] text-left text-xs">
                  <thead className="border-b border-line bg-ink-2">
                    <tr className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                      <th className="px-4 py-3 font-normal">Pack</th>
                      <th className="px-4 py-3 font-normal">Status</th>
                      <th className="px-4 py-3 font-normal">Data</th>
                      <th className="px-4 py-3 font-normal">Cells</th>
                      <th className="px-4 py-3 font-normal">Zones</th>
                      <th className="px-4 py-3 font-normal">Targets</th>
                      <th className="px-4 py-3 font-normal">JSD</th>
                      <th className="px-4 py-3 font-normal">r</th>
                      <th className="px-4 py-3 font-normal">ARI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {packs.map((row) => (
                      <tr key={row[0]} className="border-b border-line-soft last:border-0">
                        {row.map((cell, index) => (
                          <td
                            key={index}
                            className={
                              index === 1
                                ? "px-4 py-3 font-mono text-[10px] uppercase tracking-wider text-teal"
                                : index >= 5
                                  ? "px-4 py-3 font-mono text-bone-dim"
                                  : "px-4 py-3 text-bone-dim"
                            }
                          >
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="mt-3 text-[11px] text-slate">
                Status reflects validation maturity, not regulatory clearance. All packs are
                Research Use Only.
              </p>
            </section>

            <section id="reproducibility" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">Reproducibility</h2>
              <p className="mt-3 text-sm leading-relaxed text-bone-dim">
                Every run stores the pipeline version, disease pack version, parameters, stage
                timestamps, and a summary. Results and reports are written to object storage and
                linked to the run. Re-running creates a new run rather than overwriting history.
              </p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {[
                  ["Pipeline", "topiome-analysis 0.1.0-baseline"],
                  ["Pack", "disease pack id + SemVer, pinned per run"],
                  ["Parameters", "JSON, stored with the run"],
                  ["Artifacts", "results.json, report.html, error.log"],
                ].map(([k, v]) => (
                  <div key={k} className="flex items-start gap-2.5 rounded-xl border border-line bg-ink-2 p-4">
                    <Check className="mt-0.5 size-3.5 shrink-0 text-teal" />
                    <div>
                      <p className="text-xs font-medium text-bone">{k}</p>
                      <p className="mt-1 font-mono text-[10px] text-slate">{v}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section id="limitations" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">Limitations</h2>
              <ul className="mt-4 space-y-2.5">
                {[
                  "Cell-type deconvolution is an inference from bulk spot expression; it is not single-cell ground truth.",
                  "Spatial domains are computational regions labeled by marker scores; they are not pathological diagnoses.",
                  "Reference atlas coverage limits what can be distinguished. Unknown cell states are forced into known types.",
                  "Spots with low counts, high mitochondrial fraction, or high residual have less reliable composition.",
                  "Phase 1 supports Visium only. Visium HD, Xenium, and CosMx require different pipelines.",
                  "Synthetic benchmarks measure numerical recovery, not clinical or biological validity.",
                  "Results require independent validation before any research or clinical decision.",
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-xs leading-relaxed text-bone-dim">
                    <CircleDot className="mt-0.5 size-3.5 shrink-0 text-amber" />
                    {item}
                  </li>
                ))}
              </ul>
            </section>

            <section id="ruo" className="scroll-mt-24">
              <h2 className="display text-3xl text-bone">RUO policy</h2>
              <div className="mt-4">
                <RuoNotice />
              </div>
              <p className="mt-4 text-xs leading-relaxed text-slate">
                Topiome is a research tool. It is not a medical device, not a diagnostic, and
                not a substitute for pathologist review. Clinical use requires a separate
                product line, quality management system, and regulatory pathway. Read the full{" "}
                <Link href="/legal/ruo" className="text-acid underline decoration-acid/30 underline-offset-2">
                  RUO policy
                </Link>
                .
              </p>
            </section>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
