"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Crosshair,
  Layers,
  Maximize2,
  Minus,
  MousePointer2,
  Plus,
  RotateCcw,
  ShieldQuestion,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn, formatNumber, titleCase } from "@/lib/utils";
import type { ResultPayload, Spot } from "@/lib/types";

type ViewMode = "domain" | "celltype" | "uncertainty";

const CELL_COLORS = [
  "#5FE0C0",
  "#C8F751",
  "#FFB86B",
  "#FF6B6B",
  "#8DB6D9",
  "#B08BBB",
  "#E8B4B8",
  "#7FB77E",
  "#6FA8DC",
  "#F2D06B",
  "#9AD0C2",
  "#D08B5B",
];

const FALLBACK_DOMAIN = "#7A8A80";

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function hexToRgb(hex: string): [number, number, number] {
  const cleaned = hex.replace("#", "");
  const full =
    cleaned.length === 3
      ? cleaned
          .split("")
          .map((char) => char + char)
          .join("")
      : cleaned;
  const value = Number.parseInt(full, 16);
  if (!Number.isFinite(value)) return [122, 138, 128];
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
}

function mix(a: string, b: string, t: number): string {
  const [ar, ag, ab] = hexToRgb(a);
  const [br, bg, bb] = hexToRgb(b);
  const ratio = clamp(t, 0, 1);
  return `rgb(${Math.round(ar + (br - ar) * ratio)}, ${Math.round(
    ag + (bg - ag) * ratio,
  )}, ${Math.round(ab + (bb - ab) * ratio)})`;
}

function uncertaintyColor(value: number): string {
  const v = clamp(value, 0, 1);
  return v < 0.5 ? mix("#5FE0C0", "#FFB86B", v / 0.5) : mix("#FFB86B", "#FF6B6B", (v - 0.5) / 0.5);
}

interface HitSpot {
  x: number;
  y: number;
  radius: number;
  index: number;
}

export function SpatialMap({
  payload,
  className,
}: {
  payload: ResultPayload;
  className?: string;
}) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const hitsRef = useRef<HitSpot[]>([]);
  const dragRef = useRef<{ x: number; y: number; panX: number; panY: number } | null>(null);

  const [size, setSize] = useState({ width: 0, height: 0 });
  const [mode, setMode] = useState<ViewMode>("domain");
  const [pickedCellType, setSelectedCellType] = useState<string>("");
  const [dragging, setDragging] = useState(false);
  const [focusDomain, setFocusDomain] = useState<string | null>(null);
  const [dimUncertain, setDimUncertain] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [hovered, setHovered] = useState<number | null>(null);
  const [tooltip, setTooltip] = useState({ x: 0, y: 0 });

  const spots = payload.spots;
  const cellTypes = useMemo(() => Object.keys(payload.composition ?? {}), [payload.composition]);
  const selectedCellType = cellTypes.includes(pickedCellType)
    ? pickedCellType
    : (cellTypes[0] ?? "");
  const domainColor = useMemo(() => {
    const map = new Map<string, string>();
    for (const domain of payload.domains_summary ?? []) map.set(domain.id, domain.color);
    for (const spot of spots) {
      if (!map.has(spot.domain)) map.set(spot.domain, FALLBACK_DOMAIN);
    }
    return map;
  }, [payload.domains_summary, spots]);

  useEffect(() => {
    const element = wrapperRef.current;
    if (!element) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) return;
      const { width, height } = entry.contentRect;
      setSize({ width, height });
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const selectedIndex = selectedCellType ? cellTypes.indexOf(selectedCellType) : 0;
  const selectedColor = CELL_COLORS[selectedIndex % CELL_COLORS.length];
  const domainStats = useMemo(() => {
    const map = new Map<string, { count: number; pct: number; name: string; color: string }>();
    for (const domain of payload.domains_summary ?? []) {
      map.set(domain.id, {
        count: domain.count,
        pct: domain.pct,
        name: domain.name,
        color: domain.color,
      });
    }
    if (map.size === 0) {
      for (const spot of spots) {
        const current = map.get(spot.domain) ?? {
          count: 0,
          pct: 0,
          name: spot.domain_name ?? titleCase(spot.domain),
          color: FALLBACK_DOMAIN,
        };
        current.count += 1;
        map.set(spot.domain, current);
      }
      for (const value of map.values()) {
        value.pct = (value.count / Math.max(spots.length, 1)) * 100;
      }
    }
    return [...map.entries()]
      .map(([id, value]) => ({ id, ...value }))
      .sort((a, b) => b.count - a.count);
  }, [payload.domains_summary, spots]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || spots.length === 0 || size.width === 0 || size.height === 0) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(size.width * dpr);
    canvas.height = Math.round(size.height * dpr);
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, size.width, size.height);
    context.fillStyle = "#080e0a";
    context.fillRect(0, 0, size.width, size.height);

    // Subtle grid.
    context.strokeStyle = "rgba(200, 247, 81, 0.055)";
    context.lineWidth = 1;
    const grid = 36;
    for (let x = 0; x <= size.width; x += grid) {
      context.beginPath();
      context.moveTo(x + 0.5, 0);
      context.lineTo(x + 0.5, size.height);
      context.stroke();
    }
    for (let y = 0; y <= size.height; y += grid) {
      context.beginPath();
      context.moveTo(0, y + 0.5);
      context.lineTo(size.width, y + 0.5);
      context.stroke();
    }

    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;
    for (const spot of spots) {
      if (spot.x < minX) minX = spot.x;
      if (spot.x > maxX) maxX = spot.x;
      if (spot.y < minY) minY = spot.y;
      if (spot.y > maxY) maxY = spot.y;
    }
    const spanX = Math.max(maxX - minX, 1e-9);
    const spanY = Math.max(maxY - minY, 1e-9);
    const padding = 26;
    const fitScale = Math.min(
      (size.width - padding * 2) / spanX,
      (size.height - padding * 2) / spanY,
    );
    const scale = fitScale * zoom;

    const drawWidth = spanX * scale;
    const drawHeight = spanY * scale;
    const originX = (size.width - drawWidth) / 2 + pan.x;
    const originY = (size.height - drawHeight) / 2 + pan.y;

    const project = (spot: Spot) => ({
      x: originX + (spot.x - minX) * scale,
      y: originY + (spot.y - minY) * scale,
    });

    const radius = clamp(Math.sqrt((size.width * size.height) / (spots.length * 2.6)) * 0.5, 2.4, 7.5);

    const maxCellValue = Math.max(
      1e-6,
      ...spots.map((spot) => Number(spot.composition?.[selectedCellType] ?? 0)),
    );

    const hits: HitSpot[] = [];
    for (let index = 0; index < spots.length; index += 1) {
      const spot = spots[index];
      const position = project(spot);
      if (
        position.x < -radius ||
        position.x > size.width + radius ||
        position.y < -radius ||
        position.y > size.height + radius
      ) {
        continue;
      }

      let color = FALLBACK_DOMAIN;
      let alpha = 0.92;

      if (mode === "domain") {
        color = domainColor.get(spot.domain) ?? FALLBACK_DOMAIN;
        if (focusDomain && spot.domain !== focusDomain) alpha = 0.14;
      } else if (mode === "celltype") {
        const value = Number(spot.composition?.[selectedCellType] ?? 0);
        const normalized = clamp(value / maxCellValue, 0, 1);
        color = selectedColor;
        alpha = 0.16 + Math.pow(normalized, 0.75) * 0.84;
      } else {
        color = uncertaintyColor(spot.uncertainty);
        alpha = 0.92;
      }

      if (dimUncertain && spot.uncertainty > 0.7 && mode !== "uncertainty") {
        alpha *= 0.2;
      }

      context.globalAlpha = alpha;
      context.fillStyle = color;
      context.beginPath();
      context.arc(position.x, position.y, radius, 0, Math.PI * 2);
      context.fill();

      if (index === hovered) {
        context.globalAlpha = 1;
        context.strokeStyle = "#f3f0e8";
        context.lineWidth = 1.6;
        context.beginPath();
        context.arc(position.x, position.y, radius + 2.5, 0, Math.PI * 2);
        context.stroke();
      }

      hits.push({ x: position.x, y: position.y, radius: radius + 4, index });
    }

    context.globalAlpha = 1;
    hitsRef.current = hits;

    // Scale hint and count overlay.
    context.font = "500 9px var(--font-geist-mono), monospace";
    context.fillStyle = "rgba(138, 147, 140, 0.85)";
    context.fillText(`n = ${formatNumber(spots.length)} spots`, 12, size.height - 12);
    context.textAlign = "right";
    context.fillText(mode === "domain" ? "domain map" : mode === "celltype" ? selectedCellType : "uncertainty", size.width - 12, size.height - 12);
    context.textAlign = "left";
  }, [
    spots,
    size,
    mode,
    selectedCellType,
    selectedColor,
    domainColor,
    focusDomain,
    dimUncertain,
    zoom,
    pan,
    hovered,
  ]);

  function handlePointerDown(event: React.PointerEvent<HTMLCanvasElement>) {
    const canvas = event.currentTarget;
    canvas.setPointerCapture(event.pointerId);
    dragRef.current = { x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
    setDragging(true);
  }

  function handlePointerMove(event: React.PointerEvent<HTMLCanvasElement>) {
    const drag = dragRef.current;
    if (drag) {
      setPan({
        x: drag.panX + (event.clientX - drag.x),
        y: drag.panY + (event.clientY - drag.y),
      });
      return;
    }

    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    let nearest: HitSpot | null = null;
    let best = Infinity;
    for (const hit of hitsRef.current) {
      const distance = (hit.x - x) ** 2 + (hit.y - y) ** 2;
      if (distance < best && distance <= hit.radius ** 2) {
        best = distance;
        nearest = hit;
      }
    }

    if (nearest) {
      if (hovered !== nearest.index) setHovered(nearest.index);
      setTooltip({ x, y });
    } else if (hovered !== null) {
      setHovered(null);
    }
  }

  function handlePointerUp() {
    dragRef.current = null;
    setDragging(false);
  }

  function resetView() {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setHovered(null);
  }

  const hoveredSpot = hovered !== null ? spots[hovered] : null;
  const hoveredComposition = hoveredSpot
    ? Object.entries(hoveredSpot.composition ?? {})
        .sort((a, b) => b[1] - a[1])
        .slice(0, 4)
    : [];

  return (
    <div className={cn("relative flex flex-col overflow-hidden rounded-2xl border border-line bg-ink-2", className)}>
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2.5">
        <div className="flex rounded-lg border border-line bg-ink-3/70 p-0.5">
          {[
            { id: "domain" as const, label: "Domains", icon: Layers },
            { id: "celltype" as const, label: "Cell types", icon: MousePointer2 },
            { id: "uncertainty" as const, label: "Uncertainty", icon: ShieldQuestion },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setMode(item.id)}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-[10px] transition focus-ring",
                  mode === item.id
                    ? "bg-acid/15 text-acid"
                    : "text-slate hover:bg-bone/5 hover:text-bone",
                )}
              >
                <Icon className="size-3" />
                <span className="hidden sm:inline">{item.label}</span>
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-1.5">
          {mode === "celltype" ? (
            <select
              value={selectedCellType}
              onChange={(event) => setSelectedCellType(event.target.value)}
              className="h-8 rounded-lg border border-line bg-ink-3 px-2 text-[10px] text-bone outline-none focus:border-acid/50"
              aria-label="Cell type layer"
            >
              {cellTypes.map((cellType) => (
                <option key={cellType} value={cellType}>
                  {titleCase(cellType)}
                </option>
              ))}
            </select>
          ) : null}

          {mode !== "uncertainty" ? (
            <button
              type="button"
              onClick={() => setDimUncertain((value) => !value)}
              className={cn(
                "inline-flex h-8 items-center gap-1.5 rounded-lg border px-2 text-[10px] transition focus-ring",
                dimUncertain
                  ? "border-coral/40 bg-coral/10 text-coral"
                  : "border-line text-slate hover:text-bone",
              )}
              title="Dim spots with uncertainty above 0.70"
            >
              <Crosshair className="size-3" />
              <span className="hidden md:inline">Dim uncertain</span>
            </button>
          ) : null}

          <div className="flex items-center rounded-lg border border-line bg-ink-3/70">
            <button
              type="button"
              onClick={() => setZoom((value) => clamp(value / 1.25, 1, 8))}
              className="flex size-8 items-center justify-center text-slate transition hover:text-bone focus-ring"
              aria-label="Zoom out"
            >
              <Minus className="size-3" />
            </button>
            <span className="w-9 text-center font-mono text-[9px] text-slate">
              {zoom.toFixed(1)}×
            </span>
            <button
              type="button"
              onClick={() => setZoom((value) => clamp(value * 1.25, 1, 8))}
              className="flex size-8 items-center justify-center text-slate transition hover:text-bone focus-ring"
              aria-label="Zoom in"
            >
              <Plus className="size-3" />
            </button>
            <button
              type="button"
              onClick={resetView}
              className="flex size-8 items-center justify-center border-l border-line text-slate transition hover:text-bone focus-ring"
              aria-label="Reset view"
            >
              <RotateCcw className="size-3" />
            </button>
          </div>
        </div>
      </div>

      <div ref={wrapperRef} className="relative h-[380px] w-full sm:h-[520px]">
        <canvas
          ref={canvasRef}
          className={cn(
            "absolute inset-0 size-full touch-none",
            dragging ? "cursor-grabbing" : hovered !== null ? "cursor-pointer" : "cursor-grab",
          )}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={() => {
            dragRef.current = null;
            setDragging(false);
            setHovered(null);
          }}
          role="img"
          aria-label="Spatial map of the tissue sample. Use the layer controls to switch between domains, cell types, and uncertainty."
        />

        {zoom > 1 ? (
          <div className="pointer-events-none absolute right-2 top-2 flex items-center gap-1 rounded-full border border-line bg-ink/80 px-2 py-1 font-mono text-[9px] text-slate backdrop-blur">
            <Maximize2 className="size-2.5" />
            drag to pan
          </div>
        ) : null}

        {hoveredSpot ? (
          <div
            className="pointer-events-none absolute z-10 w-56 rounded-xl border border-line bg-ink/95 p-3 shadow-2xl backdrop-blur"
            style={{
              left: clamp(
                tooltip.x + 14,
                8,
                Math.max(8, (size.width || 300) - 232),
              ),
              top: clamp(
                tooltip.y + 14,
                8,
                Math.max(8, (size.height || 300) - 172),
              ),
            }}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                {hoveredSpot.barcode}
              </p>
              <span
                className={cn(
                  "size-1.5 rounded-full",
                  hoveredSpot.qc_pass ? "bg-teal" : "bg-coral",
                )}
              />
            </div>
            <div className="mt-1.5 flex items-center gap-1.5">
              <span
                className="size-2 rounded-full"
                style={{ background: domainColor.get(hoveredSpot.domain) ?? FALLBACK_DOMAIN }}
              />
              <p className="text-xs font-medium text-bone">
                {hoveredSpot.domain_name || titleCase(hoveredSpot.domain)}
              </p>
            </div>
            <div className="mt-2 flex items-center justify-between border-t border-line pt-2 text-[10px]">
              <span className="text-slate">Uncertainty</span>
              <span
                className="font-mono"
                style={{ color: uncertaintyColor(hoveredSpot.uncertainty) }}
              >
                {hoveredSpot.uncertainty.toFixed(2)}
              </span>
            </div>
            <div className="mt-2 space-y-1">
              {hoveredComposition.map(([id, value]) => (
                <div key={id} className="flex items-center gap-2">
                  <span className="w-16 shrink-0 truncate text-[9px] text-slate">{titleCase(id)}</span>
                  <span className="h-1 flex-1 overflow-hidden rounded-full bg-bone/10">
                    <span
                      className="block h-full rounded-full bg-teal"
                      style={{ width: `${clamp(value, 0, 1) * 100}%` }}
                    />
                  </span>
                  <span className="w-7 text-right font-mono text-[9px] text-bone-dim">
                    {Math.round(value * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      <div className="border-t border-line px-3 py-2.5">
        {mode === "domain" ? (
          <div className="flex flex-wrap gap-x-2 gap-y-1.5">
            <button
              type="button"
              onClick={() => setFocusDomain(null)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[9px] transition",
                focusDomain === null
                  ? "border-acid/40 bg-acid/10 text-acid"
                  : "border-line text-slate hover:text-bone",
              )}
            >
              All
            </button>
            {domainStats.map((domain) => (
              <button
                key={domain.id}
                type="button"
                onClick={() => setFocusDomain(focusDomain === domain.id ? null : domain.id)}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[9px] transition",
                  focusDomain === domain.id
                    ? "border-bone/30 bg-bone/10 text-bone"
                    : "border-transparent text-slate hover:bg-bone/5 hover:text-bone",
                )}
                title={`${domain.name} · ${domain.count} spots (${domain.pct.toFixed(1)}%)`}
              >
                <span className="size-1.5 rounded-full" style={{ background: domain.color }} />
                {domain.name}
                <span className="font-mono text-[8px] opacity-70">{domain.pct.toFixed(0)}%</span>
              </button>
            ))}
          </div>
        ) : mode === "celltype" ? (
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full" style={{ background: selectedColor }} />
              <p className="text-[10px] text-bone-dim">{titleCase(selectedCellType)} composition</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[8px] uppercase tracking-wider text-slate">low</span>
              <span
                className="h-1.5 w-24 rounded-full"
                style={{
                  background: `linear-gradient(to right, ${selectedColor}22, ${selectedColor})`,
                }}
              />
              <span className="font-mono text-[8px] uppercase tracking-wider text-slate">high</span>
            </div>
          </div>
        ) : (
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-[10px] text-slate">
              Entropy + NNLS residual. Higher = less reliable composition.
            </p>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[8px] uppercase tracking-wider text-teal">low</span>
              <span className="h-1.5 w-28 rounded-full bg-gradient-to-r from-teal via-amber to-coral" />
              <span className="font-mono text-[8px] uppercase tracking-wider text-coral">high</span>
            </div>
          </div>
        )}
      </div>

      {payload.metrics ? (
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-line bg-ink-3/40 px-3 py-2">
          <p className="text-[9px] leading-relaxed text-slate">
            Synthetic benchmark: JSD{" "}
            <span className="font-mono text-teal">{payload.metrics.composition.jsd_mean.toFixed(3)}</span>
            {" · "}r{" "}
            <span className="font-mono text-teal">
              {payload.metrics.composition.dominant_type_pearson.toFixed(3)}
            </span>
            {" · "}ARI{" "}
            <span className="font-mono text-teal">{payload.metrics.domains.ari.toFixed(3)}</span>
          </p>
          <Badge variant="outline">Synthetic ground truth</Badge>
        </div>
      ) : null}
    </div>
  );
}
