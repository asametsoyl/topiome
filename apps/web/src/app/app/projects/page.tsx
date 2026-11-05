"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import { ArrowUpRight, Plus, Search, TriangleAlert } from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Field, Input, Select, Textarea } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/progress";
import { apiClient } from "@/lib/api";
import { useToast } from "@/lib/toast";
import type { DiseasePack, Project } from "@/lib/types";
import { errorMessage, relativeTime, titleCase } from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

function ProjectsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const { data, loading, error } = useApiData<[Project[], DiseasePack[]]>(() =>
    Promise.all([apiClient.projects(), apiClient.packs()]),
  );
  const [createOpen, setCreateOpen] = useState(searchParams.get("new") === "1");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [packId, setPackId] = useState(searchParams.get("pack") ?? "breast");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const projects = useMemo(() => data?.[0] ?? [], [data]);
  const packs = useMemo(() => data?.[1] ?? [], [data]);
  const packMap = useMemo(() => new Map(packs.map((pack) => [pack.id, pack])), [packs]);

  // React to ?new=1&pack=… links (state adjusted during render, not in an effect).
  const paramsKey = searchParams.toString();
  const [seenParams, setSeenParams] = useState(paramsKey);
  if (seenParams !== paramsKey) {
    setSeenParams(paramsKey);
    if (searchParams.get("new") === "1") setCreateOpen(true);
    const packParam = searchParams.get("pack");
    if (packParam) setPackId(packParam);
  }

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return projects;
    return projects.filter(
      (project) =>
        project.name.toLowerCase().includes(term) ||
        project.description.toLowerCase().includes(term) ||
        project.disease_pack.toLowerCase().includes(term),
    );
  }, [projects, query]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      const project = await apiClient.createProject({
        name: name.trim(),
        description: description.trim(),
        disease_pack: packId,
      });
      toast("Project created.", "success");
      setCreateOpen(false);
      router.push(`/app/projects/${project.id}`);
    } catch (err) {
      setFormError(errorMessage(err));
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Research"
        title="Projects"
        description="A project groups samples, runs, and reports for one study. Pick the disease pack that matches the tissue."
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="size-4" />
            New project
          </Button>
        }
      />

      {error ? (
        <div className="flex items-start gap-2.5 rounded-xl border border-coral/30 bg-coral/[0.06] px-4 py-3 text-xs text-coral">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div>
            <p className="font-medium">Could not load projects.</p>
            <p className="mt-0.5 text-coral/80">{error.message}</p>
          </div>
        </div>
      ) : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:max-w-xs">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-slate" />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search projects…"
            className="pl-9"
            aria-label="Search projects"
          />
        </div>
        <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-slate">
          {filtered.length} project{filtered.length === 1 ? "" : "s"}
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-[190px]" />
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((project) => {
            const pack = packMap.get(project.disease_pack);
            return (
              <Link
                key={project.id}
                href={`/app/projects/${project.id}`}
                className="card card-hover group flex flex-col overflow-hidden"
              >
                <div
                  className="h-1 w-full opacity-90"
                  style={{ background: pack?.color ?? "var(--color-acid)" }}
                />
                <div className="flex flex-1 flex-col p-5">
                  <div className="flex items-start justify-between gap-3">
                    <span
                      className="flex size-9 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 text-[10px] font-medium uppercase"
                      style={{ color: pack?.color ?? "var(--color-teal)" }}
                    >
                      {project.disease_pack.slice(0, 2)}
                    </span>
                    <Badge variant={pack?.status === "beta" ? "teal" : "outline"}>
                      {pack?.status ?? "pack"}
                    </Badge>
                  </div>

                  <h2 className="mt-4 text-sm font-medium text-bone">{project.name}</h2>
                  <p className="mt-1 line-clamp-2 min-h-[32px] text-xs leading-relaxed text-slate">
                    {project.description || "No description yet."}
                  </p>

                  <div className="mt-auto flex items-center justify-between gap-2 border-t border-line pt-3">
                    <div className="min-w-0">
                      <p className="truncate font-mono text-[10px] uppercase tracking-[0.1em] text-slate">
                        {pack?.short_name ?? titleCase(project.disease_pack)}
                      </p>
                      <p className="mt-0.5 font-mono text-[9px] text-slate/70">
                        updated {relativeTime(project.updated_at)}
                      </p>
                    </div>
                    <ArrowUpRight className="size-4 shrink-0 text-slate transition group-hover:text-acid" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title={query ? "No matching projects" : "No projects yet"}
          description={
            query
              ? "Try a different name, description, or disease pack."
              : "Create a project to group samples and runs for a study. The demo workspace already includes one."
          }
          action={
            query ? (
              <Button variant="secondary" onClick={() => setQuery("")}>
                Clear search
              </Button>
            ) : (
              <Button onClick={() => setCreateOpen(true)}>
                <Plus className="size-4" />
                Create a project
              </Button>
            )
          }
        />
      )}

      <Modal
        open={createOpen}
        onClose={() => {
          setCreateOpen(false);
          setFormError(null);
        }}
        title="New project"
        description="Projects pin a disease pack for their samples. You can still override the pack per run."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <Field label="Project name">
            <Input
              required
              minLength={2}
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Breast cancer spatial atlas"
              autoFocus
            />
          </Field>
          <Field label="Disease pack">
            <Select value={packId} onChange={(event) => setPackId(event.target.value)}>
              {packs.map((pack) => (
                <option key={pack.id} value={pack.id}>
                  {pack.name} · {pack.status}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Description" hint="Optional — what question is this study asking?">
            <Textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Characterize tumor-immune spatial niches in treatment-naive samples."
            />
          </Field>

          {formError ? (
            <p className="rounded-lg border border-coral/30 bg-coral/[0.06] px-3 py-2 text-xs text-coral">
              {formError}
            </p>
          ) : null}

          <div className="flex justify-end gap-2 pt-1">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setCreateOpen(false)}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              Create project
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default function ProjectsPage() {
  return (
    <Suspense
      fallback={
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-[190px]" />
          ))}
        </div>
      }
    >
      <ProjectsContent />
    </Suspense>
  );
}
