"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  ArrowUpRight,
  Blocks,
  ChevronRight,
  Dna,
  Plus,
  TriangleAlert,
} from "lucide-react";
import { PageHeader, Stat } from "@/components/app/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/progress";
import { RuoNotice } from "@/components/ui/ruo-notice";
import { apiClient } from "@/lib/api";
import type { DiseasePack } from "@/lib/types";
import { titleCase } from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

const evidenceTone = {
  established: "teal",
  emerging: "amber",
  exploratory: "outline",
} as const;

export default function PackDetailPage() {
  const params = useParams<{ id: string }>();
  const packId = params.id;
  const { data: pack, loading, error } = useApiData<DiseasePack>(
    () => apiClient.pack(packId),
    [packId],
  );

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

  if (error || !pack) {
    return (
      <div className="space-y-5">
        <Link
          href="/app/packs"
          className="inline-flex items-center gap-1.5 text-xs text-slate transition hover:text-bone"
        >
          <ArrowLeft className="size-3.5" />
          Disease packs
        </Link>
        <EmptyState
          title="Pack not found"
          description={error?.message ?? "This disease pack is not available in this workspace."}
          action={
            <Link
              href="/app/packs"
              className="inline-flex h-9 items-center rounded-xl bg-acid px-4 text-xs font-medium text-ink"
            >
              Back to packs
            </Link>
          }
        />
      </div>
    );
  }

  const metrics = Object.entries(pack.validation.metrics ?? {});

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.12em] text-slate">
        <Link href="/app/packs" className="transition hover:text-bone">
          Disease packs
        </Link>
        <ChevronRight className="size-3" />
        <span className="text-bone-dim">{pack.id}</span>
      </div>

      <PageHeader
        eyebrow={`${pack.tissue} · v${pack.version}`}
        title={pack.name}
        description={pack.description}
        actions={
          <>
            <Badge variant={pack.status === "beta" ? "teal" : "outline"}>{pack.status}</Badge>
            <Link
              href={`/app/projects?new=1&pack=${pack.id}`}
              className="inline-flex h-10 items-center gap-2 rounded-xl bg-acid px-4 text-sm font-medium text-ink transition hover:bg-[#d6ff6a]"
            >
              <Plus className="size-4" />
              New project
            </Link>
          </>
        }
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Cell types" value={pack.cell_type_count} hint="Reference profiles" tone="teal" />
        <Stat label="Spatial zones" value={pack.zone_count} hint="Marker-labeled domains" />
        <Stat label="Target genes" value={pack.target_count} hint="Evidence-graded" tone="acid" />
        <Stat
          label="Data richness"
          value={titleCase(pack.data_richness)}
          hint={`${pack.reference.minimum_samples ?? "—"} minimum reference samples`}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.6fr_1fr]">
        <div className="space-y-5">
          <Card className="overflow-hidden">
            <CardHeader
              title="Cell types"
              description="Profiles the deconvolution can resolve for this tissue."
              action={<Badge variant="outline">{pack.cell_type_count}</Badge>}
            />
            <CardBody className="grid gap-2.5 sm:grid-cols-2">
              {(pack.cell_types ?? []).map((cellType) => (
                <div
                  key={cellType.id}
                  className="rounded-xl border border-line bg-ink-3/50 px-3 py-2.5"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className="size-2 rounded-full"
                      style={{ background: cellType.color }}
                    />
                    <p className="text-xs font-medium text-bone">{cellType.name}</p>
                    <span className="ml-auto font-mono text-[9px] text-slate">{cellType.id}</span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {cellType.markers.map((marker) => (
                      <span
                        key={marker}
                        className="rounded border border-line bg-ink-2 px-1.5 py-0.5 font-mono text-[9px] text-bone-dim"
                      >
                        {marker}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>

          <Card className="overflow-hidden">
            <CardHeader
              title="Spatial zones"
              description="Domain labels come from zone marker scores, not pathology."
              action={<Badge variant="outline">{pack.zone_count}</Badge>}
            />
            <CardBody className="grid gap-2.5 sm:grid-cols-2">
              {(pack.zones ?? []).map((zone) => (
                <div key={zone.id} className="overflow-hidden rounded-xl border border-line">
                  <div className="h-0.5 w-full" style={{ background: zone.color }} />
                  <div className="bg-ink-3/50 px-3 py-2.5">
                    <p className="text-xs font-medium text-bone">{zone.name}</p>
                    <p className="mt-1 text-[10px] leading-relaxed text-slate">
                      {zone.description || "No description in this pack."}
                    </p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {zone.markers.map((marker) => (
                        <span
                          key={marker}
                          className="rounded border border-line bg-ink-2 px-1.5 py-0.5 font-mono text-[9px] text-bone-dim"
                        >
                          {marker}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>

          <Card className="overflow-hidden">
            <CardHeader
              title="Target genes"
              description="Research prioritization only — not a therapy recommendation."
              action={<Badge variant="amber">{pack.target_count} targets</Badge>}
            />
            <div className="divide-y divide-line-soft">
              {(pack.targets ?? []).map((target) => (
                <div key={target.gene} className="flex items-start gap-3 px-4 py-3 sm:px-5">
                  <span className="flex size-8 shrink-0 items-center justify-center rounded-lg border border-line bg-ink-3 font-mono text-[9px] text-teal">
                    {target.gene.slice(0, 3)}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-mono text-[11px] text-bone">{target.gene}</p>
                      <span className="text-[10px] text-slate">{target.name}</span>
                      <Badge variant={evidenceTone[target.evidence_level] ?? "outline"}>
                        {target.evidence_level}
                      </Badge>
                    </div>
                    <p className="mt-1 text-[10px] leading-relaxed text-slate">{target.rationale}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-5">
          {pack.not_assessed?.length ? (
            <Card className="border-amber/20">
              <CardHeader
                title="Not assessed"
                description="Spatial transcriptomics cannot establish these."
              />
              <CardBody className="space-y-1.5">
                {pack.not_assessed.map((item) => (
                  <p key={item} className="text-[11px] leading-relaxed text-bone-dim">
                    · {item}
                  </p>
                ))}
              </CardBody>
            </Card>
          ) : null}

          <Card>
            <CardHeader title="Validation status" description="Maturity, not clearance." />
            <CardBody className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-slate">Pack status</span>
                <Badge variant={pack.status === "beta" ? "teal" : "outline"}>{pack.status}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-slate">Last validation run</span>
                <span className="font-mono text-[10px] text-bone-dim">
                  {pack.validation.last_run ?? "Not recorded"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-slate">Approved by</span>
                <span className="font-mono text-[10px] text-bone-dim">
                  {pack.validation.approved_by ?? "Pending"}
                </span>
              </div>

              {metrics.length > 0 ? (
                <div className="space-y-2 border-t border-line pt-3">
                  {metrics.map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between text-[11px]">
                      <span className="text-slate">{titleCase(key)}</span>
                      <span className="font-mono text-bone-dim">{String(value)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-lg border border-amber/20 bg-amber/[0.04] px-3 py-2.5">
                  <p className="text-[10px] leading-relaxed text-amber/80">
                    Held-out validation is not recorded for this pack version. The synthetic
                    benchmark is reported per run; it is not clinical validation.
                  </p>
                </div>
              )}

              <Link
                href="/docs#validation"
                className="inline-flex items-center gap-1.5 border-t border-line pt-3 text-[11px] text-acid transition hover:gap-2.5"
              >
                Read the validation method
                <ArrowUpRight className="size-3" />
              </Link>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Reference sources" description="What the signatures are built from." />
            <CardBody className="space-y-4">
              <div>
                <p className="mono-label">Single-cell references</p>
                <ul className="mt-2 space-y-1.5">
                  {(pack.reference.scrna_sources ?? []).map((source) => (
                    <li key={source} className="flex items-start gap-2 text-[11px] text-bone-dim">
                      <Dna className="mt-0.5 size-3 shrink-0 text-teal" />
                      {source}
                    </li>
                  ))}
                  {(pack.reference.scrna_sources ?? []).length === 0 ? (
                    <li className="text-[11px] text-slate">Not specified.</li>
                  ) : null}
                </ul>
              </div>
              <div>
                <p className="mono-label">Spatial references</p>
                <ul className="mt-2 space-y-1.5">
                  {(pack.reference.spatial_sources ?? []).map((source) => (
                    <li key={source} className="flex items-start gap-2 text-[11px] text-bone-dim">
                      <Blocks className="mt-0.5 size-3 shrink-0 text-acid" />
                      {source}
                    </li>
                  ))}
                  {(pack.reference.spatial_sources ?? []).length === 0 ? (
                    <li className="text-[11px] text-slate">Not specified.</li>
                  ) : null}
                </ul>
              </div>
              <div className="flex items-center justify-between border-t border-line pt-3 text-[11px]">
                <span className="text-slate">Minimum samples</span>
                <span className="font-mono text-bone-dim">
                  {pack.reference.minimum_samples ?? "—"}
                </span>
              </div>
            </CardBody>
          </Card>

          {pack.atlas_reference ? (
            <Card>
              <CardHeader
                title="Independent atlas check"
                description="Zones are compared with an external atlas on real samples."
                action={
                  <Badge
                    variant={pack.atlas_reference.license_status === "cleared" ? "teal" : "amber"}
                  >
                    {pack.atlas_reference.license_status.replace("_", " ")}
                  </Badge>
                }
              />
              <CardBody className="space-y-1.5 text-[11px] leading-relaxed">
                <p className="text-bone-dim">{pack.atlas_reference.name}</p>
                <p className="text-[10px] text-slate">{pack.atlas_reference.citation}</p>
              </CardBody>
            </Card>
          ) : null}

          <Card>
            <CardHeader title="Pack facts" />
            <CardBody className="space-y-2.5">
              {[
                ["Pack ID", pack.id],
                ["Version", pack.version],
                ["Tissue", pack.tissue],
                ["Aliases", pack.aliases.join(", ") || "—"],
                ["L–R pairs", String(pack.ligand_receptor_count ?? 0)],
              ].map(([key, value]) => (
                <div key={key} className="flex items-center justify-between gap-3 text-[11px]">
                  <span className="text-slate">{key}</span>
                  <span className="max-w-[60%] truncate font-mono text-bone-dim">{value}</span>
                </div>
              ))}
            </CardBody>
          </Card>

          <RuoNotice />
        </div>
      </div>

      <div className="flex items-start gap-2.5 rounded-xl border border-line bg-ink-2/60 px-4 py-3">
        <TriangleAlert className="mt-0.5 size-4 shrink-0 text-amber" />
        <p className="text-[10px] leading-relaxed text-slate">
          Pack markers and zones are research annotations. They are not diagnostic criteria and do
          not replace pathologist review. Validate pack suitability for your tissue, platform, and
          population before relying on results.
        </p>
      </div>
    </div>
  );
}
