"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import {
  ArrowLeft,
  ArrowUpRight,
  ChevronRight,
  Download,
  FileText,
  FlaskConical,
  Microscope,
  Play,
  Trash2,
  TriangleAlert,
} from "lucide-react";
import { PageHeader, Stat } from "@/components/app/page-header";
import { RunSampleButton } from "@/components/app/run-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Field, Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiClient } from "@/lib/api";
import { useToast } from "@/lib/toast";
import type { SampleDetail } from "@/lib/types";
import {
  errorMessage,
  formatBytes,
  formatDate,
  formatNumber,
  relativeTime,
  titleCase,
} from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

export default function SampleDetailPage() {
  const params = useParams<{ id: string }>();
  const sampleId = params.id;
  const router = useRouter();
  const { toast } = useToast();

  const { data: sample, loading, error } = useApiData<SampleDetail>(
    () => apiClient.sample(sampleId),
    [sampleId],
  );

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [seed, setSeed] = useState("42");
  const [spots, setSpots] = useState("1200");
  const [creating, setCreating] = useState(false);

  async function handleDelete() {
    setDeleting(true);
    try {
      await apiClient.deleteSample(sampleId);
      toast("Sample archived.", "info");
      router.push(sample ? `/app/projects/${sample.project_id}` : "/app/projects");
    } catch (err) {
      toast(errorMessage(err), "error");
      setDeleting(false);
    }
  }

  async function handleCustomRun(event: React.FormEvent) {
    event.preventDefault();
    if (!sample) return;
    setCreating(true);
    try {
      const run = await apiClient.createRun(sample.id, {
        disease_pack: sample.disease_pack,
        params: {
          seed: Number(seed) || 42,
          ...(sample.files.length === 0 ? { n_spots: Number(spots) || 1200 } : {}),
        },
      });
      toast("Run queued with custom parameters.", "success");
      router.push(`/app/runs/${run.id}`);
    } catch (err) {
      toast(errorMessage(err), "error");
      setCreating(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-4 w-52" />
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

  if (error || !sample) {
    return (
      <div className="space-y-5">
        <Link
          href="/app/projects"
          className="inline-flex items-center gap-1.5 text-xs text-slate transition hover:text-bone"
        >
          <ArrowLeft className="size-3.5" />
          Projects
        </Link>
        <EmptyState
          title="Sample not found"
          description={error?.message ?? "This sample may have been archived or belongs to another workspace."}
          action={
            <Link
              href="/app/projects"
              className="inline-flex h-9 items-center rounded-xl bg-acid px-4 text-xs font-medium text-ink"
            >
              Back to projects
            </Link>
          }
        />
      </div>
    );
  }

  const isSynthetic = sample.files.length === 0;
  const activeRun = sample.runs.find(
    (run) => run.status === "queued" || run.status === "running",
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.12em] text-slate">
        <Link href="/app/projects" className="transition hover:text-bone">
          Projects
        </Link>
        <ChevronRight className="size-3" />
        <Link
          href={`/app/projects/${sample.project_id}`}
          className="max-w-[180px] truncate transition hover:text-bone"
        >
          project
        </Link>
        <ChevronRight className="size-3" />
        <span className="max-w-[220px] truncate text-bone-dim">{sample.name}</span>
      </div>

      <PageHeader
        eyebrow={titleCase(sample.disease_pack)}
        title={sample.name}
        description={
          isSynthetic
            ? "Synthetic demo sample. A run generates pseudospots from known profiles with ground-truth composition and zones."
            : `Uploaded ${sample.platform} sample. Files are stored in this organization's workspace.`
        }
        actions={
          <>
            <Button variant="danger" size="md" onClick={() => setDeleteOpen(true)}>
              <Trash2 className="size-4" />
              Archive
            </Button>
            <RunSampleButton
              sampleId={sample.id}
              diseasePack={sample.disease_pack}
              label={activeRun ? "Running…" : "Run analysis"}
              size="md"
            />
          </>
        }
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Stat
          label="Spots"
          value={sample.spot_count ? formatNumber(sample.spot_count) : "—"}
          hint="Detected in the last run"
          tone="acid"
        />
        <Stat label="Files" value={formatNumber(sample.files.length)} hint="Raw uploads" />
        <Stat
          label="Runs"
          value={formatNumber(sample.runs.length)}
          hint={`${sample.runs.filter((run) => run.status === "succeeded").length} completed`}
          tone="teal"
        />
        <Stat label="Created" value={formatDate(sample.created_at)} hint={relativeTime(sample.created_at)} />
      </div>

      {activeRun ? (
        <div className="flex items-center gap-3 rounded-xl border border-amber/25 bg-amber/[0.05] px-4 py-3">
          <Play className="size-4 text-amber" />
          <p className="flex-1 text-xs text-amber/90">
            A run is {activeRun.status} — {activeRun.stage}. Results will appear automatically.
          </p>
          <Link
            href={`/app/runs/${activeRun.id}`}
            className="inline-flex items-center gap-1 text-[11px] text-amber transition hover:gap-2"
          >
            Open run
            <ArrowUpRight className="size-3" />
          </Link>
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[1.6fr_1fr]">
        <div className="space-y-5">
          <Card className="overflow-hidden">
            <CardHeader
              title="Files"
              description={
                isSynthetic
                  ? "No raw files — this sample uses the synthetic generator."
                  : "Space Ranger inputs stored for this sample."
              }
              action={<Badge variant={isSynthetic ? "outline" : "teal"}>{isSynthetic ? "Synthetic" : `${sample.files.length} files`}</Badge>}
            />
            {sample.files.length > 0 ? (
              <div className="divide-y divide-line-soft">
                {sample.files.map((file) => (
                  <div key={file.id} className="flex items-center gap-3 px-4 py-3 sm:px-5">
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 text-teal">
                      <FileText className="size-3.5" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-mono text-[11px] text-bone-dim">{file.filename}</p>
                      <p className="mt-0.5 font-mono text-[9px] uppercase tracking-wider text-slate">
                        {file.kind} · {formatBytes(file.size_bytes)} ·{" "}
                        {relativeTime(file.created_at)}
                      </p>
                    </div>
                    <a
                      href={`/api/v1/samples/${sample.id}/files/${file.id}/download`}
                      className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-line px-2.5 text-[10px] text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
                      download
                    >
                      <Download className="size-3" />
                      Download
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-5">
                <EmptyState
                  compact
                  title="Synthetic sample"
                  description="No files were uploaded. Each run generates 1,200 pseudospots with known ground truth — useful for evaluating the pipeline, not for biological claims."
                  action={
                    <div className="flex items-center gap-2">
                      <FlaskConical className="size-3.5 text-teal" />
                      <span className="font-mono text-[10px] text-slate">
                        method=nnls · synthetic=true
                      </span>
                    </div>
                  }
                />
              </div>
            )}
          </Card>

          <Card className="overflow-hidden">
            <CardHeader
              title="Run history"
              description="Each run pins a pipeline and pack version."
              action={
                <Link
                  href={`/app/runs?sample_id=${sample.id}`}
                  className="inline-flex items-center gap-1 text-[11px] text-acid transition hover:gap-2"
                >
                  All runs
                  <ArrowUpRight className="size-3.5" />
                </Link>
              }
            />
            {sample.runs.length > 0 ? (
              <div className="divide-y divide-line-soft">
                {sample.runs.map((run) => (
                  <Link
                    key={run.id}
                    href={`/app/runs/${run.id}`}
                    className="group flex items-center gap-3 px-4 py-3.5 transition hover:bg-bone/[0.03] sm:px-5"
                  >
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 font-mono text-[9px] text-teal">
                      {run.summary?.n_domains ? `${run.summary.n_domains}D` : run.status.slice(0, 2).toUpperCase()}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-mono text-[10px] text-bone-dim">
                          run {run.id.slice(0, 8)}
                        </p>
                        <StatusBadge status={run.status} />
                      </div>
                      <p className="mt-1 truncate text-[10px] text-slate">
                        {run.summary?.n_spots
                          ? `${formatNumber(run.summary.n_spots)} spots · ${run.summary.method}`
                          : run.stage}
                        {" · "}
                        {relativeTime(run.created_at)}
                      </p>
                    </div>
                    <ArrowUpRight className="size-3.5 shrink-0 text-slate transition group-hover:text-acid" />
                  </Link>
                ))}
              </div>
            ) : (
              <div className="p-5">
                <EmptyState
                  compact
                  title="No runs yet"
                  description="Launch the pipeline to generate composition, domains, targets, and a report."
                />
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-5">
          <Card>
            <CardHeader title="Run parameters" description="Defaults work for most samples." />
            <CardBody>
              <form onSubmit={handleCustomRun} className="space-y-4">
                <Field
                  label="Random seed"
                  hint="Controls stochastic steps. Same seed + same inputs = reproducible output."
                >
                  <Input
                    type="number"
                    value={seed}
                    onChange={(event) => setSeed(event.target.value)}
                    min={0}
                  />
                </Field>
                {isSynthetic ? (
                  <Field label="Synthetic spots" hint="Used only when the sample has no raw files.">
                    <Input
                      type="number"
                      value={spots}
                      onChange={(event) => setSpots(event.target.value)}
                      min={100}
                      max={20000}
                    />
                  </Field>
                ) : null}

                <div className="rounded-lg border border-line bg-ink-3/60 px-3 py-2.5">
                  <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                    Pipeline
                  </p>
                  <p className="mt-1 font-mono text-[10px] text-bone-dim">
                    topiome-analysis 0.1.0-baseline
                  </p>
                  <p className="mt-0.5 font-mono text-[10px] text-slate">
                    pack {sample.disease_pack} · NNLS
                  </p>
                </div>

                <Button type="submit" className="w-full" loading={creating} disabled={Boolean(activeRun)}>
                  <Play className="size-4" />
                  {activeRun ? "Run already active" : "Queue with these parameters"}
                </Button>
              </form>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Sample metadata" />
            <CardBody className="space-y-2.5">
              {[
                ["External ID", sample.external_id || "—"],
                ["Platform", sample.platform],
                ["Species", sample.species],
                ["Condition", sample.condition || "—"],
                ["Status", sample.status],
                ["Disease pack", titleCase(sample.disease_pack)],
                ["Source", isSynthetic ? "Synthetic generator" : "Uploaded files"],
              ].map(([key, value]) => (
                <div key={key} className="flex items-center justify-between gap-3 text-[11px]">
                  <span className="text-slate">{key}</span>
                  <span className="max-w-[60%] truncate font-mono text-bone-dim">{value}</span>
                </div>
              ))}
            </CardBody>
          </Card>

          <div className="flex items-start gap-2 rounded-xl border border-amber/20 bg-amber/[0.04] px-3 py-2.5">
            <TriangleAlert className="mt-0.5 size-3.5 shrink-0 text-amber" />
            <p className="text-[10px] leading-relaxed text-amber/80">
              Research use only. Results are computational inferences; validate independently
              before any research decision.
            </p>
          </div>
        </div>
      </div>

      <Modal
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        title="Archive this sample?"
        description="The sample is hidden from the project but its runs and reports remain available for audit."
      >
        <div className="space-y-4">
          <div className="flex items-start gap-2.5 rounded-lg border border-coral/25 bg-coral/[0.05] px-3 py-2.5">
            <Microscope className="mt-0.5 size-4 shrink-0 text-coral" />
            <p className="text-xs leading-relaxed text-coral/90">
              Archiving <span className="font-medium">{sample.name}</span> does not delete stored
              files or previous results. Contact support for permanent deletion.
            </p>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setDeleteOpen(false)} disabled={deleting}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDelete} loading={deleting}>
              Archive sample
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
