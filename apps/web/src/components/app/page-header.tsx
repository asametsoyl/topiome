import { cn } from "@/lib/utils";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  className,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between",
        className,
      )}
    >
      <div className="min-w-0">
        {eyebrow ? <p className="mono-label">{eyebrow}</p> : null}
        <h1 className="display mt-1.5 text-3xl text-bone sm:text-4xl">{title}</h1>
        {description ? (
          <p className="mt-2 max-w-2xl text-xs leading-relaxed text-slate sm:text-sm">
            {description}
          </p>
        ) : null}
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

export function Stat({
  label,
  value,
  hint,
  tone = "bone",
}: {
  label: string;
  value: React.ReactNode;
  hint?: React.ReactNode;
  tone?: "bone" | "acid" | "teal" | "amber" | "coral";
}) {
  const tones = {
    bone: "text-bone",
    acid: "text-acid",
    teal: "text-teal",
    amber: "text-amber",
    coral: "text-coral",
  };
  return (
    <div className="card px-5 py-4">
      <p className="mono-label">{label}</p>
      <p className={cn("mt-2 font-mono text-2xl tracking-tight", tones[tone])}>{value}</p>
      {hint ? <p className="mt-1 text-[10px] leading-relaxed text-slate">{hint}</p> : null}
    </div>
  );
}
