import { cn } from "@/lib/utils";

export function Progress({
  value,
  className,
  tone = "acid",
}: {
  value: number;
  className?: string;
  tone?: "acid" | "teal" | "coral" | "amber";
}) {
  const tones = {
    acid: "bg-acid",
    teal: "bg-teal",
    coral: "bg-coral",
    amber: "bg-amber",
  };
  return (
    <div className={cn("h-1.5 w-full overflow-hidden rounded-full bg-bone/10", className)}>
      <div
        className={cn("h-full rounded-full transition-[width] duration-500", tones[tone])}
        style={{ width: `${Math.min(100, Math.max(0, value * 100))}%` }}
      />
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-block size-4 animate-spin rounded-full border-2 border-bone/20 border-t-acid",
        className,
      )}
      aria-label="Loading"
    />
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-lg bg-bone/5", className)} />;
}
