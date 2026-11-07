import { ArrowDownRight, MapPinned } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function AtlasVisual() {
  return (
    <div className="relative">
      <div className="absolute -inset-8 -z-10 rounded-full bg-teal/10 blur-3xl" />
      <section className="overflow-hidden rounded-2xl border border-line bg-white shadow-[0_24px_64px_-32px_rgba(25,55,42,0.24)]" aria-label="Public glioblastoma sample analysis summary">
        <header className="flex items-center justify-between gap-4 border-b border-line px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="flex size-9 items-center justify-center rounded-xl border border-teal/20 bg-teal/5 text-teal">
              <MapPinned className="size-4" />
            </span>
            <div>
              <p className="text-sm font-semibold text-bone">Public GBM · GSE331374</p>
              <p className="mt-0.5 font-mono text-[10px] text-slate">GSM9744831 · Visium · primary tumor</p>
            </div>
          </div>
          <Badge variant="amber">Exploratory · pack beta</Badge>
        </header>

        <div className="grid grid-cols-2 gap-3 p-5 sm:grid-cols-4">
          {[
            { label: "Tissue spots", value: "2,930" },
            { label: "QC passed", value: "2,727" },
            { label: "Genes", value: "36,601" },
            { label: "LR pairs tested", value: "9 / 10" },
          ].map((metric) => (
            <div key={metric.label} className="rounded-xl border border-line bg-paper p-3.5">
              <p className="text-[10px] font-medium uppercase tracking-[0.1em] text-slate">{metric.label}</p>
              <p className="mt-2 font-mono text-xl text-bone">{metric.value}</p>
            </div>
          ))}
        </div>

        <div className="mx-5 mb-5 rounded-xl border border-amber/25 bg-amber/[0.06] p-4">
          <div className="flex items-start gap-3">
            <ArrowDownRight className="mt-0.5 size-4 shrink-0 text-amber" />
            <div>
              <p className="text-xs font-semibold text-bone">Limitations remain visible</p>
              <p className="mt-1 text-xs leading-relaxed text-slate">
                Marker-score composition (no matched single-cell reference); weak correspondence to Ivy GAP zones. No ligand–receptor pair passed the current significance threshold.
              </p>
            </div>
          </div>
        </div>

        <footer className="border-t border-line px-5 py-3 text-[10px] leading-relaxed text-slate">
          Public research data · exploratory RUO output · not validated for clinical use.
        </footer>
      </section>

      <div className="absolute -bottom-4 -left-3 hidden rounded-xl border border-line bg-white px-3 py-2 shadow-lg sm:block">
        <p className="text-[9px] font-medium uppercase tracking-[0.12em] text-slate">Spatial uncertainty</p>
        <p className="mt-1 font-mono text-xs text-bone">Shown per spot in the viewer</p>
      </div>
    </div>
  );
}
