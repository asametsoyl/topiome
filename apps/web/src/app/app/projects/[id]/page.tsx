"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import {
  ArrowLeft,
  ArrowUpRight,
  Boxes,
  ChevronRight,
  Dna,
  FileUp,
  FlaskConical,
  Layers3,
  Microscope,
  Plus,
  Target,
  TriangleAlert,
  UploadCloud,
} from "lucide-react";
import { PageHeader, Stat } from "@/components/app/page-header";
import { RunSampleButton } from "@/components/app/run-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Field, Input, Select, Textarea } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/progress";
import { StatusBadge } from "@/components/ui/status-badge";
import { apiClient } from "@/lib/api";
import { useToast } from "@/lib/toast";
import type { DiseasePack, ProjectDetail, Sample } from "@/lib/types";
import {
  errorMessage,
  formatDate,
  formatNumber,
  relativeTime,
  titleCase,
} from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;
  const router = useRouter();
  const { toast } = useToast();

  const { data, loading, error, reload } = useApiData<[ProjectDetail, DiseasePack[]]>(
    () => Promise.all([apiClient.project(projectId), apiClient.packs()]),
    [projectId],
  );

  const project = data?.[0] ?? null;
  const packs = data?.[1] ?? [];
  const { data: packDetail } = useApiData<DiseasePack | null>(
    () => (project ? apiClient.pack(project.disease_pack) : Promise.resolve(null)),
    [project?.disease_pack],
  );
  const activePack =
    packDetail ?? packs.find((item) => item.id === project?.disease_pack) ?? null;

  const [uploadOpen, setUploadOpen] = useState(false);
  const [sampleName, setSampleName] = useState("");
  const [externalId, setExternalId] = useState("");
  const [condition, setCondition] = useState("");
  const [platform, setPlatform] = useState("visium");
  const [notes, setNotes] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function handleUpload(event: React.FormEvent) {
    event.preventDefault();
    if (!project) return;
    setFormError(null);
    setSubmitting(true);
    try {
      const form = new FormData();
      form.append(
        "metadata",
        JSON.stringify({
          name: sampleName.trim() || "Untitled sample",
          sample_id: externalId.trim() || sampleName.trim(),
          disease_pack: project.disease_pack,
          platform,
          species: "human",
          condition: condition.trim(),
          notes: notes.trim(),
        }),
      );
      for (const file of files) form.append("files", file);

      const sample = await apiClient.createSample(project.id, form);
      toast(
        files.length > 0
          ? "Sample uploaded. Review the files, then run the pipeline."
          : "Synthetic demo sample created. Launch a run to build the atlas.",
        "success",
      );
      setUploadOpen(false);
      setSampleName("");
      setExternalId("");
      setCondition("");
      setNotes("");
      setFiles([]);
      reload();
      router.push(`/app/samples/${sample.id}`);
    } catch (err) {
      setFormError(errorMessage(err));
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-4 w-40" />
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

  if (error || !project) {
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
          title="Project not found"
          description={error?.message ?? "This project may have been archived or belongs to another workspace."}
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

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.12em] text-slate">
        <Link href="/app/projects" className="transition hover:text-bone">
          Projects
        </Link>
        <ChevronRight className="size-3" />
        <span className="max-w-[220px] truncate text-bone-dim">{project.name}</span>
      </div>

      <PageHeader
        eyebrow={titleCase(project.disease_pack)}
        title={project.name}
        description={project.description || "No description yet."}
        actions={
          <>
            <Button variant="secondary" onClick={() => setUploadOpen(true)}>
              <UploadCloud className="size-4" />
              Add sample
            </Button>
            <Badge variant={project.archived ? "outline" : "teal"}>
              {project.archived ? "Archived" : "Active"}
            </Badge>
          </>
        }
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Stat
          label="Samples"
          value={formatNumber(project.stats.sample_count)}
          hint="Attached to this project"
        />
        <Stat
          label="Runs"
          value={formatNumber(project.stats.run_count)}
          hint={`${project.stats.completed_runs} completed`}
          tone="teal"
        />
        <Stat
          label="Spots"
          value={formatNumber(project.stats.spots)}
          hint="Total across samples"
          tone="acid"
        />
        <Stat
          label="Created"
          value={formatDate(project.created_at)}
          hint={`Updated ${relativeTime(project.updated_at)}`}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.7fr_1fr]">
        <div className="space-y-5">
          <Card className="overflow-hidden">
            <CardHeader
              title="Samples"
              description="Each sample becomes one or more versioned runs."
              action={
                <Button size="sm" variant="secondary" onClick={() => setUploadOpen(true)}>
                  <Plus className="size-3.5" />
                  Add
                </Button>
              }
            />
            {project.samples.length > 0 ? (
              <div className="divide-y divide-line-soft">
                {project.samples.map((sample) => (
                  <SampleRow key={sample.id} sample={sample} />
                ))}
              </div>
            ) : (
              <div className="p-5">
                <EmptyState
                  compact
                  title="No samples yet"
                  description="Upload Space Ranger files or create a synthetic demo sample to try the pipeline."
                  action={
                    <Button size="sm" onClick={() => setUploadOpen(true)}>
                      <UploadCloud className="size-3.5" />
                      Add a sample
                    </Button>
                  }
                />
              </div>
            )}
          </Card>

          <Card className="overflow-hidden">
            <CardHeader
              title="Runs"
              description="Most recent 20 runs in this project."
              action={
                <Link
                  href={`/app/runs?project_id=${project.id}`}
                  className="inline-flex items-center gap-1 text-[11px] text-acid transition hover:gap-2"
                >
                  All runs
                  <ArrowUpRight className="size-3.5" />
                </Link>
              }
            />
            {project.runs.length > 0 ? (
              <div className="divide-y divide-line-soft">
                {project.runs.map((run) => (
                  <Link
                    key={run.id}
                    href={`/app/runs/${run.id}`}
                    className="group flex items-center gap-3 px-4 py-3.5 transition hover:bg-bone/[0.03] sm:px-5"
                  >
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 font-mono text-[9px] text-teal">
                      {run.status === "succeeded" ? "OK" : run.status.slice(0, 2).toUpperCase()}
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
                          ? `${formatNumber(run.summary.n_spots)} spots · ${formatNumber(run.summary.n_domains ?? 0)} domains · ${run.summary.method}`
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
                  description="Add a sample, then launch the analysis pipeline."
                />
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-5">
          <Card className="overflow-hidden">
            <div
              className="h-1 w-full"
              style={{ background: activePack?.color ?? "var(--color-acid)" }}
            />
            <CardHeader
              title={activePack?.name ?? titleCase(project.disease_pack)}
              description={activePack?.short_name}
              action={<Badge variant="teal">{activePack?.status ?? "pack"}</Badge>}
            />
            <CardBody className="space-y-4">
              <p className="text-xs leading-relaxed text-slate">
                {activePack?.description ??
                  "The disease pack supplies cell types, zone definitions, and target genes for this project."}
              </p>

              {activePack ? (
                <>
                  <div className="grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-line bg-line">
                    {[
                      { icon: Dna, k: "Cell types", v: activePack.cell_type_count },
                      { icon: Layers3, k: "Zones", v: activePack.zone_count },
                      { icon: Target, k: "Targets", v: activePack.target_count },
                    ].map((item) => {
                      const Icon = item.icon;
                      return (
                        <div key={item.k} className="bg-ink-2 px-2 py-2.5 text-center">
                          <Icon className="mx-auto size-3.5 text-teal" />
                          <p className="mt-1.5 font-mono text-sm text-bone">{item.v}</p>
                          <p className="mt-0.5 font-mono text-[8px] uppercase tracking-wider text-slate">
                            {item.k}
                          </p>
                        </div>
                      );
                    })}
                  </div>

                  {activePack.zones ? (
                    <div>
                      <p className="mono-label">Zones</p>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {activePack.zones.map((zone) => (
                          <span
                            key={zone.id}
                            className="inline-flex items-center gap-1.5 rounded-full border border-line bg-ink-3 px-2 py-0.5 text-[10px] text-bone-dim"
                          >
                            <span
                              className="size-1.5 rounded-full"
                              style={{ background: zone.color }}
                            />
                            {zone.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : null}

                  <div className="border-t border-line pt-3">
                    <Link
                      href={`/app/packs/${activePack.id}`}
                      className="inline-flex items-center gap-1.5 text-[11px] text-acid transition hover:gap-2.5"
                    >
                      Open pack details
                      <ArrowUpRight className="size-3" />
                    </Link>
                  </div>
                </>
              ) : null}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Project settings" description="Metadata pinned to every run." />
            <CardBody className="space-y-2.5">
              {[
                ["Disease pack", titleCase(project.disease_pack)],
                ["Project ID", project.id.slice(0, 8)],
                ["Created", formatDate(project.created_at)],
                ["Updated", formatDate(project.updated_at)],
                ["Archived", project.archived ? "Yes" : "No"],
              ].map(([k, v]) => (
                <div key={k} className="flex items-center justify-between gap-3 text-[11px]">
                  <span className="text-slate">{k}</span>
                  <span className="truncate font-mono text-bone-dim">{v}</span>
                </div>
              ))}
            </CardBody>
          </Card>
        </div>
      </div>

      <Modal
        open={uploadOpen}
        onClose={() => {
          setUploadOpen(false);
          setFormError(null);
        }}
        title="Add a sample"
        description="Upload 10x Visium Space Ranger output, or leave files empty to generate a synthetic demo sample."
        className="max-w-xl"
      >
        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Sample name">
              <Input
                required
                value={sampleName}
                onChange={(event) => setSampleName(event.target.value)}
                placeholder="BRCA-01"
                autoFocus
              />
            </Field>
            <Field label="External ID" hint="Optional lab accession.">
              <Input
                value={externalId}
                onChange={(event) => setExternalId(event.target.value)}
                placeholder="LAB-2026-014"
              />
            </Field>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Platform">
              <Select value={platform} onChange={(event) => setPlatform(event.target.value)}>
                <option value="visium">10x Visium</option>
                <option value="demo">Synthetic demo</option>
                <option value="other">Other / unknown</option>
              </Select>
            </Field>
            <Field label="Condition" hint="Optional study annotation.">
              <Input
                value={condition}
                onChange={(event) => setCondition(event.target.value)}
                placeholder="Treatment-naive"
              />
            </Field>
          </div>

          <Field
            label="Visium files"
            hint="Space Ranger output: filtered_feature_bc_matrix.h5 (or matrix.mtx + barcodes + features) and spatial/tissue_positions.csv — or the outs/ folder as one .zip / .tar.gz. Leave empty for synthetic data."
          >
            <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-line bg-ink-3/60 px-4 py-6 text-center transition hover:border-acid/40 hover:bg-ink-3">
              <FileUp className="size-5 text-teal" />
              <span className="text-xs text-bone-dim">
                {files.length > 0
                  ? `${files.length} file${files.length === 1 ? "" : "s"} selected`
                  : "Choose files or drop a zip"}
              </span>
              {files.length > 0 ? (
                <span className="max-w-full truncate font-mono text-[10px] text-slate">
                  {files.map((file) => file.name).join(", ")}
                </span>
              ) : null}
              <input
                type="file"
                multiple
                className="sr-only"
                accept=".h5,.mtx,.gz,.tsv,.csv,.json,.png,.zip,.tar,.tgz"
                onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
              />
            </label>
          </Field>

          <Field label="Notes" hint="Optional context for your team.">
            <Textarea
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Section from the tumor periphery; 10 µm resolution."
            />
          </Field>

          <div className="flex items-start gap-2 rounded-lg border border-amber/20 bg-amber/[0.04] px-3 py-2.5">
            <TriangleAlert className="mt-0.5 size-3.5 shrink-0 text-amber" />
            <p className="text-[10px] leading-relaxed text-amber/80">
              Upload only data you have the right to use. Do not upload identifiable patient data
              without an appropriate agreement. Research use only.
            </p>
          </div>

          {formError ? (
            <p className="rounded-lg border border-coral/30 bg-coral/[0.06] px-3 py-2 text-xs text-coral">
              {formError}
            </p>
          ) : null}

          <div className="flex justify-end gap-2 pt-1">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setUploadOpen(false)}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              {files.length > 0 ? "Upload sample" : "Create demo sample"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

function SampleRow({ sample }: { sample: Sample }) {
  return (
    <div className="group flex flex-col gap-3 px-4 py-3.5 transition hover:bg-bone/[0.03] sm:flex-row sm:items-center sm:px-5">
      <span className="flex size-9 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 text-teal">
        {sample.status === "demo" ? <FlaskConical className="size-4" /> : <Microscope className="size-4" />}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <Link
            href={`/app/samples/${sample.id}`}
            className="truncate text-xs font-medium text-bone hover:text-acid"
          >
            {sample.name}
          </Link>
          <Badge variant={sample.status === "demo" ? "outline" : "teal"}>{sample.status}</Badge>
          {sample.spot_count ? (
            <span className="font-mono text-[9px] text-slate">
              {formatNumber(sample.spot_count)} spots
            </span>
          ) : null}
        </div>
        <p className="mt-1 truncate font-mono text-[10px] text-slate">
          {sample.external_id || sample.id.slice(0, 8)} · {sample.platform} ·{" "}
          {sample.condition || "no condition"} · {relativeTime(sample.created_at)}
        </p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <Link
          href={`/app/samples/${sample.id}`}
          className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-line px-3 text-[11px] text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
        >
          <Boxes className="size-3.5" />
          Open
        </Link>
        <RunSampleButton
          sampleId={sample.id}
          diseasePack={sample.disease_pack}
          label="Run"
          variant="secondary"
        />
      </div>
    </div>
  );
}
