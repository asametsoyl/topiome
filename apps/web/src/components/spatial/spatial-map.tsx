"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Crosshair,
  Image as ImageIcon,
  Layers,
  Maximize2,
  Minus,
  MousePointer2,
  Plus,
  RotateCcw,
  ShieldQuestion,
  ScanSearch,
  CircleDot,
  Network,
  Download,
  LoaderCircle,
  Trash2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { cn, formatNumber, titleCase } from "@/lib/utils";
import type { Interaction, ResultPayload, Spot } from "@/lib/types";

type ViewMode = "domain" | "celltype" | "uncertainty" | "gene" | "signaling" | "pathway";

const CELL_COLORS = [
  "#0072B2",
  "#E69F00",
  "#009E73",
  "#D55E00",
  "#CC79A7",
  "#56B4E9",
  "#7B2CBF",
  "#8C564B",
  "#5B8E7D",
  "#C51B7D",
  "#4D4D4D",
  "#B08900",
];

const FALLBACK_DOMAIN = "#7A8A80";

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function percentileScaleMax(values: number[], percentile = 0.95) {
  const positive = values.filter((value) => Number.isFinite(value) && value > 0).sort((a, b) => a - b);
  if (positive.length === 0) return 0.1;
  const index = Math.min(positive.length - 1, Math.floor((positive.length - 1) * percentile));
  return Math.max(positive[index], 0.1);
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

function pointInPolygon(x: number, y: number, polygon: { x: number; y: number }[]) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const a = polygon[i];
    const b = polygon[j];
    if ((a.y > y) !== (b.y > y) && x < ((b.x - a.x) * (y - a.y)) / (b.y - a.y) + a.x) inside = !inside;
  }
  return inside;
}

interface HitSpot {
  x: number;
  y: number;
  radius: number;
  index: number;
}

export function SpatialMap({
  payload,
  imageUrl,
  runId,
  className,
  sharedGene,
  sharedGeneInput,
  onSharedGeneInputChange,
  onSharedGeneChange,
  sharedGeneScaleMax,
  onGeneScaleMax,
  sharedGeneThreshold,
  onSharedGeneThresholdChange,
}: {
  payload: ResultPayload;
  imageUrl?: string;
  runId: string;
  className?: string;
  sharedGene?: string;
  sharedGeneInput?: string;
  onSharedGeneInputChange?: (gene: string) => void;
  onSharedGeneChange?: (gene: string) => void;
  sharedGeneScaleMax?: number;
  onGeneScaleMax?: (maximum: number) => void;
  sharedGeneThreshold?: number;
  onSharedGeneThresholdChange?: (threshold: number) => void;
}) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const hitsRef = useRef<HitSpot[]>([]);
  const dragRef = useRef<{ x: number; y: number; panX: number; panY: number } | null>(null);
  const lassoRef = useRef<{ x: number; y: number }[]>([]);
  const requestedGeneRef = useRef("");

  const [size, setSize] = useState({ width: 0, height: 0 });
  const [mode, setMode] = useState<ViewMode>("domain");
  const [pickedCellType, setSelectedCellType] = useState<string>("__dominant__");
  const [selectedInteractionId, setSelectedInteractionId] = useState("");
  const [dragging, setDragging] = useState(false);
  const [focusDomain, setFocusDomain] = useState<string | null>(null);
  const [dimUncertain, setDimUncertain] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [hovered, setHovered] = useState<number | null>(null);
  const [tooltip, setTooltip] = useState({ x: 0, y: 0 });
  const [tissueImage, setTissueImage] = useState<{ bitmap: ImageBitmap; hiresScale: number } | null>(null);
  const [imageChecked, setImageChecked] = useState(false);
  const [showTissue, setShowTissue] = useState(true);
  const [roiMode, setRoiMode] = useState(false);
  const [lasso, setLasso] = useState<{ x: number; y: number }[]>([]);
  const [selectedBarcodes, setSelectedBarcodes] = useState<Set<string>>(new Set());
  const [geneInput, setGeneInput] = useState("");
  const [geneExpression, setGeneExpression] = useState<Record<string, number> | null>(null);
  const [geneLabel, setGeneLabel] = useState("");
  const [geneThreshold, setGeneThreshold] = useState(0);
  const [geneError, setGeneError] = useState("");
  const [geneLoading, setGeneLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [mapExporting, setMapExporting] = useState(false);
  const [roiGenes, setRoiGenes] = useState<Awaited<ReturnType<typeof apiClient.roiGenes>> | null>(null);
  const [roiGenesLoading, setRoiGenesLoading] = useState(false);
  const [roiGenesError, setRoiGenesError] = useState("");

  const spots = payload.spots;
  const usesMarkerScores = payload.summary.method === "marker_score";
  const geneInputValue = sharedGeneInput ?? geneInput;
  const geneThresholdValue = sharedGeneThreshold ?? geneThreshold;

  useEffect(() => {
    let active = true;
    let bitmap: ImageBitmap | null = null;
    setImageChecked(false);
    setTissueImage(null);
    if (!imageUrl) {
      setImageChecked(true);
      return;
    }
    fetch(imageUrl, { credentials: "same-origin" })
      .then(async (response) => {
        if (!response.ok) throw new Error("Tissue image is unavailable");
        const hiresScale = Number(response.headers.get("X-Visium-Hires-Scale"));
        if (!Number.isFinite(hiresScale) || hiresScale <= 0) throw new Error("Invalid Visium image scale");
        bitmap = await createImageBitmap(await response.blob());
        if (active) {
          setTissueImage({ bitmap, hiresScale });
          setImageChecked(true);
        }
        else bitmap.close();
      })
      .catch(() => {
        if (active) {
          setTissueImage(null);
          setImageChecked(true);
        }
      });
    return () => {
      active = false;
      bitmap?.close();
    };
  }, [imageUrl]);
  useEffect(() => {
    if (sharedGene === undefined) return;
    const normalizedGene = sharedGene.trim().toUpperCase();
    const requestKey = `${runId}:${normalizedGene}`;
    if (!normalizedGene || requestedGeneRef.current === requestKey) return;
    let active = true;
    queueMicrotask(() => {
      if (!active) return;
      requestedGeneRef.current = requestKey;
      setGeneLoading(true);
      setGeneError("");
      apiClient.geneExpression(runId, sharedGene.trim())
        .then((layer) => {
          if (!active) return;
          setGeneExpression(layer.values);
          setGeneLabel(layer.gene);
          onGeneScaleMax?.(percentileScaleMax(Object.values(layer.values)));
          setGeneThreshold(0);
          setMode("gene");
        })
        .catch((error: unknown) => {
          if (active) setGeneError(error instanceof Error ? error.message : "Unable to load gene expression");
        })
        .finally(() => {
          if (active) setGeneLoading(false);
        });
    });
    return () => {
      active = false;
    };
  }, [sharedGene, runId, onGeneScaleMax]);
  const cellTypes = useMemo(() => Object.keys(payload.composition ?? {}), [payload.composition]);
  const maxGeneExpression = useMemo(
    () => sharedGeneScaleMax ?? percentileScaleMax(Object.values(geneExpression ?? {})),
    [geneExpression, sharedGeneScaleMax],
  );
  const selectedCellType = pickedCellType === "__dominant__" || cellTypes.includes(pickedCellType)
    ? pickedCellType
    : "__dominant__";
  const mapInteractions: Interaction[] = payload.summary.synthetic
    ? []
    : (payload.communication ?? []).filter((interaction) => interaction.tested && interaction.spot_scores);
  const selectedInteraction =
    mapInteractions.find((interaction) => interaction.id === selectedInteractionId) ?? mapInteractions[0];
  const pathwayLayers = useMemo(() => {
    const groups = new Map<string, { pairs: number; spotScores: Record<string, number> }>();
    for (const interaction of mapInteractions) {
      const category = interaction.category || "Other curated pairs";
      const layer = groups.get(category) ?? { pairs: 0, spotScores: {} };
      layer.pairs += 1;
      for (const [barcode, score] of Object.entries(interaction.spot_scores ?? {})) {
        layer.spotScores[barcode] = (layer.spotScores[barcode] ?? 0) + score;
      }
      groups.set(category, layer);
    }
    return [...groups.entries()].map(([name, layer]) => ({
      name,
      pairs: layer.pairs,
      spotScores: Object.fromEntries(
        Object.entries(layer.spotScores).map(([barcode, score]) => [barcode, score / layer.pairs]),
      ),
    }));
  }, [mapInteractions]);
  const [selectedPathwayName, setSelectedPathwayName] = useState("");
  const selectedPathway = pathwayLayers.find((layer) => layer.name === selectedPathwayName) ?? pathwayLayers[0];
  const selectedOverlayScores = mode === "signaling" ? selectedInteraction?.spot_scores : selectedPathway?.spotScores;
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

  const selectedIndex = selectedCellType === "__dominant__" ? 0 : Math.max(0, cellTypes.indexOf(selectedCellType));
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
    context.fillStyle = "#f4f6f3";
    context.fillRect(0, 0, size.width, size.height);

    if (!(showTissue && tissueImage)) {
      // Subtle grid is the fallback for samples without a tissue image.
      context.strokeStyle = "rgba(22, 118, 99, 0.07)";
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
    const padding = 26;
    const useTissue = showTissue && tissueImage !== null && Boolean(imageUrl);
    const spanX = Math.max(maxX - minX, 1e-9);
    const spanY = Math.max(maxY - minY, 1e-9);
    const imageWidthInFullres = useTissue ? tissueImage.bitmap.width / tissueImage.hiresScale : spanX;
    const imageHeightInFullres = useTissue ? tissueImage.bitmap.height / tissueImage.hiresScale : spanY;
    const fitScale = Math.min(
      (size.width - padding * 2) / imageWidthInFullres,
      (size.height - padding * 2) / imageHeightInFullres,
    );
    const scale = fitScale * zoom;

    const drawWidth = imageWidthInFullres * scale;
    const drawHeight = imageHeightInFullres * scale;
    const originX = (size.width - drawWidth) / 2 + pan.x;
    const originY = (size.height - drawHeight) / 2 + pan.y;

    if (useTissue) {
      context.globalAlpha = 1;
      context.drawImage(tissueImage.bitmap, originX, originY, drawWidth, drawHeight);
    }

    const project = (spot: Spot) => useTissue
      ? {
          // Spot coordinates from Space Ranger are already full-resolution pixels.
          // The image is drawn in full-resolution space too, so do not apply the
          // hires scale a second time here.
          x: originX + spot.x * scale,
          // The analysis reader stores image rows as negative y so the coordinate
          // system stays y-up. Convert back to image y-down when overlaying H&E.
          y: originY - spot.y * scale,
        }
      : {
          x: originX + (spot.x - minX) * scale,
          y: originY + (spot.y - minY) * scale,
        };

    const radius = clamp(Math.sqrt((size.width * size.height) / (spots.length * 2.6)) * 0.5, 2.4, 7.5);

    const maxCellValue = spots.reduce(
      (maximum, spot) => Math.max(maximum, Number(spot.composition?.[selectedCellType] ?? 0)),
      1e-6,
    );
    const maxInteractionValue = percentileScaleMax(Object.values(selectedOverlayScores ?? {}), 0.95);

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
        if (selectedCellType === "__dominant__") {
          const rankedTypes = Object.entries(spot.composition ?? {}).sort((a, b) => Number(b[1]) - Number(a[1]));
          const [dominantType, dominantScore] = rankedTypes[0] ?? ["", 0];
          const groupIndex = cellTypes.indexOf(dominantType);
          const normalized = clamp(Number(dominantScore) / maxCellValue, 0, 1);
          color = CELL_COLORS[Math.max(0, groupIndex) % CELL_COLORS.length];
          alpha = 0.25 + Math.pow(normalized, 0.75) * 0.75;
        } else {
          const value = Number(spot.composition?.[selectedCellType] ?? 0);
          const normalized = clamp(value / maxCellValue, 0, 1);
          color = selectedColor;
          alpha = 0.16 + Math.pow(normalized, 0.75) * 0.84;
        }
      } else if (mode === "uncertainty") {
        color = uncertaintyColor(spot.uncertainty);
        alpha = 0.92;
      } else if (mode === "signaling" || mode === "pathway") {
        const value = selectedOverlayScores?.[spot.barcode] ?? 0;
        const normalized = clamp(value / maxInteractionValue, 0, 1);
        color = mix("#F4D35E", "#C2185B", normalized);
        alpha = value > 0 ? 0.48 + normalized * 0.52 : 0;
      } else {
        const value = Number(geneExpression?.[spot.barcode] ?? 0);
        const normalized = clamp(value / maxGeneExpression, 0, 1);
        color = mix("#F4D35E", "#C2185B", Math.pow(normalized, 0.75));
        alpha = value <= 0 || value < geneThresholdValue ? 0 : 0.48 + normalized * 0.52;
      }

      if (dimUncertain && spot.uncertainty > 0.7 && mode !== "uncertainty") {
        alpha *= 0.2;
      }

      context.globalAlpha = alpha;
      context.fillStyle = color;
      context.beginPath();
      context.arc(position.x, position.y, radius, 0, Math.PI * 2);
      context.fill();

      if (selectedBarcodes.has(spot.barcode)) {
        context.globalAlpha = 1;
        context.strokeStyle = "#F4D35E";
        context.lineWidth = 1.6;
        context.beginPath();
        context.arc(position.x, position.y, radius + 2, 0, Math.PI * 2);
        context.stroke();
      }

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

    const activeLasso = lassoRef.current.length ? lassoRef.current : lasso;
    if (activeLasso.length > 1) {
      context.strokeStyle = "#F4D35E";
      context.fillStyle = "rgba(244, 211, 94, 0.12)";
      context.lineWidth = 1.5;
      context.beginPath();
      context.moveTo(activeLasso[0].x, activeLasso[0].y);
      for (const point of activeLasso.slice(1)) context.lineTo(point.x, point.y);
      context.closePath();
      context.fill();
      context.stroke();
    }

    // Scale hint and count overlay.
    context.font = "500 9px var(--font-geist-mono), monospace";
    context.fillStyle = "rgba(138, 147, 140, 0.85)";
    context.fillText(`n = ${formatNumber(spots.length)} spots`, 12, size.height - 12);
    context.textAlign = "right";
    context.fillText(mode === "domain" ? "domain map" : mode === "celltype" ? selectedCellType === "__dominant__" ? (usesMarkerScores ? "dominant marker group" : "dominant cell type") : selectedCellType : mode === "gene" ? `${geneLabel || "gene expression"} · ${geneExpression ? "log1p(CP10K)" : "not loaded"}` : mode === "signaling" ? `${selectedInteraction?.ligand ?? "ligand"} → ${selectedInteraction?.receptor ?? "receptor"} · co-expression score` : mode === "pathway" ? `${selectedPathway?.name ?? "pathway context"} · mean pair score` : "uncertainty", size.width - 12, size.height - 12);
    context.textAlign = "left";
  }, [
    spots,
    size,
    mode,
    selectedCellType,
    selectedInteraction,
    selectedOverlayScores,
    selectedPathway,
    selectedColor,
    domainColor,
    focusDomain,
    dimUncertain,
    zoom,
    pan,
    hovered,
    tissueImage,
    showTissue,
    imageUrl,
    geneExpression,
    maxGeneExpression,
    geneLabel,
    geneThresholdValue,
    selectedBarcodes,
    lasso,
  ]);

  function handlePointerDown(event: React.PointerEvent<HTMLCanvasElement>) {
    const canvas = event.currentTarget;
    canvas.setPointerCapture(event.pointerId);
    if (roiMode) {
      const rect = canvas.getBoundingClientRect();
      const point = { x: event.clientX - rect.left, y: event.clientY - rect.top };
      lassoRef.current = [point];
      setLasso([point]);
      dragRef.current = null;
      return;
    }
    dragRef.current = { x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
    setDragging(true);
  }

  function handlePointerMove(event: React.PointerEvent<HTMLCanvasElement>) {
    if (roiMode && lassoRef.current.length) {
      const rect = event.currentTarget.getBoundingClientRect();
      const next = [...lassoRef.current, { x: event.clientX - rect.left, y: event.clientY - rect.top }];
      lassoRef.current = next;
      setLasso(next);
      return;
    }
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
    if (roiMode && lassoRef.current.length > 2) {
      const polygon = lassoRef.current;
      const picked = hitsRef.current.filter((hit) => pointInPolygon(hit.x, hit.y, polygon)).map((hit) => spots[hit.index].barcode);
      setSelectedBarcodes(new Set(picked));
      setRoiGenes(null);
      setRoiGenesError("");
      lassoRef.current = [];
      setLasso([]);
      return;
    }
    dragRef.current = null;
    setDragging(false);
  }

  function resetView() {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setHovered(null);
  }

  async function loadGene(requestedGene = geneInputValue) {
    const gene = requestedGene.trim();
    if (!gene) return;
    requestedGeneRef.current = `${runId}:${gene.toUpperCase()}`;
    setGeneLoading(true);
    setGeneError("");
    onSharedGeneChange?.(gene);
    try {
      const layer = await apiClient.geneExpression(runId, gene);
      setGeneExpression(layer.values);
      setGeneLabel(layer.gene);
      onGeneScaleMax?.(percentileScaleMax(Object.values(layer.values)));
      setGeneThreshold(0);
      setMode("gene");
    } catch (error) {
      setGeneExpression(null);
      setGeneError(error instanceof Error ? error.message : "Unable to load gene expression");
    } finally {
      setGeneLoading(false);
    }
  }

  async function exportSelection() {
    setExporting(true);
    try {
      const csv = await apiClient.exportRoi(runId, [...selectedBarcodes]);
      const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `topiome-roi-${runId.slice(0, 8)}.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setGeneError(error instanceof Error ? error.message : "Unable to export selection");
    } finally {
      setExporting(false);
    }
  }

  async function exportMapPng() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    setMapExporting(true);
    try {
      await apiClient.logMapExport(runId, { width: canvas.width, height: canvas.height, mode });
      const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/png"));
      if (!blob) throw new Error("Could not render the map image");
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `topiome-map-${runId.slice(0, 8)}-${mode}.png`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setGeneError(error instanceof Error ? error.message : "Unable to export map image");
    } finally {
      setMapExporting(false);
    }
  }

  async function exploreRoiGenes() {
    setRoiGenesLoading(true);
    setRoiGenesError("");
    try {
      setRoiGenes(await apiClient.roiGenes(runId, [...selectedBarcodes]));
    } catch (error) {
      setRoiGenesError(error instanceof Error ? error.message : "Unable to compare ROI expression");
    } finally {
      setRoiGenesLoading(false);
    }
  }

  const hoveredSpot = hovered !== null ? spots[hovered] : null;
  const hoveredComposition = hoveredSpot
    ? Object.entries(hoveredSpot.composition ?? {})
        .sort((a, b) => b[1] - a[1])
        .slice(0, 4)
    : [];
  const selectedSpots = spots.filter((spot) => selectedBarcodes.has(spot.barcode));
  const selectedMeanUncertainty = selectedSpots.length
    ? selectedSpots.reduce((sum, spot) => sum + spot.uncertainty, 0) / selectedSpots.length
    : 0;
  const selectedQcPct = selectedSpots.length
    ? (selectedSpots.filter((spot) => spot.qc_pass).length / selectedSpots.length) * 100
    : 0;
  const selectedDomains = selectedSpots.reduce<Record<string, number>>((counts, spot) => {
    counts[spot.domain_name || titleCase(spot.domain)] = (counts[spot.domain_name || titleCase(spot.domain)] ?? 0) + 1;
    return counts;
  }, {});
  const selectedTopDomains = Object.entries(selectedDomains).sort((a, b) => b[1] - a[1]).slice(0, 3);
  const roiQcSpots = selectedSpots.filter((spot) => spot.qc_pass);
  const backgroundQcSpots = spots.filter((spot) => spot.qc_pass && !selectedBarcodes.has(spot.barcode));
  const roiCompositionDeltas = cellTypes.map((cellType) => {
    const roiMean = roiQcSpots.length
      ? roiQcSpots.reduce((sum, spot) => sum + Number(spot.composition?.[cellType] ?? 0), 0) / roiQcSpots.length
      : 0;
    const backgroundMean = backgroundQcSpots.length
      ? backgroundQcSpots.reduce((sum, spot) => sum + Number(spot.composition?.[cellType] ?? 0), 0) / backgroundQcSpots.length
      : 0;
    return { cellType, roiMean, backgroundMean, delta: roiMean - backgroundMean };
  }).sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta)).slice(0, 5);

  return (
    <div className={cn("relative flex flex-col overflow-hidden rounded-2xl border border-line bg-ink-2", className)}>
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-2.5">
        <div className="flex rounded-lg border border-line bg-ink-3/70 p-0.5">
          {[
            { id: "domain" as const, label: "Domains", icon: Layers },
            { id: "celltype" as const, label: usesMarkerScores ? "Marker groups" : "Cell types", icon: MousePointer2 },
            { id: "uncertainty" as const, label: "Uncertainty", icon: ShieldQuestion },
            { id: "gene" as const, label: "Gene", icon: ScanSearch },
            { id: "signaling" as const, label: "Signals", icon: CircleDot },
            { id: "pathway" as const, label: "Pathways", icon: Network },
          ].filter((item) => (item.id !== "gene" || !payload.summary.synthetic) && (item.id !== "signaling" || mapInteractions.length > 0) && (item.id !== "pathway" || pathwayLayers.length > 0)).map((item) => {
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
          {tissueImage ? (
            <button
              type="button"
              onClick={() => setShowTissue((value) => !value)}
              className={cn(
                "inline-flex h-8 items-center gap-1.5 rounded-lg border px-2 text-[10px] transition focus-ring",
                showTissue
                  ? "border-teal/35 bg-teal/10 text-teal"
                  : "border-line text-slate hover:text-bone",
              )}
              aria-pressed={showTissue}
              title={showTissue ? "Hide tissue image" : "Show tissue image"}
            >
              <ImageIcon className="size-3" />
              <span className="hidden md:inline">Tissue</span>
            </button>
          ) : null}
          {mode === "celltype" ? (
            <select
              value={selectedCellType}
              onChange={(event) => setSelectedCellType(event.target.value)}
              className="h-8 rounded-lg border border-line bg-ink-3 px-2 text-[10px] text-bone outline-none focus:border-acid/50"
              aria-label={usesMarkerScores ? "Marker score group layer" : "Cell type layer"}
            >
              <option value="__dominant__">All groups · dominant</option>
              {cellTypes.map((cellType) => (
                <option key={cellType} value={cellType}>
                  {titleCase(cellType)}
                </option>
              ))}
            </select>
          ) : null}

          {mode === "signaling" && selectedInteraction ? (
            <select
              value={selectedInteraction.id}
              onChange={(event) => setSelectedInteractionId(event.target.value)}
              className="h-8 max-w-56 rounded-lg border border-line bg-ink-3 px-2 text-[10px] text-bone outline-none focus:border-acid/50"
              aria-label="Ligand receptor interaction layer"
            >
              {mapInteractions.map((interaction) => (
                <option key={interaction.id} value={interaction.id}>
                  {interaction.ligand} → {interaction.receptor} · {interaction.category}
                </option>
              ))}
            </select>
          ) : null}

          {mode === "pathway" && selectedPathway ? (
            <select
              value={selectedPathway.name}
              onChange={(event) => setSelectedPathwayName(event.target.value)}
              className="h-8 max-w-52 rounded-lg border border-line bg-ink-3 px-2 text-[10px] text-bone outline-none focus:border-acid/50"
              aria-label="Curated pathway context layer"
            >
              {pathwayLayers.map((layer) => (
                <option key={layer.name} value={layer.name}>
                  {layer.name} · {layer.pairs} pair{layer.pairs === 1 ? "" : "s"}
                </option>
              ))}
            </select>
          ) : null}

          {mode === "gene" ? (
            <div className="flex flex-wrap items-center gap-1.5">
              <div className="flex items-center gap-1"><input value={geneInputValue} onChange={(event) => { setGeneInput(event.target.value); onSharedGeneInputChange?.(event.target.value); }} onKeyDown={(event) => { if (event.key === "Enter") void loadGene(); }} placeholder="Gene symbol" aria-label="Gene symbol" className="h-8 w-24 rounded-lg border border-line bg-ink-3 px-2 text-[10px] text-bone outline-none focus:border-acid/50" /><button type="button" onClick={() => void loadGene()} disabled={geneLoading || !geneInputValue.trim()} className="inline-flex h-8 items-center gap-1 rounded-lg border border-line px-2 text-[10px] text-bone disabled:opacity-40">{geneLoading ? <LoaderCircle className="size-3 animate-spin" /> : "Load"}</button></div>
              {geneExpression ? <><label className="flex items-center gap-1.5 text-[9px] text-slate">Min <input type="range" min={0} max={maxGeneExpression} step="0.05" value={Math.min(geneThresholdValue, maxGeneExpression)} onChange={(event) => { const value = Number(event.target.value); setGeneThreshold(value); onSharedGeneThresholdChange?.(value); }} aria-label="Minimum gene expression threshold" className="w-16 accent-acid" /><span className="w-8 font-mono text-bone-dim">{geneThresholdValue.toFixed(1)}</span></label><button type="button" onClick={() => { const selected = Object.entries(geneExpression).filter(([, value]) => value > 0 && value >= geneThresholdValue).map(([barcode]) => barcode); setSelectedBarcodes(new Set(selected)); setRoiGenes(null); }} className="h-8 rounded-lg border border-line px-2 text-[9px] text-slate hover:text-bone">Select expressing spots</button></> : null}
            </div>
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
            roiMode ? "cursor-crosshair" : dragging ? "cursor-grabbing" : hovered !== null ? "cursor-pointer" : "cursor-grab",
          )}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={() => { if (!roiMode) { dragRef.current = null; setDragging(false); setHovered(null); } }}
          role="img"
          aria-label="Spatial spot map. Tissue image is shown when available; layer controls include domains, cell classes, uncertainty, genes, and tested ligand-receptor co-expression."
        />

        {imageChecked && !tissueImage ? (
          <div className="pointer-events-none absolute left-3 top-3 rounded-lg border border-line bg-white/90 px-3 py-2 text-[10px] text-bone-dim shadow-sm">
            Tissue image unavailable · spot coordinates only
          </div>
        ) : null}

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
            {mode === "gene" && geneExpression ? <div className="mt-2 flex items-center justify-between border-t border-line pt-2 text-[10px]"><span className="text-slate">{geneLabel} · log1p(CP10K)</span><span className="font-mono text-acid">{(geneExpression[hoveredSpot.barcode] ?? 0).toFixed(3)}</span></div> : null}
            {mode === "signaling" && selectedInteraction ? <div className="mt-2 flex items-center justify-between border-t border-line pt-2 text-[10px]"><span className="text-slate">{selectedInteraction.ligand} → {selectedInteraction.receptor}</span><span className="font-mono text-teal">{(selectedInteraction.spot_scores?.[hoveredSpot.barcode] ?? 0).toExponential(2)}</span></div> : null}
            {mode === "pathway" && selectedPathway ? <div className="mt-2 flex items-center justify-between border-t border-line pt-2 text-[10px]"><span className="text-slate">{selectedPathway.name} · mean pair score</span><span className="font-mono text-teal">{(selectedPathway.spotScores[hoveredSpot.barcode] ?? 0).toExponential(2)}</span></div> : null}
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
            {selectedCellType === "__dominant__" ? (
              <div className="flex flex-wrap gap-x-3 gap-y-1.5" aria-label="Dominant group color legend">
                {cellTypes.map((cellType, index) => (
                  <span key={cellType} className="inline-flex items-center gap-1.5 text-[10px] text-bone-dim">
                    <span className="size-2 rounded-full" style={{ background: CELL_COLORS[index % CELL_COLORS.length] }} />
                    {titleCase(cellType)}
                  </span>
                ))}
                <span className="w-full text-[10px] text-slate">
                  {usesMarkerScores ? "Color shows the top marker-score group per spot; these are not calibrated cell fractions or resolved subtypes." : "Color shows the highest modeled cell-type proportion per spot."}
                </span>
                {usesMarkerScores && cellTypes.includes("immune") ? (
                  <span className="w-full text-[10px] text-slate">
                    Immune markers combine T-cell and myeloid signals here; macrophage, microglia, and T-cell subtypes are unresolved without a matched reference.
                  </span>
                ) : null}
              </div>
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <span className="size-2 rounded-full" style={{ background: selectedColor }} />
                  <p className="text-[10px] text-bone-dim">
                    {titleCase(selectedCellType)} {usesMarkerScores ? "marker score" : "composition"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[8px] uppercase tracking-wider text-slate">low</span>
                  <span className="h-1.5 w-24 rounded-full" style={{ background: `linear-gradient(to right, ${selectedColor}22, ${selectedColor})` }} />
                  <span className="font-mono text-[8px] uppercase tracking-wider text-slate">high</span>
                </div>
              </>
            )}
          </div>
        ) : mode === "gene" ? (
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-[10px] text-slate">{geneLabel ? `${geneLabel} expression · log1p(CP10K)` : "Enter a gene symbol to load its measured expression."}</p>
            <div className="flex items-center gap-2"><span className="font-mono text-[8px] uppercase tracking-wider text-slate">low</span><span className="h-1.5 w-28 rounded-full" style={{ background: "linear-gradient(to right, #F4D35E, #C2185B)" }} /><span className="font-mono text-[8px] uppercase tracking-wider text-acid">high</span></div>
          </div>
        ) : mode === "signaling" || mode === "pathway" ? (
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-[10px] text-slate">
              {mode === "signaling"
                ? `Spot contribution to curated ligand–receptor co-expression; colors scale within the selected pair. ${selectedInteraction?.q_value == null ? "No q-value available." : selectedInteraction.significant ? `BH-adjusted q = ${selectedInteraction.q_value.toPrecision(2)}.` : `Not significant after BH correction (q = ${selectedInteraction.q_value.toPrecision(2)}).`} This is not proof of signaling.`
                : "Mean spot co-expression score for pairs grouped by disease-pack context; colors scale within this group. Pathway activity is not measured."}
            </p>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[8px] uppercase tracking-wider text-slate">lower</span>
              <span className="h-1.5 w-28 rounded-full" style={{ background: "linear-gradient(to right, #F4D35E, #C2185B)" }} />
              <span className="font-mono text-[8px] uppercase tracking-wider text-teal">higher</span>
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

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-line bg-ink-3/30 px-3 py-2.5">
        <div className="flex items-center gap-2">
          <button type="button" aria-pressed={roiMode} onClick={() => { setRoiMode((active) => !active); setLasso([]); lassoRef.current = []; }} className={cn("inline-flex h-8 items-center gap-1.5 rounded-lg border px-2.5 text-[10px]", roiMode ? "border-acid/40 bg-acid/10 text-acid" : "border-line text-slate hover:text-bone")}><ScanSearch className="size-3" />{roiMode ? "Draw on tissue" : "Select ROI"}</button>
          <span className="text-[10px] text-slate">{selectedBarcodes.size ? `${selectedBarcodes.size} spots selected` : "Freehand select a region"}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <button type="button" onClick={() => void exportMapPng()} disabled={mapExporting} title="Requires an approved report; export is audit logged" className="inline-flex h-8 items-center gap-1 rounded-lg border border-line px-2 text-[10px] text-slate hover:text-bone disabled:opacity-50">{mapExporting ? <LoaderCircle className="size-3 animate-spin" /> : <Download className="size-3" />}PNG</button>
          {selectedBarcodes.size ? <><button type="button" onClick={() => setSelectedBarcodes(new Set())} className="inline-flex h-8 items-center gap-1 rounded-lg border border-line px-2 text-[10px] text-slate hover:text-bone"><Trash2 className="size-3" />Clear</button><button type="button" onClick={() => void exportSelection()} disabled={exporting} title="Requires an approved report; export is audit logged" className="inline-flex h-8 items-center gap-1 rounded-lg border border-acid/35 bg-acid/10 px-2 text-[10px] text-acid disabled:opacity-50">{exporting ? <LoaderCircle className="size-3 animate-spin" /> : <Download className="size-3" />}ROI CSV</button></> : null}
        </div>
      </div>
      {selectedSpots.length ? <div className="space-y-2 border-t border-line px-3 py-2.5"><div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] text-slate"><span>ROI summary <strong className="font-mono text-bone">{selectedSpots.length}</strong> spots</span><span>Mean uncertainty <strong className="font-mono text-bone">{selectedMeanUncertainty.toFixed(3)}</strong></span><span>QC pass <strong className="font-mono text-bone">{selectedQcPct.toFixed(1)}%</strong></span><span>Domains <strong className="font-normal text-bone">{selectedTopDomains.map(([name, count]) => `${name} ${count}`).join(" · ")}</strong></span><span className="text-slate/70">Exploratory selection; not pathology annotation.</span></div>{roiQcSpots.length >= 10 && backgroundQcSpots.length >= 10 ? <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[9px]"><span className="text-slate">QC-pass cell composition Δ (ROI − background):</span>{roiCompositionDeltas.map((item) => <span key={item.cellType} className="font-mono text-bone-dim">{titleCase(item.cellType)} <span className={item.delta >= 0 ? "text-acid" : "text-teal"}>{item.delta >= 0 ? "+" : ""}{(item.delta * 100).toFixed(1)} pp</span></span>)}<span className="text-slate/70">descriptive</span></div> : <p className="text-[9px] text-slate">Need at least 10 QC-pass spots inside and outside for ROI composition comparison.</p>}{!payload.summary.synthetic ? <button type="button" onClick={() => void exploreRoiGenes()} disabled={roiGenesLoading} className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-line px-2.5 text-[10px] text-bone-dim disabled:opacity-50">{roiGenesLoading ? <LoaderCircle className="size-3 animate-spin" /> : <ScanSearch className="size-3" />}Explore ROI-associated genes</button> : null}{roiGenesError ? <p role="status" className="text-[10px] text-coral">{roiGenesError}</p> : null}{roiGenes ? <div className="space-y-1.5"><p className="text-[10px] text-slate">Descriptive ROI vs background · {roiGenes.n_roi_qc_pass} / {roiGenes.n_background_qc_pass} QC-pass spots · no inferential test</p><div className="grid grid-cols-[4rem_1fr_5rem_5rem] gap-2 border-b border-line pb-1 font-mono text-[8px] uppercase tracking-wider text-slate"><span>Gene</span><span>Mean expression difference</span><span className="text-right">ROI detected</span><span className="text-right">Outside</span></div>{roiGenes.genes.slice(0, 8).map((item) => <div key={item.gene} className="grid grid-cols-[4rem_1fr_5rem_5rem] items-center gap-2 text-[9px]"><span className="font-mono text-bone">{item.gene}</span><span className={item.delta_mean_log1p_cp10k >= 0 ? "font-mono text-acid" : "font-mono text-teal"}>{item.delta_mean_log1p_cp10k >= 0 ? "+" : ""}{item.delta_mean_log1p_cp10k.toFixed(3)}</span><span className="text-right font-mono text-bone-dim">{(item.roi_detected_fraction * 100).toFixed(1)}%</span><span className="text-right font-mono text-bone-dim">{(item.background_detected_fraction * 100).toFixed(1)}%</span></div>)}<p className="text-[9px] leading-relaxed text-slate/70">{roiGenes.note}</p></div> : null}</div> : null}
      {geneError ? <p role="status" className="border-t border-coral/20 px-3 py-2 text-[10px] text-coral">{geneError}</p> : null}

      {payload.summary.synthetic && payload.metrics?.composition && payload.metrics?.domains ? (
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
