import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "react";

type Variant = "neutral" | "acid" | "teal" | "amber" | "coral" | "outline";

const variants: Record<Variant, string> = {
  neutral: "border-line bg-bone/5 text-bone-dim",
  acid: "border-acid/40 bg-acid/10 text-acid",
  teal: "border-teal/40 bg-teal/10 text-teal",
  amber: "border-amber/40 bg-amber/10 text-amber",
  coral: "border-coral/40 bg-coral/10 text-coral",
  outline: "border-line bg-transparent text-slate",
};

export function Badge({
  className,
  variant = "neutral",
  children,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { variant?: Variant }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.12em]",
        variants[variant],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
