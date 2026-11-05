"use client";

import { CircleDot, Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import type { AtlasCheck, Interaction, MethodConcordance, ResultPayload } from "@/lib/types";
import { cn, titleCase } from "@/lib/utils";

function domainLabel(payload: ResultPayload, id: string | null | undefined) {
  if (!id) return "—";
  return payload.domains_summary.find((domain) => domain.id === id)?.name ?? titleCase(id);
}

function formatQ(value: number | null) {
  if (value === null) return "—";
  return value < 0.001 ? "<0.001" : value.toFixed(3);
}

/** Ligand–receptor results (ported from Glio-Cartography's signaling view). */
export function CommunicationView({ payload }: { payload: ResultPayload }) {
  const interactions: Interaction[] = payload.communication ?? [];
  if (interactions.length === 0) {
    return (
      <EmptyState
        title="No ligand–receptor pairs"
        description="This disease pack does not define curated ligand–receptor pairs yet."
      />
    );
  }
  const maxScore = Math.max(...interactions.map((item) => item.score ?? 0), 1e-9);
  const significant = interactions.filter((item) => item.significant).length;

  return (
    <div className="grid gap-5 xl:grid-cols-[1.6fr_0.7fr]">
      <Card>
        <CardHeader
          title="Ligand–receptor co-localization"
          description="Curated pairs from the disease pack, scored on this sample."
          action={
            <Badge variant={significant ? "teal" : "outline"}>
              {significant}/{interactions.length} significant
            </Badge>
          }
        />
        <CardBody className="overflow-x-auto p-0">
          <table className="w-full min-w-[560px] text-left text-[11px]">
            <thead className="border-b border-line font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
              <tr>
                <th className="px-4 py-2.5 font-normal">Pair</th>
                <th className="px-3 py-2.5 font-normal">Sender → receiver</th>
                <th className="px-3 py-2.5 font-normal">Score</th>
                <th className="px-3 py-2.5 font-normal">q (BH)</th>
                <th className="px-4 py-2.5 font-normal">Strongest domain</th>
              </tr>
            </thead>
            <tbody>
              {interactions.map((item) => (
                <tr key={item.id} className="border-b border-line/60 last:border-0">
                  <td className="px-4 py-2.5">
                    <p className="font-mono text-bone">{item.name}</p>
                    {item.category ? (
                      <p className="mt-0.5 text-[10px] text-slate">{item.category}</p>
                    ) : null}
                  </td>
                  <td className="px-3 py-2.5 text-bone-dim">
                    {titleCase(item.sender)} → {titleCase(item.receiver)}
                  </td>
                  {item.tested ? (
                    <>
                      <td className="px-3 py-2.5">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-ink-3">
                            <div
                              className={cn(
                                "h-full rounded-full",
                                item.significant ? "bg-teal" : "bg-slate/50",
                              )}
                              style={{ width: `${((item.score ?? 0) / maxScore) * 100}%` }}
                            />
                          </div>
                          <span className="font-mono text-[10px] text-slate">
                            {(item.score ?? 0).toFixed(3)}
                          </span>
                        </div>
                      </td>
                      <td
                        className={cn(
                          "px-3 py-2.5 font-mono",
                          item.significant ? "text-teal" : "text-slate",
                        )}
                      >
                        {formatQ(item.q_value)}
                      </td>
                      <td className="px-4 py-2.5 text-bone-dim">
                        {domainLabel(payload, item.top_domain)}
                      </td>
                    </>
                  ) : (
                    <td colSpan={3} className="px-3 py-2.5 text-slate">
                      Not tested — missing {item.missing.join(", ")}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="How to read this" />
        <CardBody className="space-y-2.5 text-[11px] leading-relaxed text-slate">
          <p>
            The score adds same-spot and neighbour co-expression of the ligand (weighted by sender
            abundance) and the receptor (weighted by receiver abundance).
          </p>
          <p>
            q-values come from a spatial permutation test — receiver signal is shuffled across
            spots — with Benjamini–Hochberg correction across pairs.
          </p>
          <p className="flex items-start gap-2 text-amber">
            <CircleDot className="mt-0.5 size-3.5 shrink-0" />
            Co-expression suggests possible signalling; it does not prove it.
          </p>
        </CardBody>
      </Card>
    </div>
  );
}

function AtlasBody({ atlas }: { atlas: AtlasCheck }) {
  if (atlas.status !== "ok") {
    return <p className="text-[11px] leading-relaxed text-slate">{atlas.reason}</p>;
  }
  return (
    <div className="space-y-2 text-[11px] text-bone-dim">
      <div className="flex items-center justify-between">
        <span className="text-slate">Zone ↔ structure correlation</span>
        <span className="font-mono text-bone">{atlas.diagonal_mean ?? "—"}</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-slate">Top-1 match</span>
        <span className="font-mono text-bone">
          {atlas.top1_accuracy ?? "—"} ({atlas.n_zones_compared} zones)
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-slate">Genes compared</span>
        <span className="font-mono text-bone">{atlas.n_genes}</span>
      </div>
      {atlas.excluded_genes?.length ? (
        <p className="text-[10px] text-slate">
          Zone-marker genes excluded to avoid circularity: {atlas.excluded_genes.join(", ")}
        </p>
      ) : null}
      <p className="text-[10px] text-slate">{atlas.note}</p>
    </div>
  );
}

/** Method agreement + independent atlas check (both from Glio-Cartography). */
export function ReliabilityCard({ payload }: { payload: ResultPayload }) {
  const concordance: MethodConcordance | null = payload.validation?.method_concordance ?? null;
  const atlas: AtlasCheck | null = payload.validation?.atlas_check ?? null;
  const agreementLow = concordance ? concordance.mean_spot_agreement < 0.7 : false;

  return (
    <Card>
      <CardHeader
        title="Reliability checks"
        description="Signals that do not depend on synthetic ground truth."
      />
      <CardBody className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs text-bone">Deconvolution method agreement</p>
            {concordance ? (
              <Badge variant={agreementLow ? "amber" : "teal"}>
                {concordance.mean_spot_agreement.toFixed(2)}
              </Badge>
            ) : (
              <Badge variant="outline">n/a</Badge>
            )}
          </div>
          <p className="text-[11px] leading-relaxed text-slate">
            {concordance
              ? `${concordance.methods.join(" vs ")} · cell-type Pearson ${
                  concordance.mean_cell_type_pearson ?? "—"
                }. Disagreement raises each spot's uncertainty.`
              : "Only one method ran for this sample."}
          </p>
        </div>

        <div className="space-y-2 border-t border-line pt-4">
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs text-bone">{atlas ? atlas.name : "External atlas check"}</p>
            <Badge variant={atlas?.status === "ok" ? "teal" : "outline"}>
              {atlas ? (atlas.status === "ok" ? "compared" : "skipped") : "none"}
            </Badge>
          </div>
          {atlas ? (
            <>
              <AtlasBody atlas={atlas} />
              <p className="flex items-start gap-1.5 text-[10px] text-slate">
                <Info className="mt-0.5 size-3 shrink-0" />
                {atlas.citation}
              </p>
            </>
          ) : (
            <p className="text-[11px] text-slate">
              This disease pack has no independent atlas reference yet.
            </p>
          )}
        </div>
      </CardBody>
    </Card>
  );
}

/** What the analysis cannot establish (Glio-Cartography's "not assessed" list). */
export function NotAssessedNotice({ items }: { items: string[] | undefined }) {
  if (!items?.length) return null;
  return (
    <div className="rounded-2xl border border-amber/25 bg-amber/5 px-4 py-3">
      <p className="text-xs font-medium text-amber">Not assessed by this analysis</p>
      <ul className="mt-1.5 grid gap-x-6 gap-y-1 text-[11px] text-bone-dim sm:grid-cols-2">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-1.5">
            <CircleDot className="mt-0.5 size-3 shrink-0 text-amber/70" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
