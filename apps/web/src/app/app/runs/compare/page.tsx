"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useMemo } from "react";
import {
  ArrowLeftRight,
  ArrowUpRight,
  ChevronRight,
  GitCompareArrows,
  Info,
  TriangleAlert,
} from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { NotAssessedNotice } from "@/components/app/run-insights";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/progress";
import { RuoNotice } from "@/components/ui/ruo-notice";
import { apiClient } from "@/lib/api";
import type {
  CompareRunSide,
  CompositionDelta,
  DomainShare,
  InteractionCompare,
  InteractionSide,
  RunComparison,
} from "@/lib/types";
import { cn, formatDateTime, formatNumber, formatPercent, titleCase } from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

// Fixed side colours: A is teal, B is acid. Labels are always printed too.
const sideTone = {
  A: { text: "text-teal", bar: "bg-teal", badge: "teal" },
  B: { text: "text-acid", bar: "bg-acid", badge: "acid" },
} as const;

function signed(value: number, digits = 1) {
  const fixed = Math.abs(value).toFixed(digits);
  if (Number(fixed) === 0) return fixed;
  return `${value > 0 ? "+" : "−"}${fixed}`;
}

function formatQ(value: number | null) {
  if (value === null) return "—";
  return value < 0.001 ? "<0.001" : value.toFixed(3);
}

function SideBadge({ label }: { label: "A" | "B" }) {
  return (
    <Badge variant={sideTone[label].badge} className="px-1.5">
      {label}
    </Badge>
  );
}

function RunSideCard({ side }: { side: CompareRunSide }) {
  const agreementLow = side.method_agreement !== null && side.method_agreement < 0.7;
  const rows: Array<[string, React.ReactNode]> = [
    ["Disease pack", `${side.pack_name} · ${side.pack_version}`],
    ["Pipeline", side.pipeline_version],
    ["Spots modeled", `${formatNumber(side.modeled_spots)} of ${formatNumber(side.n_spots)}`],
    ["Domains · cell types", `${side.n_domains} · ${side.n_cell_types}`],
    [
      "Method agreement",
      side.method_agreement === null ? (
        "n/a"
      ) : (
        <span className={agreementLow ? "text-amber" : undefined}>
          {side.method_agreement.toFixed(2)}
          {agreementLow ? " (low)" : ""}
        </span>
      ),
    ],
    [
      "Significant L–R pairs",
      `${side.significant_interactions} of ${side.tested_interactions} tested`,
    ],
    ["Input", side.synthetic ? "Synthetic demo data" : "Uploaded sample"],
    ["Finished", formatDateTime(side.finished_at)],
  ];

  return (
    <Card className="min-w-0">
      <CardHeader
        title={
          <span className="flex items-center gap-2">
            <SideBadge label={side.label} />
            <span className="font-mono">Run {side.run_id.slice(0, 8)}</span>
          </span>
        }
        description={side.sample_name ?? `Sample ${side.sample_id.slice(0, 8)}`}
        action={
          <Link
            href={`/app/runs/${side.run_id}`}
            className="inline-flex shrink-0 items-center gap-1 text-[11px] text-slate transition hover:text-bone"
          >
            Open
            <ArrowUpRight className="size-3" />
          </Link>
        }
      />
      <CardBody className="space-y-2.5">
        {rows.map(([key, value]) => (
          <div key={key} className="flex items-center justify-between gap-3 text-[11px]">
            <span className="text-slate">{key}</span>
            <span className="truncate text-right font-mono text-bone-dim">{value}</span>
          </div>
        ))}
        {side.warnings.length > 0 ? (
          <ul className="space-y-1 border-t border-line pt-3">
            {side.warnings.map((warning) => (
              <li key={warning} className="flex items-start gap-1.5 text-[10px] text-amber/90">
                <TriangleAlert className="mt-0.5 size-3 shrink-0" />
                {warning}
              </li>
            ))}
          </ul>
        ) : null}
      </CardBody>
    </Card>
  );
}

function DeltaBar({ delta, scale }: { delta: number; scale: number }) {
  const width = Math.min(50, (Math.abs(delta) / scale) * 50);
  return (
    <div className="relative h-2 rounded-full bg-ink-3">
      <span className="absolute inset-y-0 left-1/2 w-px bg-line" />
      {delta !== 0 ? (
        <span
          className={cn(
            "absolute inset-y-0 rounded-full",
            delta < 0 ? "right-1/2 bg-teal" : "left-1/2 bg-acid",
          )}
          style={{ width: `${width}%` }}
        />
      ) : null}
    </div>
  );
}

function CompositionCard({ rows }: { rows: CompositionDelta[] }) {
  // At least 5 percentage points full scale, so tiny shifts do not look large.
  const scale = Math.max(0.05, ...rows.map((row) => Math.abs(row.delta ?? 0)));
  return (
    <Card className="min-w-0">
      <CardHeader
        title="Cell-type composition"
        description="Mean proportion across all spots in each run (spots that failed QC count as 0). Bars show B − A."
      />
      <CardBody className="space-y-3">
        <div className="grid grid-cols-[minmax(0,1.2fr)_3.5rem_minmax(0,1.6fr)_3.5rem_3.5rem] items-center gap-3 font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
          <span>Cell type</span>
          <span className="text-right text-teal">A</span>
          <span className="flex justify-between normal-case tracking-normal">
            <span className="text-teal">← higher in A</span>
            <span className="text-acid">higher in B →</span>
          </span>
          <span className="text-acid">B</span>
          <span className="text-right">Δ pp</span>
        </div>
        {rows.map((row) => (
          <div
            key={row.cell_type}
            className="grid grid-cols-[minmax(0,1.2fr)_3.5rem_minmax(0,1.6fr)_3.5rem_3.5rem] items-center gap-3 text-[11px]"
          >
            <span className="truncate text-bone-dim" title={row.cell_type}>
              {titleCase(row.cell_type)}
            </span>
            <span className="text-right font-mono text-bone-dim">
              {row.a === null ? "—" : formatPercent(row.a)}
            </span>
            {row.delta === null ? (
              <span className="text-center text-[10px] text-slate">
                only in {row.a === null ? "B" : "A"}&apos;s pack
              </span>
            ) : (
              <DeltaBar delta={row.delta} scale={scale} />
            )}
            <span className="font-mono text-bone-dim">
              {row.b === null ? "—" : formatPercent(row.b)}
            </span>
            <span className="text-right font-mono text-slate">
              {row.delta === null ? "—" : signed(row.delta * 100)}
            </span>
          </div>
        ))}
      </CardBody>
    </Card>
  );
}

function ShareCell({ pct, count, label }: { pct: number | null; count: number | null; label: "A" | "B" }) {
  if (pct === null) return <span className="text-[10px] text-slate">not in pack</span>;
  return (
    <div className="space-y-1">
      <div className="flex items-baseline gap-1.5">
        <span className="font-mono text-bone-dim">{pct.toFixed(1)}%</span>
        <span className="font-mono text-[9px] text-slate">{formatNumber(count)}</span>
      </div>
      <div className="h-1 w-full max-w-24 overflow-hidden rounded-full bg-ink-3">
        <div
          className={cn("h-full rounded-full", sideTone[label].bar)}
          style={{ width: `${Math.min(100, pct)}%` }}
        />
      </div>
    </div>
  );
}

function DomainCard({ rows }: { rows: DomainShare[] }) {
  return (
    <Card className="min-w-0">
      <CardHeader
        title="Domain share"
        description="Share of all spots in each domain. Spots that failed QC or matched no zone are Unassigned."
      />
      <CardBody className="overflow-x-auto p-0">
        <table className="w-full min-w-[420px] text-left text-[11px]">
          <thead className="border-b border-line font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
            <tr>
              <th className="px-5 py-2.5 font-normal">Domain</th>
              <th className="px-3 py-2.5 font-normal text-teal">A</th>
              <th className="px-3 py-2.5 font-normal text-acid">B</th>
              <th className="px-5 py-2.5 text-right font-normal">Δ pp</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-line/60 last:border-0">
                <td className="px-5 py-2.5">
                  <span className="flex items-center gap-2 text-bone-dim">
                    <span
                      className="size-2 shrink-0 rounded-full border border-line"
                      style={row.color ? { backgroundColor: row.color } : undefined}
                    />
                    {row.name}
                  </span>
                </td>
                <td className="px-3 py-2.5">
                  <ShareCell pct={row.a_pct} count={row.a_count} label="A" />
                </td>
                <td className="px-3 py-2.5">
                  <ShareCell pct={row.b_pct} count={row.b_count} label="B" />
                </td>
                <td className="px-5 py-2.5 text-right font-mono text-slate">
                  {row.delta_pct === null ? "—" : signed(row.delta_pct)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardBody>
    </Card>
  );
}

function InteractionCell({ side }: { side: InteractionSide | null }) {
  if (side === null) return <span className="text-[10px] text-slate">not in pack</span>;
  if (!side.tested) {
    return (
      <span className="text-[10px] text-slate" title={`Missing: ${side.missing.join(", ")}`}>
        not tested
      </span>
    );
  }
  return (
    <div>
      <p className={cn("font-mono", side.significant ? "text-teal" : "text-slate")}>
        q {formatQ(side.q_value)}
      </p>
      <p className="mt-0.5 font-mono text-[10px] text-slate">
        score {(side.score ?? 0).toFixed(3)}
      </p>
    </div>
  );
}

function significantIn(row: InteractionCompare) {
  const a = row.a?.significant ?? false;
  const b = row.b?.significant ?? false;
  if (a && b) return "A + B";
  if (a) return "A only";
  if (b) return "B only";
  return "—";
}

function CommunicationCard({ rows }: { rows: InteractionCompare[] }) {
  if (rows.length === 0) {
    return (
      <EmptyState
        compact
        title="No ligand–receptor pairs"
        description="Neither disease pack defines curated ligand–receptor pairs yet."
      />
    );
  }
  return (
    <Card>
      <CardHeader
        title="Ligand–receptor pairs"
        description="Each run's own permutation test, BH-corrected within that run. Comparing q-values is not a test of difference between runs."
      />
      <CardBody className="overflow-x-auto p-0">
        <table className="w-full min-w-[640px] text-left text-[11px]">
          <thead className="border-b border-line font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
            <tr>
              <th className="px-5 py-2.5 font-normal">Pair</th>
              <th className="px-3 py-2.5 font-normal">Sender → receiver</th>
              <th className="px-3 py-2.5 font-normal text-teal">A</th>
              <th className="px-3 py-2.5 font-normal text-acid">B</th>
              <th className="px-5 py-2.5 text-right font-normal">q &lt; 0.05 in</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-line/60 last:border-0">
                <td className="px-5 py-2.5">
                  <p className="font-mono text-bone">{row.name}</p>
                  {row.category ? (
                    <p className="mt-0.5 text-[10px] text-slate">{row.category}</p>
                  ) : null}
                </td>
                <td className="px-3 py-2.5 text-bone-dim">
                  {titleCase(row.sender)} → {titleCase(row.receiver)}
                </td>
                <td className="px-3 py-2.5">
                  <InteractionCell side={row.a} />
                </td>
                <td className="px-3 py-2.5">
                  <InteractionCell side={row.b} />
                </td>
                <td className="px-5 py-2.5 text-right font-mono text-bone-dim">
                  {significantIn(row)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardBody>
    </Card>
  );
}

function ComparisonView({ data }: { data: RunComparison }) {
  const notAssessed = useMemo(
    () => Array.from(new Set([...data.a.not_assessed, ...data.b.not_assessed])),
    [data],
  );

  return (
    <>
      {data.warnings.length > 0 ? (
        <div className="flex items-start gap-2.5 rounded-xl border border-amber/25 bg-amber/[0.05] px-4 py-3">
          <TriangleAlert className="mt-0.5 size-4 shrink-0 text-amber" />
          <div className="min-w-0">
            <p className="text-xs font-medium text-amber">Read this comparison with care</p>
            <ul className="mt-1 space-y-0.5">
              {data.warnings.map((warning) => (
                <li key={warning} className="text-[11px] leading-relaxed text-amber/80">
                  {warning}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-2">
        <RunSideCard side={data.a} />
        <RunSideCard side={data.b} />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <CompositionCard rows={data.composition} />
        <DomainCard rows={data.domains} />
      </div>

      <CommunicationCard rows={data.communication} />

      <NotAssessedNotice items={notAssessed} />

      <p className="flex items-start gap-2 text-[11px] leading-relaxed text-slate">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        {data.note}
      </p>
    </>
  );
}

function CompareContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const a = searchParams.get("a");
  const b = searchParams.get("b");

  const { data, loading, error } = useApiData<RunComparison | null>(
    () => (a && b ? apiClient.compareRuns(a, b) : Promise.resolve(null)),
    [a, b],
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-1.5 font-mono text-[10px] text-slate">
        <Link href="/app/runs" className="transition hover:text-bone">
          Runs
        </Link>
        <ChevronRight className="size-3" />
        <span className="text-bone-dim">Compare</span>
      </div>

      <PageHeader
        eyebrow="Side by side"
        title="Compare runs"
        description="Two finished runs next to each other, read from their stored results. Nothing is re-analysed."
        actions={
          a && b ? (
            <>
              <Button
                variant="secondary"
                onClick={() =>
                  router.replace(`/app/runs/compare?${new URLSearchParams({ a: b, b: a })}`)
                }
              >
                <ArrowLeftRight className="size-4" />
                Swap A / B
              </Button>
              <Link
                href="/app/runs?compare=1"
                className="inline-flex h-10 items-center gap-2 rounded-xl border border-line bg-bone/5 px-4 text-sm font-medium text-bone transition hover:bg-bone/10"
              >
                <GitCompareArrows className="size-4" />
                Change runs
              </Link>
            </>
          ) : null
        }
      />

      <RuoNotice />

      {!a || !b ? (
        <EmptyState
          title="Pick two runs to compare"
          description="Choose two completed runs on the Runs page. The first becomes A, the second B."
          action={
            <Link
              href="/app/runs?compare=1"
              className="inline-flex h-9 items-center rounded-xl bg-acid px-4 text-xs font-medium text-ink"
            >
              Choose runs
            </Link>
          }
        />
      ) : error ? (
        <div className="flex items-start gap-2.5 rounded-xl border border-coral/30 bg-coral/[0.06] px-4 py-3 text-xs text-coral">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div>
            <p className="font-medium">Could not compare these runs.</p>
            <p className="mt-0.5 text-coral/80">{error.message}</p>
            <Link
              href="/app/runs?compare=1"
              className="mt-2 inline-block text-bone-dim underline underline-offset-2"
            >
              Choose other runs
            </Link>
          </div>
        </div>
      ) : loading || !data ? (
        <div className="space-y-5">
          <div className="grid gap-5 lg:grid-cols-2">
            <Skeleton className="h-72" />
            <Skeleton className="h-72" />
          </div>
          <Skeleton className="h-64" />
        </div>
      ) : (
        <ComparisonView data={data} />
      )}
    </div>
  );
}

export default function CompareRunsPage() {
  return (
    <Suspense fallback={<Skeleton className="h-64" />}>
      <CompareContent />
    </Suspense>
  );
}
