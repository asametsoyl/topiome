import { Badge } from "@/components/ui/badge";

const DOMAINS = [
  { id: "tumor_core", name: "Tumor core", color: "#FF6B6B" },
  { id: "invasive_margin", name: "Invasive margin", color: "#FF9F43" },
  { id: "stroma", name: "Stroma", color: "#C8B08A" },
  { id: "immune_aggregate", name: "Immune aggregate", color: "#6FA8DC" },
  { id: "normal_gland", name: "Normal gland", color: "#9AD0C2" },
  { id: "necrosis", name: "Necrosis", color: "#5C5C5C" },
];

function domainAt(x: number, y: number): string {
  const tumor = Math.hypot(x - 0.63, y - 0.42);
  const immune = Math.hypot(x - 0.3, y - 0.63);
  const normal = Math.hypot(x - 0.22, y - 0.28);
  const necrosis = Math.hypot(x - 0.8, y - 0.74);
  if (tumor < 0.13) return "tumor_core";
  if (tumor < 0.2) return "invasive_margin";
  if (immune < 0.1) return "immune_aggregate";
  if (normal < 0.09) return "normal_gland";
  if (necrosis < 0.07) return "necrosis";
  return "stroma";
}

function buildSpots() {
  const spots: Array<{ x: number; y: number; domain: string; opacity: number }> = [];
  const cols = 24;
  const rows = 18;
  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      const x = 0.08 + (col / (cols - 1)) * 0.84 + (row % 2 ? 0.018 : 0);
      const y = 0.08 + (row / (rows - 1)) * 0.84;
      const edge = Math.hypot((x - 0.5) / 0.47, (y - 0.5) / 0.43);
      if (edge > 1) continue;
      const noise = (Math.sin(col * 12.9898 + row * 78.233) * 43758.5453) % 1;
      if (Math.abs(noise) > 0.94 && edge > 0.85) continue;
      spots.push({
        x: 40 + x * 480,
        y: 30 + y * 360,
        domain: domainAt(x, y),
        opacity: 0.82 + (Math.abs(noise) % 1) * 0.18,
      });
    }
  }
  return spots;
}

const palette = Object.fromEntries(DOMAINS.map((domain) => [domain.id, domain.color]));
const spots = buildSpots();

export function AtlasVisual() {
  return (
    <div className="relative">
      <div className="absolute -inset-8 -z-10 rounded-full bg-teal/10 blur-3xl" />
      <div className="overflow-hidden rounded-2xl border border-line bg-ink-2 shadow-[0_30px_80px_-20px_rgba(0,0,0,0.8)]">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="size-1.5 rounded-full bg-teal" />
            <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-slate">
              DEMO-BRCA-01
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="teal">NNLS</Badge>
            <Badge variant="outline">v0.1.0</Badge>
          </div>
        </div>

        <div className="relative bg-[#080e0a]">
          <svg
            viewBox="0 0 560 420"
            className="w-full"
            role="img"
            aria-label="Spatial domain map of a demo breast cancer sample"
          >
            <defs>
              <radialGradient id="glow" cx="62%" cy="42%" r="55%">
                <stop offset="0%" stopColor="#FF6B6B" stopOpacity="0.16" />
                <stop offset="100%" stopColor="#FF6B6B" stopOpacity="0" />
              </radialGradient>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1c2a22" strokeWidth="0.5" />
              </pattern>
            </defs>

            <rect width="560" height="420" fill="#080e0a" />
            <rect width="560" height="420" fill="url(#grid)" opacity="0.6" />
            <rect width="560" height="420" fill="url(#glow)" />

            <g fill="none" stroke="#C8F751" strokeOpacity="0.18" strokeWidth="0.8">
              <path d="M 300 150 C 360 130, 420 170, 425 215 C 430 265, 380 295, 330 285 C 285 277, 265 235, 280 195 C 290 168, 290 156, 300 150Z" />
              <path d="M 318 168 C 362 155, 400 182, 403 214 C 406 250, 372 271, 338 264 C 306 258, 294 230, 304 202 C 311 185, 310 174, 318 168Z" />
              <path d="M 340 188 C 366 181, 384 197, 385 214 C 386 234, 366 246, 347 242 C 329 238, 323 222, 329 207 C 333 197, 335 191, 340 188Z" />
            </g>

            <g>
              {spots.map((spot, index) => (
                <circle
                  key={index}
                  cx={spot.x}
                  cy={spot.y}
                  r={4.6}
                  fill={palette[spot.domain]}
                  opacity={spot.opacity}
                />
              ))}
            </g>

            <g stroke="#0A110C" strokeWidth="1.4" opacity="0.35">
              {spots.map((spot, index) => (
                <circle key={`ring-${index}`} cx={spot.x} cy={spot.y} r={4.6} fill="none" />
              ))}
            </g>

            <g fontFamily="var(--font-geist-mono), monospace" fontSize="8" fill="#8A938C">
              <line x1="40" y1="398" x2="110" y2="398" stroke="#8A938C" strokeWidth="1" />
              <text x="40" y="392">500 µm</text>
              <text x="430" y="392">n = 1,200 spots</text>
            </g>

            <g>
              <circle cx="63" cy="76" r="3" fill="#FF6B6B" />
              <line x1="66" y1="74" x2="98" y2="58" stroke="#FF6B6B" strokeOpacity="0.5" />
              <text x="102" y="61" fontFamily="var(--font-geist-mono), monospace" fontSize="8" fill="#FF6B6B">
                tumor core
              </text>

              <circle cx="160" cy="300" r="3" fill="#6FA8DC" />
              <line x1="163" y1="298" x2="196" y2="286" stroke="#6FA8DC" strokeOpacity="0.5" />
              <text x="200" y="289" fontFamily="var(--font-geist-mono), monospace" fontSize="8" fill="#6FA8DC">
                immune aggregate
              </text>
            </g>

            <g opacity="0.8">
              <circle cx="430" cy="140" r="12" fill="none" stroke="#5FE0C0" strokeWidth="0.8" />
              <circle cx="430" cy="140" r="3" fill="#5FE0C0" />
              <line x1="430" y1="128" x2="430" y2="118" stroke="#5FE0C0" strokeWidth="0.8" />
              <line x1="418" y1="140" x2="408" y2="140" stroke="#5FE0C0" strokeWidth="0.8" />
            </g>
          </svg>
        </div>

        <div className="grid grid-cols-3 gap-px border-t border-line bg-line">
          {[
            { label: "Composition JSD", value: "0.099", hint: "target < 0.12" },
            { label: "Dominant-type r", value: "0.862", hint: "target > 0.85" },
            { label: "Domain ARI", value: "0.634", hint: "target > 0.55" },
          ].map((metric) => (
            <div key={metric.label} className="bg-ink-2 px-4 py-3">
              <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                {metric.label}
              </p>
              <p className="mt-1 font-mono text-lg text-bone">{metric.value}</p>
              <p className="mt-0.5 font-mono text-[9px] text-teal/80">{metric.hint}</p>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap gap-x-3 gap-y-1.5 border-t border-line px-4 py-3">
          {DOMAINS.map((domain) => (
            <span key={domain.id} className="inline-flex items-center gap-1.5 text-[10px] text-slate">
              <span className="size-1.5 rounded-full" style={{ background: domain.color }} />
              {domain.name}
            </span>
          ))}
        </div>
      </div>

      <div className="absolute -bottom-4 -left-3 hidden rounded-xl border border-line bg-ink-2 px-3 py-2 shadow-xl sm:block">
        <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate">Uncertainty</p>
        <div className="mt-1.5 flex items-center gap-2">
          <div className="h-1.5 w-24 rounded-full bg-gradient-to-r from-teal via-amber to-coral" />
          <span className="font-mono text-[10px] text-bone">0.08</span>
        </div>
      </div>
    </div>
  );
}
