"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import {
  ArrowUpRight,
  Filter,
  RefreshCw,
  Search,
  TriangleAlert,
  X,
} from "lucide-react";
import { PageHeader, Stat } from "@/components/app/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiClient } from "@/lib/api";
import type { Run, RunStatus } from "@/lib/types";
import { cn, formatNumber, relativeTime, titleCase } from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

const tabs: Array<{ id: "all" | RunStatus; label: string }> = [
  { id: "all", label: "All" },
  { id: "running", label: "Running" },
  { id: "succeeded", label: "Completed" },
  { id: "queued", label: "Queued" },
  { id: "failed", label: "Failed" },
];

function RunsContent() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project_id");
  const sampleId = searchParams.get("sample_id");

  const { data, loading, error, reload } = useApiData<Run[]>(
    () => apiClient.runs({ project_id: projectId ?? undefined, sample_id: sampleId ?? undefined }),
    [projectId, sampleId],
  );

  const [tab, setTab] = useState<"all" | RunStatus>("all");
  const [query, setQuery] = useState("");

  const runs = useMemo(() => data ?? [], [data]);
  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    return runs.filter((run) => {
      if (tab !== "all" && run.status !== tab) return false;
      if (!term) return true;
      return (
        run.id.toLowerCase().includes(term) ||
        run.disease_pack.toLowerCase().includes(term) ||
        run.stage.toLowerCase().includes(term)
      );
    });
  }, [runs, tab, query]);

  const counts = useMemo(
    () => ({
      completed: runs.filter((run) => run.status === "succeeded").length,
      active: runs.filter((run) => run.status === "running" || run.status === "queued").length,
      failed: runs.filter((run) => run.status === "failed").length,
      spots: runs.reduce((total, run) => total + (run.summary?.n_spots ?? 0), 0),
    }),
    [runs],
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Evidence trail"
        title="Runs"
        description="Every analysis is a versioned run: pipeline, disease pack, parameters, warnings, result, and report."
        actions={
          <Button variant="secondary" onClick={reload} loading={loading}>
            <RefreshCw className="size-4" />
            Refresh
          </Button>
        }
      />

      {projectId || sampleId ? (
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="acid">
            <Filter className="size-3" />
            Filtered view
          </Badge>
          <span className="font-mono text-[10px] text-slate">
            {projectId ? `project ${projectId.slice(0, 8)}` : null}
            {projectId && sampleId ? " · " : null}
            {sampleId ? `sample ${sampleId.slice(0, 8)}` : null}
          </span>
          <Link
            href="/app/runs"
            className="inline-flex items-center gap-1 rounded-full border border-line px-2 py-0.5 text-[10px] text-slate transition hover:text-bone"
          >
            <X className="size-3" />
            Clear
          </Link>
        </div>
      ) : null}

      {error ? (
        <div className="flex items-start gap-2.5 rounded-xl border border-coral/30 bg-coral/[0.06] px-4 py-3 text-xs text-coral">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div>
            <p className="font-medium">Could not load runs.</p>
            <p className="mt-0.5 text-coral/80">{error.message}</p>
          </div>
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Total runs" value={formatNumber(runs.length)} hint="Most recent 50" />
        <Stat label="Completed" value={formatNumber(counts.completed)} tone="teal" hint="Succeeded" />
        <Stat label="Active" value={formatNumber(counts.active)} tone="amber" hint="Queued or running" />
        <Stat
          label="Spots processed"
          value={formatNumber(counts.spots)}
          tone="acid"
          hint={`${counts.failed} failed run${counts.failed === 1 ? "" : "s"}`}
        />
      </div>

      <Card className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-line px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-1">
            {tabs.map((item) => {
              const count =
                item.id === "all"
                  ? runs.length
                  : runs.filter((run) => run.status === item.id).length;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setTab(item.id)}
                  className={cn(
                    "inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[11px] transition focus-ring",
                    tab === item.id
                      ? "bg-acid/10 text-acid"
                      : "text-slate hover:bg-bone/5 hover:text-bone",
                  )}
                >
                  {item.label}
                  <span className="font-mono text-[9px] opacity-70">{count}</span>
                </button>
              );
            })}
          </div>
          <div className="relative w-full lg:max-w-xs">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-slate" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by run ID, pack, stage…"
              className="h-9 pl-9 text-xs"
              aria-label="Search runs"
            />
          </div>
        </div>

        {loading ? (
          <div className="space-y-2 p-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <Skeleton key={index} className="h-14" />
            ))}
          </div>
        ) : filtered.length > 0 ? (
          <div>
            <div className="hidden grid-cols-[1.4fr_1fr_0.9fr_0.9fr_0.9fr_0.8fr] gap-3 border-b border-line bg-ink-3/40 px-5 py-2.5 font-mono text-[9px] uppercase tracking-[0.12em] text-slate lg:grid">
              <span>Run</span>
              <span>Disease pack</span>
              <span>Status</span>
              <span>Spots</span>
              <span>Domains</span>
              <span className="text-right">Created</span>
            </div>
            <div className="divide-y divide-line-soft">
              {filtered.map((run) => (
                <Link
                  key={run.id}
                  href={`/app/runs/${run.id}`}
                  className="group grid gap-3 px-4 py-3.5 transition hover:bg-bone/[0.03] sm:px-5 lg:grid-cols-[1.4fr_1fr_0.9fr_0.9fr_0.9fr_0.8fr] lg:items-center"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 font-mono text-[9px] text-teal">
                      {run.status === "succeeded" ? "OK" : run.status.slice(0, 2).toUpperCase()}
                    </span>
                    <div className="min-w-0">
                      <p className="font-mono text-[10px] text-bone-dim">{run.id.slice(0, 8)}</p>
                      <p className="mt-0.5 truncate text-[10px] text-slate">
                        {run.stage} · {run.pipeline_version}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-bone-dim">
                      {titleCase(run.disease_pack)}
                    </span>
                    <Badge variant="outline">{run.pack_version}</Badge>
                  </div>
                  <div>
                    <StatusBadge status={run.status} />
                  </div>
                  <p className="font-mono text-[11px] text-bone-dim">
                    {run.summary?.n_spots ? formatNumber(run.summary.n_spots) : "—"}
                  </p>
                  <p className="font-mono text-[11px] text-bone-dim">
                    {run.summary?.n_domains ?? "—"}
                  </p>
                  <div className="flex items-center justify-between gap-2 lg:justify-end">
                    <span className="font-mono text-[10px] text-slate">
                      {relativeTime(run.created_at)}
                    </span>
                    <ArrowUpRight className="size-3.5 text-slate transition group-hover:text-acid" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-5">
            <EmptyState
              title={query || tab !== "all" ? "No runs match this view" : "No runs yet"}
              description={
                query || tab !== "all"
                  ? "Clear the filter or search term to see all runs."
                  : "Open a sample and launch the analysis pipeline to create the first run."
              }
              action={
                query || tab !== "all" ? (
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setQuery("");
                      setTab("all");
                    }}
                  >
                    Clear filters
                  </Button>
                ) : (
                  <Link
                    href="/app/projects"
                    className="inline-flex h-9 items-center rounded-xl bg-acid px-4 text-xs font-medium text-ink"
                  >
                    Go to projects
                  </Link>
                )
              }
            />
          </div>
        )}
      </Card>
    </div>
  );
}

export default function RunsPage() {
  return (
    <Suspense fallback={<Skeleton className="h-64" />}>
      <RunsContent />
    </Suspense>
  );
}
