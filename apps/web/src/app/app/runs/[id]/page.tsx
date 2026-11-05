"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowUpRight,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Download,
  ExternalLink,
  FileText,
  Play,
  RefreshCw,
  TriangleAlert,
  XCircle,
} from "lucide-react";
import { PageHeader, Stat } from "@/components/app/page-header";
import {
  CommunicationView,
  NotAssessedNotice,
  ReliabilityCard,
} from "@/components/app/run-insights";
import { SpatialMap } from "@/components/spatial/spatial-map";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Progress, Skeleton, Spinner } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { Tabs } from "@/components/ui/tabs";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import type { ResultPayload, RunDetail } from "@/lib/types";
import {
  cn,
  errorMessage,
  formatDateTime,
  formatNumber,
  relativeTime,
  titleCase,
} from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

const stages = [
  { id: "queued", label: "Queued" },
  { id: "loading", label: "Load + QC" },
  { id: "deconvolution", label: "Deconvolution" },
  { id: "spatial", label: "Spatial smoothing" },
  { id: "domains", label: "Domains" },
  { id: "targets", label: "Targets" },
  { id: "report", label: "Report" },
  { id: "done", label: "Done" },
];

const stageOrder = Object.fromEntries(stages.map((stage, index) => [stage.id, index]));

const evidenceTone = {
  established: "teal",
  emerging: "amber",
  exploratory: "outline",
} as const;

export default function RunDetailPage() {
  const params = useParams<{ id: string }>();
  const runId = params.id;
  const router = useRouter();
  const { toast } = useToast();

  const {
    data: run,
    loading,
    error,
    reload,
  } = useApiData<RunDetail>(() => apiClient.run(runId), [runId]);

  const succeeded = run?.status === "succeeded";

  const { data: result } = useApiData<{ run_id: string; payload: ResultPayload } | null>(
    () => (succeeded ? apiClient.results(runId) : Promise.resolve(null)),
    [runId, succeeded],
  );

  const [retrying, setRetrying] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (!run) return;
    if (run.status !== "queued" && run.status !== "running") return;
    const timer = window.setInterval(() => reload(), 2000);
    return () => window.clearInterval(timer);
  }, [run, reload]);

  const payload = result?.payload ?? null;
  const summary = run?.summary ?? null;

  const composition = useMemo(() => {
    if (!summary?.composition_mean) return [];
    return Object.entries(summary.composition_mean).sort((a, b) => b[1] - a[1]);
  }, [summary]);

  async function handleRetry() {
    setRetrying(true);
    try {
      const next = await apiClient.retryRun(runId);
      toast("Retry queued as a new run.", "success");
      router.push(`/app/runs/${next.id}`);
    } catch (err) {
      toast(errorMessage(err), "error");
      setRetrying(false);
    }
  }

  async function handleCancel() {
    setCancelling(true);
    try {
      await apiClient.cancelRun(runId);
      toast("Run cancelled.", "info");
      reload();
    } catch (err) {
      toast(errorMessage(err), "error");
    } finally {
      setCancelling(false);
    }
  }

  if (loading && !run) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-4 w-60" />
        <Skeleton className="h-24 w-full" />
        <div className="grid gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-[104px]" />
          ))}
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="space-y-5">
        <Link
          href="/app/runs"
          className="inline-flex items-center gap-1.5 text-xs text-slate transition hover:text-bone"
        >
          <ArrowLeft className="size-3.5" />
          Runs
        </Link>
        <EmptyState
          title="Run not found"
          description={error?.message ?? "This run may belong to another workspace."}
          action={
            <Link
              href="/app/runs"
              className="inline-flex h-9 items-center rounded-xl bg-acid px-4 text-xs font-medium text-ink"
            >
              Back to runs
            </Link>
          }
        />
      </div>
    );
  }

  const active = run.status === "queued" || run.status === "running";
  const currentStageIndex = stageOrder[run.stage] ?? -1;
  const failed = run.status === "failed";
  const cancelled = run.status === "cancelled";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.12em] text-slate">
        <Link href="/app/runs" className="transition hover:text-bone">
          Runs
        </Link>
        <ChevronRight className="size-3" />
        <span className="text-bone-dim">{run.id.slice(0, 8)}</span>
      </div>

      <PageHeader
        eyebrow={`${titleCase(run.disease_pack)} · pack ${run.pack_version}`}
        title={`Run ${run.id.slice(0, 8)}`}
        description={`${run.pipeline_version} · created ${formatDateTime(run.created_at)}`}
        actions={
          <>
            <StatusBadge status={run.status} />
            {active ? (
              <Button variant="danger" onClick={handleCancel} loading={cancelling}>
                Cancel
              </Button>
            ) : (
              <Button variant="secondary" onClick={handleRetry} loading={retrying}>
                <RefreshCw className="size-4" />
                Re-run
              </Button>
            )}
            <a
              href={`/api/v1/runs/${run.id}/report`}
              target="_blank"
              rel="noreferrer"
              className={cn(
                "inline-flex h-10 items-center gap-2 rounded-xl px-4 text-sm font-medium transition",
                succeeded
                  ? "bg-acid text-ink hover:bg-[#d6ff6a]"
                  : "pointer-events-none border border-line text-slate opacity-60",
              )}
            >
              <FileText className="size-4" />
              Report
              <ExternalLink className="size-3.5" />
            </a>
          </>
        }
      />

      {failed ? (
        <div className="flex items-start gap-3 rounded-xl border border-coral/30 bg-coral/[0.06] px-4 py-3.5">
          <XCircle className="mt-0.5 size-4 shrink-0 text-coral" />
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-coral">
              Run failed{failed && run.error_code ? ` · ${run.error_code}` : ""}
            </p>
            <p className="mt-1 break-words text-[11px] leading-relaxed text-coral/80">
              {run.error_message ?? "The pipeline stopped before producing a result."}
            </p>
          </div>
          {run.sample ? (
            <Link
              href={`/app/samples/${run.sample.id}`}
              className="shrink-0 text-[11px] text-bone-dim underline underline-offset-2"
            >
              Open sample
            </Link>
          ) : null}
        </div>
      ) : null}

      {cancelled ? (
        <div className="flex items-center gap-2.5 rounded-xl border border-line bg-ink-2 px-4 py-3 text-xs text-slate">
          <XCircle className="size-4 text-slate" />
          This run was cancelled. Re-run creates a new run with the same parameters.
        </div>
      ) : null}

      {active ? (
        <Card className="overflow-hidden">
          <CardBody className="space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <span className="flex size-10 items-center justify-center rounded-xl border border-acid/30 bg-acid/10 text-acid">
                  <Spinner className="border-acid/25 border-t-acid" />
                </span>
                <div>
                  <p className="text-sm font-medium text-bone">{titleCase(run.stage)}</p>
                  <p className="mt-0.5 text-[11px] text-slate">
                    {run.status === "queued"
                      ? "Waiting for a worker…"
                      : "Pipeline running. This page refreshes automatically."}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-mono text-2xl text-bone">{Math.round(run.progress * 100)}%</p>
                <p className="font-mono text-[9px] uppercase tracking-wider text-slate">progress</p>
              </div>
            </div>

            <Progress value={run.progress} className="h-2" />

            <div className="grid gap-2 sm:grid-cols-4">
              {stages.slice(1, 5).map((stage, index) => {
                const stageIndex = index + 1;
                const done = currentStageIndex > stageIndex || run.status === "succeeded";
                const current = currentStageIndex === stageIndex;
                return (
                  <div
                    key={stage.id}
                    className={cn(
                      "flex items-center gap-2 rounded-lg border px-2.5 py-2",
                      done
                        ? "border-teal/25 bg-teal/[0.04]"
                        : current
                          ? "border-acid/30 bg-acid/[0.06]"
                          : "border-line bg-ink-3/40",
                    )}
                  >
                    {done ? (
                      <CheckCircle2 className="size-3.5 shrink-0 text-teal" />
                    ) : current ? (
                      <Spinner className="size-3.5" />
                    ) : (
                      <CircleDot className="size-3.5 shrink-0 text-slate/50" />
                    )}
                    <span
                      className={cn(
                        "text-[10px]",
                        done ? "text-teal" : current ? "text-acid" : "text-slate",
                      )}
                    >
                      {stage.label}
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-line pt-3 font-mono text-[10px] text-slate">
              <span>sample {run.sample_id.slice(0, 8)}</span>
              <span>pack {run.pack_version}</span>
              <span>started {run.started_at ? relativeTime(run.started_at) : "—"}</span>
              <span className="text-teal">parameters pinned</span>
            </div>
          </CardBody>
        </Card>
      ) : null}

      {succeeded && summary ? (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Stat
              label="Spots modeled"
              value={formatNumber(summary.modeled_spots ?? summary.n_spots)}
              hint={`${formatNumber(summary.passed_spots)} passed QC of ${formatNumber(summary.n_spots)}`}
              tone="acid"
            />
            <Stat
              label="Domains"
              value={formatNumber(summary.n_domains)}
              hint={`${summary.n_cell_types} cell types`}
              tone="teal"
            />
            <Stat
              label="Top cell type"
              value={titleCase(summary.dominant_cell_type ?? "—")}
              hint="Mean composition across spots"
            />
            <Stat
              label="Runtime"
              value={`${summary.runtime_seconds.toFixed(1)}s`}
              hint={summary.synthetic ? "Synthetic demo sample" : "Uploaded sample"}
            />
          </div>

          {summary.warnings?.length > 0 ? (
            <div className="flex items-start gap-2.5 rounded-xl border border-amber/25 bg-amber/[0.05] px-4 py-3">
              <TriangleAlert className="mt-0.5 size-4 shrink-0 text-amber" />
              <div className="min-w-0">
                <p className="text-xs font-medium text-amber">Run warnings</p>
                <ul className="mt-1 space-y-0.5">
                  {summary.warnings.map((warning) => (
                    <li key={warning} className="text-[11px] leading-relaxed text-amber/80">
                      {warning}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : null}

          {payload ? (
            <div className="grid gap-5 xl:grid-cols-[1.7fr_1fr]">
              <div className="min-w-0">
                <SpatialMap payload={payload} />
              </div>

              <div className="space-y-5">
                <Card>
                  <CardHeader
                    title="Run details"
                    description="Pinned versions and provenance."
                    action={<Badge variant="teal">{summary.method}</Badge>}
                  />
                  <CardBody className="space-y-2.5">
                    {[
                      ["Sample", run.sample?.name ?? run.sample_id.slice(0, 8)],
                      ["Disease pack", `${titleCase(run.disease_pack)} · ${run.pack_version}`],
                      ["Pipeline", run.pipeline_version],
                      ["Method", summary.method],
                      ["Genes", formatNumber(summary.n_genes)],
                      ["Started", formatDateTime(run.started_at)],
                      ["Finished", formatDateTime(run.finished_at)],
                      ...(run.provenance
                        ? [
                            ["Reference", run.provenance.reference.version],
                            ["Pack sha256", run.provenance.disease_pack.sha256.slice(0, 12)],
                            ["Commit", run.provenance.software.commit.slice(0, 12)],
                          ]
                        : []),
                    ].map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between gap-3 text-[11px]">
                        <span className="text-slate">{key}</span>
                        <span
                          className="max-w-[60%] truncate font-mono text-bone-dim"
                          title={value}
                        >
                          {value}
                        </span>
                      </div>
                    ))}
                    {run.sample ? (
                      <Link
                        href={`/app/samples/${run.sample.id}`}
                        className="mt-1 inline-flex items-center gap-1.5 border-t border-line pt-3 text-[11px] text-acid transition hover:gap-2.5"
                      >
                        Open sample
                        <ArrowUpRight className="size-3" />
                      </Link>
                    ) : null}
                  </CardBody>
                </Card>

                <Card>
                  <CardHeader
                    title="Top targets"
                    description="Research prioritization, not a treatment recommendation."
                    action={<Badge variant="outline">evidence</Badge>}
                  />
                  <CardBody className="space-y-3">
                    {(payload.target_scores ?? []).slice(0, 5).map((target, index) => (
                      <div key={target.gene} className="space-y-1">
                        <div className="flex items-center justify-between gap-2">
                          <p className="flex items-center gap-1.5 text-xs text-bone">
                            <span className="font-mono text-[9px] text-slate">
                              {String(index + 1).padStart(2, "0")}
                            </span>
                            {target.gene}
                            <span className="truncate text-[10px] font-normal text-slate">
                              {target.name}
                            </span>
                          </p>
                          <Badge variant={evidenceTone[target.evidence_level] ?? "outline"}>
                            {target.evidence_level}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="h-1 flex-1 overflow-hidden rounded-full bg-bone/10">
                            <span
                              className="block h-full rounded-full bg-gradient-to-r from-teal to-acid"
                              style={{ width: `${Math.min(100, target.overall_score * 100)}%` }}
                            />
                          </span>
                          <span className="w-9 text-right font-mono text-[10px] text-bone-dim">
                            {target.overall_score.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </CardBody>
                </Card>

                <Card>
                  <CardHeader title="QC snapshot" description="Per-spot filters before modeling." />
                  <CardBody className="space-y-2.5">
                    {payload.qc ? (
                      <>
                        {[
                          ["Passed spots", formatNumber(payload.qc.summary.passed_spots)],
                          ["Median counts", formatNumber(payload.qc.summary.median_counts)],
                          ["Median genes", formatNumber(payload.qc.summary.median_genes)],
                          [
                            "Median mito",
                            `${(payload.qc.summary.median_mito_fraction * 100).toFixed(2)}%`,
                          ],
                        ].map(([key, value]) => (
                          <div
                            key={key}
                            className="flex items-center justify-between gap-3 text-[11px]"
                          >
                            <span className="text-slate">{key}</span>
                            <span className="font-mono text-bone-dim">{value}</span>
                          </div>
                        ))}
                        <div className="border-t border-line pt-2.5 font-mono text-[9px] leading-relaxed text-slate">
                          min counts {payload.qc.summary.thresholds.min_counts} · min genes{" "}
                          {payload.qc.summary.thresholds.min_genes} · max mito{" "}
                          {(payload.qc.summary.thresholds.max_mito_fraction * 100).toFixed(0)}%
                        </div>
                      </>
                    ) : null}
                  </CardBody>
                </Card>
              </div>
            </div>
          ) : (
            <Card>
              <CardBody className="flex items-center justify-center gap-3 py-12 text-xs text-slate">
                <Spinner />
                Loading result payload…
              </CardBody>
            </Card>
          )}

          {payload ? <NotAssessedNotice items={payload.summary.not_assessed} /> : null}

          {payload ? (
            <Tabs
              tabs={[
                {
                  id: "domains",
                  label: "Domains",
                  content: <DomainsTable payload={payload} />,
                },
                {
                  id: "composition",
                  label: "Composition",
                  content: <CompositionView composition={composition} summary={summary} />,
                },
                {
                  id: "targets",
                  label: "Target evidence",
                  content: <TargetTable payload={payload} />,
                },
                {
                  id: "communication",
                  label: "Communication",
                  content: <CommunicationView payload={payload} />,
                },
                {
                  id: "validation",
                  label: "Validation",
                  content: <ValidationView payload={payload} />,
                },
                {
                  id: "report",
                  label: "Report",
                  content: <ReportView run={run} onChanged={reload} />,
                },
              ]}
            />
          ) : null}
        </>
      ) : null}

      {!active && !succeeded && !failed && !cancelled ? (
        <EmptyState
          title="Run has no result"
          description="The run is not active and produced no result payload. Re-run to try again."
          action={
            <Button onClick={handleRetry} loading={retrying}>
              <Play className="size-4" />
              Re-run
            </Button>
          }
        />
      ) : null}
    </div>
  );
}

function DomainsTable({ payload }: { payload: ResultPayload }) {
  return (
    <Card className="overflow-hidden">
      <CardHeader
        title="Spatial domains"
        description="Clusters of smoothed composition, labeled by disease-pack zone markers."
        action={<Badge variant="outline">{payload.domains_summary.length} domains</Badge>}
      />
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-xs">
          <thead className="border-b border-line bg-ink-3/40 font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
            <tr>
              <th className="px-4 py-2.5 font-normal">Domain</th>
              <th className="px-4 py-2.5 font-normal">Spots</th>
              <th className="px-4 py-2.5 font-normal">Share</th>
              <th className="px-4 py-2.5 font-normal">Mean uncertainty</th>
              <th className="px-4 py-2.5 font-normal">Top cell types</th>
            </tr>
          </thead>
          <tbody>
            {payload.domains_summary.map((domain) => (
              <tr key={domain.id} className="border-b border-line-soft last:border-0">
                <td className="px-4 py-3">
                  <span className="flex items-center gap-2 text-bone-dim">
                    <span className="size-2 rounded-full" style={{ background: domain.color }} />
                    {domain.name}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-bone-dim">{formatNumber(domain.count)}</td>
                <td className="px-4 py-3 font-mono text-slate">{domain.pct.toFixed(1)}%</td>
                <td className="px-4 py-3">
                  <span
                    className="font-mono"
                    style={{
                      color:
                        domain.mean_uncertainty > 0.7
                          ? "var(--color-coral)"
                          : domain.mean_uncertainty > 0.5
                            ? "var(--color-amber)"
                            : "var(--color-teal)",
                    }}
                  >
                    {domain.mean_uncertainty.toFixed(2)}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1.5">
                    {domain.top_cell_types.slice(0, 3).map((cell) => (
                      <span
                        key={cell.id}
                        className="rounded-full border border-line bg-ink-3 px-2 py-0.5 font-mono text-[9px] text-slate"
                      >
                        {titleCase(cell.id)} {(cell.value * 100).toFixed(0)}%
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function CompositionView({
  composition,
  summary,
}: {
  composition: Array<[string, number]>;
  summary: RunDetail["summary"];
}) {
  return (
    <div className="grid gap-5 lg:grid-cols-[1.3fr_1fr]">
      <Card>
        <CardHeader
          title="Mean cell composition"
          description="Average NNLS fractions across modeled spots."
        />
        <CardBody className="space-y-3">
          {composition.map(([cellType, value]) => (
            <div key={cellType}>
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs text-bone-dim">{titleCase(cellType)}</p>
                <p className="font-mono text-[11px] text-bone">{(value * 100).toFixed(1)}%</p>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-bone/10">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-teal/70 to-acid"
                  style={{ width: `${Math.min(100, value * 100)}%` }}
                />
              </div>
            </div>
          ))}
        </CardBody>
      </Card>

      <div className="space-y-5">
        <Card>
          <CardHeader title="Interpretation" description="What these fractions mean — and do not." />
          <CardBody className="space-y-3 text-[11px] leading-relaxed text-slate">
            <p>
              Fractions estimate the share of each reference cell type in a spot under an
              equal-RNA-content assumption. They are not counts of cells.
            </p>
            <p>
              Composition is constrained to the cell types in this disease pack. Cell states or
              types missing from the reference are forced into the closest available profile.
            </p>
            <p className="text-amber/80">
              Research use only. Do not use these fractions for diagnosis or treatment decisions.
            </p>
          </CardBody>
        </Card>
        {summary ? (
          <Card>
            <CardHeader title="Coverage" />
            <CardBody className="space-y-2">
              {[
                ["Cell types modeled", formatNumber(summary.n_cell_types)],
                ["Spots modeled", formatNumber(summary.modeled_spots)],
                ["Dominant type", titleCase(summary.dominant_cell_type ?? "—")],
              ].map(([key, value]) => (
                <div key={key} className="flex items-center justify-between text-[11px]">
                  <span className="text-slate">{key}</span>
                  <span className="font-mono text-bone-dim">{value}</span>
                </div>
              ))}
            </CardBody>
          </Card>
        ) : null}
      </div>
    </div>
  );
}

function TargetTable({ payload }: { payload: ResultPayload }) {
  return (
    <Card className="overflow-hidden">
      <CardHeader
        title="Target evidence"
        description="Pack-defined genes ranked by scaled expression overall and across domains."
        action={<Badge variant="amber">Hypothesis generator</Badge>}
      />
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-xs">
          <thead className="border-b border-line bg-ink-3/40 font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
            <tr>
              <th className="px-4 py-2.5 font-normal">Gene</th>
              <th className="px-4 py-2.5 font-normal">Evidence</th>
              <th className="px-4 py-2.5 font-normal">Score</th>
              <th className="px-4 py-2.5 font-normal">Top domains</th>
              <th className="px-4 py-2.5 font-normal">Detected</th>
            </tr>
          </thead>
          <tbody>
            {payload.target_scores.map((target) => {
              const topDomains = Object.entries(target.by_domain)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3);
              return (
                <tr key={target.gene} className="border-b border-line-soft last:border-0">
                  <td className="px-4 py-3">
                    <p className="font-mono text-[11px] text-bone">{target.gene}</p>
                    <p className="mt-0.5 text-[10px] text-slate">{target.name}</p>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={evidenceTone[target.evidence_level] ?? "outline"}>
                      {target.evidence_level}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="h-1 w-16 overflow-hidden rounded-full bg-bone/10">
                        <span
                          className="block h-full rounded-full bg-acid"
                          style={{ width: `${target.overall_score * 100}%` }}
                        />
                      </span>
                      <span className="font-mono text-[10px] text-bone-dim">
                        {target.overall_score.toFixed(2)}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {topDomains.map(([domain, value]) => (
                        <span
                          key={domain}
                          className="rounded-full border border-line bg-ink-3 px-1.5 py-0.5 font-mono text-[9px] text-slate"
                        >
                          {titleCase(domain)} {value.toFixed(2)}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {target.detected ? (
                      <span className="inline-flex items-center gap-1 text-[10px] text-teal">
                        <CheckCircle2 className="size-3" /> Yes
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate">Not detected</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="border-t border-line bg-ink-3/40 px-4 py-2.5">
        <p className="text-[10px] leading-relaxed text-slate">
          Scores are relative expression summaries, not causal or therapeutic evidence. Validate
          any target hypothesis experimentally.
        </p>
      </div>
    </Card>
  );
}

function ValidationView({ payload }: { payload: ResultPayload }) {
  const metrics = payload.metrics;
  return (
    <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
      <Card>
        <CardHeader
          title="Benchmark result"
          description="Synthetic ground truth for this run."
          action={<Badge variant={metrics ? "teal" : "outline"}>{metrics ? "Reported" : "None"}</Badge>}
        />
        <CardBody className="space-y-3">
          {metrics ? (
            <>
              {[
                {
                  label: "Composition JSD",
                  value: metrics.composition.jsd_mean,
                  display: metrics.composition.jsd_mean.toFixed(3),
                  target: "< 0.12",
                  pass: metrics.composition.jsd_mean < 0.12,
                },
                {
                  label: "Dominant-type Pearson",
                  value: metrics.composition.dominant_type_pearson,
                  display: metrics.composition.dominant_type_pearson.toFixed(3),
                  target: "> 0.85",
                  pass: metrics.composition.dominant_type_pearson > 0.85,
                },
                {
                  label: "Domain ARI",
                  value: metrics.domains.ari,
                  display: metrics.domains.ari.toFixed(3),
                  target: "> 0.55",
                  pass: metrics.domains.ari > 0.55,
                },
                {
                  label: "Domain NMI",
                  value: metrics.domains.nmi,
                  display: metrics.domains.nmi.toFixed(3),
                  target: "reported",
                  pass: true,
                },
              ].map((metric) => (
                <div
                  key={metric.label}
                  className="flex items-center justify-between gap-3 rounded-lg border border-line bg-ink-3/40 px-3 py-2.5"
                >
                  <div>
                    <p className="text-[11px] text-bone-dim">{metric.label}</p>
                    <p className="mt-0.5 font-mono text-[9px] text-slate">target {metric.target}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm text-bone">{metric.display}</span>
                    <span
                      className={cn(
                        "size-1.5 rounded-full",
                        metric.pass ? "bg-teal" : "bg-coral",
                      )}
                    />
                  </div>
                </div>
              ))}
              <p className="text-[10px] leading-relaxed text-slate">{metrics.note}</p>
            </>
          ) : (
            <EmptyState
              compact
              title="No benchmark available"
              description="This run has no ground truth, so composition and domain metrics cannot be computed."
            />
          )}
        </CardBody>
      </Card>

      <div className="space-y-5">
        <ReliabilityCard payload={payload} />
        <Card>
          <CardHeader title="What this proves" />
          <CardBody className="space-y-2.5 text-[11px] leading-relaxed text-slate">
            <p className="flex items-start gap-2">
              <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-teal" />
              The estimator recovers known composition and zones from synthetic pseudospots.
            </p>
            <p className="flex items-start gap-2">
              <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-teal" />
              The pipeline is reproducible with pinned versions and parameters.
            </p>
          </CardBody>
        </Card>
        <Card className="border-amber/20">
          <CardHeader title="What it does not prove" />
          <CardBody className="space-y-2.5 text-[11px] leading-relaxed text-slate">
            <p className="flex items-start gap-2">
              <CircleDot className="mt-0.5 size-3.5 shrink-0 text-amber" />
              Biological generalization to real tissue or independent cohorts.
            </p>
            <p className="flex items-start gap-2">
              <CircleDot className="mt-0.5 size-3.5 shrink-0 text-amber" />
              Clinical validity, utility, or regulatory clearance.
            </p>
            <p className="flex items-start gap-2">
              <CircleDot className="mt-0.5 size-3.5 shrink-0 text-amber" />
              Correctness of the reference atlas for your population.
            </p>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}

function ReportView({ run, onChanged }: { run: RunDetail; onChanged: () => void }) {
  const { me } = useAuth();
  const { toast } = useToast();
  const [confirmed, setConfirmed] = useState(false);
  const [note, setNote] = useState("");
  const [approving, setApproving] = useState(false);

  const report = run.report;
  const approved = report?.status === "approved";
  const canApprove = me?.role !== undefined && me.role !== "viewer";

  async function handleApprove(event: React.FormEvent) {
    event.preventDefault();
    if (!confirmed) return;
    setApproving(true);
    try {
      await apiClient.approveReport(run.id, { confirm_ruo: true, note: note.trim() });
      toast("Report approved. Export is now available.", "success");
      onChanged();
    } catch (err) {
      toast(errorMessage(err), "error");
    } finally {
      setApproving(false);
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
      <Card>
        <CardHeader
          title="Self-contained HTML report"
          description="Methods, QC, domains, targets, provenance, warnings, and the RUO notice."
          action={
            <Badge variant={approved ? "teal" : "amber"}>{approved ? "Approved" : "Draft"}</Badge>
          }
        />
        <CardBody className="space-y-4">
          <div className="rounded-xl border border-line bg-ink-3/50 p-5">
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-xl border border-line bg-ink-2 text-teal">
                <FileText className="size-5" />
              </span>
              <div>
                <p className="text-sm font-medium text-bone">
                  {titleCase(run.disease_pack)} atlas · {run.id.slice(0, 8)}
                </p>
                <p className="mt-0.5 font-mono text-[10px] text-slate">
                  {run.pipeline_version} · {run.summary?.n_spots ?? 0} spots
                </p>
              </div>
            </div>
            {approved && report ? (
              <p className="mt-3 text-[11px] leading-relaxed text-slate">
                Approved by <span className="text-bone">{report.approved_by_name ?? "a member"}</span>{" "}
                {relativeTime(report.approved_at)}.
                {report.approval_note ? <> Note: “{report.approval_note}”</> : null} Every export is
                recorded in the audit log.
              </p>
            ) : (
              <p className="mt-3 text-[11px] leading-relaxed text-amber">
                Draft. A person must review and approve this report before it can be exported or
                shared outside Topiome.
              </p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <a
              href={`/api/v1/runs/${run.id}/report`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-10 items-center gap-2 rounded-xl border border-line px-4 text-xs text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
            >
              <ExternalLink className="size-4" />
              {approved ? "Open report" : "Preview draft"}
            </a>
            {approved ? (
              <a
                href={`/api/v1/runs/${run.id}/report/export`}
                className="inline-flex h-10 items-center gap-2 rounded-xl bg-acid px-4 text-xs font-medium text-ink transition hover:bg-[#d6ff6a]"
              >
                <Download className="size-4" />
                Export HTML
              </a>
            ) : (
              <span
                className="inline-flex h-10 cursor-not-allowed items-center gap-2 rounded-xl border border-line px-4 text-xs text-slate opacity-60"
                title="Approve the report to enable export"
              >
                <Download className="size-4" />
                Export HTML
              </span>
            )}
          </div>

          {!approved && report ? (
            canApprove ? (
              <form
                onSubmit={handleApprove}
                className="space-y-3 rounded-xl border border-amber/30 bg-amber/5 p-4"
              >
                <p className="text-xs font-medium text-bone">Approve for research use</p>
                <label className="flex items-start gap-2.5 text-[11px] leading-relaxed text-bone-dim">
                  <input
                    type="checkbox"
                    checked={confirmed}
                    onChange={(event) => setConfirmed(event.target.checked)}
                    className="mt-0.5 size-4 shrink-0 accent-[#c8f751]"
                  />
                  I reviewed this report, including its uncertainty and warnings, and confirm it is
                  for Research Use Only — not for diagnosis, prognosis, or treatment decisions.
                </label>
                <Textarea
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                  placeholder="Optional note for the audit log (e.g. reviewed with PI)"
                  maxLength={1000}
                  className="min-h-16 text-xs"
                />
                <Button type="submit" size="sm" disabled={!confirmed} loading={approving}>
                  <CheckCircle2 className="size-3.5" />
                  Approve report
                </Button>
              </form>
            ) : (
              <p className="rounded-xl border border-line p-4 text-[11px] text-slate">
                Viewers cannot approve reports. Ask an analyst, admin, or owner in your lab.
              </p>
            )
          ) : null}
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Report contents" />
        <CardBody className="space-y-2.5">
          {[
            "Sample and run metadata",
            "QC summary and thresholds",
            "Spatial domain map and legend",
            "Cell composition per domain",
            "Target evidence table",
            "Ligand–receptor communication",
            "Method agreement and external atlas check",
            "Benchmark metrics and warnings",
            "Versions, hashes, and parameters (provenance)",
            "Approval status and RUO notice",
          ].map((item) => (
            <p key={item} className="flex items-start gap-2 text-[11px] text-bone-dim">
              <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-teal" />
              {item}
            </p>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
