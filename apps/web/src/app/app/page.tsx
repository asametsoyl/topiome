"use client";

import Link from "next/link";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  CircleDot,
  FolderKanban,
  Microscope,
  Play,
  Plus,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import { PageHeader, Stat } from "@/components/app/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Progress, Skeleton } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { DashboardSummary, Project } from "@/lib/types";
import { formatDateTime, formatNumber, relativeTime, titleCase } from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

export default function DashboardPage() {
  const { me } = useAuth();
  const { data, loading, error } = useApiData<[DashboardSummary, Project[]]>(() =>
    Promise.all([apiClient.dashboard(), apiClient.projects()]),
  );

  const summary = data?.[0];
  const projects = data?.[1] ?? [];
  const packMap = new Map((summary?.disease_packs ?? []).map((pack) => [pack.id, pack]));
  const firstName = me?.user.name.split(" ")[0] ?? "researcher";

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Workspace overview"
        title={`Welcome back, ${firstName}.`}
        description="Your projects, recent runs, and the evidence behind every atlas — in one place."
        actions={
          <>
            <Link
              href="/app/projects?new=1"
              className="inline-flex h-10 items-center gap-2 rounded-xl border border-line px-4 text-sm text-bone transition hover:border-[#3a4d41]"
            >
              <Plus className="size-4" />
              New project
            </Link>
            <Link
              href="/app/runs"
              className="inline-flex h-10 items-center gap-2 rounded-xl bg-acid px-4 text-sm font-medium text-ink transition hover:bg-[#d6ff6a]"
            >
              View runs
              <ArrowRight className="size-4" />
            </Link>
          </>
        }
      />

      {error ? (
        <div className="flex items-start gap-2.5 rounded-xl border border-coral/30 bg-coral/[0.06] px-4 py-3 text-xs text-coral">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div>
            <p className="font-medium">Could not load the dashboard.</p>
            <p className="mt-0.5 text-coral/80">{error.message}</p>
          </div>
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-[104px]" />
          ))
        ) : (
          <>
            <Stat
              label="Projects"
              value={formatNumber(summary?.projects ?? 0)}
              hint="Active research projects"
            />
            <Stat
              label="Samples"
              value={formatNumber(summary?.samples ?? 0)}
              hint="Uploaded or demo samples"
            />
            <Stat
              label="Runs"
              value={formatNumber(summary?.runs ?? 0)}
              hint={`${summary?.completed_runs ?? 0} completed · ${summary?.failed_runs ?? 0} failed`}
              tone="teal"
            />
            <Stat
              label="Spots analyzed"
              value={formatNumber(summary?.spots_analyzed ?? 0)}
              hint="Across all samples"
              tone="acid"
            />
          </>
        )}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.65fr_1fr]">
        <Card className="overflow-hidden">
          <CardHeader
            title="Recent runs"
            description="Every run keeps its pipeline version, pack version, parameters, and warnings."
            action={
              <Link
                href="/app/runs"
                className="inline-flex items-center gap-1 text-[11px] text-acid transition hover:gap-2"
              >
                All runs
                <ArrowUpRight className="size-3.5" />
              </Link>
            }
          />
          {loading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 3 }).map((_, index) => (
                <Skeleton key={index} className="h-14" />
              ))}
            </div>
          ) : summary && summary.recent_runs.length > 0 ? (
            <div className="divide-y divide-line-soft">
              {summary.recent_runs.map((run) => {
                const pack = packMap.get(run.disease_pack);
                return (
                  <Link
                    key={run.id}
                    href={`/app/runs/${run.id}`}
                    className="group flex items-center gap-3 px-4 py-3.5 transition hover:bg-bone/[0.03] sm:px-5"
                  >
                    <span
                      className="flex size-9 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 text-[10px] font-medium uppercase"
                      style={{ color: pack?.color ?? "var(--color-teal)" }}
                    >
                      {run.disease_pack.slice(0, 2)}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="truncate text-xs font-medium text-bone">
                          {pack?.short_name ?? titleCase(run.disease_pack)}
                        </p>
                        <StatusBadge status={run.status} />
                      </div>
                      <p className="mt-1 truncate font-mono text-[10px] text-slate">
                        {run.summary?.n_spots
                          ? `${formatNumber(run.summary.n_spots)} spots`
                          : "Awaiting spots"}
                        {" · "}
                        {run.summary?.method ?? "pipeline"} · {relativeTime(run.created_at)}
                      </p>
                      {run.status === "running" || run.status === "queued" ? (
                        <Progress value={run.progress} className="mt-2 max-w-[220px]" />
                      ) : null}
                    </div>
                    <div className="hidden shrink-0 text-right sm:block">
                      <p className="font-mono text-[10px] text-slate">{run.stage}</p>
                      <p className="mt-1 font-mono text-[10px] text-bone-dim">
                        {run.summary?.n_domains ? `${run.summary.n_domains} domains` : "—"}
                      </p>
                    </div>
                    <ArrowUpRight className="size-3.5 shrink-0 text-slate transition group-hover:text-acid" />
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="p-5">
              <EmptyState
                title="No runs yet"
                description="Create a project, add a sample, and launch the analysis pipeline. The demo sample is a one-click start."
                action={
                  <Link
                    href="/app/projects?new=1"
                    className="inline-flex h-9 items-center gap-2 rounded-xl bg-acid px-4 text-xs font-medium text-ink"
                  >
                    <Plus className="size-3.5" />
                    Create a project
                  </Link>
                }
              />
            </div>
          )}
        </Card>

        <div className="space-y-5">
          <Card>
            <CardHeader title="Start a new atlas" description="Four steps from raw spots to a report." />
            <CardBody className="space-y-1">
              {[
                {
                  icon: FolderKanban,
                  title: "Create a project",
                  body: "Pick the disease pack that matches your tissue.",
                  href: "/app/projects?new=1",
                },
                {
                  icon: Microscope,
                  title: "Add a sample",
                  body: "Upload Space Ranger files or use the demo sample.",
                  href: "/app/projects",
                },
                {
                  icon: Play,
                  title: "Run the baseline",
                  body: "QC → NNLS → domains → targets → uncertainty.",
                  href: "/app/runs",
                },
                {
                  icon: Activity,
                  title: "Read the atlas",
                  body: "Inspect composition and confidence, then share the report.",
                  href: "/app/runs",
                },
              ].map((step, index) => {
                const Icon = step.icon;
                return (
                  <Link
                    key={step.title}
                    href={step.href}
                    className="group flex items-start gap-3 rounded-xl px-2 py-2.5 transition hover:bg-bone/[0.03]"
                  >
                    <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 text-teal">
                      <Icon className="size-3.5" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="flex items-center gap-2 text-xs font-medium text-bone">
                        <span className="font-mono text-[9px] text-slate">0{index + 1}</span>
                        {step.title}
                      </p>
                      <p className="mt-1 text-[11px] leading-relaxed text-slate">{step.body}</p>
                    </div>
                    <ArrowUpRight className="mt-1 size-3.5 text-slate opacity-0 transition group-hover:opacity-100" />
                  </Link>
                );
              })}
            </CardBody>
          </Card>

          <Card className="border-teal/20 bg-teal/[0.03]">
            <CardBody className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="inline-flex size-8 items-center justify-center rounded-lg border border-teal/30 bg-teal/10 text-teal">
                  <ShieldCheck className="size-4" />
                </span>
                <Badge variant="teal">Benchmark passing</Badge>
              </div>
              <div>
                <p className="text-sm font-medium text-bone">Breast baseline · v0.1.0</p>
                <p className="mt-1 text-[11px] leading-relaxed text-slate">
                  Synthetic pseudospot benchmark, 1,200 spots. Numerical recovery only — not
                  clinical validation.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-line bg-line">
                {[
                  { k: "JSD", v: "0.099" },
                  { k: "Pearson", v: "0.862" },
                  { k: "ARI", v: "0.634" },
                ].map((metric) => (
                  <div key={metric.k} className="bg-ink-2 px-2 py-2">
                    <p className="font-mono text-[9px] uppercase tracking-wider text-slate">
                      {metric.k}
                    </p>
                    <p className="mt-0.5 font-mono text-sm text-teal">{metric.v}</p>
                  </div>
                ))}
              </div>
              <Link
                href="/docs#validation"
                className="inline-flex items-center gap-1.5 text-[11px] text-teal transition hover:gap-2.5"
              >
                How validation works
                <ArrowUpRight className="size-3" />
              </Link>
            </CardBody>
          </Card>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.2fr_1fr]">
        <Card>
          <CardHeader
            title="Projects"
            description="Your active research workspaces."
            action={
              <Link
                href="/app/projects"
                className="inline-flex items-center gap-1 text-[11px] text-acid transition hover:gap-2"
              >
                Open all
                <ArrowUpRight className="size-3.5" />
              </Link>
            }
          />
          {loading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 2 }).map((_, index) => (
                <Skeleton key={index} className="h-14" />
              ))}
            </div>
          ) : projects.length > 0 ? (
            <div className="divide-y divide-line-soft">
              {projects.slice(0, 4).map((project) => {
                const pack = packMap.get(project.disease_pack);
                return (
                  <Link
                    key={project.id}
                    href={`/app/projects/${project.id}`}
                    className="group flex items-center gap-3 px-4 py-3.5 transition hover:bg-bone/[0.03] sm:px-5"
                  >
                    <span
                      className="size-2.5 shrink-0 rounded-full"
                      style={{ background: pack?.color ?? "var(--color-acid)" }}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-medium text-bone">{project.name}</p>
                      <p className="mt-0.5 truncate text-[10px] text-slate">
                        {pack?.short_name ?? titleCase(project.disease_pack)} · updated{" "}
                        {relativeTime(project.updated_at)}
                      </p>
                    </div>
                    <ArrowUpRight className="size-3.5 text-slate transition group-hover:text-acid" />
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="p-5">
              <EmptyState
                compact
                title="No projects yet"
                description="Create your first project to organize samples and runs."
              />
            </div>
          )}
        </Card>

        <Card className="overflow-hidden">
          <CardHeader
            title="Data notice"
            description="What this workspace contains."
            action={<Badge variant="amber">Synthetic demo</Badge>}
          />
          <CardBody className="space-y-3 text-[11px] leading-relaxed text-slate">
            <div className="flex items-start gap-2.5">
              <CircleDot className="mt-0.5 size-3.5 shrink-0 text-teal" />
              <p>
                The seeded demo sample is <span className="text-bone-dim">synthetic</span>. Spot
                expression, cell composition, and zones are generated from known profiles with
                known ground truth.
              </p>
            </div>
            <div className="flex items-start gap-2.5">
              <CircleDot className="mt-0.5 size-3.5 shrink-0 text-teal" />
              <p>
                No patient data is present. Uploading data requires the right to use it and, where
                applicable, ethics approval.
              </p>
            </div>
            <div className="flex items-start gap-2.5">
              <ShieldCheck className="mt-0.5 size-3.5 shrink-0 text-amber" />
              <div>
                <p className="text-amber/90">Research use only.</p>
                <p className="mt-1">
                  Results are computational inferences and must be independently validated.
                </p>
              </div>
            </div>
            <div className="border-t border-line pt-3">
              <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                Last activity
              </p>
              <p className="mt-1 font-mono text-[10px] text-bone-dim">
                {summary?.recent_runs[0]
                  ? formatDateTime(summary.recent_runs[0].created_at)
                  : "No runs yet"}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="flex items-center justify-between gap-4 rounded-xl border border-line bg-ink-2/60 px-4 py-3">
        <p className="text-[11px] text-slate">
          <Sparkles className="mr-1.5 inline size-3.5 text-acid" />
          Tip: every run stores its parameters and pack version — re-running creates a new run
          instead of overwriting history.
        </p>
        <Link href="/docs#reproducibility" className="shrink-0 text-[11px] text-acid">
          Reproducibility
        </Link>
      </div>
    </div>
  );
}
