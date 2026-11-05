import { ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";

export function RuoNotice({ className, compact = false }: { className?: string; compact?: boolean }) {
  if (compact) {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full border border-amber/40 bg-amber/10 px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-amber",
          className,
        )}
      >
        <ShieldAlert className="size-3" />
        Research use only
      </span>
    );
  }

  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-xl border border-amber/25 bg-amber/[0.06] px-4 py-3",
        className,
      )}
    >
      <ShieldAlert className="mt-0.5 size-4 shrink-0 text-amber" />
      <p className="text-xs leading-relaxed text-amber/90">
        <span className="font-medium text-amber">For Research Use Only.</span> Topiome is not
        intended for diagnosis, prognosis, treatment selection, or clinical decision-making.
        Results are computational inferences from research data and must be independently
        validated.
      </p>
    </div>
  );
}
