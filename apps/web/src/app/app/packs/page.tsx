"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  ArrowUpRight,
  Blocks,
  Dna,
  Layers3,
  Search,
  ShieldCheck,
  Target,
  TriangleAlert,
} from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/progress";
import { apiClient } from "@/lib/api";
import type { DiseasePack } from "@/lib/types";
import { cn } from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

const filters = [
  { id: "all", label: "All packs" },
  { id: "beta", label: "Beta" },
  { id: "draft", label: "Draft" },
];

export default function PacksPage() {
  const { data, loading, error } = useApiData<DiseasePack[]>(() => apiClient.packs());
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");

  const packs = useMemo(() => data ?? [], [data]);
  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    return packs.filter((pack) => {
      if (filter !== "all" && pack.status !== filter) return false;
      if (!term) return true;
      return (
        pack.name.toLowerCase().includes(term) ||
        pack.tissue.toLowerCase().includes(term) ||
        pack.aliases.some((alias) => alias.toLowerCase().includes(term)) ||
        pack.id.toLowerCase().includes(term)
      );
    });
  }, [packs, filter, query]);

  const counts = {
    beta: packs.filter((pack) => pack.status === "beta").length,
    draft: packs.filter((pack) => pack.status === "draft").length,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Knowledge layer"
        title="Disease packs"
        description="Each pack is a versioned bundle of cell types, markers, spatial zones, target genes, and report sections. The pipeline is shared; the biology is a pack."
        actions={<Badge variant="outline">v0.1.0</Badge>}
      />

      {error ? (
        <div className="flex items-start gap-2.5 rounded-xl border border-coral/30 bg-coral/[0.06] px-4 py-3 text-xs text-coral">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div>
            <p className="font-medium">Could not load disease packs.</p>
            <p className="mt-0.5 text-coral/80">{error.message}</p>
          </div>
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-3">
        <Card className="flex items-center gap-3 px-4 py-3">
          <span className="flex size-9 items-center justify-center rounded-lg border border-line bg-ink-3 text-teal">
            <Blocks className="size-4" />
          </span>
          <div>
            <p className="font-mono text-lg text-bone">{packs.length}</p>
            <p className="text-[10px] text-slate">Available packs</p>
          </div>
        </Card>
        <Card className="flex items-center gap-3 px-4 py-3">
          <span className="flex size-9 items-center justify-center rounded-lg border border-line bg-ink-3 text-acid">
            <ShieldCheck className="size-4" />
          </span>
          <div>
            <p className="font-mono text-lg text-bone">{counts.beta}</p>
            <p className="text-[10px] text-slate">Beta · baseline running</p>
          </div>
        </Card>
        <Card className="flex items-center gap-3 px-4 py-3">
          <span className="flex size-9 items-center justify-center rounded-lg border border-line bg-ink-3 text-amber">
            <Layers3 className="size-4" />
          </span>
          <div>
            <p className="font-mono text-lg text-bone">{counts.draft}</p>
            <p className="text-[10px] text-slate">Draft · in progress</p>
          </div>
        </Card>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-1">
          {filters.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setFilter(item.id)}
              className={cn(
                "rounded-lg px-3 py-1.5 text-[11px] transition focus-ring",
                filter === item.id
                  ? "bg-acid/10 text-acid"
                  : "text-slate hover:bg-bone/5 hover:text-bone",
              )}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="relative w-full sm:max-w-xs">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-slate" />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by cancer, tissue, alias…"
            className="h-9 pl-9 text-xs"
            aria-label="Search disease packs"
          />
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-[240px]" />
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((pack) => (
            <Link
              key={pack.id}
              href={`/app/packs/${pack.id}`}
              className="card card-hover group flex flex-col overflow-hidden"
            >
              <div className="h-1 w-full" style={{ background: pack.color }} />
              <div className="flex flex-1 flex-col p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-sm font-medium text-bone">{pack.name}</h2>
                    <p className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                      {pack.tissue} · {pack.id} · v{pack.version}
                    </p>
                  </div>
                  <Badge variant={pack.status === "beta" ? "teal" : "outline"}>
                    {pack.status}
                  </Badge>
                </div>

                <p className="mt-3 line-clamp-3 text-xs leading-relaxed text-slate">
                  {pack.description}
                </p>

                <div className="mt-4 grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-line bg-line">
                  {[
                    { icon: Dna, value: pack.cell_type_count, label: "cells" },
                    { icon: Layers3, value: pack.zone_count, label: "zones" },
                    { icon: Target, value: pack.target_count, label: "targets" },
                  ].map((item) => {
                    const Icon = item.icon;
                    return (
                      <div key={item.label} className="bg-ink-2 px-2 py-2 text-center">
                        <Icon className="mx-auto size-3 text-slate" />
                        <p className="mt-1 font-mono text-sm text-bone">{item.value}</p>
                        <p className="font-mono text-[8px] uppercase tracking-wider text-slate">
                          {item.label}
                        </p>
                      </div>
                    );
                  })}
                </div>

                <div className="mt-auto flex items-center justify-between gap-2 pt-4">
                  <span className="inline-flex items-center gap-1.5 font-mono text-[9px] uppercase tracking-[0.1em] text-slate">
                    <span
                      className={cn(
                        "size-1.5 rounded-full",
                        pack.data_richness === "high"
                          ? "bg-teal"
                          : pack.data_richness === "medium"
                            ? "bg-amber"
                            : "bg-slate",
                      )}
                    />
                    {pack.data_richness} data richness
                  </span>
                  <ArrowUpRight className="size-3.5 text-slate transition group-hover:text-acid" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No packs match this filter"
          description="Try a different status, cancer name, tissue, or alias."
        />
      )}

      <div className="flex items-start gap-2.5 rounded-xl border border-amber/20 bg-amber/[0.04] px-4 py-3">
        <ShieldCheck className="mt-0.5 size-4 shrink-0 text-amber" />
        <p className="text-[11px] leading-relaxed text-amber/80">
          <span className="font-medium text-amber">Status is validation maturity, not regulatory clearance.</span>{" "}
          Beta = baseline running, validation incomplete. Draft = under development. All packs are
          Research Use Only. No pack is clinically validated.
        </p>
      </div>

      <p className="text-[10px] leading-relaxed text-slate">
        Pack contents are versioned YAML. Adding a disease is a data and validation task — markers,
        zones, target evidence, benchmark samples, expert review — not a new pipeline.
      </p>
    </div>
  );
}
